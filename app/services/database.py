import sqlite3,threading,time
from pathlib import Path
class Database:
    def __init__(self,path='data/mhxy.db'):
        Path(path).parent.mkdir(parents=True,exist_ok=True);self.lock=threading.Lock();self.conn=sqlite3.connect(path,check_same_thread=False);self.init()
    def init(self):
        with self.conn:
            self.conn.execute('CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,ts REAL,account_id TEXT,level TEXT,event TEXT,message TEXT)')
            self.conn.execute('CREATE TABLE IF NOT EXISTS worker_state(account_id TEXT PRIMARY KEY,state TEXT,task_name TEXT,reconnect_count INTEGER,last_heartbeat REAL,last_screen_change REAL,error_message TEXT)')
    def event(self,aid,level,event,message):
        with self.lock,self.conn:self.conn.execute('INSERT INTO events(ts,account_id,level,event,message) VALUES(?,?,?,?,?)',(time.time(),aid,level,event,message))
    def state(self,s):
        with self.lock,self.conn:self.conn.execute('INSERT INTO worker_state(account_id,state,task_name,reconnect_count,last_heartbeat,last_screen_change,error_message) VALUES(?,?,?,?,?,?,?) ON CONFLICT(account_id) DO UPDATE SET state=excluded.state,task_name=excluded.task_name,reconnect_count=excluded.reconnect_count,last_heartbeat=excluded.last_heartbeat,last_screen_change=excluded.last_screen_change,error_message=excluded.error_message',(s.account_id,s.state.value,s.task_name,s.reconnect_count,s.last_heartbeat,s.last_screen_change,s.error_message))
    def recent_events(self,limit=200):
        with self.lock:rows=self.conn.execute('SELECT ts,account_id,level,event,message FROM events ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
        return [{'ts':r[0],'account_id':r[1],'level':r[2],'event':r[3],'message':r[4]} for r in rows]
