# Brief: Tern (made-up product, for testing only)

Project: Tern, a triage tool for volunteers who monitor shorebird nesting beaches.
One line: volunteers upload nest photos; Tern flags nests at risk of disturbance (dogs, foot traffic, high tide) and tells the coordinator which beach to visit first.
Event: Coastwatch Hack, a regional conservation hackathon. Audience: judges (two ecologists, one engineer) and the sponsor's cloud team.
Mode: Persuade.

Thesis: Tern is a field report set as one exploded diagram of a beach survey: photos in at the bottom, a ranked visit list out at the top, every claim a measured result or a labelled gap.

Story beats: 1 hero object; 2 problem (volunteers file hundreds of photos a week and the coordinator reads them one by one, so at-risk nests are found after the damage); 3 response (a classifier flags risk and the tide model ranks beaches; the coordinator decides); 4 capabilities: (a) nest-photo risk classifier, (b) tide-and-footfall risk model, (c) visit-list ranking with the evidence beside each beach; 5 platform: runs on Tidewater Cloud; services: Datastore (stores photos and survey records, the strongest), Vision (the classifier), Run (hosts the app); 6 proof; 7 misses; 8 close: link to the prototype at https://example.org/tern (a placeholder URL for this test).

Proof sources (these are SAMPLE figures for this test, not real results):
| Number | Source | As of | Tag |
| 87% of 200 held-out nest photos classified correctly | held-out set eval-2026-10-12 | 2026-10-12 | SAMPLE |
| 4 min median from upload to a ranked visit list | 30 simulated survey days | 2026-10-12 | SAMPLE |
| 12 of 30 simulated days ranked the wrongest beach first | same | 2026-10-12 | SAMPLE (a miss) |
| Field trial with real volunteers | none yet | - | NOT MEASURED |

Words: never name the sponsor (say "the host cloud" in prose; the service names are fine); say "coordinator", not "admin"; photos are real public-domain nest images, tide data is real public data, survey days are simulated.
Assets: a generated hero is wanted, but do not spend credits or generate anything in this test; write the prompts only.
Constraints: do not deploy anything; no external network assets in the page.
