# Honesty rules

The page's credibility is its whole value. These rules keep it, each with its reason. The honesty scan (`scripts/honesty_scan.py`) enforces the mechanical ones; the rest need judgement.

1. **Every number has a source.** It lives in a data or content file whose header names the document, query or endpoint and the as-of date. Why: an unsourced number is a claim; a reviewer will test one and the rest lose credit.
2. **Gaps are shown as gaps.** A result nobody measured is labelled `NOT MEASURED` in the warn colour. It is never zero and never "healthy". Why: a page with no gaps is not believed, and a fake zero is worse than an absence.
3. **Misses stay in the ledger.** If a test failed or a figure is weak, it appears with the same weight as the wins. If a miss is too damaging to show on the page, move it to speaker notes with the user's agreement; do not quietly drop it and still claim the area is covered.
4. **No absolutes.** Do not write "never", "always", "100%", "guaranteed", "perfect" about behaviour you cannot prove for every case. Say what is checked and how ("every figure is matched to an engine result before it is shown"). Why: absolutes invite the one counterexample.
5. **Say precisely what is real and what is synthetic.** Example of the wrong way: "all data is synthetic" when public reference data is also used. Describe each layer separately. Why: both over- and under-claiming are errors.
6. **Generated media is labelled.** AI-generated art is not described as a photograph, and a generated map is not described as a real region. Provenance for every raster.
7. **Recorded outputs are quoted verbatim.** Do not rewrite a model's answer to read better. Why: the quote is evidence.
8. **Charts show printed values only.** A bar or dot for a number the row's copy does not state is an unsourced claim.
9. **Naming rules are followed.** If the brief says the client is never named, or prefers one word to another ("desk", not "dashboard"), the scan checks for the banned words.
10. **Latency, cost and quality claims name their conditions.** Median and p95, over how many runs, on what data, from where. A single run is not a median.
11. **Sample, illustrative or test figures are tagged as such.** If the owner supplies figures as sample or illustrative, tag them `SAMPLE` (or `ILLUSTRATIVE`) on the page, not `MEASURED`, and say so in the data statement. Why: `MEASURED` is a promise that a real run produced the number; a placeholder wearing that tag is the exact fault the page exists to avoid. Ask the owner when a figure's status is unclear.
12. **Do not derive numbers the source does not state.** 94% of 120 is 112.8, not a whole number, and 9 of 120 is not a percentage until the owner says it is. Print the source's figure and describe the rest in words ("the rest"). If you must derive one, tag it `DERIVED` and show the arithmetic in the data file. Why: a derived number is a new claim with no run behind it.
13. **Do not say more than the source says.** Restate a finding as given. "No field trial with real volunteers has been run" is what the source says; "no volunteer has ever used it" is a bigger claim. The same goes for quantity words with no number behind them ("hundreds of photos a week"): give them a ledger row with a source, tag them, or say "many". Why: the review of a test build caught exactly these, and each one is an unsourced claim.
14. **Headings must agree with their tags.** A section titled "Measured" over figures tagged `SAMPLE` contradicts itself. The generator titles the ledger from the tags; if you write your own heading, check it against the rows beneath.
15. **Do not present a build as production unless it is.** If the product shows no synthetic-data marker of its own, the page or video must say so.
