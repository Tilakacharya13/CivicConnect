import { Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import PublicNavbar from './components/PublicNavbar'
import CitizenLayout from './layouts/CitizenLayout'
import AdminLayout from './layouts/AdminLayout'
import LandingPage from './pages/public/LandingPage'
import AuthPage from './pages/public/AuthPage'
import CitizenHome from './pages/citizen/CitizenHome'
import ReportPage from './pages/citizen/ReportPage'
import MyComplaints from './pages/citizen/MyComplaints'
import NotificationsPage from './pages/citizen/NotificationsPage'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminQueue from './pages/admin/AdminQueue'
import AllComplaints from './pages/admin/AllComplaints'
import OverduePage from './pages/admin/OverduePage'
import AnalyticsPage from './pages/admin/AnalyticsPage'
import { PageLoader } from './components/ui'
import { motion } from 'framer-motion'

function destination(user) { return user?.role === 'admin' ? '/admin/dashboard' : '/citizen/home' }
function GuestRoute() {
  const { user, loading } = useAuth()
  if (loading) return <PageLoader />
  return user ? <Navigate to={destination(user)} replace /> : <Outlet />
}
function RoleRoute({ role }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <PageLoader />
  if (!user) return <Navigate to="/" replace state={{ from: location }} />
  if (user.role !== role) return <Navigate to={destination(user)} replace />
  return <Outlet />
}
function NotFound() {
  return <main className="container-page grid min-h-[70vh] place-items-center py-16 text-center"><div><span className="text-xs font-bold uppercase tracking-[.18em] text-indigo-600">404 · Page not found</span><h1 className="mt-3 text-3xl font-extrabold text-slate-900">This page is off the map.</h1><a href="/" className="mt-6 inline-flex rounded-xl bg-slate-800 px-5 py-3 font-semibold text-white">Back to CivicConnect</a></div></main>
}
export default function App() {
  const location = useLocation()
  return <motion.div key={location.pathname} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{duration:.2}}><Routes>
    <Route element={<GuestRoute />}><Route element={<><PublicNavbar /><Outlet /></>}>
      <Route index element={<LandingPage />} /><Route path="login" element={<AuthPage mode="login" />} /><Route path="register" element={<AuthPage mode="register" />} />
    </Route></Route>
    <Route element={<RoleRoute role="citizen" />}><Route path="/citizen" element={<CitizenLayout />}>
      <Route index element={<Navigate to="home" replace />} /><Route path="home" element={<CitizenHome />} /><Route path="report" element={<ReportPage />} /><Route path="my-complaints" element={<MyComplaints />} /><Route path="notifications" element={<NotificationsPage />} />
    </Route></Route>
    <Route element={<RoleRoute role="admin" />}><Route path="/admin" element={<AdminLayout />}>
      <Route index element={<Navigate to="dashboard" replace />} /><Route path="dashboard" element={<AdminDashboard />} /><Route path="queue" element={<AdminQueue />} /><Route path="complaints" element={<AllComplaints />} /><Route path="overdue" element={<OverduePage />} /><Route path="analytics" element={<AnalyticsPage />} />
    </Route></Route>
    <Route path="*" element={<NotFound />} />
  </Routes></motion.div>
}
