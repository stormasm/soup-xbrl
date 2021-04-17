import os
import re
from pvx0 import XBRLParser, GAAPSerializer, DEISerializer

def getfiles(mypath):
    files = set()
    for file in os.listdir(mypath):
        if file.endswith(".xml"):
            files.add(os.path.join(mypath, file))
    return(files)


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
    doc_date = getdate_from_filename(file)
    gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date=doc_date, context="current", ignore_errors=0)
    #gaap_obj = xbrl_parser.parseGAAP(xbrl, context="current", ignore_errors=0)
    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)
    #print(result)
    #dei_obj = xbrl_parser.parseDEI(xbrl)
    #serializer = DEISerializer()
    #result = serializer.dump(dei_obj)
    print(result)

if __name__ == "__main__":

    f1 = '/ubnt-20201231_htm.xml'
    f2 = '/ubnt-20191231_htm.xml'

    path = os.environ['BMTOP']
    path = path + '/edgar-data/ubnt'
    #path = path + '/tmp/edgar'

#   files = getfiles(path)
#   for path in files:
#       parse(path)
    path = path + f1
    parse(path)
