import os
import re
from pv4xb import XBRLParser

def getdate_from_filename(input):
    p = re.compile('(-)[0-9]*(_)')
    q = p.search(input)
    x = q.group()
    x = x[1:9]
    return(x)

def parse(file):
    print("\nData for ",file)
    xbrl_parser = XBRLParser()
    xbrl = xbrl_parser.parse(open(file))
    #xbrl_parser.process_gaap_tags(xbrl, doc_date="20191231")
    doc_date = getdate_from_filename(file)
    xbrl_parser.process_context_tags(xbrl, doc_date=doc_date)

if __name__ == "__main__":

    f1 = 'ubnt-20200331_htm.xml'
    f2 = 'ubnt-20191231_htm.xml'
    f3 = 'ubnt-20230331_htm.xml'

    path = os.environ['BMTOP']
    path = path + '/edgar-data/ubnt/'
    path = path + f3
    parse(path)
