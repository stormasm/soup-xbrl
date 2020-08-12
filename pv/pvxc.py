#! /usr/bin/env python
# encoding: utf-8

import re
from marshmallow import Schema, fields
import datetime
import collections
import six
import logging
from contextref import ContextRef


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

if 'OrderedDict' in dir(collections):
    odict = collections
else:
    import ordereddict as odict


def soup_maker(fh):
    """ Takes a file handler returns BeautifulSoup"""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(fh, "lxml")
        for tag in soup.find_all():
            tag.name = tag.name.lower()
    except ImportError:
        from BeautifulSoup import BeautifulStoneSoup
        soup = BeautifulStoneSoup(fh)
    return soup


class XBRLFile(object):
    def __init__(self, fh):
        """
        fh should be a seekable file-like byte stream object
        """
        self.headers = odict.OrderedDict()
        self.fh = fh


class XBRLParserException(Exception):
    pass


class XBRLParser(object):

    def __init__(self, precision=0):
        self.precision = precision

    @classmethod
    def parse(self, file_handle):
        """
        parse is the main entry point for an XBRLParser. It takes a file
        handle.
        """

        xbrl_obj = XBRL()

        # if no file handle was given create our own
        if not hasattr(file_handle, 'read'):
            file_handler = open(file_handle)
        else:
            file_handler = file_handle

        # Store the headers
        xbrl_file = XBRLPreprocessedFile(file_handler)

        xbrl = soup_maker(xbrl_file.fh)
        file_handler.close()
        xbrl_base = xbrl.find(name=re.compile("xbrl*:*"))

        if xbrl.find('xbrl') is None and xbrl_base is None:
            raise XBRLParserException('The xbrl file is empty!')

        # lookahead to see if we need a custom leading element
        lookahead = xbrl.find(name=re.compile("context",
                              re.IGNORECASE | re.MULTILINE)).name
        if ":" in lookahead:
            self.xbrl_base = lookahead.split(":")[0] + ":"
        else:
            self.xbrl_base = ""

        return xbrl

    @classmethod
    def parseGAAP(self,
                  xbrl,
                  doc_date="",
                  context="current",
                  ignore_errors=0):
        """
        Parse GAAP from our XBRL soup and return a GAAP object.
        """
        gaap_obj = GAAP()

        if ignore_errors == 2:
            logging.basicConfig(filename='/tmp/xbrl.log',
                level=logging.ERROR,
                format='%(asctime)s %(levelname)s %(name)s %(message)s')
            logger = logging.getLogger(__name__)
        else:
            logger = None

        # the default is today
        if doc_date == "":
            doc_date = str(datetime.date.today())
        doc_date = re.sub(r"[^0-9]+", "", doc_date)

        # current is the previous quarter
        if context == "current":
            context = 90

        if context == "year":
            context = 360

        context = int(context)

        if context % 90 == 0:
            context_extended = list(range(context, context + 9))
            expected_start_date = \
                datetime.datetime.strptime(doc_date, "%Y%m%d") \
                - datetime.timedelta(days=context)
        elif context == "instant":
            expected_start_date = None
        else:
            raise XBRLParserException('invalid context')

        # we need expected end date unless instant
        if context != "instant":
            expected_end_date = \
                datetime.datetime.strptime(doc_date, "%Y%m%d")

        doc_root = ""

        # we might need to attach the document root
        if len(self.xbrl_base) > 1:
            doc_root = self.xbrl_base

        # collect all contexts up that are relevant to us
        # TODO - Maybe move this to Preprocessing Ingestion
        context_ids = []
        context_tags = xbrl.find_all(name=re.compile(doc_root + "context",
                                     re.IGNORECASE | re.MULTILINE))

        cr = ContextRef(context_tags)
        cr.refs = context_tags
        cr.format(context_tags)

        print("number of context_tags =",len(context_tags))

        try:
            for context_tag in context_tags:

                #print("\n",context_tag,"\n")

                # we don't want any segments
                if context_tag.find(doc_root + "entity") is None:
                    continue
                if context_tag.find(doc_root + "entity").find(
                doc_root + "segment") is None:
                    context_id = context_tag.attrs['id']

                    found_start_date = None
                    found_end_date = None

                    if context_tag.find(doc_root + "instant"):
                        instant = \
                            datetime.datetime.strptime(re.compile('[^\d]+')
                                                       .sub('', context_tag
                                                       .find(doc_root +
                                                             "instant")
                                                        .text)[:8], "%Y%m%d")
                        if instant == expected_end_date:
                            context_ids.append(context_id)
                            continue

                    if context_tag.find(doc_root + "period").find(
                    doc_root + "startdate"):
                        found_start_date = \
                            datetime.datetime.strptime(re.compile('[^\d]+')
                                                       .sub('', context_tag
                                                       .find(doc_root +
                                                             "period")
                                                       .find(doc_root +
                                                             "startdate")
                                                        .text)[:8], "%Y%m%d")
                    if context_tag.find(doc_root + "period").find(doc_root +
                    "enddate"):
                        found_end_date = \
                            datetime.datetime.strptime(re.compile('[^\d]+')
                                                       .sub('', context_tag
                                                       .find(doc_root +
                                                             "period")
                                                       .find(doc_root +
                                                             "enddate")
                                                       .text)[:8], "%Y%m%d")
                    if found_end_date and found_start_date:
                        for ce in context_extended:
                            if found_end_date - found_start_date == \
                            datetime.timedelta(days=ce):
                                if found_end_date == expected_end_date:
                                    context_ids.append(context_id)
        except IndexError:
            raise XBRLParserException('problem getting contexts')

        liabilities_and_equity = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(liabilitiesand)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.liabilities_and_equity = \
            self.data_processing(liabilities_and_equity, xbrl,
                ignore_errors, logger, context_ids)

        liabilities = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(liabilities)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.liabilities = \
            self.data_processing(liabilities, xbrl, ignore_errors,
                logger, context_ids)

        cash_and_cashequivalents = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(cashandcashequivalentsatcarryingvalue)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.cash_and_cashequivalents = \
            self.data_processing(cash_and_cashequivalents, xbrl, ignore_errors,
                logger, context_ids)


        return gaap_obj

    @staticmethod
    def trim_decimals(s, precision=-3):
        """
        Convert from scientific notation using precision
        """
        encoded = s.encode('ascii', 'ignore')
        str_val = ""
        if six.PY3:
            str_val = str(encoded, encoding='ascii', errors='ignore')[:precision]
        else:
            # If precision is 0, this must be handled seperately
            if precision == 0:
                str_val = str(encoded)
            else:
                str_val = str(encoded)[:precision]
        if len(str_val) > 0:
            return float(str_val)
        else:
            return 0

    @staticmethod
    def is_number(s):
        """
        Test if value is numeric
        """
        try:
            s = float(s)
            return True
        except ValueError:
            return False

    @classmethod
    def data_processing(self,
                        elements,
                        xbrl,
                        ignore_errors,
                        logger,
                        context_ids=[],
                        **kwargs):
        """
        Process a XBRL tag object and extract the correct value as
        stated by the context.
        """
        options = kwargs.get('options', {'type': 'Number',
                                         'no_context': False})

        if options['type'] == 'String':
            if len(elements) > 0:
                    return elements[0].text

        if options['no_context'] == True:
            if len(elements) > 0 and XBRLParser().is_number(elements[0].text):
                    return elements[0].text

        ### So this took me awhile to figure out so I will document here:
        ### elements is a soup class called ResultSet which is a Python list
        ### elements[0] is a <class 'bs4.element.Tag'>
        ### elements[0].name is the tag name
        ### print(type(elements[0]))
        ### print(elements[0].name)
        ### show the context ids
        ### for context_id in context_ids:
        ###     print(context_id)

        try:

            # Extract the correct values by context
            correct_elements = []
            for element in elements:
                std = element.attrs['contextref']
                if std in context_ids:
                    correct_elements.append(element)
            elements = correct_elements

            if len(elements) > 0 and XBRLParser().is_number(elements[0].text):
                decimals = elements[0].attrs['decimals']
                if decimals is not None:
                    attr_precision = decimals
                    if xbrl.precision != 0 \
                    and xbrl.precison != attr_precision:
                        xbrl.precision = attr_precision
                if elements:
                    return XBRLParser().trim_decimals(elements[0].text,
                        int(xbrl.precision))
                else:
                    return 0
            else:
                return 0
        except Exception as e:
            if ignore_errors == 0:
                raise XBRLParserException('value extraction error')
            elif ignore_errors == 1:
                return 0
            elif ignore_errors == 2:
                logger.error(str(e) + " error at " +
                    ''.join(elements[0].text))


