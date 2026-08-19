/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        toy: {
          green: '#289d4d',
          darkgreen: '#1a6b34',
          lightgreen: '#3bc465',
          plastic: '#181b22',
        }
      },
      boxShadow: {
        'toy-bevel': 'inset 3px 3px 6px rgba(255,255,255,0.25), inset -3px -3px 6px rgba(0,0,0,0.5), 0 10px 25px rgba(0,0,0,0.6)',
        'tile-inset': 'inset 2px 2px 4px rgba(255,255,255,0.3), inset -2px -2px 4px rgba(0,0,0,0.6)',
        'pocket': 'inset 3px 3px 8px rgba(0,0,0,0.8), inset -1px -1px 3px rgba(255,255,255,0.1)',
      }
    },
  },
  plugins: [],
}
