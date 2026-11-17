import { FilePlus2 } from 'lucide-react'
import Button from './Button'

export default function EmptyState({ title = 'Nothing here yet', description = 'When you add something, it will show up here.', actionLabel, actionTo = '/report', icon: Icon = FilePlus2 }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center">
      <div className="mx-auto grid size-12 place-items-center rounded-2xl bg-brand-50 text-brand-600"><Icon size={22} /></div>
      <h3 className="mt-4 text-base font-bold text-slate-900">{title}</h3>
      <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-500">{description}</p>
      {actionLabel && <Button to={actionTo} className="mt-6">{actionLabel}</Button>}
    </div>
  )
}
