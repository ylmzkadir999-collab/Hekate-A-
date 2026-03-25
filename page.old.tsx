"use client"
import Link from "next/link"
import { motion } from "framer-motion"
import { useEffect, useRef } from "react"

export default function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current!
    const ctx = canvas.getContext("2d")!
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    const stars = Array.from({ length: 300 }, () => ({
      x: Math.random() * canvas.width, y: Math.random() * canvas.height,
      r: Math.random() * 1.4, a: Math.random() * 0.8 + 0.1,
      s: Math.random() * 0.4 + 0.05, t: Math.random() * Math.PI * 2,
    }))
    let raf: number
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      stars.forEach(s => {
        s.t += s.s * 0.025
        ctx.beginPath()
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255,255,255,${s.a * (0.65 + 0.35 * Math.sin(s.t))})`
        ctx.fill()
      })
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => cancelAnimationFrame(raf)
  }, [])

  return (
    <div className="relative min-h-screen overflow-auto">
      <canvas ref={canvasRef} className="fixed inset-0 z-0 pointer-events-none" />
      <div className="nebula-bg fixed inset-0 z-0 pointer-events-none" />

      <div className="relative z-10">
        {/* Nav */}
        <nav className="flex items-center justify-between px-10 py-5 border-b border-gold/10">
          <div className="font-cinzel-d text-lg text-gold-bright tracking-[0.25em]">𓂀 HEKATE</div>
          <div className="flex gap-6">
            <Link href="/pricing" className="font-cinzel text-[10px] tracking-widest text-silver/50 uppercase hover:text-gold transition-colors">Planlar</Link>
            <Link href="/auth/login" className="font-cinzel text-[10px] tracking-widest text-silver/50 uppercase hover:text-gold transition-colors">Giriş</Link>
            <Link href="/auth/login" className="px-4 py-2 border border-gold/30 rounded-full font-cinzel text-[10px] tracking-widest text-gold uppercase hover:bg-gold/10 transition-all">
              Başla →
            </Link>
          </div>
        </nav>

        {/* Hero */}
        <div className="text-center py-32 px-6">
          <motion.div initial={{opacity:0,y:-20}} animate={{opacity:1,y:0}} className="text-7xl sigil-float inline-block mb-8">𓂀</motion.div>
          <motion.h1 initial={{opacity:0}} animate={{opacity:1}} transition={{delay:.2}} className="font-cinzel-d text-5xl md:text-7xl text-gold-bright tracking-[0.2em] mb-4">
            HEKATE PRIME
          </motion.h1>
          <motion.p initial={{opacity:0}} animate={{opacity:1}} transition={{delay:.3}} className="font-cinzel text-[10px] tracking-[0.5em] text-gold/40 uppercase mb-8">
            Üç Yolun Kesişiminde AI Oracle
          </motion.p>
          <motion.p initial={{opacity:0}} animate={{opacity:1}} transition={{delay:.4}} className="text-xl text-silver/60 italic max-w-xl mx-auto mb-12 font-garamond leading-relaxed">
            Tarot, astroloji ve psikoloji — mistik bilgeliği modern zihne taşıyan AI danışmanın.
          </motion.p>
          <motion.div initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} transition={{delay:.5}} className="flex gap-4 justify-center flex-wrap">
            <Link href="/auth/login" className="px-8 py-4 bg-gradient-to-r from-amethyst to-astral text-white font-cinzel text-xs tracking-widest uppercase rounded-xl shadow-[0_4px_24px_rgba(74,30,110,0.5)] hover:shadow-[0_8px_32px_rgba(74,30,110,0.7)] hover:-translate-y-0.5 transition-all">
              ✦ Ritüele Gir
            </Link>
            <Link href="/pricing" className="px-8 py-4 border border-gold/30 text-gold font-cinzel text-xs tracking-widest uppercase rounded-xl hover:bg-gold/5 hover:-translate-y-0.5 transition-all">
              Planları Gör →
            </Link>
          </motion.div>
        </div>

        {/* Features */}
        <div className="max-w-5xl mx-auto px-6 pb-24">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon:"🔮", title:"AI Oracle Engine", desc:"HEKATE PRIME sistem promptu ile güçlü, tutarlı ve büyülü AI yanıtları." },
              { icon:"🃏", title:"Gerçek Tarot Sistemi", desc:"22 Major Arcana kartı, üç farklı açılım türü, psikolojik yorumlar." },
              { icon:"⭐", title:"Astroloji & Sinastri", desc:"Gezegen enerjileri, doğum haritası ve ilişki uyum analizi." },
            ].map((f,i) => (
              <motion.div key={i} initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{delay:.6+i*.1}}
                className="glass-card rounded-2xl p-6 text-center hover:border-gold/20 transition-all">
                <div className="text-4xl mb-3">{f.icon}</div>
                <div className="font-cinzel text-sm text-gold-bright tracking-wider mb-2">{f.title}</div>
                <p className="text-silver/50 text-sm italic">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
