import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { TOKEN_KEY } from '../api/client'

const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(localStorage.getItem(TOKEN_KEY)))
  const logout = useCallback((redirect = true) => {
    localStorage.removeItem(TOKEN_KEY); setUser(null); setLoading(false)
    if (redirect) navigate('/login', { replace: true })
  }, [navigate])
  useEffect(() => {
    const unauthorized = () => { localStorage.removeItem(TOKEN_KEY); setUser(null); setLoading(false); navigate('/login', { replace: true }) }
    window.addEventListener('civicconnect:unauthorized', unauthorized)
    return () => window.removeEventListener('civicconnect:unauthorized', unauthorized)
  }, [navigate])
  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) { setLoading(false); return }
    api.get('/auth/me').then(({ data }) => setUser(data)).catch(() => { localStorage.removeItem(TOKEN_KEY); setUser(null) }).finally(() => setLoading(false))
  }, [])
  const login = useCallback(async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem(TOKEN_KEY, data.access_token)
    const me = await api.get('/auth/me')
    const authenticatedUser = { ...me.data, role: data.role || me.data.role }
    setUser(authenticatedUser)
    return authenticatedUser
  }, [])
  const register = useCallback(async ({ name, email, password }) => {
    await api.post('/auth/register', { name, email, password })
    return login(email, password)
  }, [login])
  const loginWithFirebase = useCallback(async (idToken, name) => {
    const { data } = await api.post('/auth/firebase', { id_token: idToken, name })
    localStorage.setItem(TOKEN_KEY, data.access_token)
    const me = await api.get('/auth/me')
    const authenticatedUser = { ...me.data, role: data.role || me.data.role }
    setUser(authenticatedUser)
    return authenticatedUser
  }, [])
  const value = useMemo(() => ({ user, loading, login, register, loginWithFirebase, logout }), [user, loading, login, register, loginWithFirebase, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside AuthProvider')
  return value
}
