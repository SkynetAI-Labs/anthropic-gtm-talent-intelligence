# Part 4 — Recruitment pipeline and analytics

Five hypothetical vacancies each have one seat. The mapped talent pool contains 50 fictional people, of whom 30 have entered an application process. Twenty remain prospects without an application.

The seeded funnel contains 30 Applied, 24 Screened, 16 Shortlisted, 10 Interview, 6 Offer and 4 Hired events. Offer outcomes are four accepted, one declined and one pending. The declined and pending offers belong to the fifth search. Four searches are filled and one remains open.

Applied means the candidate has agreed to enter this search. Mapped prospects are not automatically applicants. Hired means accepted offer, not employment start. Recruiter review is required for progression. Rejection or withdrawal needs a recorded human-reviewed reason. Further offers or hires against a filled single-seat vacancy are blocked.

## Definitions

- Mapped people: all 50 distinct profiles, including prospects without applications.
- Applications: candidate-vacancy pairs, tracked separately from mapped people.
- Open vacancies: searches without an accepted offer, displayed out of the total.
- Funnel: applications ever reaching each stage, retaining subsequent closures. The denominator is the preceding stage count.
- Time-to-hire: Applied to accepted offer, completed applications only.
- Time-to-fill: opening to first accepted offer, completed searches only.
- Open age: today's date minus opening for unfilled searches.
- Source conversion: accepted offers divided by applications attributed to that source at entry.

Accepted divided by offers extended includes pending decisions and is not a final close rate. The dashboard does not diagnose poor performance from the smallest funnel ratio. All data is simulated; the sample cannot establish channel effectiveness.

The v2 database is separate from the original database to preserve earlier local edits. This single-user demonstration has no authentication, real candidate data or ATS connection.
