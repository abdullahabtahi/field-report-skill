---
name: field-report-landing
description: Build a dark, Palantir-grade "field report" landing page or case-study site in one consistent design world - near-black ground, hairline isometric linework, one reserved signal colour, an exploded layer-stack hero, scroll-scrubbed frame sequence, interactive figures drawn from sourced data, and an honest ledger of what was and was not measured. Use this whenever the user wants a landing page, case study, hackathon showcase, product story or "forward-deployed-engineer" style site that should feel like Palantir Foundry, QuantumBlack or an engineering report, or asks to reuse the same style, design and process as an earlier landing page, even if they never say "skill" or name the style. Also use it for the Magnific still-to-video-to-frames recipe behind such a hero. Do NOT use it for in-app UI such as dashboards, cockpits, admin screens or forms (an Operate surface), for generic bright SaaS marketing pages with metric tiles, for slide decks, or for logos and print design.
---

# Field report landing

A landing page built as an engineering field report: one exploded diagram of the system carries the story, every claim on it is a sourced result or a labelled gap, and the whole page lives in one strict visual world. This skill supplies that world and the process around it. It does not replace general design judgement: if an `impeccable` skill is available, call it for context loading, shaping, polish and audit, and use this skill for *what the page should look like and how the assets and proof are handled*.

Why this exists: the owner builds hackathon projects and turns each into a forward-deployed-engineer case study page. They want every one of those pages in this same design system: the colours, the design elements, the strong visual design and the Magnific-generated hero. So treat the world in `references/design-world.md` as **locked by default**: keep the palette, type, form language and motion exactly, and change only the content, the hero object, the story beats, the proof and the generated assets. Offer a different palette or type only if the user asks. Consistency across the owner's case studies is the point; a new look per project would defeat it.

The first page built this way was good because of a few decisions that are easy to lose (restraint, one hero object, sourced numbers, graded media, a real finish review). The references hold those decisions with their reasons so a new page starts from them, not from a blank slate.

For a hackathon case study the audience is the judges and the host's partners. Show the problem, the solution, the capabilities, how the host's platform services carry the system (name them, strongest first), the measured proof, the honest misses, and the event credit near the footer.

## Before you start

1. If `impeccable` is available (project `.claude/skills/impeccable` or user level), invoke it first and let it load `PRODUCT.md` / `DESIGN.md`. Do not redo what it does. If it is not available, do the same by hand: read any `PRODUCT.md`, `DESIGN.md` and existing surface briefs, and note what already exists.
2. Do not spend money (Magnific credits, any paid API) or deploy anything without the user saying so. Estimate cost first (`simulate_cost` for Magnific) and report it.
3. Never depend on uncommitted code in someone else's checkout; copy what you need from `assets/` here.

## Workflow

