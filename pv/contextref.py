import re

class ContextRef(object):

    def __init__(self, xbrl):
        self.xbrl = xbrl

    @classmethod
    def processtag_period(self,tag):
        #print(tag.period)
        if(tag.period.startdate) == None:
            print(tag.period.instant.string)
        else:
            print(tag.period.startdate.string)
            print(tag.period.enddate.string)

    @classmethod
    def format(self,refs):
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
