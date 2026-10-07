import type { Metadata } from "next";
import { Geist_Mono, Outfit, Space_Grotesk } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-headline",
  subsets: ["latin"],
});

const spaceGrotesk = Space_Grotesk({
  variable: "--font-label",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "SwarmSense - Szintetikus piackutatás-demó",
  description:
    "Portfóliódarab: 18 szintetikus AI persona válaszol a kérdésedre, regisztráció nélkül. A futás élőben követhető, az eredmény PDF-ben letölthető. Valódi piackutatást nem vált ki.",
  openGraph: {
    title: "SwarmSense - Szintetikus piackutatás-demó",
    description:
      "Üzenetek, árazás és pozicionálás előszűrése 18 szintetikus persona válaszaival. Portfóliódarab, nem valódi piackutatás.",
    type: "website",
    locale: "hu_HU",
  },
  twitter: {
    card: "summary_large_image",
    title: "SwarmSense",
    description:
      "Szintetikus personák válaszai egy kérdésre: portfóliódarab, regisztráció nélkül.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="hu"
      className={`${outfit.variable} ${spaceGrotesk.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        {children}
      </body>
    </html>
  );
}
