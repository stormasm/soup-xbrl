import os
import re
from pvxc import XBRLParser, GAAPSerializer

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
#   gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date="20200331", context="current", ignore_errors=0)
#   gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date="20191231", context="current", ignore_errors=0)

#   I want this to work so I do not need to know the date for every filing...
#   A blank doc_date should get the current date...

    doc_date = getdate_from_filename(file)
    gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date=doc_date)

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)
    print(result)

if __name__ == "__main__":

    f1 = 'ubnt-20201231_htm.xml'
    f2 = 'ubnt-20191231_htm.xml'
    f3 = 'ubnt-20230331_htm.xml'

    path = os.environ['BMTOP']
    path = path + '/edgar-data/ubnt/'
    path = path + f3
    parse(path)
