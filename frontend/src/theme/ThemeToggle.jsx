import { Moon, Sun } from 'lucide-react'
import { useTheme } from './ThemeContext'
export default function ThemeToggle({ className = '' }) {
  const { theme, toggleTheme } = useTheme()
  const dark = theme === 'dark'
  return <button type="button" onClick={toggleTheme} aria-label={`Switch to ${dark ? 'light' : 'dark'} mode`} title={`Switch to ${dark ? 'light' : 'dark'} mode`} className={`grid size-10 place-items-center rounded-xl border border-slate-200/70 bg-white/70 text-slate-600 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-700/70 dark:bg-slate-900/70 dark:text-slate-200 ${className}`}>{dark ? <Sun size={17} /> : <Moon size={17} />}</button>
}
