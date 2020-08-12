class ContextRef(object):

    def __init__(self, refs):
        self.refs = refs

    @classmethod
    def format(self,refs):
        for ref in refs:
            print("\n",ref,"\n")
