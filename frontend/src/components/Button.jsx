import { LoaderCircle } from 'lucide-react'
import { Link } from 'react-router-dom'

const variants = {
  primary: 'bg-brand-600 text-white shadow-sm hover:bg-brand-700 focus-visible:ring-brand-200',
  secondary: 'border border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50 focus-visible:ring-slate-200',
  ghost: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 focus-visible:ring-slate-200',
  dark: 'bg-slate-900 text-white hover:bg-slate-800 focus-visible:ring-slate-300',
  danger: 'bg-rose-600 text-white hover:bg-rose-700 focus-visible:ring-rose-200',
}

const sizes = {
  sm: 'min-h-9 px-3.5 text-xs',
  md: 'min-h-11 px-5 text-sm',
  lg: 'min-h-12 px-6 text-sm',
}

export default function Button({ variant = 'primary', size = 'md', loading = false, disabled = false, to, href, className = '', children, ...props }) {
  const classes = `inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition duration-200 focus-visible:outline-none focus-visible:ring-4 disabled:pointer-events-none disabled:opacity-55 ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`
  const content = <>{loading && <LoaderCircle size={16} className="animate-spin" />}{children}</>
  const common = { className: classes, 'aria-busy': loading || undefined, ...props }
  if (to) return <Link to={to} {...common}>{content}</Link>
  if (href) return <a href={href} {...common}>{content}</a>
  return <button disabled={disabled || loading} {...common}>{content}</button>
}
