import { Suspense, lazy, useEffect, useState } from 'react'
const CityScene = lazy(() => import('./CityScene'))
export default function HeroSceneLoader() {
  const [allowed, setAllowed] = useState(false)
  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const update = () => setAllowed(!media.matches && window.innerWidth > 700 && !('deviceMemory' in navigator && navigator.deviceMemory <= 2))
    update(); media.addEventListener?.('change', update); window.addEventListener('resize', update)
    return () => { media.removeEventListener?.('change', update); window.removeEventListener('resize', update) }
  }, [])
  return <div className="hero-scene-frame"><div className="hero-scene-glow"/><div className="hero-scene-grid"/>{allowed ? <Suspense fallback={<div className="hero-scene-fallback"/>}><CityScene/></Suspense> : <div className="hero-static-city" aria-label="Abstract illustration of a connected neighborhood"><div className="static-city-block block-a"/><div className="static-city-block block-b"/><div className="static-city-block block-c"/><span className="static-pin pin-a">●</span><span className="static-pin pin-b">●</span></div>}</div>
}
