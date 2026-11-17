import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { Bell, ClipboardList, Home, Plus } from 'lucide-react'
import { useEffect, useState } from 'react'
import api from '../api/client'
import ProfileDropdown from '../components/ProfileDropdown'
import BottomTabBar from '../components/BottomTabBar'
import ThemeToggle from '../theme/ThemeToggle'

const links = [{to:'/citizen/home',label:'Home',icon:Home},{to:'/citizen/my-complaints',label:'My Complaints',icon:ClipboardList},{to:'/citizen/notifications',label:'Notifications',icon:Bell}]
export default function CitizenLayout() {
  const [unread, setUnread] = useState(0)
  const location = useLocation()
  useEffect(() => { api.get('/notifications').then(({data}) => setUnread(data.unread_count)).catch(() => {}) }, [location.pathname])
  return <div className="min-h-screen bg-slate-50 pb-24 md:pb-0"><header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/75 backdrop-blur-xl dark:border-slate-700/50"><div className="container-page flex h-[68px] items-center justify-between"><NavLink to="/citizen/home" className="flex items-center gap-2"><span className="grid size-9 place-items-center rounded-xl bg-gradient-to-br from-indigo-600 via-violet-600 to-cyan-500 text-xs font-black text-white shadow-glow">CC</span><span className="hidden font-extrabold text-slate-900 lg:inline">CivicConnect</span></NavLink><nav className="hidden items-center gap-1 md:flex">{links.map(({to,label,icon:Icon}) => <NavLink key={to} to={to} className={({isActive})=>`flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold ${isActive?'bg-indigo-50 text-indigo-800 dark:bg-indigo-400/10 dark:text-indigo-200':'text-slate-500 hover:bg-slate-50 hover:text-slate-800 dark:hover:bg-slate-800'}`}><Icon size={16}/>{label}{label==='Notifications'&&unread>0&&<span className="ml-1 rounded-full bg-red-100 px-1.5 py-0.5 text-[10px] font-bold text-red-700">{unread}</span>}</NavLink>)}<NavLink to="/citizen/report" className="ml-2 inline-flex items-center gap-2 rounded-xl bg-slate-800 px-4 py-2.5 text-sm font-semibold text-white shadow-glow transition hover:bg-slate-700"><Plus size={16}/>Report issue</NavLink></nav><div className="flex items-center gap-2"><ThemeToggle/><ProfileDropdown/></div></div></header><main className="container-page py-7 sm:py-9"><Outlet/></main><BottomTabBar unread={unread}/></div>
}
