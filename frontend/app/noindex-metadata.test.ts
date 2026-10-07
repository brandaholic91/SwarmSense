import { metadata as resultMetadata } from "@/app/eredmeny/[id]/page";
import { metadata as replayMetadata } from "@/app/eredmeny/[id]/visszajatszas/page";
import * as samplePage from "@/app/minta/page";
import { metadata as waitingMetadata } from "@/app/waiting/[run_id]/page";

describe("per-run pages are kept out of search indexes", () => {
  it.each([
    ["result", resultMetadata],
    ["replay", replayMetadata],
    ["waiting", waitingMetadata],
  ])("%s page sets noindex, nofollow", (_name, metadata) => {
    expect(metadata.robots).toEqual({ index: false, follow: false });
  });

  it("the sample page stays indexable", () => {
    const { metadata } = samplePage as { metadata?: { robots?: unknown } };
    expect(metadata?.robots).toBeUndefined();
  });
});
