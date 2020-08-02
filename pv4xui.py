import os
from pv4xb import XBRLParser, GAAPSerializer

def parse(file):
    print("\nData for ",file)
    xbrl_parser = XBRLParser()
    xbrl = xbrl_parser.parse(open(file))
#   gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date="20200331", context="current", ignore_errors=0)
#   gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date="20191231", context="current", ignore_errors=0)

#   I want this to work so I do not need to know the date for every filing...
#   A blank doc_date should get the current date...
    gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date="20191231")

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)
    print(result)

if __name__ == "__main__":

    f1 = 'ubnt-20200331_htm.xml'
    f2 = 'ubnt-20191231_htm.xml'

    path = os.environ['BMTOP']
    path = path + '/equity-data/edgar/'
    path = path + f2
    parse(path)
