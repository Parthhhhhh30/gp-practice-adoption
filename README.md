# CASEWORK — The Support Investigation Desk

**Independent legal-tech-inspired support investigation lab; not affiliated with Solve Intelligence or an actual law firm.** All customers, legal matters, systems, logs and outcomes are fictional.

**Live:** https://casework-investigation-desk-parthhhh.vercel.app/

## What actually works

- Four independent support cases, each with a controlled state and diagnostic flow.
- **Real HTTP calls to fictional Vercel server endpoints**, including an actual HTTP 200 GraphQL response whose body contains an application-level error, followed by a successful request when a required variable is supplied. The fictional endpoints do not integrate with real software.
- Login-session, document-version/security and legal-boundary diagnostics executed by `/api/lab`.
- An investigation history, human-reviewed written responses, issue handovers and closure rules.
- Priority routing: a possible confidentiality event can be escalated without first completing a routine support checklist.
- Reviewed, fictional troubleshooting articles that can be reused within other related practice cases.
- A controlled, deterministic evaluation of eight routing fixtures.

**Persistence:** Browser-local IndexedDB. It survives a refresh and is isolated by browser profile, but **is not a cloud database, authenticated service, multi-user CRM or secure customer ticket store.** The source is an educational portfolio exercise, not enterprise infrastructure.

## Model connector

`/api/ai` contains an actual Google Gemini generateContent integration for **optional critique of fictional, unsent customer replies**. Live calls require a securely configured `GEMINI_API_KEY` *and* explicit `CASEWORK_ALLOW_MODEL_CALLS=true` on the Vercel project. Both are absent by default. The public baseline does **not** make model calls; the interface never labels deterministic rules as AI output.

**Security/usage caveat:** Enabling a provider key on a public unauthenticated endpoint can expose its quota to abuse. Do not enable public model calls without effective rate limits and access protection. No new API payments or subscriptions are required for the current functional investigations.

## Tests

Run `npm test` (Node 20+). It covers the rules and actual Vercel endpoint handlers. Playwright smoke tests run against the deployed application via GitHub Actions and check a complete issue journey, browser storage, escalation and mobile navigation.

## What the project cannot prove

It does not demonstrate support for actual Solve customers, production GraphQL/NetDocuments/iManage integration, genuine patent advice, compliance certification, measured commercial impact or independently validated AI evaluation. It is a working **simulation** of support operations, not a replacement for Intercom, Pylon or Zendesk.
