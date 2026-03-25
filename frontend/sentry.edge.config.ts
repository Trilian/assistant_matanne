// Sentry edge runtime initialization
// Only active when @sentry/nextjs is installed and NEXT_PUBLIC_SENTRY_DSN is set
if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const Sentry = require("@sentry/nextjs");
    Sentry.init({
      dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
      environment: process.env.NEXT_PUBLIC_ENVIRONMENT || "development",
      tracesSampleRate: 0.1,
      debug: false,
    });
  } catch {
    // @sentry/nextjs not installed — skip
  }
}
