/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#5B84B1",
        accent: "#E6B8A2",
        cream: "#FAF7F2",
        card: "#FFFFFF",
        text: "#223",
      },
    },
  },
  plugins: [],
}
