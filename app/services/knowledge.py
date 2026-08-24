from pathlib import Path
class KnowledgeService:
    def __init__(self,root='knowledge/xyq-skills'):self.root=Path(root)
    def available(self):return self.root.exists()
    def search(self,query,max_files=5):
        if not self.available():return []
        out=[]
        for p in self.root.rglob('*.md'):
            text=p.read_text(encoding='utf-8',errors='ignore')
            if query.lower() in text.lower():out.append({'file':str(p),'snippet':text[:1000]})
            if len(out)>=max_files:break
        return out
    def context(self,q):return '\n\n'.join(f"[{x['file']}]\n{x['snippet']}" for x in self.search(q))