1. **Brief.** Fill `references/brief-template.md` with the user: audience, mode, thesis, story beats, proof sources, naming rules, palette overrides, closing action. Ask for what is missing; do not invent proof. The thesis is one sentence and it must be arguable ("a field report set as one exploded diagram", not "a modern landing page").
2. **Ground.** Ask for 2-3 reference sites or screenshots (or look up the named ones) and write down the *grammar* you borrow (layer diagrams, bracketed legends, dashed leaders), not their artwork. A page that copies assets is a liability; one that learns grammar is a style.
3. **Direction contract.** Copy `assets/direction-contract.template.md` into the project's surface-brief location (`.impeccable/surfaces/<slug>.md` when Impeccable is in use, else `docs/landing-direction.md`) and fill it. The contract has THESIS, OWN-WORLD, STORY, FIRST VIEWPORT, FORM, FINISH. Read `references/design-world.md` for the default world and why each rule exists. Keep the palette and type as parameters; keep the restraint rules as invariants.
4. **Story.** Follow `references/story-spine.md`. The spine is problem, response, the hero object turning, capabilities you can push on, the platform, proof, an honest ledger of misses, the close. A page that is all measurement fails the reader (that was real feedback on the first build): show the problem, the solution and the capabilities, then prove them.
5. **Assets.** Read `references/asset-recipe.md`. Use the frames in `assets/style-reference/` as the style reference so the new hero matches the owner's earlier pages. Generate a still from style references, then a short clip with that still as the start frame, then cut and grade frames with `scripts/frames_from_clip.sh`. Ask before generating; stills first, they are cheap. No text inside generated media: it garbles, and numbers must be exact.
6. **Build.** Start from the generator, not a blank file. Run `python3 scripts/scaffold_page.py --example > landing.config.json`, fill the config from the brief (layers, problem, response, capabilities, platform, ledger rows, misses, words to ban), then `python3 scripts/scaffold_page.py --config landing.config.json --out dist/`. It writes a complete single-file page in the house world (hero stack with legend, problem and response, capability frames, platform list, ledger with misses, close) plus `results.json`, from one config, so a number on the page cannot drift from its data. It refuses to build if the config has banned words, absolutes, an unknown tag, a figure without a source and date, a bar that is not the printed number, or no misses. `python3 scripts/make_stack_svg.py --config layers.json --out stack.svg` makes the hero alone. Then read `references/build-checklist.md` and add what the generator does not: interactive figures drawing from data files (headers naming sources), the scroll sequence with `assets/frameSequence.ts` and `assets/usePinnedSequence.ts`, a map or architecture figure if the story needs one. In a React or Next project, port the generated markup and CSS and keep the config as the source of truth. Scope CSS under one root class; keep files under 800 lines.
7. **Honesty pass.** Read `references/honesty-rules.md`, then run `python3 scripts/honesty_scan.py <src-dir> --banned "<words>"`. It catches absolutes, forbidden names and numbers that are not in a data file. It is a heuristic, so read what it flags.
8. **Verify in bounded passes.** Build, then one batched round of screenshots (desktop and 390 px mobile, plus reduced-motion), fix everything found in one batch, confirm once, stop. Run `python3 scripts/asset_version_check.py` when any raster changed. Then get an independent finish review (a fresh agent with `references/finish-review.md`) and fix what it scores.
9. **Document.** Add the landing world to `DESIGN.md` (tokens, form language, motion, figures, rasters) and write `PROVENANCE.md` for every shipped raster. Unreviewed and undocumented is unfinished.

## Decision points that belong to the user

- The thesis and the story beats.
- Any spend (generation credits) and any deploy.
- Naming rules and what may be said about data (real versus synthetic).
- Whether a fidelity gap between hero and generated frames is acceptable.

## Output

- A direction contract, the page code under a scoped root class, data files with sourced numbers, graded rasters with provenance, an updated `DESIGN.md`, and a short report that says what was built, what was measured, what was not, and what you are unsure of.

## Known failure modes (and why they matter)

- **Glow and bloom in generated frames** break the "no glow" rule and make the hero and orbit look like different pages. Lift the black point and cut saturation when grading; check frames against the hero side by side.
- **The reserved signal colour disappears after grading**, so the orbit reads flat. Re-check that the one accent survives.
- **Hero and orbit drift apart** (line weight, grey, a layer drawn differently). Unify the hero SVG to the generated frames, not the other way round.
- **Legend clips at 390 px.** Test mobile in the same pass as desktop.
- **Second half of the page goes text-only** with empty right halves. Give every long section a figure.
- **Captions not tied to the layer on screen.** Anchor each caption to the active layer with a bracket or leader.
- **About 325 MB of RAM from holding every decoded frame.** Use the sliding window; release when far away.
- **Stale immutable assets.** Long-cache rasters need a version query that is bumped when a file changes.
- **Absolutes in copy** ("never makes things up"). They invite the one counterexample. Say what is checked and how.
- **Calling data real or synthetic wrongly.** State what is each, precisely.
