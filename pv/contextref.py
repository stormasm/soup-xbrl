import re
from validate import ValidDate

class ContextRef(object):

    def __init__(self, xbrl):
        self.xbrl = xbrl

    @classmethod
    def processtag_period(self,tag):
        vd = ValidDate()
        #print(tag.period)
        if(tag.period.startdate) == None:
            d1 = tag.period.instant.string
            result = vd.remove_unwanted_chars(d1)
            print(result)
        else:
            d2 = tag.period.startdate.string
            d3 = tag.period.enddate.string
            result = vd.remove_unwanted_chars(d2)
            print(result)
            result = vd.remove_unwanted_chars(d3)
            print(result)

    @classmethod
    def process(self,refs):
        for idx,ref in enumerate(refs):
            print("\n")
            print(idx,"\n")
            print(ref['id'])
            self.processtag_period(ref)
            #print(ref)

    @classmethod
    def getContextTags(self,xbrl):
        doc_root = ""
        context_tags = xbrl.find_all(name=re.compile(doc_root + "context",
                                        re.IGNORECASE | re.MULTILINE))
        return(context_tags)
