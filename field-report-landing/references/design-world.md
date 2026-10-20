# The Field Report world

Defaults for the look. Values are parameters (change them per project); the *rules* and their reasons are the invariants. When you change a value, keep the relationship (one signal colour, one state colour, hairlines at low opacity), not the hex.

## Contents
- Thesis and what it refuses
- Ground, ink and colour
- Type
- Form language
- Motion
- Figures and interactivity
- Map and architecture figures
- Tags
- Responsive and accessibility

## Thesis and what it refuses

A field report set as one exploded systems diagram: the deployed system read bottom to top, every claim on it a result or a labelled gap. It refuses the SaaS hero with metric tiles and any claim without a source.
Why: reviewers (hackathon judges, technical buyers) have seen the bright SaaS page a thousand times. A page that reads like an engineering report earns trust before it asks for any.

## Ground, ink and colour

| Token | Default | Rule and reason |
|---|---|---|
| `--ground` | `#0e1116` | Matte near-black. Matte, not glossy: gloss and gradients read as consumer. |
| `--ink` | `#ecebe6` | Warm off-white. Pure white vibrates on near-black. |
| `--ink-2` | ink at 68% | Secondary text. Keep above 4.5:1 on the ground; measure it. |
| `--ink-3` | ink at 34% | Decoration only: leaders, dividers, inactive ticks. It measures about 2.8:1 on the ground, below the 4.5:1 floor, so it is never used for text (a test build found the generator had used it for captions). Text uses `--ink-2` or stronger. |
| `--rule` | ink at 16% | Hairlines. One weight everywhere so the page feels drawn, not decorated. |
| `--sig` | `#9db7cf` | ONE steel-blue, reserved for the signal path and the active layer. If it appears on decoration it stops meaning anything. |
| `--warn` | `#d6a15f` | ONE warm colour, only for a missed, unmeasured or at-risk item. It makes gaps visible, which is the credibility device. |

No gradients, no glass, no glow, no shadows, no cards. Why: each one adds an effect that is not information; the world works because everything on screen is a line, a label or a figure.

## Type

- Display and body: one grotesque at regular weight (default Schibsted Grotesk; any neutral grotesque works). Display `clamp(2.5rem, 4.2vw, 4.5rem)`, tracking about -0.025em. Large and light beats bold.
- Labels: the same family, uppercase, tracked, small.
- Mono: only for figures, ids, hashes and tags. Why: mono carries "this is data"; using it for prose cheapens that signal.
- A page uses at most two families.

## Form language

- Sharp corners. Hairline brackets with short serif ticks for legends. Dashed leaders from a thing to its label. Arrow lists for components. Thin isometric linework for diagrams.
- Tags are outlined, never filled.
- Legends are numbered and bracketed; the numbering ties the hero to the sections below it.
Why: this is the visual grammar of layer diagrams and engineering drawings; it signals rigour without ornament.

## Motion

One authored moment: the pinned scroll sequence (a rendered orbit of the hero object drawn on a canvas as the section scrolls). Plus the hero slabs drawing in and one travelling dash on the signal arrow. Everything stops under `prefers-reduced-motion`, where the sequence becomes a static still with all captions listed. Also fall back to the still on save-data.
Why: one moment is memorable; five is noise. And a page that autoplays heavy media at people who asked it not to is a defect.

## Figures and interactivity

- One figure frame: hairline border, control bar on top, caption with the data's origin below.
- Controls: outlined switches, outlined chip buttons, a segmented control whose pressed state inverts to ink.
- Each figure draws from a baked snapshot in a data file whose header names the endpoint, query or document and the as-of date. Quote recorded outputs verbatim.
- Charts draw only values already printed in the row's copy. No axis numbers; labels carry the values. Reference values are a vertical tick, earlier or weaker values a hollow dot.
Why: a chart that shows a number the copy does not state is an unsourced claim. Baked snapshots keep the page fast and make every figure auditable.

## Map and architecture figures

- Map: a WebGL map library over public-domain outlines with no basemap; arcs coloured by tier (ink low, signal medium, warn high); scroll-zoom off so the page keeps scrolling.
- Architecture: isometric platforms in the hero's slab grammar; a chip with a signal-colour left tick marks a service of the cloud provider you are showcasing; traced paths animate as dashed hops. Above about 1100 px the trace can be scroll-linked and pinned; any control takes over, and scrolling back to the top hands it back. Provide a visible skip control so no one is trapped in a long pinned section.
Why: for a platform showcase the architecture is the proof; make it explorable but never a trap.

## Dimmed and inactive states

An inactive step, tab or slab is distinguished by a hairline border, weight or position, not by fading its text. Dimmed text must still meet 4.5:1 (measure it): a review of a test build found inactive trace steps at 2.1:1 and 3.2:1 because they were dimmed with opacity.

## Tags

Outlined vocabulary such as `MEASURED`, `TESTED IN CI`, `NOT MEASURED`, `BY DESIGN`. Use the set that fits the project but keep it small and defined once.

## Responsive and accessibility

- Mobile: legends open their brackets and keep a right gutter (a clipped legend at 390 px was a real defect); sequences step every other frame; the stack sits behind content at low opacity when space is tight.
- Contrast measured, not eyeballed, for ink-2 and for inactive rail numerals.
- Visible focus ring in the signal colour; skip-to-content; every canvas has a text alternative; reduced motion honoured.
