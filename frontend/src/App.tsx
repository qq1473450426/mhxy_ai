import { useEffect, useState } from 'react'
import {
  Bell, ChevronDown, ChevronLeft, ChevronRight, ClipboardList, FileCheck2, FileText,
  Home, Inbox, Menu, Package, Search, Settings, ShieldCheck, Users, XCircle, Activity,
  BarChart3, CircleDot, MoreHorizontal, RefreshCw,
} from 'lucide-react'

type Status = '运行中' | '待审核' | '已完成' | '已取消'
type Task = { id:string; name:string; type:string; publisher:string; condition:string; status:Status; progress:number; created:string }

const taskRows: Task[] = [
  {id:'100156',name:'降妖伏魔',type:'主线任务',publisher:'GM001',condition:'角色等级 ≥ 30级',status:'运行中',progress:75,created:'2024-05-20 14:30:25'},
  {id:'100155',name:'师门日常',type:'日常任务',publisher:'GM002',condition:'加入门派',status:'运行中',progress:40,created:'2024-05-20 13:15:10'},
  {id:'100154',name:'帮派建设',type:'支线任务',publisher:'GM001',condition:'加入帮派 ≥ 3天',status:'待审核',progress:0,created:'2024-05-20 12:45:33'},
  {id:'100153',name:'科举考试',type:'活动任务',publisher:'GM003',condition:'等级 ≥ 20级',status:'已完成',progress:100,created:'2024-05-20 11:20:18'},
  {id:'100152',name:'宝图任务',type:'日常任务',publisher:'GM001',condition:'等级 ≥ 25级',status:'已完成',progress:100,created:'2024-05-20 10:05:42'},
  {id:'100151',name:'节日活动',type:'活动任务',publisher:'GM002',condition:'活动期间',status:'已取消',progress:0,created:'2024-05-20 09:30:15'},
  {id:'100150',name:'隐藏剧情',type:'隐藏任务',publisher:'GM003',condition:'完成前置任务',status:'运行中',progress:60,created:'2024-05-20 08:22:31'},
  {id:'100149',name:'竞技挑战',type:'特殊任务',publisher:'GM001',condition:'PVP排名 ≥ 100名',status:'待审核',progress:0,created:'2024-05-19 16:45:20'},
]
const navTop = [
  {label:'首页',icon:Home},{label:'玩家管理',icon:Users},{label:'任务管理',icon:ClipboardList,active:true},
  {label:'物品管理',icon:Package},{label:'数据统计',icon:BarChart3},{label:'系统设置',icon:Settings},
]
const navGroups = [
  {title:'任务管理',items:['任务列表','创建任务','任务模板','任务审核','任务日志']},
  {title:'任务分类',items:['主线任务','支线任务','日常任务','活动任务','隐藏任务','特殊任务']},
]
const typeClass:Record<string,string>={主线任务:'tag red',日常任务:'tag blue',支线任务:'tag green',活动任务:'tag purple',隐藏任务:'tag amber',特殊任务:'tag pink'}
const statusClass:Record<Status,string>={运行中:'status success',待审核:'status warning',已完成:'status info',已取消:'status danger'}

function Kpi({icon:Icon,title,value,tone,trend}:{icon:React.ElementType,title:string,value:number,tone:string,trend:string}){
  return <div className={`kpi ${tone}`}><div className="kpiIcon"><Icon size={18}/></div><div><div className="kpiTitle">{title}</div><div className="kpiValue">{value}<span className="unit">个</span></div><div className="kpiTrend">较昨日 <b>{trend}</b></div></div></div>
}

