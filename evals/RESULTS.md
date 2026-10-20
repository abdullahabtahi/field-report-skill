# Eval results (2026-10-20)

Two made-up briefs, each built once with the skill and once without it (a fresh agent each, no questions allowed), then scored by an objective grader (`evals/grade.py`, 20 and 23 checks). Briefs are in `evals/files/`.

| | Brief | With skill | Without skill | Tokens (with / without) | Time (with / without) |
|---|---|---|---|---|---|
| 1 | Ferryline: hero plus ledger | 20 / 20 | 17 / 20 | 126k / 95k | 405 s / 282 s |
| 2 | Tern: the whole page | 23 / 23 | 18 / 23 | 128k / 137k | 269 s / 511 s |

Side-by-side hero screenshots: `evals/results/iteration-1-hero-comparison.png`, `evals/results/iteration-2-hero-comparison.png`.

## What the numbers say
- **Fidelity to the design system and to the honesty rules is the skill's clear gain.** Without it, runs invented their own section names, used a gradient or blur, a saturated cyan or an orange where the house uses a muted steel-blue and amber, no start-frame step in the asset prompts, and (brief 2) no cost-approval step.
- **Iteration 1 cost about 30% more tokens; iteration 2 cost less** (the generator in `scripts/` builds most of the page, so the agent did less hand work). Treat the time and token figures as one sample each.
- **The baseline was not weak.** Both no-skill runs kept every printed number in a data file, showed the misses, did not name the sponsor, and the brief-2 baseline built richer interaction (an explode toggle, a filterable ledger). The skill adds consistency and checks, not a better page in every respect.

## Independent finish review (brief 2, with-skill page)
A fresh reviewer scored the page against `references/finish-review.md` and returned disposition **fix** with six must-fix items. Causes in the skill, now fixed: the generator headed the ledger "Measured, and what was not" over SAMPLE figures (heading now follows the tags); a quantity word ("hundreds of photos") had no source (the checks now warn on quantity words); text claimed more than its source (new honesty rule); dimmed trace steps measured 2.1:1 and 3.2:1 (new rule: dimmed text keeps 4.5:1); and no `DESIGN.md` (the scaffolder now writes `DESIGN-landing.md` and `PROVENANCE.md`). The page itself was not re-fixed. The generator also used the low-contrast `--ink-3` token for text; it no longer does.

## Trigger description
The description optimiser (3 iterations, 2 runs per query, 20 queries, 12 train and 8 held out) measured **0% recall on every iteration, including for the original description**, with 100% precision (nothing triggered, so nothing falsely triggered). A harness that never triggers the skill gives no signal about the description, so its rewrite is **not adopted** and the original is kept. Whether the skill triggers on its own for real requests is **untested**. The query set (`evals/trigger-evals.json`) was not reviewed by the owner.

## Grader changes made during the runs (disclosed)
- Mobile-breakpoint check now understands em and rem; two house-colour checks added.
- The colour-count check counts only colours with value above 0.5 (a dark neutral had been counted as a third hue; this helped the with-skill score in iteration 1).
- The "never" absolute no longer matches "never measured / been / run / tried / tested" (a baseline page said "what was never measured", which is legitimate; the same fix was made in the scaffolder and scan). This raised the baseline in iteration 2 from 17 to 18.
- Several checks encode the skill's own conventions (contract section names, start frames in prompts), so they measure whether the skill is followed, not whether the page is better.

## What this does not prove
- Two briefs, one run per arm: no variance estimate.
- Neither page used a generated hero, a scroll sequence, an interactive data figure, a map or an architecture figure with real data; those are not exercised. The orbit and caption items in the finish review were marked not built.
- Nothing here shows the skill triggers on its own, or that the generator's hero layout generalises to hero objects other than a layer stack.
- Not tested on a real project, in Safari or Firefox, or with a screen reader.
