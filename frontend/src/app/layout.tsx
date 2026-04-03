import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { TooltipProvider } from "@/composants/ui/tooltip";
import { FournisseurQuery } from "@/fournisseurs/fournisseur-query";
import { FournisseurAuth } from "@/fournisseurs/fournisseur-auth";
import { FournisseurTheme } from "@/fournisseurs/fournisseur-theme";
import { Toaster } from "@/composants/ui/sonner";
import { EnregistrementSW } from "@/composants/enregistrement-sw";
import { TransitionGlobale } from "@/composants/disposition/transition-globale";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#1a1a2e" },
  ],
};

export const metadata: Metadata = {
  title: "Assistant Matanne",
  description: "Hub de gestion familiale",
  manifest: "/manifest.json",
  icons: {
    apple: "/icons/icon-192x192.png",
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Matanne",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="fr"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <FournisseurTheme>
          <FournisseurQuery>
            <FournisseurAuth>
              <TooltipProvider>
                <TransitionGlobale>{children}</TransitionGlobale>
              </TooltipProvider>
            </FournisseurAuth>
          </FournisseurQuery>
          <Toaster richColors position="top-right" />
          <EnregistrementSW />
        </FournisseurTheme>
      </body>
    </html>
  );
}
