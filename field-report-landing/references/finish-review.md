# Finish review

Run this with a fresh agent that did not build the page, so it judges the result, not the intentions. Give it the direction contract, the built page (screenshots at desktop and 390 px, plus reduced motion) and this checklist. It returns a verdict per item and a disposition (`ship` or `fix`). Fix what it scores, then stop: one review, one fix batch, one confirmation.

## Score each, with evidence (a screenshot or a file and line)

1. **Contract fit.** Does each section obey OWN-WORLD? Look for gradients, glow, cards, filled tags, a second accent colour. Any "glow" in generated frames counts.
2. **Hero and orbit unification.** Same line weight, same grey, same drawing of each layer. List mismatches.
3. **Signal colour.** Is the one accent present in hero, orbit and figures, and only on the signal path and the active layer? Is the warn colour only on gaps?
4. **Captions anchored.** Does each pinned caption point at its active layer with a bracket or leader? Does the camera move far enough between first and last caption?
5. **No text-only stretches.** Every long section has a figure or diagram; no empty half-screens.
6. **Story completeness.** Problem, response, capabilities, platform, proof, misses, close all present; not measurement-only.
7. **Honesty.** Sample five numbers: each traces to a data file with a source. The misses are shown. No absolutes. Real versus synthetic stated precisely.
8. **Mobile at 390 px.** Legend not clipped, no horizontal scroll, order sensible.
9. **Accessibility.** Contrast of secondary text, inactive labels and dimmed states measured (not eyeballed; opacity-dimmed steps are the usual failure); focus ring; skip control in pinned sections; reduced motion shows a still with all captions.
10. **Performance.** No large memory growth while scrolling the sequence; rasters carry the version query.
11. **Headings and tags agree.** No section titled "Measured" over `SAMPLE` figures; no text claims more than its source; quantity words have a source.
12. **Documentation.** `DESIGN.md` entry and `PROVENANCE.md` exist and match what shipped.

## What the first review found (so you can look for the same things)

Bloom and arrow-tip glow in orbit frames; the orbit losing the signal blue after grading; a layer drawn differently in the hero and the orbit; the legend clipped on mobile; kicker numerals that added noise; inactive rail numerals too dim; captions not anchored to a layer; second half of the page text-only.
