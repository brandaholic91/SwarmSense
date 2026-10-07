import { render } from "@testing-library/react";

import PrivacyPage from "@/app/privacy/page";
import TermsPage from "@/app/terms/page";
import { messages } from "@/lib/messages";

vi.mock("next/server", () => ({ connection: async () => {} }));

afterEach(() => {
  vi.unstubAllEnvs();
});

async function pageText(page: () => Promise<React.JSX.Element>) {
  const { container } = render(await page());
  return container.textContent ?? "";
}

describe("Privacy page", () => {
  it("states the facts of the demo", async () => {
    const text = await pageText(PrivacyPage);

    for (const phrase of ["14 nap", "DeepSeek", "Resend", "IP-cím", "HMAC", "Discord", "NAIH"]) {
      expect(text).toContain(phrase);
    }
  });

  it("no longer mentions the old product", async () => {
    const text = (await pageText(PrivacyPage)).toLowerCase();

    for (const phrase of ["mágikus", "várólista", "leiratkoz", "hozzájárulás", "15 percen", "7 naptári"]) {
      expect(text).not.toContain(phrase);
    }
  });

  it("shows the contact address when CONTACT_EMAIL is set", async () => {
    vi.stubEnv("CONTACT_EMAIL", "kapcsolat@example.test");
    const text = await pageText(PrivacyPage);

    expect(text).toContain("kapcsolat@example.test");
    expect(text).not.toContain(messages.legal.contactFallback);
    expect(text).not.toContain(messages.legal.linkWarning);
    expect(text).toContain(messages.legal.deletionBody);
  });

  it("shows the fallback sentence without CONTACT_EMAIL", async () => {
    vi.stubEnv("CONTACT_EMAIL", "");
    const text = await pageText(PrivacyPage);

    expect(text).toContain(messages.legal.contactFallback);
    expect(text).not.toContain("@");
  });

  it("warns against posting the run link in a public issue without CONTACT_EMAIL", async () => {
    vi.stubEnv("CONTACT_EMAIL", "");
    const text = await pageText(PrivacyPage);

    expect(text).toContain(messages.legal.linkWarning);
    expect(text).toContain(messages.legal.deletionBodyNoAddress);
    expect(text).not.toContain(messages.legal.deletionBody);
  });
});

describe("Terms page", () => {
  it("describes a free demo without the old product", async () => {
    const text = (await pageText(TermsPage)).toLowerCase();

    expect(text).toContain("bemutató");
    for (const phrase of ["mágikus", "előfizetés", "e-mailben kézbesíti", "próba", "fizetős", "díjazás"]) {
      expect(text).not.toContain(phrase);
    }
  });

  it("shows the contact address when CONTACT_EMAIL is set", async () => {
    vi.stubEnv("CONTACT_EMAIL", "kapcsolat@example.test");

    expect(await pageText(TermsPage)).toContain("kapcsolat@example.test");
  });

  it("shows the fallback sentence without CONTACT_EMAIL", async () => {
    vi.stubEnv("CONTACT_EMAIL", "");

    expect(await pageText(TermsPage)).toContain(messages.legal.contactFallback);
  });
});
