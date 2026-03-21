# Result Email Compatibility Design-Intent Checklist (Story 5.2)

> **Scope:** This is a design-intent checklist based on rendered HTML inspection (`@react-email/render` output reviewed manually). It is NOT a live client rendering test — no external tooling (Litmus, Email on Acid) was used. Live client verification is deferred to a future Epic 5 story.

- Date: 2026-03-21
- Template: `frontend/emails/result-email.tsx`
- Verification method: Rendered HTML string inspection; structural and inline-style review against email client constraints

## Design-Intent Checklist

- [x] Gmail (web): above-the-fold summary now prioritizes consensus block (`role="alert"`) followed by aggregate score; table-safe markup, no floats or CSS grid.
- [x] Gmail (mobile): media-query fallback (`max-width: 620px`) stacks `.persona-column` cells to one column; no fixed card widths.
- [x] Apple Mail: spacing and left-border stance markers remain visible on persona cards — all styles inline, no external stylesheet dependency.
- [x] Outlook 2019: table structure keeps primary layout intact; no `border-radius` on table elements; no critical clipping expected in consensus block or first persona row.

## Notes

- Layout uses table-safe markup with `role="presentation"` for layout tables.
- All style-critical properties are inline CSS.
- Accent and stance semantics use shared tokens from `frontend/lib/tokens.ts`.
- `border-radius` was removed from `<table>` elements during code review (2026-03-21) to ensure Outlook 2019 compatibility.
- Persona cards now render full argument model (`primary_argument`, `change_condition`) with stance label text retained for non-color-only semantics.
- Footer now includes an explicit AI simulation interpretive disclaimer for FR18 transparency.
