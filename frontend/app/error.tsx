"use client"; // A hibahatár csak kliens komponens lehet.

import Link from "next/link";

import { messages } from "@/lib/messages";
import { accent, onSurface } from "@/lib/tokens";

// Ha egy oldal szerveroldali hívása elbukik (pl. a háttér nem érhető el),
// a Next ezt mutatja a csupasz alapértelmezett hibaoldal helyett.
export default function ErrorPage({ unstable_retry }: { unstable_retry: () => void }) {
  return (
    <div className="mx-auto w-full max-w-3xl space-y-6 px-6 py-12" style={{ color: onSurface }}>
      <p role="alert" className="text-lg font-semibold">
        {messages.genericError}
      </p>
      <div className="flex flex-wrap gap-6 text-sm font-semibold">
        <button
          type="button"
          onClick={() => unstable_retry()}
          style={{ color: accent }}
          className="underline underline-offset-4"
        >
          {messages.errorPage.retry}
        </button>
        <Link href="/" style={{ color: accent }} className="underline underline-offset-4">
          {messages.errorPage.home}
        </Link>
      </div>
    </div>
  );
}
