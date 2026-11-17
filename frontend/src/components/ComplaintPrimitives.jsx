import { Check } from 'lucide-react'
import Badge from './Badge'

export function PriorityMeter({ score, label, compact = false }) {
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0))
  const color = label === 'Critical' ? 'bg-rose-500' : label === 'High' ? 'bg-orange-500' : label === 'Medium' ? 'bg-amber-500' : 'bg-emerald-500'
  return (
    <div className={compact ? '' : 'rounded-2xl border border-slate-200 bg-white p-5 sm:p-6'}>
      <div className="flex items-center justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[.12em] text-slate-400">Priority score</p><p className="mt-1 text-2xl font-extrabold tracking-tight text-slate-950">{safeScore}<span className="text-sm font-semibold text-slate-400"> / 100</span></p></div><Badge>{label}</Badge></div>
      <div className="mt-4 h-2.5 overflow-hidden rounded-full bg-slate-100"><div className={`h-full rounded-full transition-all duration-700 ${color}`} style={{ width: `${safeScore}%` }} /></div>
      {!compact && <div className="mt-2 flex justify-between text-[11px] font-medium text-slate-400"><span>Lower</span><span>Higher priority</span></div>}
    </div>
  )
}

const steps = ['Reported', 'Verified', 'Assigned', 'In Progress', 'Resolved']
const stepIndex = { Reported: 0, Verified: 1, Assigned: 2, Scheduled: 3, 'In Progress': 3, Resolved: 4 }

export function StatusStepper({ status }) {
  const active = stepIndex[status] ?? 0
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-7">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm font-bold text-slate-900">Progress</p><p className="mt-1 text-xs text-slate-500">We’ll keep this timeline up to date.</p></div><Badge type="status">{status}</Badge></div>
      <div className="grid grid-cols-5">
        {steps.map((step, index) => {
          const complete = index < active || status === 'Resolved'
          const current = index === active && status !== 'Resolved'
          return <div key={step} className="relative flex flex-col items-center text-center">
            {index < steps.length - 1 && <div className={`absolute left-1/2 top-3.5 h-0.5 w-full ${index < active ? 'bg-brand-500' : 'bg-slate-200'}`} />}
            <div className={`relative z-10 grid size-7 place-items-center rounded-full border-2 ${complete ? 'border-brand-600 bg-brand-600 text-white' : current ? 'border-brand-600 bg-white text-brand-600 ring-4 ring-brand-100' : 'border-slate-200 bg-white text-transparent'}`}>{complete ? <Check size={14} strokeWidth={3} /> : <span className="size-2 rounded-full bg-current" />}</div>
            <span className={`mt-3 text-[10px] font-semibold sm:text-xs ${complete || current ? 'text-slate-800' : 'text-slate-400'}`}>{step}</span>
          </div>
        })}
      </div>
    </div>
  )
}
