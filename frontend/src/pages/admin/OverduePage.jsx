import { useCallback, useEffect, useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { getOverdue } from '../../api/complaints'
import { getApiError } from '../../api/client'
import { EmptyState, PageHeader, Skeleton } from '../../components/ui'
import { RequestError } from '../../components/RequestState'
import { QueueBoard } from '../../components/admin/QueueViews'

export default function OverduePage(){const [items,setItems]=useState([]);const [loading,setLoading]=useState(true);const [error,setError]=useState('');const load=useCallback(()=>{setLoading(true);setError('');getOverdue().then(setItems).catch(e=>setError(getApiError(e))).finally(()=>setLoading(false))},[]);useEffect(()=>{load()},[load]);const grouped={Critical:[],High:[],Medium:[],Low:[]};items.forEach(item=>grouped[item.priority_label]?.push(item));return <><PageHeader eyebrow="SLA monitoring" title="Overdue complaints" description="Unresolved complaints whose expected resolution time has passed."/>{error?<RequestError message={error} retry={load}/>:loading?<div className="grid gap-3">{[1,2].map(n=><Skeleton key={n} className="h-36"/>)}</div>:items.length===0?<EmptyState icon={AlertTriangle} title="No overdue complaints" description="There are no unresolved reports past their expected resolution time."/>:<QueueBoard queue={grouped} loading={loading} error={error} retry={load} onRefresh={load}/>}</>}
