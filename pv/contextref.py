class ContextRef(object):

    def __init__(self, refs):
        self.refs = refs

    @classmethod
    def format(self,refs):
        for idx,ref in enumerate(refs):
            print("\n")
            print(idx,"\n")
            print(ref)
