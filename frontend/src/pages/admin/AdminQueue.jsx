import { useCallback, useEffect, useState } from 'react'
import { getQueue } from '../../api/complaints'
import { getApiError } from '../../api/client'
import { PageHeader } from '../../components/ui'
import { QueueBoard } from '../../components/admin/QueueViews'

export default function AdminQueue(){const [queue,setQueue]=useState(null);const [loading,setLoading]=useState(true);const [error,setError]=useState('');const load=useCallback(()=>{setLoading(true);setError('');getQueue().then(setQueue).catch(e=>setError(getApiError(e))).finally(()=>setLoading(false))},[]);useEffect(()=>{load()},[load]);return <><PageHeader eyebrow="Work management" title="Priority queue" description="Review open reports by urgency and SLA target."/><QueueBoard queue={queue} loading={loading} error={error} retry={load} onRefresh={load}/></>}
