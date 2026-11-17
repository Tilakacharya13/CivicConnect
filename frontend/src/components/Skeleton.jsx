export function Skeleton({ className = '' }) {
  return <div className={`animate-pulse rounded-lg bg-slate-200/80 ${className}`} aria-hidden="true" />
}

export function ComplaintSkeleton() {
  return (
    <div className="surface p-5 sm:p-6">
      <div className="flex items-start justify-between gap-4"><Skeleton className="h-5 w-2/5" /><Skeleton className="h-6 w-20 rounded-full" /></div>
      <Skeleton className="mt-4 h-4 w-4/5" />
      <div className="mt-6 flex flex-wrap gap-4"><Skeleton className="h-4 w-24" /><Skeleton className="h-4 w-32" /><Skeleton className="h-4 w-20" /></div>
    </div>
  )
}
