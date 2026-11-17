import { forwardRef } from 'react'

function FieldFrame({ label, hint, error, id, children }) {
  return (
    <div className="space-y-2">
      {label && <label htmlFor={id} className="block text-sm font-semibold text-slate-700">{label}</label>}
      {children}
      {error ? <p className="text-xs font-medium text-rose-600" role="alert">{error}</p> : hint && <p className="text-xs text-slate-500">{hint}</p>}
    </div>
  )
}

export const Input = forwardRef(function Input({ label, hint, error, id, className = '', ...props }, ref) {
  return <FieldFrame label={label} hint={hint} error={error} id={id}><input ref={ref} id={id} className={`field ${error ? 'border-rose-300 focus:border-rose-400 focus:ring-rose-100' : ''} ${className}`} aria-invalid={Boolean(error)} {...props} /></FieldFrame>
})

export const Select = forwardRef(function Select({ label, hint, error, id, className = '', children, ...props }, ref) {
  return <FieldFrame label={label} hint={hint} error={error} id={id}><select ref={ref} id={id} className={`field ${error ? 'border-rose-300 focus:border-rose-400 focus:ring-rose-100' : ''} ${className}`} aria-invalid={Boolean(error)} {...props}>{children}</select></FieldFrame>
})

export const Textarea = forwardRef(function Textarea({ label, hint, error, id, className = '', ...props }, ref) {
  return <FieldFrame label={label} hint={hint} error={error} id={id}><textarea ref={ref} id={id} className={`field min-h-32 resize-y ${error ? 'border-rose-300 focus:border-rose-400 focus:ring-rose-100' : ''} ${className}`} aria-invalid={Boolean(error)} {...props} /></FieldFrame>
})
