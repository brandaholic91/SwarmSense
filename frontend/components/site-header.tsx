"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { accent, onSurface, outlineVariant, surfaceContainer } from "@/lib/tokens";

// A közös felső sáv. A főoldalnak saját sávja van (logó és gomb), ott ez nem jelenik meg.
export function SiteHeader() {
  const pathname = usePathname();
  if (pathname === "/") {
    return null;
  }

  return (
    <header
      className="sticky top-0 z-40 flex h-20 shrink-0 items-center justify-center border-b"
      style={{ backgroundColor: surfaceContainer, borderColor: outlineVariant }}
    >
      <Link
        href="/"
        className="text-lg font-semibold tracking-tight"
        style={{ fontFamily: "var(--font-headline)", color: onSurface }}
      >
        Swarm<span style={{ color: accent }}>Sense</span>
      </Link>
    </header>
  );
}
