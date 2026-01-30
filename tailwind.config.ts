import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: "#0B1B2B",
        },
        copper: {
          500: "#C46B38",
          600: "#B85A2A",
        },
      },
    },
  },
  plugins: [],
};

export default config;
