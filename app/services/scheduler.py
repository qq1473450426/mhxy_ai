class Scheduler:
    def __init__(self):self.workers={}
    def register(self,w):self.workers[w.account_id]=w
    def idle_replacement(self,exclude):
        c=[w for aid,w in self.workers.items() if aid!=exclude and w.is_available_for_replacement()];c.sort(key=lambda x:x.priority,reverse=True);return c[0] if c else None
