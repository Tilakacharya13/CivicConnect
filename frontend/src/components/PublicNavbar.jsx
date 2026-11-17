import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, Menu, X } from 'lucide-react'
import { Button } from './ui'
import ThemeToggle from '../theme/ThemeToggle'

export default function PublicNavbar() {
  const [open, setOpen] = useState(false)
  return <header className="relative z-30 border-b border-slate-200/70 bg-white/75 backdrop-blur-xl dark:border-slate-700/50"><div className="container-page flex h-[72px] items-center justify-between"><Link to="/" className="flex items-center gap-2.5"><span className="grid size-9 place-items-center rounded-xl bg-gradient-to-br from-indigo-600 via-violet-600 to-cyan-500 text-xs font-black text-white shadow-glow">CC</span><span className="text-lg font-extrabold tracking-tight text-slate-900">CivicConnect</span></Link><nav className="hidden items-center gap-3 md:flex"><ThemeToggle/><Link className="rounded-xl px-3 py-2 text-sm font-semibold text-slate-600 hover:text-slate-900" to="/login">Login</Link><Button as={Link} to="/register" className="px-4 py-2">Sign up <ArrowUpRight size={16}/></Button></nav><div className="flex items-center gap-2 md:hidden"><ThemeToggle/><button onClick={() => setOpen(!open)} className="grid size-10 place-items-center rounded-xl border border-slate-200 text-slate-700 dark:border-slate-700 dark:text-white" aria-label={open ? 'Close navigation' : 'Open navigation'}>{open ? <X/> : <Menu/>}</button></div></div>{open && <nav className="absolute inset-x-0 top-full border-b border-slate-200 bg-white p-4 shadow-lg dark:border-slate-700 dark:bg-slate-900 md:hidden"><div className="container-page grid gap-2"><Link onClick={() => setOpen(false)} className="rounded-xl px-4 py-3 font-semibold text-slate-700 hover:bg-slate-50" to="/login">Login</Link><Link onClick={() => setOpen(false)} className="rounded-xl bg-slate-800 px-4 py-3 text-center font-semibold text-white" to="/register">Sign up to report an issue</Link></div></nav>}</header>
}
