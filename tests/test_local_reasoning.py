from app.services.ai import LocalReasoningEngine

def test_reconnect_priority():
    d=LocalReasoningEngine().decide('A01',{'state':'RUNNING','connected':False,'battle_detected':False,'dialog_detected':False,'target_found':False,'task_done':False,'confidence':.1},{'task_name':'test'})
    assert d.action=='RECONNECT'

def test_task_complete():
    d=LocalReasoningEngine().decide('A01',{'state':'RUNNING','connected':True,'battle_detected':False,'dialog_detected':False,'target_found':False,'task_done':True,'confidence':.9},{'task_name':'test'})
    assert d.action=='TASK_COMPLETE'
