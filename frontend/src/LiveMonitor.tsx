import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, RefreshCw, ShieldAlert, Swords, WifiOff, Radio } from 'lucide-react'

type Worker={account_id:number;name:string;state:string;level:number|null;exp_percent:number|null;world:string|null;task:string|null;progress:number;battle:boolean;reconnect_count:number;backup_switch_count:number;character:string|null;role:string|null;updated_at:string|null;error:string|null}
async function api<T>(path:string):Promise<T>{const r=await fetch(path);if(!r.ok)throw Error(await r.text());return r.json()}
export default function LiveMonitor(){
 const [workers,setWorkers]=useState<Worker[]>([]),[error,setError]=useState(''),[streaming,setStreaming]=useState(false)
 const load=async()=>{try{setError('');setWorkers((await api<{workers:Worker[]}>('/api/live/')).workers)}catch(e){setError(e instanceof Error?e.message:'实时状态获取失败')}}
 useEffect(()=>{load();const es=new EventSource('/api/live/stream/');es.onopen=()=>setStreaming(true);es.onerror=()=>setStreaming(false);es.addEventListener('live',e=>{try{setWorkers(JSON.parse((e as MessageEvent).data))}catch{}});return()=>es.close()},[])
 const bad=workers.filter(x=>['DISCONNECTED','ERROR'].includes(x.state)).length,battle=workers.filter(x=>x.battle).length
 return <div className="livePage">
  <section className="hero"><div><div className="eyebrow">LIVE CONTROL</div><h1>五开实时监控</h1><p>状态通过实时事件流推送，浏览器断线后会自动恢复。</p></div><div className="heroActions"><span className={`streamState ${streaming?'on':'off'}`}><Radio size={14}/>{streaming?'实时连接':'等待连接'}</span><button className="primary" onClick={load}><RefreshCw size={15}/>刷新</button></div></section>
  <section className="liveSummary"><div><Activity/><b>{workers.length}</b><span>账号</span></div><div><Swords/><b>{battle}</b><span>战斗中</span></div><div className={bad?'danger':''}><WifiOff/><b>{bad}</b><span>掉线/异常</span></div></section>
  {error&&<div className="liveError"><AlertTriangle size={17}/>{error}</div>}
  <section className="liveGrid">{workers.map(w=><article className={`liveCard ${['DISCONNECTED','ERROR'].includes(w.state)?'hasError':''}`} key={w.account_id}>
   <div className="liveHead"><div><strong>{w.name}</strong><small>#{w.account_id} · {w.character||'角色未识别'}</small></div><span className={`status ${['DISCONNECTED','ERROR'].includes(w.state)?'danger':w.state==='STOPPED'?'muted':'success'}`}><i/>{w.state}</span></div>
   <div className="liveInfo"><div><span>等级</span><b>{w.level??'--'}</b></div><div><span>地图</span><b>{w.world||'未识别'}</b></div><div><span>任务</span><b>{w.task||'空闲'}</b></div></div>
   <div className="liveProgress"><div><span>经验</span><b>{w.exp_percent==null?'--':`${w.exp_percent}%`}</b></div><div className="progress"><i style={{width:`${Math.min(100,Math.max(0,w.exp_percent??0))}%`}}/></div></div>
   <div className="liveFooter"><span>{w.battle?'战斗中':'非战斗'}</span><span>重连 {w.reconnect_count}</span><span>备用 {w.backup_switch_count}</span>{w.error&&<span className="errorText"><ShieldAlert size={13}/>{w.error}</span>}</div>
  </article>)}</section>
  {!workers.length&&!error&&<div className="emptyState">暂无账号，请先添加账号。</div>}
 </div>
}
