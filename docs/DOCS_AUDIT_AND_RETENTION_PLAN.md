# DOCS_AUDIT_AND_RETENTION_PLAN.md
_Last updated: 2026-04-09_

## 1. Goal

This file explains:
- which markdown files should remain active
- which should be updated
- which should be archived later
- which are likely redundant

This is a retention plan only.
It does **not** delete or overwrite history.

---

## 2. Recommended Active Docs (Keep)

### Keep as core operational docs
- `AOI_MASTER_ROADMAP.md`
- `AOI_PROJECT_STATE.md`
- `AOI_DEBUG_EVOLUTION.md`
- `README_phase1.md`
- `MES_INTEGRATION_BLUEPRINT.md`
- `REPO_CLEANUP_NOTE.md`

### Keep as working prompts / collaboration docs
- `AOI_IMPLEMENTATION_NEXT_PROMPT.md`
- `AOI_CLAUDE.md`
- `AOI_CHAT_INIT.md`
- `AOI_CLI_START_PROMPT.md`
- `AOI_COWORK_INSTRUCTIONS.md`
- `CLAUDE_PHASE2_API_PROMPT.md`

### Keep as baseline planning history
- `AOI_PHASE1_APPROVED_PLAN.md`

### Keep as granular debug history
- `DEBUG_LOG.md`

---

## 3. Recommended Update Targets

### Needs update now or soon
- `AOI_PROJECT_STATE.md`
  - should reference the new master roadmap
- `README_phase1.md`
  - should eventually include Phase 2 API run instructions after implementation
- `AOI_IMPLEMENTATION_NEXT_PROMPT.md`
  - should be refreshed once Phase 2 starts
- `REPO_CLEANUP_NOTE.md`
  - should reflect final cleanup status after second doc pass

---

## 4. Recommended Archive Candidates (Not delete now)

### Archive later under `docs/archive/` after Phase 2 begins
- `AOI_CHAT_INIT.md`
- `AOI_CLI_START_PROMPT.md`

Reason:
These are startup helper docs, useful historically, but they are not long-term system docs.

### Archive later only if superseded
- `AOI_PHASE1_APPROVED_PLAN.md`

Reason:
Once the master roadmap fully supersedes phase planning, this can become history rather than active guidance.

---

## 5. Root-level File Recommendation

### `DEBUG_LOG.md` in repo root
Recommendation:
- keep for now if it is currently referenced
- long-term: move to `docs/DEBUG_LOG.md` only and remove the duplicate root copy later

### Screenshot file
- `Snipaste_2026-04-01_20-00-05.jpg`
Recommendation:
- move later to `docs/archive/screenshots/`
- do not keep as a root-level tracked artifact long-term

---

## 6. Important Rule

Do not delete “history” docs aggressively.
This repo has interview value partly because it preserves:
- debugging history
- engineering reasoning
- project evolution
- phase-by-phase decision making

The goal is **structured retention**, not aggressive cleanup.
