# Nagorik Sheba — Task List / Backlog

Generated as part of Week 1 initiation. Convert each item into a GitHub Issue as work begins; keep this file as the source-of-truth backlog and check items off as they're completed.

Legend: `[H]` High priority · `[M]` Medium · `[L]` Low — mirrors SRS requirement priorities.

---

## Week 1 — Initiation & SRS

- [x] Define project scope, objectives, and team roles
- [x] Draft SRS document (AI-assisted, team-reviewed) — `docs/Nagorik_Sheba_SRS_v0.1.docx`
- [ ] Create GitHub repository, add collaborators, protect `main` branch
- [ ] Add `README.md`, `CONTRIBUTING.md`, `.gitignore`
- [ ] Create folder scaffold: `backend/`, `website/`, `mobile/`, `docs/`, `scripts/`
- [ ] Team review pass on SRS — confirm/adjust requirement priorities before Week 2
- [ ] Set up shared task board (GitHub Projects) mirroring this file

## Week 2 — Design (proposed)

- [ ] `[H]` Entity-Relationship Diagram covering: users, complaints, departments, wards, toilets, ratings, emergency_services, endorsements
- [ ] `[H]` API contract (routes, request/response shapes) for all modules in SRS §3
- [ ] `[H]` System architecture diagram (client / agent pipeline / data / jurisdiction layers)
- [ ] `[M]` Wireframes: citizen complaint flow, staff dashboard, public toilet map, emergency directory
- [ ] `[H]` Sign up for Barikoi API key (free tier); test Ward-by-Geolocation coverage against Khulna coordinates before committing to it as the jurisdiction resolver
- [ ] `[L]` Draft SMS message format spec (structured command syntax)

## Week 3+ — Implementation backlog (by module)

### Backend core
- [ ] `[H]` Auth: JWT issuing/verification, bcrypt password hashing
- [ ] `[H]` Citizen signup with selfie + NID upload, perceptual-hash consistency check
- [ ] `[H]` Staff account seeding script (7 departments)
- [ ] `[H]` Role-based dashboard routing on login

### Complaint pipeline
- [ ] `[H]` Complaint submission endpoint (text, photo, GPS)
- [ ] `[H]` Jurisdiction resolver via Barikoi API (GPS → ward/City Corporation/Union Parishad), with manual polygon fallback
- [ ] `[H]` Location+category duplicate lock / resubmission block
- [ ] `[H]` Moderation Agent (LLM + rule-based fallback)
- [ ] `[H]` Classification Agent (LLM + rule-based fallback)
- [ ] `[H]` Verification Agent: EXIF check, perceptual-hash duplicate detection, AI content-consistency check
- [ ] `[H]` Priority Agent (frequency + endorsement weighted scoring)
- [ ] `[H]` Routing Agent (deterministic, SLA assignment)
- [ ] `[M]` SLA-breach escalation to higher administrative tier

### Citizen participation
- [ ] `[M]` Complaint search (SQLite FTS5, keyword + category + ward filters)
- [ ] `[M]` Complaint endorsement ("similar complaint" voting), feeding Priority Agent
- [ ] `[M]` Reopen-if-unsatisfied flow
- [ ] `[M]` Resolution photo requirement before status = done

### New modules
- [ ] `[M]` Public toilet locator: schema, seed data (15–20 real Khulna locations), map markers
- [ ] `[M]` Toilet cleanliness rating endpoint + rolling average
- [ ] `[L]` Citizen-submitted toilet proposal + staff approval flow
- [ ] `[M]` Emergency services directory: schema, seed Khulna fire service stations + national numbers
- [ ] `[M]` "Nearest station" haversine query + click-to-call UI
- [ ] `[M]` SMS webhook endpoint (Twilio sandbox) + message parser
- [ ] `[M]` SMS reply with complaint ID + tracking link
- [ ] `[M]` Verification-tier flag for SMS-only (no-photo) complaints

### Transparency features
- [ ] `[M]` Public complaint feed (anonymized, no login)
- [ ] `[M]` Ward-level department scorecard (avg resolution time, open/closed ratio)
- [ ] `[L]` Public closure notes on resolved complaints

### Frontend / Website
- [ ] `[H]` Citizen dashboard: category picker, complaint form, track tab
- [ ] `[H]` Staff dashboard: priority queue, agent trail view, status controls
- [ ] `[M]` Public map view: toilets + emergency stations + complaint feed layers
- [ ] `[M]` Mobile-responsive breakpoint pass (900px staff multi-panel)
- [ ] `[L]` PWA offline-first pass (service worker, low-bandwidth mode)

### Mobile (if required by course scope)
- [ ] `[M]` Rebuild Expo app: Login, Signup (NID/selfie), Home, Report (map pin picker)
- [ ] `[L]` Push notifications (Firebase Cloud Messaging)

### Test data
- [ ] `[H]` Generate synthetic SPECIMEN NID card dataset via `scripts/mock_nid_generator.py`
- [ ] `[M]` Pair mock cards with team members' own consenting selfies for end-to-end signup testing

### QA / Documentation
- [ ] `[M]` End-to-end test pass mirroring the original curl-tested flows, extended to new modules
- [ ] `[M]` Update SRS to v0.2/v1.0 after Week 2 design review
- [ ] `[L]` Record demo video / prepare defense walkthrough

---

## How to use this file

1. When starting a task, create a matching GitHub Issue, assign an owner, add labels (`backend`, `frontend`, `ai-agent`, `week-N`, etc.).
2. Reference the issue number in your PR (`Closes #N`).
3. Check the box here once merged to `dev`.
4. Re-prioritize freely — this is a living backlog, not a fixed contract.