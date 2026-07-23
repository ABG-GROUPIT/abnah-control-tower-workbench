import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

const repositoryName = process.env.GITHUB_REPOSITORY?.split("/")[1] ?? "";
const base = process.env.GITHUB_ACTIONS === "true" && repositoryName
  ? `/${repositoryName}/`
  : "/";

export default defineConfig({
  base,
  root: path.resolve(__dirname, "github-pages"),
  publicDir: path.resolve(__dirname, "github-pages/public"),
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname),
    },
  },
  build: {
    outDir: path.resolve(__dirname, "pages-dist"),
    emptyOutDir: true,
    sourcemap: true,
  },
  server: {
    port: 4173,
  },
});
