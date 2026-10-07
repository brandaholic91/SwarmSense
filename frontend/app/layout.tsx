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
  title: "SwarmSense - Szintetikus piackutatás percek alatt",
  description:
    "Validald az üzenetedet szintetikus AI personákkal. Tedd fel a kérdésedet, és perceken belül strukturált kutatási eredményt kapsz.",
  openGraph: {
    title: "SwarmSense - Szintetikus piackutatás percek alatt",
    description:
      "Gyors piaci visszajelzés AI personákkal: üzenetek, árazás és pozicionálás tesztelése várakozás nélkül.",
    type: "website",
    locale: "hu_HU",
  },
  twitter: {
    card: "summary_large_image",
    title: "SwarmSense",
    description:
      "Piaci visszajelzés percek alatt szintetikus personákkal.",
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
