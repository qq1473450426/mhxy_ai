import { useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, RefreshCw, ShieldAlert, Swords, WifiOff, Radio, Eye, Target, Clock3 } from 'lucide-react'

type Candidate={state:string;confidence:number;source:string;evidence?:string[]}
type Perception={
 account_id:number; state:string; confidence:number; detector:string; candidates:Candidate[]; ocr_text:string; template_matches:Record<string,unknown>;
 window_available?:boolean; window_rect?:[number,number,number,number]; level?:number; level_known?:boolean; exp_percent?:number; map_name?:string; error?:string
}
type Worker={account_id:number;name:string;state:string;level:number|null;exp_percent:number|null;world:string|null;task:string|null;progress:number;battle:boolean;reconnect_count:number;backup_switch_count:number;character:string|null;role:string|null;updated_at:string|null;error:string|null}
async function api<T>(path:string):Promise<T>{const r=await fetch(path);if(!r.ok)throw Error(await r.text());return r.json()}
const pct=(n:number)=>`${Math.round(Math.min(1,Math.max(0,n))*100)}%`

export default function LiveMonitor(){
 const [workers,setWorkers]=useState<Worker[]>([]),[error,setError]=useState(''),[streaming,setStreaming]=useState(false),[selected,setSelected]=useState<number|null>(null),[perception,setPerception]=useState<Perception|null>(null),[perceptionError,setPerceptionError]=useState('')
 const load=async()=>{try{setError('');setWorkers((await api<{workers:Worker[]}>('/api/live/')).workers)}catch(e){setError(e instanceof Error?e.message:'实时状态获取失败')}}
 const loadPerception=async(id:number)=>{try{setPerceptionError('');setPerception(await api<Perception>(`/api/desktop/${id}/perception/`))}catch(e){setPerception(null);setPerceptionError(e instanceof Error?e.message:'感知状态获取失败')}}
 useEffect(()=>{load();const es=new EventSource('/api/live/stream/');es.onopen=()=>setStreaming(true);es.onerror=()=>setStreaming(false);es.addEventListener('live',e=>{try{setWorkers(JSON.parse((e as MessageEvent).data))}catch{}});const t=setInterval(load,10000);return()=>{es.close();clearInterval(t)}},[])
 useEffect(()=>{if(selected==null){setPerception(null);return}loadPerception(selected);const t=setInterval(()=>loadPerception(selected),1500);return()=>clearInterval(t)},[selected])
 const bad=workers.filter(x=>['DISCONNECTED','ERROR'].includes(x.state)).length,battle=workers.filter(x=>x.battle).length
 const current=useMemo(()=>workers.find(x=>x.account_id===selected)||null,[workers,selected])
 return <div className="livePage">
  <section className="hero"><div><div className="eyebrow">LIVE CONTROL · PERCEPTION</div><h1>实时监控</h1><p>截图由桌面适配器获取，状态由 Perception 只读识别；当前阶段不会执行点击或游戏动作。</p></div><div className="heroActions"><span className={`streamState ${streaming?'on':'off'}`}><Radio size={14}/>{streaming?'实时连接':'等待连接'}</span><button className="primary" onClick={load}><RefreshCw size={15}/>刷新</button></div></section>
  <section className="liveSummary"><div><Activity/><b>{workers.length}</b><span>账号</span></div><div><Swords/><b>{battle}</b><span>战斗中</span></div><div className={bad?'danger':''}><WifiOff/><b>{bad}</b><span>掉线/异常</span></div></section>
  {error&&<div className="liveError"><AlertTriangle size={17}/>{error}</div>}
  <section className="liveGrid">{workers.map(w=><article className={`liveCard ${['DISCONNECTED','ERROR'].includes(w.state)?'hasError':''} ${selected===w.account_id?'selected':''}`} key={w.account_id} onClick={()=>setSelected(w.account_id)}>
   <div className="liveHead"><div><strong>{w.name}</strong><small>#{w.account_id} · {w.character||'角色未识别'}</small></div><span className={`status ${['DISCONNECTED','ERROR'].includes(w.state)?'danger':w.state==='STOPPED'?'muted':'success'}`}><i/>{w.state}</span></div>
   <div className="liveInfo"><div><span>等级</span><b>{w.level??'--'}</b></div><div><span>地图</span><b>{w.world||'未识别'}</b></div><div><span>任务</span><b>{w.task||'空闲'}</b></div></div>
   <div className="liveProgress"><div><span>经验</span><b>{w.exp_percent==null?'--':`${w.exp_percent}%`}</b></div><div className="progress"><i style={{width:`${Math.min(100,Math.max(0,w.exp_percent??0))}%`}}/></div></div>
   <div className="liveFooter"><span>{w.battle?'战斗中':'非战斗'}</span><span>重连 {w.reconnect_count}</span><span>备用 {w.backup_switch_count}</span>{w.error&&<span className="errorText"><ShieldAlert size={13}/>{w.error}</span>}</div>
  </article>)}</section>

  {selected!=null&&<section className="panel perceptionPanel">
    <div className="panelHead"><div><h2><Eye size={17}/> 桌面感知</h2><span>账号 #{selected} · 1.5 秒轮询 · 只读模式</span></div><div className="heroActions"><span className="streamState on"><Target size={14}/>不执行动作</span><button className="iconButton" onClick={()=>loadPerception(selected)} title="立即识别"><RefreshCw size={15}/></button></div></div>
    {perceptionError?<div className="liveError"><AlertTriangle size={17}/>{perceptionError}<span>请先在多开控制中选择并绑定该账号的游戏窗口。</span></div>:perception&&<div className="perceptionBody">
      <div className="perceptionPrimary"><div className="stateBadge"><strong>{perception.state}</strong><span>{pct(perception.confidence)} 置信度</span></div><div className="perceptionMeta"><span><Target size={14}/>来源：{perception.detector||'none'}</span><span><Clock3 size={14}/>窗口：{perception.window_available?'可用':'不可用'}</span><span>OCR：{perception.ocr_text||'无文本证据'}</span></div></div>
      <div className="candidateGrid">{(perception.candidates||[]).sort((a,b)=>b.confidence-a.confidence).map(c=><div className="candidate" key={`${c.state}-${c.source}`}><div><b>{c.state}</b><small>{c.source}{c.evidence?.length?' · '+c.evidence.join(' / '):''}</small></div><strong>{pct(c.confidence)}</strong><i><em style={{width:pct(c.confidence)}}/></i></div>)}{!perception.candidates?.length&&<div className="emptyState">没有足够证据，当前保持 UNKNOWN，不做猜测。</div>}</div>
      <div className="perceptionFacts"><div><span>等级</span><b>{perception.level_known?perception.level:'--'}</b></div><div><span>经验</span><b>{perception.exp_percent==null?'--':`${perception.exp_percent}%`}</b></div><div><span>地图</span><b>{perception.map_name||current?.world||'--'}</b></div></div>
    </div>}
  </section>}
  {!workers.length&&!error&&<div className="emptyState">暂无账号，请先添加账号。</div>}
 </div>
}
