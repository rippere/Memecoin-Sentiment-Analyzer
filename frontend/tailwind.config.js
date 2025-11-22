/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // Custom colors for crypto dashboard
      colors: {
        // Backgrounds (dark theme)
        'bg-primary': '#0f1419',
        'bg-secondary': '#1a1f2e',
        'bg-card': '#252d3d',

        // Text colors
        'text-primary': '#e6e9f0',
        'text-secondary': '#8b93b6',

        // Sentiment colors (industry standard)
        'bullish': '#16c784',      // Green for positive
        'bearish': '#ea3943',      // Red for negative
        'neutral': '#8b93b6',      // Gray for neutral

        // Accent colors
        'accent': '#3861fb',       // Blue for interactive
        'accent-purple': '#936df8', // Purple accent
      },
    },
  },
  plugins: [],
}
