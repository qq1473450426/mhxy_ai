from dataclasses import dataclass,field
from typing import Any
@dataclass
class CandidateAction:
    action:str; score:float; reason:str; params:dict[str,Any]=field(default_factory=dict)
@dataclass
class Decision:
    action:str; confidence:float; reason:str; params:dict[str,Any]=field(default_factory=dict); alternatives:list[CandidateAction]=field(default_factory=list)
class LocalReasoningEngine:
    def __init__(self): self.memory={}
    def mem(self,aid): return self.memory.setdefault(aid,{'last_action':'','last_result':'','failed':{},'repeat':0})
    def remember_result(self,aid,action,result):
        m=self.mem(aid);m['repeat']=m['repeat']+1 if m['last_action']==action else 1;m['last_action']=action;m['last_result']=result
        if result!='success':m['failed'][action]=m['failed'].get(action,0)+1
    def candidates(self,o):
        state=o.get('state','UNKNOWN');connected=o.get('connected',True);battle=o.get('battle_detected',False);dialog=o.get('dialog_detected',False);done=o.get('task_done',False);target=o.get('target_found',False);conf=float(o.get('confidence',0))
        c=[]
        if not connected:c.append(CandidateAction('RECONNECT',1,'连接异常优先恢复'))
        if done:c.append(CandidateAction('TASK_COMPLETE',.99,'任务已完成'))
        if battle and target:c.append(CandidateAction('BATTLE_ACTION',.93,'战斗且目标明确'))
        elif battle:c.append(CandidateAction('WAIT_BATTLE',.72,'战斗中目标不确定'))
        if dialog:c.append(CandidateAction('HANDLE_DIALOG',.86,'发现对话界面'))
        if state in ('IDLE','RUNNING') and connected and not done:c.append(CandidateAction('CONTINUE_TASK',.82+min(conf,.15),'任务仍在运行'))
        c.append(CandidateAction('WAIT',.35,'证据不足，先观察'));return c
    def decide(self,aid,observation,task):
        m=self.mem(aid);c=self.candidates(observation)
        for x in c:
            x.score-=min(m['failed'].get(x.action,0)*.08,.30)
            if x.action==m['last_action'] and m['repeat']>=4:x.score-=.20
        if m['repeat']>=4:c.append(CandidateAction('WAIT',.70,'同一动作重复过多，先观察'))
        c.sort(key=lambda x:x.score,reverse=True);b=c[0]
        return Decision(b.action,max(0,min(1,b.score)),b.reason,b.params,c[:5])