function App(){
  const [mobileNav,setMobileNav]=useState(false)
  const [refreshAt,setRefreshAt]=useState(new Date())
  const [apiOnline,setApiOnline]=useState(false)
  useEffect(()=>{const ping=async()=>{try{const r=await fetch('/api/status/',{cache:'no-store'});setApiOnline(r.ok)}catch{setApiOnline(false)}};ping();const t=window.setInterval(()=>{ping();setRefreshAt(new Date())},2000);return()=>window.clearInterval(t)},[])
  return <div className="appShell">
    <header className="topbar">
      <div className="brandBlock"><div className="brandMark">GM</div><div><div className="brandTitle">GM任务管理系统</div><div className="brandSub">游戏运营管理后台</div></div></div>
      <button className="mobileMenu" onClick={()=>setMobileNav(v=>!v)}><Menu size={20}/></button>
      <nav className="topNav">{navTop.map(({label,icon:Icon,active})=><button key={label} className={active?'topNavItem active':'topNavItem'}><Icon size={19}/><span>{label}</span></button>)}</nav>
      <div className="topActions"><div className="notif"><Bell size={19}/><i>12</i></div><div className="notif"><Inbox size={19}/><i>5</i></div><div className="avatar">GM</div><div className="profile"><b>GM001</b><span><CircleDot size={10} fill="currentColor"/> 在线</span></div><ChevronDown size={17}/></div>
    </header>
    <aside className={mobileNav?'sidebar open':'sidebar'}><div className="sideInner">
      {navGroups.map(group=><div className="navSection" key={group.title}><div className="sectionTitle">{group.title}<ChevronDown size={14}/></div>{group.items.map((item,idx)=><button className={item==='任务列表'?'sideItem active':'sideItem'} key={item}><span className="miniIcon">{idx===0?<FileText size={14}/>:<CircleDot size={10}/>}</span>{item}</button>)}</div>)}
      <div className="serverCard"><div className="serverTitle">当前服务器</div><div className="serverName">梦幻西游 · 再续前缘</div><div className="serverState"><span className={apiOnline?'dot on':'dot'}></span>{apiOnline?'运行中':'本地UI'}</div><div className="serverVersion">版本：v2.3.0</div></div>
    </div></aside>
    <main className="mainContent">
      <section className="filterBar">
        <label>任务名称<input placeholder="请输入任务名称"/></label><label>任务类型<select defaultValue="全部类型"><option>全部类型</option><option>主线任务</option><option>日常任务</option></select></label><label>任务状态<select defaultValue="全部状态"><option>全部状态</option><option>运行中</option><option>待审核</option><option>已完成</option></select></label>
        <label>创建时间<div className="dateRange"><input placeholder="开始日期"/><span>至</span><input placeholder="结束日期"/></div></label><button className="primary"><Search size={15}/>查询</button><button className="ghost" onClick={()=>setRefreshAt(new Date())}><RefreshCw size={14}/>重置</button>
      </section>
      <section className="kpiGrid"><Kpi icon={ClipboardList} title="任务总数" value={156} tone="blue" trend="+12 ↓"/><Kpi icon={Activity} title="进行中" value={68} tone="green" trend="+8 ↓"/><Kpi icon={FileCheck2} title="待审核" value={23} tone="amber" trend="-3 ↓"/><Kpi icon={ShieldCheck} title="已完成" value={65} tone="purple" trend="+7 ↓"/><Kpi icon={XCircle} title="已取消" value={8} tone="red" trend="-2 ↓"/></section>
      <section className="panel taskPanel"><div className="panelHead"><div><h2>任务列表</h2><span>实时同步 · {refreshAt.toLocaleTimeString()}</span></div><div className="panelActions"><button className="ghost">批量操作 <ChevronDown size={14}/></button><button className="ghost">导出数据</button></div></div>
        <div className="tableWrap"><table><thead><tr><th><input type="checkbox"/></th><th>任务ID</th><th>任务名称</th><th>任务类型</th><th>发布人</th><th>接取条件</th><th>状态</th><th>进度</th><th>创建时间</th><th>操作</th></tr></thead><tbody>{taskRows.map(row=><tr key={row.id}><td><input type="checkbox"/></td><td>{row.id}</td><td className="nameCell">{row.name}</td><td><span className={typeClass[row.type]}>{row.type}</span></td><td>{row.publisher}</td><td>{row.condition}</td><td><span className={statusClass[row.status]}>{row.status}</span></td><td>{row.progress?<div className="progressCell"><div className="progress"><i style={{width:`${row.progress}%`}}/></div><span>{row.progress}%</span></div>:<span className="muted">-</span>}</td><td>{row.created}</td><td><div className="rowActions"><button>编辑</button><button>详情</button><button><MoreHorizontal size={15}/></button></div></td></tr>)}</tbody></table></div>
        <div className="tableFoot"><span>显示第 1 到第 8 条记录，总共 156 条记录</span><div className="pager"><button><ChevronLeft size={14}/></button><button className="current">1</button><button>2</button><button>3</button><button>4</button><button>5</button><button>…</button><button>20</button><button><ChevronRight size={14}/></button><button>10条/页 <ChevronDown size={13}/></button></div></div>
      </section>
      <section className="bottomGrid">
        <div className="panel chartPanel"><div className="panelHead slim"><div><h2>任务统计</h2><span>最近7天</span></div><button className="selectLite">最近7天 <ChevronDown size={13}/></button></div><div className="lineChart"><div className="yAxis"><span>100</span><span>80</span><span>60</span><span>40</span><span>20</span><span>0</span></div><svg viewBox="0 0 420 150" preserveAspectRatio="none"><defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#1890ff" stopOpacity=".38"/><stop offset="100%" stopColor="#1890ff" stopOpacity="0"/></linearGradient></defs><path d="M0,85 C35,50 45,98 72,68 S117,45 130,55 175,60 190,38 228,52 245,64 274,70 296,61 331,55 345,69 375,75 395,48 420,40 L420,150 L0,150 Z" fill="url(#area)"/><path d="M0,85 C35,50 45,98 72,68 S117,45 130,55 175,60 190,38 228,52 245,64 274,70 296,61 331,55 345,69 375,75 395,48 420,40" fill="none" stroke="#4aa3ff" strokeWidth="2"/><g fill="#4aa3ff">{[[0,85],[72,68],[130,55],[190,38],[245,64],[296,61],[345,69],[420,40]].map(([x,y])=><circle key={`${x}-${y}`} cx={x} cy={y} r="3"/>)}</g></svg><div className="xAxis"><span>05-14</span><span>05-15</span><span>05-16</span><span>05-17</span><span>05-18</span><span>05-19</span><span>05-20</span></div></div><div className="chartLegend"><span className="legendDot blue"></span>任务数量</div></div>
        <div className="panel donutPanel"><div className="panelHead slim"><h2>任务类型分布</h2></div><div className="donutRow"><div className="donut"><div className="donutHole"><b>156</b><span>任务总数</span></div></div><div className="legendList"><div><i className="c red"></i>主线任务 <span>28 (17.9%)</span></div><div><i className="c green"></i>支线任务 <span>32 (20.5%)</span></div><div><i className="c blue"></i>日常任务 <span>45 (28.8%)</span></div><div><i className="c purple"></i>活动任务 <span>25 (16.0%)</span></div><div><i className="c amber"></i>隐藏任务 <span>15 (9.6%)</span></div><div><i className="c slate"></i>特殊任务 <span>11 (7.1%)</span></div></div></div></div>
        <div className="panel noticePanel"><div className="panelHead slim"><h2>系统公告</h2><button className="linkBtn">更多</button></div><ul>{['2024年5月20日 版本更新公告','服务器维护通知','新活动【端午节】即将开启','违规玩家处理公告','任务系统优化说明'].map((x,i)=><li key={x}><span>• {x}</span><time>{['05-20','05-19','05-18','05-17','05-16'][i]}</time></li>)}</ul></div>
      </section>
    </main>
  </div>
}

export default App
