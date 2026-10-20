# Brief: Ferryline (made-up product, for testing only)

Project: Ferryline, a disruption copilot for the dispatch desk of an island ferry operator.
One line: when weather or a breakdown breaks the timetable, Ferryline proposes a re-plan (which vessel, which sailings, which passengers to notify) in under a minute; a dispatcher approves it.
Event: Hack the Tides, a regional maritime-tech hackathon. Audience: the judges (maritime engineers and two investors).
Mode: Persuade.

Thesis: Ferryline is a field report set as one exploded diagram of the dispatch desk: weather in at the bottom, an approved re-plan out at the top, every claim a measured result or a labelled gap.

Story beats: 1 hero object; 2 problem (a storm cancels sailings and the desk re-plans by phone and spreadsheet); 3 response (a copilot that proposes and a dispatcher who decides); 4 capabilities: (a) weather-to-timetable impact model, (b) re-plan solver, (c) passenger notice drafting; 5 platform: runs on the host's cloud, show which services carry which step; 6 proof; 7 misses; 8 close: link to the live prototype.

Proof sources (these are SAMPLE figures for this test):
| Number | Source | As of | Tag |
| 38 s median time to a proposed re-plan | simulation run sim-2026-10-11, 120 storm scenarios | 2026-10-11 | MEASURED |
| 81% of sailings recovered within 60 min | same run | 2026-10-11 | MEASURED |
| 94% of passenger notices matched the approved re-plan | same run, 120 notices sampled | 2026-10-11 | MEASURED |
| Real-vessel pilot | none yet | - | NOT MEASURED |
| 9 of 120 scenarios left a vessel idle for over 2 hours | same run | 2026-10-11 | MEASURED (a miss) |

Words: never name the operator (call it "an island ferry operator"); say "dispatch desk", not "control room"; the scenarios are simulated, the weather feed is real public data.
Assets: a generated hero is wanted, but do not spend credits or generate anything in this test; write the prompts only.
Constraints: do not deploy anything; no external network assets in the page.
