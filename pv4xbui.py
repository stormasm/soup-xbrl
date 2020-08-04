import os
from pv4xb import XBRLParser

def parse(file):
    print("\nData for ",file)
    xbrl_parser = XBRLParser()
    xbrl = xbrl_parser.parse(open(file))
    #xbrl_parser.process_gaap_tags(xbrl, doc_date="20191231")
    xbrl_parser.process_context_tags(xbrl, doc_date="20191231")


if __name__ == "__main__":

    f1 = 'ubnt-20200331_htm.xml'
    f2 = 'ubnt-20191231_htm.xml'

    path = os.environ['BMTOP']
    path = path + '/equity-data/edgar/'
    path = path + f2
    parse(path)
