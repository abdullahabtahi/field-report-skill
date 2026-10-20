# Build and performance checklist

Engineering decisions behind the page, with the reason for each. Framework-specific items assume React or Next.js; the ideas carry over.

## Contents
- Structure
- Scroll-scrubbed sequences
- Assets and caching
- Data and figures
- Fonts and CSS
- Verification

## Structure

- Make the page shell a **server component**; keep a single small client component (for example a reveal-on-scroll root) and put interactivity in the figures. Why: the page is mostly static; shipping all of it as client JS slows the first paint for no gain.
- One section per file; CSS split by concern and each file under about 800 lines. Why: reviewable, and the finish review reads the whole file.
- Scope every selector under one root class (for example `.fde`) and set `html:has(.root)` colour scheme there. Why: a landing world must not leak into an app that lives in the same project, and nothing from the app should leak in.

## Scroll-scrubbed sequences

Use `assets/frameSequence.ts` and `assets/usePinnedSequence.ts`.
- Decoded RGBA is about 3 MB a frame. Holding a whole 146-frame clip cost about 325 MB of RAM in headless Chromium. The window approach (frames near the viewport, sparse anchors for fast scrolls, release when far away) costs no measurable amount beyond the rest of the page.
- Prioritise the few frames nearest the shown one, then anchors, then the rest of the window. Under fast scrolling the window keeps moving, so anchors must not queue behind frames that get dropped.
- On screens up to 720 px step every other frame.
- If frames cannot load at all, or the user has reduced motion or save-data, show one static still and list all captions. Why: the page must still tell the story without the animation.
- Draw frames to a canvas, not as an `<img>` swap; one canvas avoids layout and decode jank.

## Assets and caching

- Serve rasters from a folder with a one-year immutable cache, and build every URL through one helper that appends `?v=<LANDING_ASSET_VERSION>`. **Bump the version whenever any raster changes**; otherwise visitors keep the old file for a year. `scripts/asset_version_check.py` automates the reminder.
- Ship responsive variants (`-1200`, `-1800`, full) with `srcset` for large stills.
- Generation sidecars and `PROVENANCE.md` live outside the served folder.
- Material icon font or other app-only stylesheets must not load on the landing; move them to the app layout. Why: a landing page that downloads the app's icon font pays for it on every visit.

## Data and figures

- Every figure draws from a baked snapshot in a data file. The header names the source (endpoint, document, query) and the as-of date. Why: it keeps the page fast and every number auditable.
- Components contain no numeric claims; copy and numbers live in a content file or data files. Why: the honesty scan can then check one place, and a change of number cannot be missed in a component.
- Map: lazily load the WebGL library and public-domain outlines; no basemap; disable scroll-zoom.

## Fonts and CSS

- If the project shadows the framework's font module with its own type declarations, add any new Google font there too, or the type check fails. (Seen once; check your setup.)
- Load the display font for real: with Next.js use the framework's font loader and set `--fde-sans` (and `--fde-mono`) from it; in a static HTML page self-host the font file with `@font-face`, or accept the system fallback and say so. Naming a font in CSS without loading it silently shows a fallback, so screenshots lie about the type. Compare a screenshot against the reference frames once the font loads.
- Tokens (`assets/tokens.css`) are CSS variables on the root class; the world is changed by changing variables, not by editing components.

## Verification

- Build, then one batched screenshot round: desktop, 390 px mobile, reduced motion. Fix everything in one batch, confirm once, stop.
- Check: legend not clipped at 390 px; contrast of secondary text and inactive labels measured; focus ring visible; skip control present in any pinned section; no console errors.
- Run `scripts/honesty_scan.py` and `scripts/asset_version_check.py`.
