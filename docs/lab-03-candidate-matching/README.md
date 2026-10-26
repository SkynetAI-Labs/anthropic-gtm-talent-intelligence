# Part 3 — Explainable matching

The demonstration uses deterministic rules, not a connected language model. There is no Claude API integration or API cost. AI assisted project development; candidate assessment itself is rule-based.

## Scoring v1.1

Each role has competency weights totalling 100 in config/scoring.json. Evidenced competencies earn their weight proportion of 75 points. Relevant years earn up to 15 points against a role-specific illustrative benchmark. A direct industry context earns 10 points. No geography, name, nationality, age or other protected characteristic is read by the scorer.

Only declared skills with a non-empty evidence note earn credit. This verifies data presence, not truth or quality. Unknown or absent evidence earns zero but is displayed as unverified, never as proof that the candidate lacks the capability.

- Exact Match: score at least 85, all mandatory evidence present, experience benchmark met and direct industry context.
- Closest Match: score at least 65 after Exact checks.
- Transferable Skills Match: score at least 45 after earlier checks.
- Insufficient evidence: below 45, or no evidenced competencies.

The labels classify rule outcomes, not probabilities or recommendations to hire. A mandatory gap prevents Exact but does not automatically reject the candidate. A transferable label does not establish actual transferability without human screening.

Outputs include component points, matched competencies and evidence, unverified competencies, mandatory gaps, evidence coverage, screening questions and rule version. Recruiter review status comes from the candidate-vacancy application.

## Human oversight and limitations

Weights and thresholds are illustrative and have not been empirically validated. Years and industry context can disadvantage adjacent candidates; reviewers should inspect underlying evidence and consider equivalent capabilities. Never automate rejection or selection using these scores. Location is a search filter only. Do not infer protected traits from employment history or other fields. No claim of legal compliance or proven absence of bias is made.

Before production: validate scoring with job experts, assess adverse impacts using an appropriately governed process, improve evidence quality, implement permissions and audit controls, establish candidate correction routes and perform a proper data/privacy review. Changing rules requires calibration and regression tests.
