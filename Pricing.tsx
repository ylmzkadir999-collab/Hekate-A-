"use client"
import { useState } from "react"
import { motion } from "framer-motion"
import { useHekate } from "@/lib/store"
import { stripeApi } from "@/lib/api"
import { useRouter } from "next/navigation"

const PLANS = [
  {
    tier: "free",
    name: "Arayışçı",
    price: "$0",
    period: "/ sonsuza dek",
    icon: "🌙",
    color: "border-silver/20",
    highlight: false,
    features: [
      { text: "5 mesaj / gün", available: true },
      { text: "Günlük tarot kartı", available: true },
      { text: "Günlük burç yorumu", available: true },
      { text: "Doğum haritası", available: false },
      { text: "Sinastri analizi", available: false },
      { text: "Shadow Mode", available: false },
      { text: "PDF rapor", available: false },
    ],
  },
  {
    tier: "premium",
    name: "Mistik",
    price: "$9.99",
    period: "/ ay",
    icon: "⭐",
    color: "border-astral/40",
    highlight: true,
    badge: "EN POPÜLER",
    features: [
      { text: "Sınırsız mesaj", available: true },
      { text: "Günlük tarot açılımı", available: true },
      { text: "Doğum haritası analizi", available: true },
      { text: "Sinastri (ilişki analizi)", available: true },
      { text: "Shadow Mode", available: true },
      { text: "Celtic Cross açılımı", available: true },
      { text: "PDF rapor", available: false },
    ],
  },
  {
    tier: "pro",
    name: "Oracle",
    price: "$19.99",
    period: "/ ay",
    icon: "𓂀",
    color: "border-gold/40",
    highlight: false,
    features: [
      { text: "Sınırsız mesaj", available: true },
      { text: "Tüm tarot açılımları", available: true },
      { text: "Tam astroloji raporu", available: true },
      { text: "Sinastri + karmasal analiz", available: true },
      { text: "Shadow Mode + derin analiz", available: true },
      { text: "PDF rapor export", available: true },
      { text: "Özel ritüel takvimi", available: true },
    ],
  },
]

export default function PricingPage() {
  const { token, user } = useHekate()
  const [loading, setLoading] = useState<string | null>(null)
  const router = useRouter()

  const handleUpgrade = async (tier: string) => {
    if (!token) { router.push("/auth/login"); return }
    if (tier === "free") return

    setLoading(tier)
    try {
      const { checkout_url } = await stripeApi.createCheckout(tier, token)
      window.location.href = checkout_url
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen nebula-bg flex flex-col">
      {/* Header */}
      <div className="text-center pt-20 pb-12 px-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-5xl mb-4 sigil-float inline-block"
        >
          𓂀
        </motion.div>
        <motion.h1
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="font-cinzel-d text-3xl text-gold-bright tracking-widest mb-2"
        >
          RITÜEL SEÇ
        </motion.h1>
        <p className="font-cinzel text-[10px] tracking-[0.4em] text-gold/40 uppercase mb-4">
          Hangi yolu seçtiğinde kaderin şekillenir
        </p>
        <p className="text-silver/50 italic max-w-md mx-auto">
          Her kehanet bir kapı açar. Hangi kapıya girdiğin, yolculuğunun derinliğini belirler.
        </p>
      </div>

      {/* Plans */}
      <div className="flex flex-col md:flex-row gap-6 max-w-5xl mx-auto px-6 pb-20 w-full">
        {PLANS.map((plan, i) => (
          <motion.div
            key={plan.tier}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 + 0.3 }}
            className={`flex-1 relative glass-card rounded-2xl p-6 ${plan.color} ${
              plan.highlight ? "shadow-[0_0_40px_rgba(168,85,247,0.2)]" : ""
            }`}
          >
            {plan.badge && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-amethyst to-astral text-white font-cinzel text-[9px] tracking-widest px-4 py-1 rounded-full">
                {plan.badge}
              </div>
            )}

            <div className="text-center mb-6">
              <div className="text-4xl mb-3">{plan.icon}</div>
              <div className="font-cinzel-d text-xl text-gold-bright tracking-wider mb-1">{plan.name}</div>
              <div className="flex items-baseline justify-center gap-1">
                <span className="font-cinzel text-3xl text-silver">{plan.price}</span>
                <span className="font-cinzel text-xs text-silver/40">{plan.period}</span>
              </div>
            </div>

            <ul className="space-y-3 mb-8">
              {plan.features.map((f, j) => (
                <li key={j} className={`flex items-center gap-3 text-sm ${f.available ? "text-silver" : "text-silver/25"}`}>
                  <span className={f.available ? "text-gold" : "text-silver/20"}>
                    {f.available ? "✦" : "×"}
                  </span>
                  {f.text}
                </li>
              ))}
            </ul>

            <button
              onClick={() => handleUpgrade(plan.tier)}
              disabled={loading === plan.tier || user?.tier === plan.tier}
              className={`w-full py-3 rounded-xl font-cinzel text-xs tracking-widest uppercase transition-all ${
                user?.tier === plan.tier
                  ? "bg-gold/10 border border-gold/20 text-gold/50 cursor-default"
                  : plan.tier === "free"
                  ? "bg-transparent border border-silver/20 text-silver/50 cursor-default"
                  : plan.highlight
                  ? "bg-gradient-to-r from-amethyst to-astral text-white shadow-[0_4px_20px_rgba(74,30,110,0.4)] hover:shadow-[0_8px_28px_rgba(74,30,110,0.6)] hover:-translate-y-0.5"
                  : "bg-gradient-to-r from-cave to-purple border border-gold/30 text-gold hover:border-gold hover:shadow-[0_4px_20px_rgba(201,168,76,0.2)] hover:-translate-y-0.5"
              } disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none`}
            >
              {loading === plan.tier ? "Yönlendiriliyor..." :
               user?.tier === plan.tier ? "✦ Mevcut Plan" :
               plan.tier === "free" ? "Mevcut" : "Yükselt →"}
            </button>
          </motion.div>
        ))}
      </div>

      {/* Features comparison note */}
      <div className="text-center pb-12 text-silver/30 font-cinzel text-[10px] tracking-widest">
        ✦ Tüm planlar Stripe ile güvenli ödeme · İstediğin zaman iptal et ✦
      </div>
    </div>
  )
}
