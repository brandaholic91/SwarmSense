import { act, fireEvent, render, screen } from "@testing-library/react";

import { RotatingPlaceholder } from "@/components/rotating-placeholder";

const setMatchMedia = (matches: boolean) => {
  window.matchMedia = ((query: string) => ({
    matches,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })) as typeof window.matchMedia;
};

describe("RotatingPlaceholder", () => {
  let originalMatchMedia: typeof window.matchMedia;

  beforeEach(() => {
    originalMatchMedia = window.matchMedia;
    vi.useFakeTimers();
    setMatchMedia(false);
  });

  afterEach(() => {
    vi.useRealTimers();
    window.matchMedia = originalMatchMedia;
  });

  it("cycles placeholder examples every 4 seconds", () => {
    render(
      <RotatingPlaceholder
        aria-label="Research topic"
        examples={["Example A", "Example B", "Example C"]}
      />
    );

    const field = screen.getByLabelText("Research topic");
    expect(field).toHaveAttribute("placeholder", "Example A");

    act(() => {
      vi.advanceTimersByTime(4000);
    });

    expect(field).toHaveAttribute("placeholder", "Example B");

    act(() => {
      vi.advanceTimersByTime(4000);
    });

    expect(field).toHaveAttribute("placeholder", "Example C");
  });

  it("stops cycling on focus and does not restart after blur", () => {
    render(
      <RotatingPlaceholder
        aria-label="Audience"
        examples={["Sample A", "Sample B", "Sample C"]}
      />
    );

    const field = screen.getByLabelText("Audience");

    act(() => {
      vi.advanceTimersByTime(4000);
    });

    expect(field).toHaveAttribute("placeholder", "Sample B");

    fireEvent.focus(field);

    act(() => {
      vi.advanceTimersByTime(12000);
    });

    expect(field).toHaveAttribute("placeholder", "Sample B");

    fireEvent.blur(field);

    act(() => {
      vi.advanceTimersByTime(4000);
    });

    expect(field).toHaveAttribute("placeholder", "Sample B");
  });

  it("stops cycling when focused before any timer tick (zero-tick focus)", () => {
    render(
      <RotatingPlaceholder
        aria-label="Zero tick"
        examples={["First", "Second", "Third"]}
      />
    );

    const field = screen.getByLabelText("Zero tick");
    expect(field).toHaveAttribute("placeholder", "First");

    fireEvent.focus(field);

    act(() => {
      vi.advanceTimersByTime(8000);
    });

    expect(field).toHaveAttribute("placeholder", "First");
  });

  it("does not add aria-live or role=status to the textarea", () => {
    const { container } = render(
      <RotatingPlaceholder
        aria-label="Accessible field"
        examples={["One", "Two", "Three"]}
      />
    );

    const field = screen.getByLabelText("Accessible field");
    expect(field).not.toHaveAttribute("aria-live");
    expect(field).not.toHaveAttribute("role", "status");
    expect(container.querySelector("[aria-live]")).toBeNull();
    expect(container.querySelector("[role='status']")).toBeNull();
  });

  it("disables cycling when prefers-reduced-motion is enabled", () => {
    setMatchMedia(true);

    render(
      <RotatingPlaceholder
        aria-label="Reduced motion"
        examples={["Alpha", "Beta", "Gamma"]}
      />
    );

    const field = screen.getByLabelText("Reduced motion");
    expect(field).toHaveAttribute("placeholder", "Alpha");

    act(() => {
      vi.advanceTimersByTime(8000);
    });

    expect(field).toHaveAttribute("placeholder", "Alpha");
  });
});
