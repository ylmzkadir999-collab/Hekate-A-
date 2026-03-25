/**
 * HEKATE PRIME — API Client
 * Typed wrapper for all backend calls
 */

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...rest } = options
  const res = await fetch(`${API}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(rest.headers || {}),
    },
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw { status: res.status, detail: err.detail || err }
  }
  return res.json()
}

// ── Oracle ────────────────────────────────────────────────

export async function* streamOracleChat(
  message: string,
  token: string,
  opts: { sessionId?: string; mode?: string; shadowMode?: boolean } = {}
) {
  const res = await fetch(`${API}/api/oracle/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      message,
      session_id: opts.sessionId,
      mode: opts.mode || "oracle",
      shadow_mode: opts.shadowMode || false,
      stream: true,
    }),
  })

  if (!res.ok) {
    const err = await res.json()
    throw err
  }

  const reader = res.body!.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split("\n")

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6))
          yield data
        } catch {}
      }
    }
  }
}

export const oracleApi = {
  getSessions: (token: string) =>
    apiFetch<any[]>("/api/oracle/sessions", { token }),
  getMessages: (sessionId: string, token: string) =>
    apiFetch<any[]>(`/api/oracle/sessions/${sessionId}/messages`, { token }),
  getMemory: (token: string) =>
    apiFetch<{memory: string[]}>("/api/oracle/memory", { token }),
  clearMemory: (token: string) =>
    apiFetch("/api/oracle/memory", { method: "DELETE", token }),
}

// ── Profile ───────────────────────────────────────────────

export const profileApi = {
  getMe: (token: string) =>
    apiFetch<any>("/api/profile/me", { token }),
  update: (data: any, token: string) =>
    apiFetch<any>("/api/profile/me", { method: "PATCH", body: JSON.stringify(data), token }),
  getLifePath: (token: string) =>
    apiFetch<any>("/api/profile/life-path", { token }),
}

// ── Tarot ─────────────────────────────────────────────────

export const tarotApi = {
  draw: (question: string | null, spread: string, token: string) =>
    apiFetch<any>("/api/tarot/draw", {
      method: "POST",
      body: JSON.stringify({ question, spread }),
      token,
    }),
  getHistory: (token: string) =>
    apiFetch<any[]>("/api/tarot/history", { token }),
}

// ── Astro ─────────────────────────────────────────────────

export const astroApi = {
  getDaily: (token: string) =>
    apiFetch<any>("/api/astro/daily", { token }),
  synastry: (data: any, token: string) =>
    apiFetch<any>("/api/astro/synastry", { method: "POST", body: JSON.stringify(data), token }),
}

// ── Payments ──────────────────────────────────────────────

export const stripeApi = {
  createCheckout: (tier: string, token: string) =>
    apiFetch<{checkout_url: string}>("/api/stripe/create-checkout", {
      method: "POST",
      body: JSON.stringify({ tier }),
      token,
    }),
  getPortal: (token: string) =>
    apiFetch<{portal_url: string}>("/api/stripe/portal", { method: "POST", token }),
  getSubscription: (token: string) =>
    apiFetch<any>("/api/stripe/subscription", { token }),
}
