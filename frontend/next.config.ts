import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/app/login.html',
        destination: '/login',
      },
      {
        source: '/app/login',
        destination: '/login',
      },
      {
        source: '/app/dashboard',
        destination: '/dashboard',
      },
      {
        source: '/app/dashboard/',
        destination: '/dashboard',
      },
    ];
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
