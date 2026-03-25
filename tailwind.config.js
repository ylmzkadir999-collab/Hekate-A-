/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        void:     "#04030A",
        abyss:    "#08051A",
        cave:     "#0F0820",
        deep:     "#160B2E",
        purple:   "#1E0A3C",
        amethyst: "#4A1E6E",
        violet:   "#7B3FA0",
        astral:   "#A855F7",
        lavender: "#C084FC",
        gold:     "#C9A84C",
        "gold-bright": "#E8C56A",
        silver:   "#D1D5DB",
      },
      fontFamily: {
        cinzel:    ["var(--font-cinzel)", "serif"],
        "cinzel-d": ["var(--font-cinzel-decorative)", "serif"],
        garamond:  ["var(--font-garamond)", "serif"],
      },
      animation: {
        "float":      "float 4s ease-in-out infinite",
        "glow-pulse": "glowPulse 3s ease-in-out infinite",
        "spin-slow":  "spin 20s linear infinite",
        "fade-up":    "fadeUp 0.5s ease forwards",
      },
      keyframes: {
        float:     { "0%,100%": {transform:"translateY(0)"}, "50%": {transform:"translateY(-8px)"} },
        glowPulse: { "0%,100%": {opacity:"0.6"}, "50%": {opacity:"1"} },
        fadeUp:    { from: {opacity:"0",transform:"translateY(12px)"}, to: {opacity:"1",transform:"translateY(0)"} },
      },
      backgroundImage: {
        "nebula": "radial-gradient(ellipse 100% 70% at 15% 10%, rgba(30,10,60,0.9) 0%, transparent 55%), radial-gradient(ellipse 70% 90% at 85% 90%, rgba(74,30,110,0.35) 0%, transparent 55%), radial-gradient(ellipse 50% 50% at 50% 50%, rgba(168,85,247,0.04) 0%, transparent 60%)",
      },
    },
  },
  plugins: [],
}
