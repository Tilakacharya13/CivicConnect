import { ArrowUpRight, CalendarDays, MapPin, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'
import Badge from './Badge'

export function formatDate(value) {
  if (!value) return 'Not available'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Not available'
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' }).format(date)
}

export default function ComplaintCard({ complaint }) {
  return (
    <Link to={`/complaints/${complaint.id}`} className="group block rounded-2xl border border-slate-200/80 bg-white p-5 shadow-soft transition duration-200 hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lift sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="mb-1.5 text-[11px] font-bold uppercase tracking-[.13em] text-slate-400">CC-{String(complaint.id).padStart(4, '0')} <span className="mx-1 text-slate-300">·</span> {complaint.category}</p>
          <h3 className="truncate text-base font-bold text-slate-900 transition group-hover:text-brand-700 sm:text-lg">{complaint.title}</h3>
        </div>
        <div className="flex shrink-0 items-center gap-2"><Badge>{complaint.priority_label}</Badge><ArrowUpRight size={17} className="text-slate-300 transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-brand-600" /></div>
      </div>
      <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-500">{complaint.description}</p>
      <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs font-medium text-slate-500">
        <span className="inline-flex items-center gap-1.5"><MapPin size={14} className="text-slate-400" />{complaint.location}</span>
        <span className="inline-flex items-center gap-1.5"><TrendingUp size={14} className="text-slate-400" />Score {complaint.priority_score}/100</span>
        <span className="inline-flex items-center gap-1.5"><CalendarDays size={14} className="text-slate-400" />Due {formatDate(complaint.expected_resolution_at)}</span>
        <Badge type="status" className="ml-auto">{complaint.status}</Badge>
      </div>
    </Link>
  )
}
