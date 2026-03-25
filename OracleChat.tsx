"use client"
import { useState, useRef, useEffect, useCallback } from "react"
import { useHekate, type OracleMode } from "@/lib/store"
import { streamOracleChat } from "@/lib/api"
import { motion, AnimatePresence } from "framer-motion"

const MODES: { id: OracleMode; label: string; icon: string; hint: string }[] = [
  { id: "oracle",     label: "Oracle",       icon: "🔮", hint: "Sorularını yıldızlara sor..." },
  { id: "tarot",      label: "Tarot",        icon: "🃏", hint: '"Üç kart çek" veya sorunla ilgili bir şey söyle...' },
  { id: "astro",      label: "Astroloji",    icon: "⭐", hint: "Gezegen enerjileri veya doğum haritası sor..." },
  { id: "synastry",   label: "Sinastri",     icon: "💞", hint: "İkinci kişinin adını ve burcunu söyle..." },
  { id: "numerology", label: "Numeroloji",   icon: "🔢", hint: "İsim veya tarih söyle..." },
  { id: "shadow",     label: "Shadow Mode",  icon: "🌑", hint: "Sert gerçekle yüzleş — hiçbir şey gizlenemez..." },
]

function formatOracleText(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-gold-bright">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-lavender">$1</em>')
    .replace(/\n\n/g, '</p><p class="mt-3">')
    .replace(/\n/g, "<br/>")
}

