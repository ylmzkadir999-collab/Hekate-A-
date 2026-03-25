/**
 * HEKATE PRIME — Global State (Zustand)
 */
import { create } from "zustand"
import { persist } from "zustand/middleware"

export type OracleMode = "oracle" | "tarot" | "astro" | "synastry" | "numerology" | "shadow" | "coffee" | "palm"
export type Tier = "free" | "premium" | "pro"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  mode: OracleMode
  timestamp: Date
  isStreaming?: boolean
}

export interface UserProfile {
  id: string
  email: string
  full_name?: string
  zodiac_sign?: string
  life_path_number?: number
  tier: Tier
  daily_message_count: number
  birth_date?: string
  subscription_status?: string
  subscription_current_period_end?: string
}

interface HekateStore {
  // Auth
  user: UserProfile | null
  token: string | null
  setUser: (user: UserProfile | null) => void
  setToken: (token: string | null) => void

  // Oracle
  currentMode: OracleMode
  shadowMode: boolean
  sessionId: string | null
  messages: Message[]
  isLoading: boolean

  setMode: (mode: OracleMode) => void
  setShadowMode: (v: boolean) => void
  setSessionId: (id: string | null) => void
  addMessage: (msg: Omit<Message, "id" | "timestamp">) => string
  updateMessage: (id: string, content: string, isStreaming?: boolean) => void
  clearMessages: () => void
  setLoading: (v: boolean) => void

  // UI
  sidebarOpen: boolean
  setSidebarOpen: (v: boolean) => void
}

export const useHekate = create<HekateStore>()(
  persist(
    (set, get) => ({
      // Auth
      user: null,
      token: null,
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),

      // Oracle
      currentMode: "oracle",
      shadowMode: false,
      sessionId: null,
      messages: [],
      isLoading: false,

      setMode: (mode) => set({ currentMode: mode, shadowMode: mode === "shadow" }),
      setShadowMode: (v) => set({ shadowMode: v }),
      setSessionId: (id) => set({ sessionId: id }),
      addMessage: (msg) => {
        const id = `msg_${Date.now()}_${Math.random().toString(36).slice(2)}`
        set((s) => ({
          messages: [...s.messages, { ...msg, id, timestamp: new Date() }],
        }))
        return id
      },
      updateMessage: (id, content, isStreaming = false) =>
        set((s) => ({
          messages: s.messages.map((m) =>
            m.id === id ? { ...m, content, isStreaming } : m
          ),
        })),
      clearMessages: () => set({ messages: [], sessionId: null }),
      setLoading: (v) => set({ isLoading: v }),

      // UI
      sidebarOpen: true,
      setSidebarOpen: (v) => set({ sidebarOpen: v }),
    }),
    {
      name: "hekate-store",
      partialize: (s) => ({
        currentMode: s.currentMode,
        sidebarOpen: s.sidebarOpen,
        // Don't persist messages — load from DB
      }),
    }
  )
)

// Tier limits helper
export const TIER_LIMITS = {
  free:    { daily: 5,    shadow: false, birthChart: false, synastry: false, pdf: false },
  premium: { daily: 9999, shadow: true,  birthChart: true,  synastry: true,  pdf: false },
  pro:     { daily: 9999, shadow: true,  birthChart: true,  synastry: true,  pdf: true  },
}

export const canUseFeature = (tier: Tier, feature: keyof typeof TIER_LIMITS.free) =>
  TIER_LIMITS[tier]?.[feature] ?? false
