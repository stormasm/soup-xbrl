import os
from bluemesa.edgar.pv2x import XBRLParser, GAAPSerializer, DEISerializer
#from xbrl import XBRLParser, GAAPSerializer, DEISerializer

def getfiles(mypath):
    files = set()
    for file in os.listdir(mypath):
        if file.endswith(".xml"):
            files.add(os.path.join(mypath, file))
    return(files)

def parse(file):
    print("\nData for ",file)
    xbrl_parser = XBRLParser()
    xbrl = xbrl_parser.parse(open(file))
    #gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date="20131228", context="current", ignore_errors=0)
    gaap_obj = xbrl_parser.parseGAAP(xbrl, context="current", ignore_errors=0)
    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)
    #print(result)
    #dei_obj = xbrl_parser.parseDEI(xbrl)
    #serializer = DEISerializer()
    #result = serializer.dump(dei_obj)
    print(result)

if __name__ == "__main__":
    path = os.environ['BMTOP']
    # path = path + '/equity-data/edgar'
    path = path + '/tmp/edgar'
    files = getfiles(path)
    for file in files:
        parse(file)
