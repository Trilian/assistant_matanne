import type { NextConfig } from "next";
import bundleAnalyzer from "@next/bundle-analyzer";

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

const isProduction = process.env.NODE_ENV === "production";

function construireCsp(): string {
  const connectSrc = process.env.NEXT_PUBLIC_API_URL
    ? `${process.env.NEXT_PUBLIC_API_URL} ${process.env.NEXT_PUBLIC_API_URL.replace(/^https?:/, "wss:")}`
    : "http://localhost:8000 ws://localhost:8000 wss://localhost:8000";

  const scriptSrc = isProduction
    ? "script-src 'self'"
    : "script-src 'self' 'unsafe-inline' 'unsafe-eval'";
  const styleSrc = isProduction ? "style-src 'self'" : "style-src 'self' 'unsafe-inline'";

  return [
    "default-src 'self'",
    scriptSrc,
    styleSrc,
    "img-src 'self' data: blob: https://*.supabase.co",
    "font-src 'self' data:",
    `connect-src 'self' https://*.supabase.co https://*.sentry.io ${connectSrc}`,
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join("; ");
}

const nextConfig: NextConfig = {
  // Standalone output pour Docker staging
  output: process.env.NEXT_OUTPUT === "standalone" ? "standalone" : undefined,
  // Permettre les images depuis le backend et Supabase
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.supabase.co" },
    ],
    formats: ["image/avif", "image/webp"],
    minimumCacheTTL: 2592000, // 30 jours
  },
  // Headers de sécurité
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Strict-Transport-Security",
            value: "max-age=63072000; includeSubDomains; preload",
          },
          {
            key: "Permissions-Policy",
            value: "camera=(self), microphone=(self), geolocation=(self), payment=()",
          },
          {
            key: "Content-Security-Policy",
            value: construireCsp(),
          },
          { key: "X-Permitted-Cross-Domain-Policies", value: "none" },
        ],
      },
    ];
  },
};

let config = withBundleAnalyzer(nextConfig);

// Wrap with Sentry if @sentry/nextjs is available and configured
if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
  try {
    // Dynamic import not possible in config, use require
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { withSentryConfig } = require("@sentry/nextjs");
    config = withSentryConfig(config, {
      silent: true,
      hideSourceMaps: true,
    });
  } catch {
    // @sentry/nextjs not installed — skip
  }
}

export default config;
