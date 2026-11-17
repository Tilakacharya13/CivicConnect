import { AlertCircle, RotateCw } from 'lucide-react'
import { Button, Card, EmptyState, SkeletonCard } from './ui'

export function LoadingList({ count = 3 }) { return <div className="grid gap-4">{Array.from({length:count},(_,i)=><SkeletonCard key={i}/>)}</div> }
export function RequestError({ message, retry }) { return <Card className="flex flex-col items-start gap-4 border-red-200 bg-red-50/60 p-5 sm:flex-row sm:items-center"><span className="grid size-10 shrink-0 place-items-center rounded-xl bg-red-100 text-red-700"><AlertCircle size={20}/></span><div className="flex-1"><h3 className="font-bold text-slate-900">We couldn’t load this view</h3><p className="mt-1 text-sm text-slate-600">{message}</p></div>{retry&&<Button variant="secondary" onClick={retry}><RotateCw size={16}/>Try again</Button>}</Card> }
export { EmptyState }