export default function OracleChat() {
  const {
    user, token, currentMode, shadowMode,
    messages, isLoading, sessionId,
    setMode, setSessionId, addMessage, updateMessage, setLoading
  } = useHekate()

  const [input, setInput] = useState("")
  const chatRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" })
    }, 50)
  }, [])

  useEffect(() => { scrollToBottom() }, [messages, scrollToBottom])

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading || !token) return

    const text = input.trim()
    setInput("")
    if (inputRef.current) inputRef.current.style.height = "50px"

    // Shadow mode trigger
    if (/gölgeyi göster|shadow mode|sert gerçek|acı gerçek/i.test(text)) {
      setMode("shadow")
    }

    // Add user message
    addMessage({ role: "user", content: text, mode: currentMode })

    // Add loading message
    setLoading(true)
    const aiId = addMessage({ role: "assistant", content: "", mode: currentMode, isStreaming: true })

    try {
      let fullText = ""
      for await (const event of streamOracleChat(text, token, {
        sessionId: sessionId || undefined,
        mode: currentMode,
        shadowMode,
      })) {
        if (event.type === "session_id") {
          setSessionId(event.session_id)
        } else if (event.type === "text") {
          fullText += event.text
          updateMessage(aiId, fullText, true)
          scrollToBottom()
        } else if (event.type === "done") {
          updateMessage(aiId, fullText, false)
        }
      }
    } catch (err: any) {
      const errMsg = err?.detail?.message || err?.detail?.code === "DAILY_LIMIT_REACHED"
        ? `✦ Günlük mesaj limitine ulaştın. [Premium'a geç →](/pricing)`
        : err?.detail?.code === "UPGRADE_REQUIRED"
        ? `✦ Bu özellik için tier yükseltmen gerekiyor. [Planları gör →](/pricing)`
        : "Kozmik bağlantı kesildi... Yıldızlar hizalanıyor, tekrar dene."
      updateMessage(aiId, errMsg, false)
    } finally {
      setLoading(false)
    }
  }, [input, isLoading, token, currentMode, shadowMode, sessionId, addMessage, updateMessage, setLoading, setMode, setSessionId, scrollToBottom])

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  const activeMode = MODES.find(m => m.id === currentMode) || MODES[0]

  return (
    <div className="flex flex-col h-full">
      {/* Mode tabs */}
      <div className="flex border-b border-[var(--border)] bg-[rgba(6,4,14,0.5)] overflow-x-auto">
        {MODES.map((m) => (
          <button
            key={m.id}
            onClick={() => setMode(m.id)}
            className={`px-4 py-3 font-cinzel text-[10px] tracking-widest uppercase whitespace-nowrap transition-all border-b-2 ${
              currentMode === m.id
                ? m.id === "shadow"
                  ? "text-lavender border-astral bg-[rgba(168,85,247,0.06)]"
                  : "text-gold-bright border-gold bg-[rgba(201,168,76,0.04)]"
                : "text-silver/40 border-transparent hover:text-silver/70"
            }`}
          >
            {m.icon} {m.label}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div ref={chatRef} className="flex-1 overflow-y-auto p-6 flex flex-col gap-5">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center h-full gap-6 text-center"
          >
            <div className="text-6xl sigil-float">𓂀</div>
            <div>
              <div className="font-cinzel-d text-2xl text-gold-bright tracking-widest mb-2">
                HEKATE PRIME
              </div>
              <div className="font-cinzel text-[10px] tracking-[0.4em] text-gold/40 uppercase mb-4">
                Üç Yolun Kesişiminde
              </div>
              <p className="text-silver/50 italic max-w-md">
                {user?.full_name ? `${user.full_name}, yıldızlar seninle konuşmak için sabırsızlanıyor.` : "Sorularını yıldızlara ilet."}
              </p>
            </div>
            <div className="grid grid-cols-3 gap-3 max-w-sm">
              {["Kariyer", "Aşk", "Tarot Açılımı", "Sinastri", "Numeroloji", "Shadow Analiz"].map(s => (
                <button
                  key={s}
                  onClick={() => { setInput(s); inputRef.current?.focus() }}
                  className="px-3 py-2 text-xs font-cinzel tracking-wide text-gold/60 border border-[var(--border)] rounded-lg hover:border-gold/40 hover:text-gold transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse self-end max-w-[85%]" : "max-w-[88%]"}`}
            >
              {/* Avatar */}
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0 border border-[var(--border)] ${
                msg.role === "assistant"
                  ? "bg-gradient-to-br from-amethyst to-cave shadow-[0_0_20px_rgba(74,30,110,0.5)]"
                  : "bg-gradient-radial from-gold/20 to-gold/5"
              }`}>
                {msg.role === "assistant" ? "𓂀" : "✨"}
              </div>

              <div>
                <div className={`px-5 py-4 text-[15px] leading-relaxed ${
                  msg.role === "assistant"
                    ? `glass-card rounded-tl rounded-bl-2xl rounded-br-2xl rounded-tr-2xl oracle-text ${
                        msg.mode === "shadow"
                          ? "border-astral/30 bg-[rgba(8,4,16,0.95)]"
                          : ""
                      }`
                    : "bg-gradient-to-br from-amethyst/60 to-cave/80 border border-violet/25 rounded-tl-2xl rounded-bl-2xl rounded-br-2xl text-indigo-100"
                }`}>
                  {msg.mode === "shadow" && msg.role === "assistant" && (
                    <span className="block font-cinzel text-[10px] tracking-widest text-astral mb-2">
                      🌑 SHADOW MODE AKTİF
                    </span>
                  )}
                  {msg.isStreaming && !msg.content ? (
                    <div className="flex gap-1.5 items-center py-1">
                      <div className="w-2 h-2 bg-astral rounded-full typing-dot" />
                      <div className="w-2 h-2 bg-astral rounded-full typing-dot" />
                      <div className="w-2 h-2 bg-astral rounded-full typing-dot" />
                    </div>
                  ) : (
                    <p dangerouslySetInnerHTML={{ __html: formatOracleText(msg.content) }} />
                  )}
                </div>
                <div className="text-[10px] text-silver/25 mt-1 tracking-wide font-cinzel">
                  {msg.role === "assistant"
                    ? (shadowMode ? "Gölgeler konuşuyor" : "Yıldızlar okunuyor") + " · "
                    : ""}
                  {new Date(msg.timestamp).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-[var(--border)] bg-[rgba(4,3,10,0.8)] backdrop-blur-xl">
        <div className="flex gap-3 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => {
              setInput(e.target.value)
              e.target.style.height = "50px"
              e.target.style.height = Math.min(e.target.scrollHeight, 130) + "px"
            }}
            onKeyDown={handleKey}
            placeholder={activeMode.hint}
            rows={1}
            className="flex-1 bg-[rgba(15,8,32,0.7)] border border-[var(--border)] rounded-xl px-4 py-3 text-silver text-[15px] font-garamond outline-none resize-none min-h-[50px] max-h-[130px] focus:border-gold/40 placeholder:text-silver/20 placeholder:italic transition-colors"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="w-12 h-12 bg-gradient-to-br from-amethyst to-violet rounded-xl flex items-center justify-center text-xl transition-all shadow-[0_4px_20px_rgba(74,30,110,0.45)] hover:shadow-[0_8px_28px_rgba(74,30,110,0.65)] hover:-translate-y-0.5 disabled:opacity-40 disabled:cursor-not-allowed disabled:transform-none"
          >
            ✦
          </button>
        </div>
        <p className="text-[10px] text-silver/20 text-center mt-2 font-cinzel tracking-widest">
          Enter ile gönder · Shift+Enter satır ekle
        </p>
      </div>
    </div>
  )
}
