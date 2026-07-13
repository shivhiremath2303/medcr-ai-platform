import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "@/styles/globals.css";
import { AppProviders } from "@/core/providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    template: '%s | MedCr Legal AI',
    default: 'MedCr Legal AI Platform | Enterprise Investigation Assistant',
  },
  description: "Enterprise-grade AI platform for legal investigation assistance using Hybrid RAG, Multi-Agent Reasoning, and Grounded Citations.",
  keywords: ["Legal AI", "RAG", "Legal Investigation", "AI Conflict Detection", "Case Timeline AI", "Legal NLP"],
  authors: [{ name: "MedCr Platform Team" }],
  icons: {
    icon: '/favicon.ico',
  },
  openGraph: {
    title: 'MedCr Legal AI Platform',
    description: 'Enterprise-grade AI for legal professionals.',
    type: 'website',
  }
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#09090b' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5, // A11y: allow zoom
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="scroll-smooth">
      <body className={`${inter.variable} font-sans antialiased selection:bg-primary/10 selection:text-primary`}>
        <AppProviders>
          {children}
        </AppProviders>
      </body>
    </html>
  );
}
