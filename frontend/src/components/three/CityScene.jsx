import { Canvas, useFrame } from '@react-three/fiber'
import { Float, Html, OrbitControls, RoundedBox } from '@react-three/drei'
import { Suspense, useRef } from 'react'
import * as THREE from 'three'

function City() {
  const group = useRef()
  useFrame(({ pointer }, delta) => {
    if (!group.current) return
    group.current.rotation.y += delta * 0.045
    group.current.rotation.x += (pointer.y * 0.06 - group.current.rotation.x) * 0.025
    group.current.rotation.z += (pointer.x * 0.04 - group.current.rotation.z) * 0.025
  })
  const buildings = [[-1.5,0,-.9,.8,1.4,.8],[-.35,0,-1.15,.85,2.1,.65],[.85,0,-.75,.8,1.15,.8],[1.55,0,.3,.6,1.8,.65],[.35,0,.55,1.05,1.55,.95],[-1.15,0,.6,.8,1.05,.8]]
  return <group ref={group}>
    <mesh rotation={[-Math.PI/2,0,0]} position={[0,-.04,0]} receiveShadow><planeGeometry args={[5,4]}/><meshStandardMaterial color="#172554" roughness={.84}/></mesh>
    <mesh rotation={[-Math.PI/2,0,0]} position={[0,-.025,0]}><ringGeometry args={[.78,.86,48]}/><meshBasicMaterial color="#22d3ee" transparent opacity={.55}/></mesh>
    {buildings.map(([x,y,z,w,h,d],i)=><group key={i} position={[x,y,z]}><RoundedBox args={[w,h,d]} radius={.08} smoothness={3} position={[0,h/2,0]} castShadow><meshStandardMaterial color={i%2?'#303b71':'#4451a2'} metalness={.26} roughness={.4}/></RoundedBox><mesh position={[0,h*.67,d/2+.006]}><planeGeometry args={[w*.48,.045]}/><meshBasicMaterial color={i%2?'#67e8f9':'#c4b5fd'} transparent opacity={.8}/></mesh></group>)}
    <Float speed={1.5} rotationIntensity={.1} floatIntensity={.25}><group position={[-1.25,1.65,.45]}><mesh castShadow><sphereGeometry args={[.18,16,16]}/><meshStandardMaterial color="#22d3ee" emissive="#0891b2" emissiveIntensity={.4}/></mesh><mesh position={[0,-.18,0]} rotation={[Math.PI,0,0]}><coneGeometry args={[.11,.25,12]}/><meshStandardMaterial color="#22d3ee"/></mesh><Html position={[.28,.15,0]} distanceFactor={8} transform><div className="scene-pin"><span className="scene-pin-dot"/> Report location</div></Html></group></Float>
    <Float speed={1.1} rotationIntensity={.08} floatIntensity={.18}><group position={[1.45,1.55,-.25]}><mesh castShadow><sphereGeometry args={[.16,16,16]}/><meshStandardMaterial color="#a78bfa" emissive="#7c3aed" emissiveIntensity={.35}/></mesh><mesh position={[0,-.16,0]} rotation={[Math.PI,0,0]}><coneGeometry args={[.1,.22,12]}/><meshStandardMaterial color="#a78bfa"/></mesh></group></Float>
  </group>
}
export default function CityScene() { return <Canvas shadows dpr={[1,1.5]} camera={{position:[4.8,4,6],fov:37}} gl={{alpha:true,antialias:true}}><color attach="background" args={['#080d1b']}/><fog attach="fog" args={['#080d1b',8,16]}/><ambientLight intensity={1.5}/><directionalLight position={[4,7,5]} intensity={3} castShadow shadow-mapSize={[1024,1024]}/><pointLight position={[-3,3,-3]} color="#8b5cf6" intensity={5}/><Suspense fallback={null}><City/></Suspense><OrbitControls enablePan={false} enableZoom={false} autoRotate autoRotateSpeed={.12} maxPolarAngle={Math.PI/2.15} minPolarAngle={Math.PI/4}/></Canvas> }
