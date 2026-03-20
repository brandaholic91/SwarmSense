# Design System Documentation

## 1. Overview & Creative North Star: "The Silent Authority"

This design system is built for a sober, high-density B2B environment where data is the protagonist. We are moving away from the "standard" SaaS template to achieve an aesthetic of **Precision Brutalism**. 

The Creative North Star is **The Silent Authority**. Like a high-end physical timepiece or a Bloomberg terminal, the UI should feel expensive, indestructible, and surgically precise. We achieve this not through decorative flair, but through the "luxury of space" (generous vertical padding) and extreme typographic hierarchy. We replace traditional structural lines with tonal layering to create a layout that feels carved from a single block of obsidian.

---

## 2. Colors & Surface Architecture

The palette is rooted in the `zinc` spectrum, utilizing a "Deep Dark" philosophy. The single amber accent is used sparingly, acting as a laser-sight for the user’s attention.

### The "No-Line" Rule
Standard UI relies on borders to separate content. This system prohibits 1px solid borders for sectioning. Boundaries must be defined through **Background Color Shifts**. For example, a content block using `surface-container-low` (#131316) should sit directly on a `background` (#0e0e10) to define its shape.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of materials. 
- **Base Layer:** `surface` (#0e0e10) for the primary application canvas.
- **Structural Sections:** `surface-container` (#19191d) for sidebars or navigation regions.
- **Information Nodes:** `surface-container-high` (#1f1f24) for cards or data modules.
- **Actionable Layers:** `surface-container-highest` (#25252b) for hovered states or active overlays.

### Signature Textures & Glass
To avoid a "flat" digital look, use **Glassmorphism** for floating elements (modals, tooltips). Use `surface-variant` (#25252b) at 60% opacity with a `20px` backdrop-blur. 
For main CTAs, use a subtle radial gradient: `primary` (#ffb95f) to `primary-dim` (#fea619). This provides a "honed metal" feel rather than a plastic, flat color.

---

## 3. Typography: The Editorial Scale

Typography is our primary tool for expressing authority. We use a dual-font system to separate narrative from data.

- **The Sans-Serif (Inter):** Used for headlines and body. Use `display-lg` (3.5rem) for high-impact data summaries. The generous `line-height` in `body-md` ensures that even dense research papers feel breathable.
- **The Monospace (Space Grotesk):** Assigned to `label-md` and all numerical data. Monospaced numbers ensure that columns of data align perfectly, conveying a sense of mathematical "correctness."

**Editorial Intent:** Use `headline-lg` (2rem) with `zinc-50` for page titles, but drop the body text to `zinc-400`. This high-contrast pairing ensures the user's eye gravitates toward the structure of the information immediately.

---

## 4. Elevation & Depth

We eschew traditional drop shadows for **Tonal Layering**.

- **The Layering Principle:** Depth is achieved by "stacking" surface tiers. Place a `surface-container-lowest` (#000000) card on a `surface-container-low` (#131316) section to create a soft, natural "recessed" effect.
- **Ambient Shadows:** For floating elements like dropdowns, use an extra-diffused shadow: `offset: 0 20px, blur: 40px, color: rgba(0,0,0, 0.4)`. The shadow must feel like a natural light obstruction, not a glow.
- **The Ghost Border:** If a border is required for accessibility (e.g., input focus), use the `outline-variant` (#47474e) at **20% opacity**. Never use 100% opaque borders for containment.

---

## 5. Components

### Buttons
- **Primary:** Background: `primary` (#ffb95f), Text: `on_primary` (#5c3800). Shape: `md` (0.375rem). No border.
- **Secondary:** Background: `surface-container-highest` (#25252b), Text: `on_surface` (#e7e4ec).
- **Tertiary:** No background. Text: `zinc-400`. Amber `primary` text on hover.

### Inputs & Search
- **The Data-Entry Cell:** Background: `surface-container-low` (#131316). Border: None. Bottom-only `outline-variant` (#47474e) at 10% opacity. 
- **Focus State:** Transition the bottom border to `primary` (#ffb95f) with a `1px` height.

### Cards & Lists
- **Rule:** Absolute prohibition of divider lines.
- **Separation:** Use the Spacing Scale. Use `8` (2.75rem) or `10` (3.5rem) of vertical white space to separate list items. 
- **Interaction:** On hover, change the item background to `surface-container-high` (#1f1f24) and apply a `sm` (0.125rem) corner radius.

### Chips & Badges
- **Status Badges:** Use `tertiary_container` (#f8a010) background with `on_tertiary_fixed` (#2a1700) text for high-priority alerts.
- **Data Chips:** Use `secondary_container` (#3b3b3e) for metadata, keeping the aesthetic sober and secondary to the primary data point.

---

## 6. Do's and Don'ts

### Do
- **Use the `24` Spacing Token:** Apply `py-24` (8.5rem) to major page sections. The tool must feel "expensive" through its refusal to crowd the user.
- **Align Data to the Right:** All numerical data in tables should be right-aligned using the Monospace font for vertical scanning.
- **Use Intentional Asymmetry:** If a dashboard has three widgets, don't make them equal widths. Use a 2/3 and 1/3 split to create an editorial, non-templated look.

### Don't
- **No "AI Glow":** Do not use purple/blue gradients or neon blurs. All light must come from the Amber `primary` source or tonal shifts.
- **No Heavy Outlines:** Avoid `outline` (#75757c) at full opacity. It breaks the "Silent Authority" aesthetic and makes the tool look like a generic UI kit.
- **No Vibrant Success States:** Avoid bright green. Use `zinc-50` for success icons with a subtle `primary` (Amber) checkmark.