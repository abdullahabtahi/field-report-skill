## Landing surface: Field Report (dark), {project}

A separate world for the case-study page of {project} ({event}). It is a Persuade surface: a forward-deployed-engineering case study set as one exploded isometric stack of the system's layers. App rules (if this repo has an app) do not apply to it, and nothing here may leak into app components. Tokens are scoped under `.fde` (`tokens.css`).

- **Ground and ink:** matte near-black ground (`#0e1116`), warm off-white ink (`#ecebe6`), secondary text at 68% ink, hairlines at 16% ink. One pale steel-blue (`#9db7cf`, `--sig`) is reserved for the signal path and the active layer. One warm state colour (`--warn`, `#d6a15f`) marks only a missed or unmeasured item. `--ink-3` (34% ink, about 2.8:1) is decoration only, never text.
- **Type:** one grotesque at regular weight (display `clamp(2.5rem, 4.2vw, 4.5rem)`, tracking -0.025em), uppercase tracked small labels, mono only for figures, ids and tags.
- **Form language:** sharp corners, hairline brackets with serif ticks, dashed leaders, no cards, no gradients, no glow, no glass. Tags are outlined, never filled.
- **Motion:** the hero slabs drawing in and one travelling dash on the signal arrow; everything is off under `prefers-reduced-motion`, where the drawing is complete.
- **Figures:** one figure frame (hairline border, control bar, caption naming the data's origin). Charts draw only values printed in the row's copy.
- **Honesty:** every number lives in `landing.config.json` / `results.json` with a source and as-of date; figures supplied as placeholders are tagged `SAMPLE`; gaps and misses are shown in the warn colour; real, synthetic and generated material are stated separately.
- **Rasters:** see `PROVENANCE.md`.
- **Direction contract:** {contract}
