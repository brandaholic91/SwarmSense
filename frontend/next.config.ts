import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Önálló szerver a .next/standalone mappába: a Docker-kép ebből fut.
  output: "standalone",
};

export default nextConfig;
