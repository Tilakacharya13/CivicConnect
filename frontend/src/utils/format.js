export const dateTime = value => value ? new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) : 'Not available'
export const dateOnly = value => value ? new Date(value).toLocaleDateString([], { dateStyle: 'medium' }) : 'Not available'
export function countdown(value, now = Date.now()) {
  if (!value) return 'No target set'
  const diff = new Date(value).getTime() - now
  const hours = Math.abs(diff) / 3600000
  const whole = Math.floor(hours)
  const minutes = Math.floor((hours - whole) * 60)
  if (diff < 0) return `OVERDUE by ${whole >= 24 ? `${(hours / 24).toFixed(1)} days` : `${whole}.${Math.floor(minutes / 6)} hours`}`
  return `${whole}h remaining`
}
export const slaTarget = { Critical: 24, High: 72, Medium: 168, Low: 336 }
export const apiAsset = path => path ? `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}${path}` : ''
