/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html' // Scans all .html files
  ],
  darkMode: "class",
  theme: {
    extend: {
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        card: {
          DEFAULT: "var(--card)",
          foreground: "var(--card-foreground)",
        },
        popover: {
          DEFAULT: "var(--popover)",
          foreground: "var(--popover-foreground)",
        },
        primary: {
          light: "var(--primary-light)",
          DEFAULT: "var(--primary)",
          dark: "var(--primary-dark)",
          foreground: "var(--primary-foreground)",
        },
        secondary: {
          light: "var(--secondary-light)",
          DEFAULT: "var(--secondary)",
          dark: "var(--secondary-dark)",
          foreground: "var(--secondary-foreground)",
        },
        muted: {
          DEFAULT: "var(--muted)",
          foreground: "var(--muted-foreground)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          foreground: "var(--accent-foreground)",
        },
        destructive: {
          DEFAULT: "var(--destructive)",
          foreground: "var(--destructive-foreground)",
        },
        border: "var(--border)",
        input: "var(--input)",
        ring: "var(--ring)",
        chart: {
          1: "var(--chart-1)",
          2: "var(--chart-2)",
          3: "var(--chart-3)",
          "4.": "var(--chart-4)", // Note: The key was "4." in the original, keeping it.
          5: "var(--chart-5)",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        serif: ["var(--font-serif)"],
        mono: ["var(--font-mono)"],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "gradient-animation": {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
        "aurora": {
          "from": { backgroundPosition: "50% 50%, 50% 50%" },
          "to": { backgroundPosition: "350% 50%, 350% 50%" },
        },
        "slide-in-left": {
          "from": { opacity: 0, transform: "translateX(-20px)" },
          "to": { opacity: 1, transform: "translateX(0)" },
        },
        "fadeIn": {
          "from": { opacity: 0, transform: "translateY(10px)" },
          "to": { opacity: 1, transform: "translateY(0)" },
        },
        "pulse-soft": {
          "0%, 100%": { boxShadow: "0 0 0 0 var(--primary-light)" },
          "50%": { boxShadow: "0 0 0 10px rgba(0,0,0,0)" },
        },
        "shimmer": {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "gradient-pulse": "gradient-animation 8s ease-in-out infinite",
        "aurora": "aurora 60s linear infinite", 
        "fade-in-up": "fadeIn 0.5s ease-out forwards",
        "slide-in-left": "slide-in-left 0.5s ease-out forwards",
        "pulse-soft": "pulse-soft 2s infinite",
        "shimmer": "shimmer 1.5s infinite",
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'), // This will help style your form fields
  ],
}