import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const ThemeContext = createContext(null)
function preferredTheme() {
  const saved = localStorage.getItem('civicconnect_theme')
  return saved || (window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
}
export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(preferredTheme)
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    document.documentElement.dataset.theme = theme
    localStorage.setItem('civicconnect_theme', theme)
  }, [theme])
  const value = useMemo(() => ({ theme, toggleTheme: () => setTheme(value => value === 'dark' ? 'light' : 'dark') }), [theme])
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
export function useTheme() { return useContext(ThemeContext) }
