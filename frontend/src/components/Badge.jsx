const priorityStyles = {
  Critical: 'bg-rose-50 text-rose-700 ring-rose-600/15',
  High: 'bg-orange-50 text-orange-700 ring-orange-600/15',
  Medium: 'bg-amber-50 text-amber-700 ring-amber-600/15',
  Low: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
}

const statusStyles = {
  Reported: 'bg-slate-100 text-slate-700 ring-slate-600/10',
  Verified: 'bg-blue-50 text-blue-700 ring-blue-600/15',
  Assigned: 'bg-violet-50 text-violet-700 ring-violet-600/15',
  Scheduled: 'bg-violet-50 text-violet-700 ring-violet-600/15',
  'In Progress': 'bg-amber-50 text-amber-700 ring-amber-600/15',
  Resolved: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
}

export default function Badge({ children, type = 'priority', className = '' }) {
  const styles = type === 'status' ? statusStyles : priorityStyles
  return <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-bold ring-1 ring-inset ${styles[children] || 'bg-slate-100 text-slate-700 ring-slate-600/10'} ${className}`}>{children}</span>
}
