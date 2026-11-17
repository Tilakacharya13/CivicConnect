import { Bell, ClipboardList, Home, Plus, UserRound } from 'lucide-react'
import { NavLink, useLocation } from 'react-router-dom'

const tabs = [
  { to: '/citizen/home', label: 'Home', icon: Home },
  { to: '/citizen/my-complaints', label: 'My cases', icon: ClipboardList },
  { to: '/citizen/report', label: 'Report', icon: Plus },
  { to: '/citizen/notifications', label: 'Alerts', icon: Bell },
]
export default function BottomTabBar({ unread = 0 }) {
  const location = useLocation()
  return <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-slate-200 bg-white/95 px-1 pb-[max(env(safe-area-inset-bottom),8px)] pt-2 backdrop-blur md:hidden"><div className="mx-auto grid max-w-lg grid-cols-5">{tabs.slice(0, 2).map(({ to,label,icon:Icon }) => <NavLink key={to} to={to} className={({isActive}) => `flex flex-col items-center gap-1 py-1 text-[10px] font-semibold ${isActive ? 'text-slate-900' : 'text-slate-400'}`}><Icon size={19}/>{label}</NavLink>)}<NavLink to="/citizen/report" className={({isActive}) => `-mt-5 mx-auto grid size-12 place-items-center rounded-2xl border-4 border-slate-50 shadow-lg ${isActive ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-white'}`} aria-label="Report issue"><Plus size={22}/></NavLink>{tabs.slice(3).map(({ to,label,icon:Icon }) => <NavLink key={to} to={to} className={({isActive}) => `relative flex flex-col items-center gap-1 py-1 text-[10px] font-semibold ${isActive ? 'text-slate-900' : 'text-slate-400'}`}><Icon size={19}/>{label}{label==='Alerts'&&unread>0&&<span className="absolute right-1 top-0 size-2 rounded-full bg-red-500"/>}</NavLink>)}<button onClick={() => window.dispatchEvent(new CustomEvent('civicconnect:open-profile'))} className={`flex flex-col items-center gap-1 py-1 text-[10px] font-semibold ${location.pathname === '/citizen/profile' ? 'text-slate-900' : 'text-slate-400'}`}><UserRound size={19}/>Profile</button></div></nav>
}