# Preprocessing to fix broken XML
# TODO - Run tests to see if other XML processing errors can occur
class XBRLPreprocessedFile(XBRLFile):
    def __init__(self, fh):
        super(XBRLPreprocessedFile, self).__init__(fh)

        if self.fh is None:
            return

        xbrl_string = self.fh.read()

        # find all closing tags as hints
        closing_tags = [t.upper() for t in re.findall(r'(?i)</([a-z0-9_\.]+)>',
                        xbrl_string)]

        # close all tags that don't have closing tags and
        # leave all other data intact
        last_open_tag = None
        tokens = re.split(r'(?i)(</?[a-z0-9_\.]+>)', xbrl_string)
        new_fh = StringIO()
        for idx, token in enumerate(tokens):
            is_closing_tag = token.startswith('</')
            is_processing_tag = token.startswith('<?')
            is_cdata = token.startswith('<!')
            is_tag = token.startswith('<') and not is_cdata
            is_open_tag = is_tag and not is_closing_tag \
                and not is_processing_tag
            if is_tag:
                if last_open_tag is not None:
                    new_fh.write("</%s>" % last_open_tag)
                    last_open_tag = None
            if is_open_tag:
                tag_name = re.findall(r'(?i)<*>', token)[0]
                if tag_name.upper() not in closing_tags:
                    last_open_tag = tag_name
            new_fh.write(token)
        new_fh.seek(0)
        self.fh = new_fh


class XBRL(object):
    def __str__(self):
        return ""


# Base GAAP object
class GAAP(object):
    def __init__(self,
                 liabilities_and_equity=0.0,
                 liabilities=0.0,
                 cash_and_cashequivalents=0.0):

        self.liabilities_and_equity = liabilities_and_equity
        self.liabilities = liabilities
        self.cash_and_cashequivalents = cash_and_cashequivalents

class GAAPSerializer(Schema):
    liabilities_and_equity = fields.Number()
    liabilities = fields.Number()
    cash_and_cashequivalents = fields.Number()

# Base Custom object
class Custom(object):

    def __init__(self):
        return None

    def __call__(self):
        return self.__dict__.items()
