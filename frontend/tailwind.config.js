/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#1b4332",
        secondary: "#0c0d10",
        accent: "#b45309",
        surface: "#ffffff",
        background: "#f6f2ee",
        border: "#e7e1db"
      }
    }
  },
  plugins: []
};
