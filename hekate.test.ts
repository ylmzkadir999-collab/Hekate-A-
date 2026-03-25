/**
 * HEKATE PRIME — Frontend Tests (Jest)
 */

// ── Store Tests ────────────────────────────────────────────
describe("Hekate Store", () => {
  beforeEach(() => {
    jest.resetModules()
  })

  test("default mode is oracle", async () => {
    const { useHekate } = await import("../lib/store")
    const store = useHekate.getState()
    expect(store.currentMode).toBe("oracle")
  })

  test("setMode changes currentMode", async () => {
    const { useHekate } = await import("../lib/store")
    useHekate.getState().setMode("tarot")
    expect(useHekate.getState().currentMode).toBe("tarot")
  })

  test("shadow mode activates when mode set to shadow", async () => {
    const { useHekate } = await import("../lib/store")
    useHekate.getState().setMode("shadow")
    expect(useHekate.getState().shadowMode).toBe(true)
  })

  test("shadow mode deactivates when switching to non-shadow mode", async () => {
    const { useHekate } = await import("../lib/store")
    useHekate.getState().setMode("shadow")
    useHekate.getState().setMode("oracle")
    expect(useHekate.getState().shadowMode).toBe(false)
  })

  test("addMessage returns unique id", async () => {
    const { useHekate } = await import("../lib/store")
    const id1 = useHekate.getState().addMessage({ role: "user", content: "Test 1", mode: "oracle" })
    const id2 = useHekate.getState().addMessage({ role: "user", content: "Test 2", mode: "oracle" })
    expect(id1).not.toBe(id2)
  })

  test("updateMessage updates content", async () => {
    const { useHekate } = await import("../lib/store")
    const id = useHekate.getState().addMessage({ role: "assistant", content: "", mode: "oracle", isStreaming: true })
    useHekate.getState().updateMessage(id, "Yıldızlar konuşuyor...", false)
    const msg = useHekate.getState().messages.find(m => m.id === id)
    expect(msg?.content).toBe("Yıldızlar konuşuyor...")
    expect(msg?.isStreaming).toBe(false)
  })

  test("clearMessages empties messages array", async () => {
    const { useHekate } = await import("../lib/store")
    useHekate.getState().addMessage({ role: "user", content: "test", mode: "oracle" })
    useHekate.getState().clearMessages()
    expect(useHekate.getState().messages).toHaveLength(0)
    expect(useHekate.getState().sessionId).toBeNull()
  })

  test("setUser stores user correctly", async () => {
    const { useHekate } = await import("../lib/store")
    const user = { id: "123", email: "test@test.com", tier: "premium" as const,
                   daily_message_count: 0 }
    useHekate.getState().setUser(user)
    expect(useHekate.getState().user?.tier).toBe("premium")
  })
})

// ── Tier Limits Tests ──────────────────────────────────────
describe("Tier Limits", () => {
  test("free tier has 5 daily messages", async () => {
    const { TIER_LIMITS } = await import("../lib/store")
    expect(TIER_LIMITS.free.daily).toBe(5)
  })

  test("premium tier has unlimited messages", async () => {
    const { TIER_LIMITS } = await import("../lib/store")
    expect(TIER_LIMITS.premium.daily).toBe(9999)
  })

  test("free tier cannot use shadow mode", async () => {
    const { TIER_LIMITS } = await import("../lib/store")
    expect(TIER_LIMITS.free.shadow).toBe(false)
  })

  test("premium tier can use shadow mode", async () => {
    const { TIER_LIMITS } = await import("../lib/store")
    expect(TIER_LIMITS.premium.shadow).toBe(true)
  })

  test("canUseFeature returns correct values", async () => {
    const { canUseFeature } = await import("../lib/store")
    expect(canUseFeature("free", "shadow")).toBe(false)
    expect(canUseFeature("premium", "shadow")).toBe(true)
    expect(canUseFeature("pro", "pdf")).toBe(true)
    expect(canUseFeature("premium", "pdf")).toBe(false)
  })
})

// ── API Client Tests ───────────────────────────────────────
describe("API Client", () => {
  beforeEach(() => {
    global.fetch = jest.fn()
  })

  test("profileApi.getMe sends correct headers", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: "123", email: "test@test.com", tier: "free" }),
    })

    const { profileApi } = await import("../lib/api")
    await profileApi.getMe("test-token")

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/profile/me"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      })
    )
  })

  test("stripeApi.createCheckout sends tier in body", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ checkout_url: "https://checkout.stripe.com/test" }),
    })

    const { stripeApi } = await import("../lib/api")
    const result = await stripeApi.createCheckout("premium", "test-token")

    expect(result.checkout_url).toBe("https://checkout.stripe.com/test")
    const callArgs = (global.fetch as jest.Mock).mock.calls[0]
    const body = JSON.parse(callArgs[1].body)
    expect(body.tier).toBe("premium")
  })

  test("apiFetch throws on non-ok response", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 403,
      statusText: "Forbidden",
      json: async () => ({ detail: { code: "UPGRADE_REQUIRED" } }),
    })

    const { profileApi } = await import("../lib/api")
    await expect(profileApi.getMe("bad-token")).rejects.toMatchObject({
      status: 403,
    })
  })
})
