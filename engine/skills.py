from pathlib import Path
import re

class SkillStore:
    """读取本地 Skill 文件；支持关键词检索和简单坐标提取。"""
    def __init__(self,root='skills'):
        self.root=Path(root)
        self.knowledge_root=Path('xyq-skills')
    def files(self):
        roots=(self.root, self.knowledge_root)
        return [p for root in roots if root.exists() for p in root.rglob('*.md') if p.is_file()]
    def search(self,query):
        out=[]
        for p in self.files():
            try:t=p.read_text(encoding='utf-8',errors='ignore')
            except Exception:continue
            if query.lower() in t.lower() or query.lower() in p.stem.lower():out.append({'file':str(p),'text':t[:4000]})
        return out[:20]
    def coordinates(self,query):
        out=[]
        for hit in self.search(query):
            for x,y in re.findall(r'x\s*[:=]\s*(-?\d+).*?y\s*[:=]\s*(-?\d+)',hit['text'],re.I|re.S):out.append({'x':int(x),'y':int(y),'file':hit['file']})
        return out
