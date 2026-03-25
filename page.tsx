"use client"
import { useState } from "react"
import { createClient } from "@supabase/supabase-js"
import { useRouter } from "next/navigation"
import { useHekate } from "@/lib/store"
import { motion } from "framer-motion"
import { profileApi } from "@/lib/api"

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

type AuthMode = "login" | "signup"

export default function AuthPage() {
  const [mode, setMode] = useState<AuthMode>("login")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const { setUser, setToken } = useHekate()
  const router = useRouter()

  const handleSubmit = async () => {
    setLoading(true)
    setError("")

    try {
      if (mode === "signup") {
        const { data, error } = await supabase.auth.signUp({
          email, password,
          options: { data: { full_name: name } }
        })
        if (error) throw error
        setSuccess("Doğrulama maili gönderildi. Gelen kutunu kontrol et.")
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error

        const token = data.session!.access_token
        setToken(token)

        const profile = await profileApi.getMe(token)
        setUser(profile)
        router.push("/dashboard")
      }
    } catch (err: any) {
      setError(err.message || "Bir hata oluştu")
    } finally {
      setLoading(false)
    }
  }

  const handleGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/auth/callback` }
    })
  }

  return (
    <div className="min-h-screen nebula-bg flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-5xl sigil-float inline-block mb-4">𓂀</div>
          <div className="font-cinzel-d text-2xl text-gold-bright tracking-widest mb-1">HEKATE PRIME</div>
          <div className="font-cinzel text-[9px] tracking-[0.4em] text-gold/35 uppercase">
            {mode === "login" ? "Kapıyı aç" : "Ritüele katıl"}
          </div>
        </div>

        {/* Card */}
        <div className="glass-card rounded-2xl p-8">
          {/* Toggle */}
          <div className="flex rounded-xl overflow-hidden border border-[var(--border)] mb-6">
            {(["login", "signup"] as AuthMode[]).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 py-2.5 font-cinzel text-[10px] tracking-widest uppercase transition-all ${
                  mode === m
                    ? "bg-gradient-to-r from-amethyst/60 to-cave text-gold-bright"
                    : "text-silver/40 hover:text-silver/60"
                }`}
              >
                {m === "login" ? "Giriş" : "Kayıt"}
              </button>
            ))}
          </div>

          {/* Fields */}
          <div className="space-y-4">
            {mode === "signup" && (
              <div>
                <label className="font-cinzel text-[10px] tracking-widest text-gold/50 uppercase block mb-1.5">İsim</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="Adını söyle, arayışçı..."
                  className="w-full bg-[rgba(15,8,32,0.8)] border border-[var(--border)] rounded-xl px-4 py-3 text-silver font-garamond text-[15px] outline-none focus:border-gold/40 placeholder:text-silver/20 placeholder:italic transition-colors"
                />
              </div>
            )}

            <div>
              <label className="font-cinzel text-[10px] tracking-widest text-gold/50 uppercase block mb-1.5">E-posta</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="ruhun@evren.com"
                className="w-full bg-[rgba(15,8,32,0.8)] border border-[var(--border)] rounded-xl px-4 py-3 text-silver font-garamond text-[15px] outline-none focus:border-gold/40 placeholder:text-silver/20 placeholder:italic transition-colors"
              />
            </div>

            <div>
              <label className="font-cinzel text-[10px] tracking-widest text-gold/50 uppercase block mb-1.5">Şifre</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                onKeyDown={e => e.key === "Enter" && handleSubmit()}
                className="w-full bg-[rgba(15,8,32,0.8)] border border-[var(--border)] rounded-xl px-4 py-3 text-silver font-garamond text-[15px] outline-none focus:border-gold/40 placeholder:text-silver/20 transition-colors"
              />
            </div>
          </div>

          {error && (
            <p className="mt-3 text-red-400/80 font-cinzel text-[11px] tracking-wide">{error}</p>
          )}
          {success && (
            <p className="mt-3 text-astral font-cinzel text-[11px] tracking-wide">{success}</p>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full mt-6 py-3.5 bg-gradient-to-r from-amethyst to-violet rounded-xl font-cinzel text-[11px] tracking-widest uppercase text-white shadow-[0_4px_20px_rgba(74,30,110,0.4)] hover:shadow-[0_8px_28px_rgba(74,30,110,0.6)] hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {loading ? "Kapı açılıyor..." : mode === "login" ? "✦ Giriş Yap" : "✦ Ritüele Katıl"}
          </button>

          <div className="flex items-center gap-3 my-4">
            <div className="flex-1 h-px bg-gold/10" />
            <span className="font-cinzel text-[9px] text-gold/30 tracking-widest">VEYA</span>
            <div className="flex-1 h-px bg-gold/10" />
          </div>

          <button
            onClick={handleGoogle}
            className="w-full py-3 border border-[var(--border)] rounded-xl font-cinzel text-[11px] tracking-widest uppercase text-silver/60 hover:text-silver hover:border-gold/30 transition-all"
          >
            G Google ile Devam Et
          </button>
        </div>

        <p className="text-center mt-4 font-cinzel text-[9px] text-silver/25 tracking-widest">
          Giriş yaparak Hekate'nin rehberliğini kabul etmiş olursun ✦
        </p>
      </motion.div>
    </div>
  )
}
