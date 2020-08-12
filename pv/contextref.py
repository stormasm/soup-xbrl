import re

class ContextRef(object):

    def __init__(self, xbrl):
        self.xbrl = xbrl

    @classmethod
    def format(self,refs):
        for idx,ref in enumerate(refs):
            print("\n")
            print(idx,"\n")
            print(ref)

    @classmethod
    def getContextTags(self,xbrl):
        doc_root = ""
        context_tags = xbrl.find_all(name=re.compile(doc_root + "context",
                                        re.IGNORECASE | re.MULTILINE))
        return(context_tags)
