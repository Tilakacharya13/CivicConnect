import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const dismiss = useCallback((id) => setToasts((items) => items.filter((item) => item.id !== id)), [])
  const toast = useCallback((message, type = 'success') => {
    const id = `${Date.now()}-${Math.random()}`
    setToasts((items) => [...items, { id, message, type }])
    window.setTimeout(() => dismiss(id), 4500)
  }, [dismiss])
  const value = useMemo(() => ({ toast }), [toast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 z-[100] flex w-[calc(100%-2rem)] max-w-sm flex-col gap-3" aria-live="polite">
        {toasts.map((item) => {
          const Icon = item.type === 'error' ? AlertCircle : item.type === 'info' ? Info : CheckCircle2
          return (
            <div key={item.id} className="pointer-events-auto flex items-start gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-lift animate-in" role="status">
              <Icon size={19} className={item.type === 'error' ? 'mt-0.5 text-rose-500' : item.type === 'info' ? 'mt-0.5 text-blue-500' : 'mt-0.5 text-emerald-500'} />
              <p className="flex-1 text-sm font-medium leading-5 text-slate-700">{item.message}</p>
              <button onClick={() => dismiss(item.id)} className="text-slate-400 transition hover:text-slate-700" aria-label="Dismiss notification"><X size={17} /></button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const value = useContext(ToastContext)
  if (!value) throw new Error('useToast must be used inside ToastProvider')
  return value.toast
}
