import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Statically exported and served by the FastAPI backend (see backend/app/main.py).
  output: "export",
};

export default nextConfig;
