/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./weekend/templates/**/*.html",
    "./static/js/**/*.js",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        /* Remap shield palette to Python-themed colors */
        shield: {
          red: "#4B8BBE",          // python blue (used as primary accent)
          "red-dark": "#306998", // python blue dark
          navy: "#16213e",        // python navy
          blue: "#4B8BBE",
          ice: "#FFD43B",         // python yellow (accent)
          purple: "#6B21A8",     // accent purple (used in a few CTAs)
          sky: "#38BDF8",        // sky accent
          silver: "#94A3B8",
          star: "#0f172a",        // darker text tone
          steel: "#1a2535",
        },
        // custom single-use color
        "slight-violet": "#905ead",
        tactical: {
          DEFAULT: "#0B1118",
          light: "#131C28",
          card: "#1A2738",
        },
      },
      fontFamily: {
        comic: ['"Bebas Neue"', "sans-serif"],
        display: ['"Rajdhani"', "sans-serif"],
        body: ['"DM Sans"', "sans-serif"],
      },
      backgroundImage: {
        halftone:
          "radial-gradient(circle, rgba(56,189,248,0.12) 1px, transparent 1px)",
        "grid-tactical":
          "linear-gradient(rgba(56,189,248,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(56,189,248,0.04) 1px, transparent 1px)",
        "hero-gradient":
          "linear-gradient(135deg, #0B1118 0%, #1A2F4B 35%, #131C28 70%, #0B1118 100%)",
        "card-gradient":
          "linear-gradient(145deg, rgba(26,39,56,0.95) 0%, rgba(11,17,24,0.98) 100%)",
        "shield-stripe":
          "linear-gradient(90deg, #4B8BBE 0%, #4B8BBE 33%, #FFD43B 33%, #FFD43B 66%, #306998 66%, #306998 100%)",
      },
      backgroundSize: {
        halftone: "10px 10px",
        "grid-tactical": "48px 48px",
      },
      boxShadow: {
        shield: "0 0 24px rgba(75, 139, 190, 0.25), 0 0 48px rgba(255, 212, 59, 0.12)",
        "shield-red": "0 0 28px rgba(75, 139, 190, 0.35)",
        "shield-ice": "0 0 28px rgba(255, 212, 59, 0.35)",
        card: "0 8px 32px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(148,163,184,0.04)",
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "float-delayed": "float 8s ease-in-out 2s infinite",
        "pulse-glow": "pulseGlow 3s ease-in-out infinite",
        "slide-up": "slideUp 0.6s ease-out forwards",
        "slide-down": "slideDown 0.5s ease-out forwards",
        "fade-in": "fadeIn 0.8s ease-out forwards",
        "hero-text": "heroText 1s ease-out forwards",
        shimmer: "shimmer 2s linear infinite",
        glitch: "glitch 0.3s ease-in-out",
        "spin-slow": "spin 12s linear infinite",
        "blob-1": "blobMove1 20s ease-in-out infinite",
        "blob-2": "blobMove2 18s ease-in-out infinite",
        "blob-3": "blobMove3 22s ease-in-out infinite",
        "ken-burns": "kenBurns 20s ease-in-out infinite",
      },
      keyframes: {
          kenBurns: {
    "0%": {
      transform: "scale(1.1) translate(0px, 0px)"
    },
    "50%": {
      transform: "scale(1.2) translate(-20px, 10px)"
    },
    "100%": {
      transform: "scale(1.1) translate(0px, 0px)"
    },
  },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.6", transform: "scale(1)" },
          "50%": { opacity: "1", transform: "scale(1.05)" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(30px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { opacity: "0", transform: "translateY(-20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        heroText: {
          "0%": { opacity: "0", transform: "translateY(40px) skewX(-5deg)" },
          "100%": { opacity: "1", transform: "translateY(0) skewX(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        glitch: {
          "0%, 100%": { transform: "translate(0)" },
          "25%": { transform: "translate(-2px, 2px)" },
          "50%": { transform: "translate(2px, -2px)" },
          "75%": { transform: "translate(-2px, -2px)" },
        },
        blobMove1: {
          "0%, 100%": { transform: "translate(0, 0) scale(1)" },
          "33%": { transform: "translate(30px, -50px) scale(1.1)" },
          "66%": { transform: "translate(-20px, 20px) scale(0.9)" },
        },
        blobMove2: {
          "0%, 100%": { transform: "translate(0, 0) scale(1)" },
          "50%": { transform: "translate(-40px, -30px) scale(1.15)" },
        },
        blobMove3: {
          "0%, 100%": { transform: "translate(0, 0)" },
          "25%": { transform: "translate(50px, 30px)" },
          "75%": { transform: "translate(-30px, -40px)" },
        },
      },
    },
  },
  plugins: [],
};
