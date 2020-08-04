#! /usr/bin/env python
# encoding: utf-8

import re
import collections
import logging

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

    @staticmethod
    def check_textblock(tagname):
        """
        check and see if the tag name contains textblock
        and if it does contain textblock return true
        """
        x = re.search("textblock$", tagname)
        if x == None:
            return False
        return True


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
    def process_context_tags(self,
                  xbrl,
                  doc_date="",
                  context="current",
                  ignore_errors=0):
        """
        Parse context tags from our XBRL soup.
        """

        doc_root = ""

        # we might need to attach the document root
        if len(self.xbrl_base) > 1:
            doc_root = self.xbrl_base

        context_tags = xbrl.find_all(name=re.compile(doc_root + "context",
                                     re.IGNORECASE | re.MULTILINE))

        for context_tag in context_tags:
            print('\n',context_tag,'\n')

        print("number of context tags =",len(context_tags))

    @classmethod
    def process_gaap_tags(self,
                  xbrl,
                  doc_date="",
                  context="current",
                  ignore_errors=0):
        """
        Parse GAAP from our XBRL soup and return a GAAP object.
        """

        us_gaap_tags = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*",
                          re.IGNORECASE | re.MULTILINE))

        for gaap_tag in us_gaap_tags:
            name = gaap_tag.name
            bool = XBRLParser().check_textblock(name)
            if bool:
                return
            # value is a python list
            value = gaap_tag.contents
            if len(value) == 1:
                print(name,value[0])

        print("number of us_gaap_tags =",len(us_gaap_tags))

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
