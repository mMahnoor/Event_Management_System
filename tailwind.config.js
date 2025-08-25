/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./**/templates/**/*.html"],
  theme: {
    extend: {
      transform: {
        "rotate-y-180": "rotateY(180deg)",
      },
    },
  },
  plugins: [],
  safelist: [
    "border-2",
    "border-gray-300",
    "font-bold",
    "uppercase",
    "w-full",
    "p-3",
    "m-1",
    "rounded-lg",
    "shadow-sm",
    "focus:outline-none",
    "focus:border-yellow-400",
    "focus:ring-yellow-400",
    "placeholder-yellow-700/50",
  ],
};
