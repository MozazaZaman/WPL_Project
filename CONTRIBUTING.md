# Contributing to Nagorik Sheba

Guidelines for the project team so our GitHub history stays clean and reviewable — this matters for the course's evaluation of process, not just the final product.

## Repository setup (do this once)

1. Create a **private** GitHub repository named `nagorik-sheba` (make it public later only if the supervisor requires it).
2. Add all team members as collaborators.
3. Protect the `main` branch: Settings → Branches → Add rule →
   - Require a pull request before merging
   - Require at least 1 approval
   - Do not allow direct pushes to `main`
4. Add this file, the README, and a `.gitignore` (Node) as the first commit.
5. Create the initial folder structure: `backend/`, `website/`, `mobile/`, `docs/`, `scripts/`.

## Branching model

- `main` — always working, always demo-able. Never commit directly.
- `dev` — integration branch; feature branches merge here first, `dev` merges to `main` at week-end checkpoints.
- Feature branches: `feature/<short-description>` (e.g. `feature/toilet-locator`, `feature/sms-webhook`)
- Bug fixes: `fix/<short-description>`
- Docs: `docs/<short-description>`

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) style:

```
feat: add public toilet rating endpoint
fix: correct haversine distance unit bug
docs: update SRS with SMS channel requirements
refactor: extract jurisdiction resolver into utils/geo.js
test: add duplicate-complaint locking test
```

Keep commits small and scoped to one change. Don't bundle unrelated files.

## Pull requests

- One feature/fix per PR.
- PR description must state: what changed, why, and how it was tested.
- At least one other team member reviews and approves before merge.
- Squash-merge into `dev` to keep history readable.
- Link the related task/issue in the PR description (e.g. `Closes #12`).

## Issues / task tracking

- Every task in `docs/tasks.md` should become a GitHub Issue once work starts on it.
- Use labels: `backend`, `frontend`, `mobile`, `ai-agent`, `docs`, `bug`, `week-1` … `week-N`.
- Assign an owner and a rough estimate before starting.

## Code style

- Backend: consistent `async/await`, no unhandled promise rejections; run existing lint config if present.
- Frontend: keep the website framework-free per current scope; no build step introduced without team agreement.
- Bangla text (department names, UI strings) stays in UTF-8, never transliterated in code — keep it readable for all teammates.

## Environment & secrets

- Never commit `.env`, API keys, or the Claude / Barikoi / Twilio credentials.
- Provide a `.env.example` with variable names only.
- Each teammate keeps their own local `.env`.
- Never commit real personal data. Test NID/selfie data must come only from `scripts/mock_nid_generator.py` (synthetic, watermarked SPECIMEN cards) paired with a consenting teammate's own selfie — never a real third party's identity documents.

## Weekly checkpoint

At the end of each week:
1. Merge `dev` → `main` once the week's demo is stable.
2. Tag the commit (`git tag week-1`, `week-2`, …).
3. Update `docs/tasks.md` — check off completed items, add next week's backlog.