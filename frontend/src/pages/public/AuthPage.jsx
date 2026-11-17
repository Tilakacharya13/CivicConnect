import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, ShieldCheck } from 'lucide-react'
import {
  GoogleAuthProvider,
  RecaptchaVerifier,
  signInWithPhoneNumber,
  signInWithPopup,
} from 'firebase/auth'
import { useAuth } from '../../context/AuthContext'
import { getApiError } from '../../api/client'
import { firebaseConfigured, getFirebaseAuth } from '../../api/firebase'
import { Button, Input } from '../../components/ui'
import { useToast } from '../../context/ToastContext'

function firebaseErrorMessage(error) {
  const messages = {
    'auth/invalid-phone-number': 'Enter a valid phone number in international format, such as +919876543210.',
    'auth/operation-not-allowed': 'Firebase rejected this provider. Check that Phone sign-in is enabled and that the SMS region policy allows your phone number’s country.',
    'auth/too-many-requests': 'Too many attempts. Wait a while and try again.',
    'auth/unauthorized-domain': 'Add this website domain to Firebase Authentication authorized domains.',
    'auth/invalid-verification-code': 'That verification code is incorrect. Try again.',
  }
  return messages[error?.code] || error?.message || 'Firebase sign-in failed. Please try again.'
}

export default function AuthPage({ mode = 'login' }) {
  const isRegister = mode === 'register'
  const { login, register, loginWithFirebase } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [confirmation, setConfirmation] = useState(null)
  const recaptcha = useRef(null)

  useEffect(() => () => recaptcha.current?.clear(), [])

  const change = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value })
    setFieldErrors({ ...fieldErrors, [event.target.name]: '' })
    setError('')
  }

  const finishFirebaseSignIn = async (firebaseUser) => {
    const user = await loginWithFirebase(await firebaseUser.getIdToken(), form.name.trim() || undefined)
    toast(isRegister ? 'Your citizen account is ready.' : 'Welcome back.')
    navigate(user.role === 'admin' ? '/admin/dashboard' : '/citizen/home', { replace: true })
  }

  const submit = async (event) => {
    event.preventDefault()
    const next = {}
    if (isRegister && !form.name.trim()) next.name = 'Enter your name.'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) next.email = 'Enter a valid email address.'
    if (form.password.length < (isRegister ? 8 : 1)) next.password = isRegister ? 'Use at least 8 characters.' : 'Enter your password.'
    setFieldErrors(next)
    if (Object.keys(next).length) return
    setLoading(true)
    setError('')
    try {
      const user = isRegister ? await register(form) : await login(form.email, form.password)
      toast(isRegister ? 'Your citizen account is ready.' : 'Welcome back.')
      navigate(user.role === 'admin' ? '/admin/dashboard' : '/citizen/home', { replace: true })
    } catch (err) {
      setError(getApiError(err, 'Unable to sign in. Check your details and try again.'))
    } finally {
      setLoading(false)
    }
  }

  const signInWithGoogle = async () => {
    setLoading(true)
    setError('')
    try {
      const result = await signInWithPopup(getFirebaseAuth(), new GoogleAuthProvider())
      await finishFirebaseSignIn(result.user)
    } catch (err) {
      setError(firebaseErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const sendPhoneCode = async () => {
    setLoading(true)
    setError('')
    try {
      const auth = getFirebaseAuth()
      if (!recaptcha.current) {
        recaptcha.current = new RecaptchaVerifier(auth, 'firebase-recaptcha', { size: 'normal' })
      }
      const result = await signInWithPhoneNumber(auth, phone.trim(), recaptcha.current)
      setConfirmation(result)
      toast('Verification code sent.')
    } catch (err) {
      recaptcha.current?.clear()
      recaptcha.current = null
      setError(firebaseErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const verifyPhoneCode = async () => {
    setLoading(true)
    setError('')
    try {
      const result = await confirmation.confirm(code.trim())
      await finishFirebaseSignIn(result.user)
    } catch (err) {
      setError(firebaseErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return <main className="mesh-bg relative grid min-h-[calc(100vh-72px)] place-items-center overflow-hidden px-4 py-10">
    <div className="grid-bg pointer-events-none absolute inset-0" />
    <div className="relative w-full max-w-md animate-fade-in-up">
      <div className="mb-6 text-center">
        <span className="mx-auto grid size-12 place-items-center rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-glow"><ShieldCheck size={22} /></span>
        <h1 className="mt-4 text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">{isRegister ? 'Create your account' : 'Welcome Back'}</h1>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{isRegister ? 'Join your community on CivicConnect.' : 'Sign in to continue to CivicConnect.'}</p>
      </div>

      <div className="glass-panel rounded-2xl p-6 shadow-2xl sm:p-8">
        <form onSubmit={submit} noValidate className="space-y-5">
          {isRegister && <Input label="Full name" name="name" autoComplete="name" value={form.name} onChange={change} error={fieldErrors.name} placeholder="Jordan Lee" />}
          <Input label="Email address" name="email" type="email" autoComplete="email" value={form.email} onChange={change} error={fieldErrors.email} placeholder="you@example.com" />
          <label className="block">
            <span className="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-200">Password</span>
            <span className="relative block">
              <input className="field pr-12" name="password" type={show ? 'text' : 'password'} autoComplete={isRegister ? 'new-password' : 'current-password'} value={form.password} onChange={change} placeholder={isRegister ? 'At least 8 characters' : 'Your password'} />
              <button type="button" onClick={() => setShow(!show)} className="absolute inset-y-0 right-0 grid w-12 place-items-center text-slate-400 hover:text-slate-700 dark:hover:text-white" aria-label={show ? 'Hide password' : 'Show password'}>{show ? <EyeOff size={18} /> : <Eye size={18} />}</button>
            </span>
            {fieldErrors.password && <span className="mt-1.5 block text-xs text-red-600">{fieldErrors.password}</span>}
          </label>
          {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
          <Button type="submit" loading={loading} className="w-full py-3">{isRegister ? 'Create citizen account' : 'Login'}</Button>
        </form>

        <div className="my-5 flex items-center gap-3 text-xs font-semibold uppercase tracking-wide text-slate-400"><span className="h-px flex-1 bg-slate-200" />or use a verified account<span className="h-px flex-1 bg-slate-200" /></div>
        <div className="space-y-4">
          <Button type="button" variant="secondary" className="w-full py-3" onClick={signInWithGoogle} disabled={!firebaseConfigured || loading}>
            <span className="font-extrabold text-blue-600">G</span> Continue with Google
          </Button>
          <div className="space-y-3 rounded-xl border border-slate-200/80 p-4">
            <Input label="Phone number" type="tel" autoComplete="tel" value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="+919876543210" />
            <div id="firebase-recaptcha" />
            {!confirmation ? <Button type="button" variant="secondary" className="w-full" onClick={sendPhoneCode} disabled={!firebaseConfigured || loading || !phone.trim()}>Send phone OTP</Button> : <>
              <Input label="Verification code" inputMode="numeric" autoComplete="one-time-code" value={code} onChange={(event) => setCode(event.target.value)} placeholder="Enter the SMS code" />
              <Button type="button" className="w-full" onClick={verifyPhoneCode} loading={loading} disabled={code.trim().length < 4}>Verify and continue</Button>
            </>}
          </div>
          {!firebaseConfigured && <p className="text-center text-xs leading-5 text-slate-500">Google and phone sign-in need Firebase project settings. Email and password sign-in remains available.</p>}
        </div>

        <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">{isRegister ? 'Already have an account?' : 'New to CivicConnect?'} <Link className="font-bold text-indigo-700 hover:text-indigo-800 dark:text-indigo-300" to={isRegister ? '/login' : '/register'}>{isRegister ? 'Login' : 'Create an account'}</Link></p>
      </div>
      <p className="mt-5 text-center text-xs text-slate-400">Your account is protected and your reports stay connected to you.</p>
    </div>
  </main>
}
