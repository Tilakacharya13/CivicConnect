import { useEffect, useState } from 'react'
import { ChevronDown, LogOut, UserRound } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { Button } from './ui'
import { AnimatePresence, motion } from 'framer-motion'

export default function ProfileDropdown() {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  useEffect(() => { const show = () => setOpen(true); window.addEventListener('civicconnect:open-profile', show); return () => window.removeEventListener('civicconnect:open-profile', show) }, [])
  return <div className="relative"><button onClick={() => setOpen(value => !value)} aria-expanded={open} className="flex items-center gap-2 rounded-xl px-2 py-1.5 text-left transition hover:bg-slate-100 dark:hover:bg-slate-800"><span className="grid size-9 place-items-center rounded-full bg-gradient-to-br from-indigo-100 to-violet-200 text-sm font-bold text-indigo-800 dark:from-indigo-400/20 dark:to-violet-400/20 dark:text-indigo-100">{user?.name?.slice(0, 1)?.toUpperCase() || <UserRound size={16} />}</span><span className="hidden max-w-32 lg:block"><span className="block truncate text-sm font-semibold text-slate-800">{user?.name}</span><span className="block text-xs capitalize text-slate-500">{user?.role}</span></span><ChevronDown size={15} className="text-slate-400" /></button><AnimatePresence>{open&&<motion.div initial={{opacity:0,y:5,scale:.98}} animate={{opacity:1,y:0,scale:1}} exit={{opacity:0,y:5,scale:.98}} className="glass-panel absolute right-0 top-full z-40 mt-2 w-56 rounded-xl p-2 shadow-xl"><div className="px-3 py-2"><p className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">{user?.name}</p><p className="truncate text-xs text-slate-500 dark:text-slate-400">{user?.email || user?.phone_number}</p></div><div className="my-1 border-t border-slate-100 dark:border-slate-700"/><Button variant="ghost" className="w-full justify-start" onClick={() => logout()}><LogOut size={16}/>Log out</Button></motion.div>}</AnimatePresence></div>
}
