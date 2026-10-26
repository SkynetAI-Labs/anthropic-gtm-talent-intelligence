# Verification record — editorial release v3

Verified 26 October 2026. This record supersedes earlier local release records.

## Results

Python 3.12.14 with the pinned requirements. A clean dependency installation was completed for v2; v3 uses the same environment and dependencies.

Final v3 automated run: **32 passed, 7 warnings in 6.40 seconds**. Warnings are the same Pandas deprecation from Streamlit's built-in chart helper, triggered when overview content renders. The chart renders successfully.

Checks cover fictional data consistency, combined search, contradictory records, missing evidence, scoring boundaries, excluded personal fields, all match categories, role-specific questions, stage progression/closure review, chronological history, filled-seat protection, coherent offers, an independently calculated analytics fixture, empty data, navigation, recruiter review/save, the selected candidate gap, the single Part 4 entry and removal of internal notes from the visible case study.

## Current demonstration

50 mapped prospects and 30 applications across five single-seat searches. Funnel ever-reached counts: 30 Applied, 24 Screened, 16 Shortlisted, 10 Interview, 6 Offer, 4 Hired. Offer outcomes: four accepted, one declined and one pending. Four vacancies are filled and one is open. Hired means accepted offer. Median completed time-to-hire is 24 days and time-to-fill is 27.5 days, both with n=4.

The selected FIC-026 example is an Enterprise Account Executive with six relevant years in cloud technology. Enterprise-sales evidence is present; AI literacy is unverified. The 88.8 score is Closest Match because the experience benchmark for Exact Match is not met. AI literacy is a specific screening topic. Scoring weights and thresholds are unchanged.

## Editorial and visual review

Navigation has Start here plus Parts 1–5. Part 4 contains Executive overview and Recruitment pipeline tabs. Part 1 presents role and market tables with the seven-step approach; detailed public-source material is in a collapsed Research notes section. Part 5 uses first-person experience and closes with a proposed week-one GTM hiring discussion.

Internal factual-signoff and publication instructions are excluded from the visible narrative and shareable source archive. A short Start here disclosure and the footer identify the independent, fictional demonstration. Technical matching limitations remain available in the collapsed rules section and technical documentation.

The revised strategy, pipeline tabs, case study and matching example were inspected in the running desktop browser. Earlier responsive review confirmed narrow layouts and sidebar controls; wide tables require horizontal scrolling. Screenshots are actual application captures. The ten-slide executive deck was rendered and inspected; changed v3 slides were rendered and checked again. The PPTX has not been opened in Microsoft PowerPoint.

Seed regeneration reproduced identical reviewed CSV/config hashes. No real-person sourcing, paid API or live Claude assessment service is connected. Assessment uses deterministic rules. No prediction or operational fairness validation is claimed.

## Sharing status

The application runs locally. No public application URL or new project repositories exist yet. The source package excludes private local review records, databases, credentials and cache files. Public hosting and repository creation remain separate actions. Dated vacancy research establishes examples of demand, not a comprehensive estimate of EMEA talent supply.


## Public release preparation

26 October 2026: the public entry point isolates each visitor in a session-specific in-memory SQLite database. The local entry point retains persistent SQLite behaviour. The three final copy touch-ups were applied. Automated run: **33 passed, 7 dependency deprecation warnings in 5.37 seconds**. The additional test verifies that one visitor’s saved stage change survives that visitor’s rerun and does not appear in a second visitor’s pipeline.
