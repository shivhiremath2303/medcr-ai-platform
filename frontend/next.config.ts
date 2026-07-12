import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  experimental: {
    // Optimization for large component libraries
    optimizePackageImports: ["lucide-react", "framer-motion"],
  },
};

export default nextConfig;
