# GIT_WORKFLOW_AND_BRANCH_POLICY.md
_Last updated: 2026-04-09_

## 1. Goal

This file defines when to:
- commit directly
- create a branch
- open a PR
- avoid unnecessary branch/PR overhead

This policy is optimized for:
- solo development
- demo readiness
- interview portfolio quality
- minimal confusion

---

## 2. Current Repo Stage

Current repo state:
- public GitHub repo exists
- Phase 1 completed and pushed
- repo still in early solo-build stage

At this stage, excessive branch/PR ceremony is not required for every tiny change.

---

## 3. Recommended Rule of Thumb

### Direct commit to `main` is OK when:
- markdown-only updates
- README changes
- docs cleanup
- small bug fix with very limited scope
- no change to output contract
- no change to training / inference behavior

### Use a branch when:
- adding FastAPI service
- changing inference behavior
- changing JSON contract logic
- adding YOLO phase code
- changing file structure materially
- integrating with MES-side adapters
- any feature that may require rollback

### Open a PR when:
- the change is architecturally significant
- you want a review checkpoint before merge
- the change affects demo behavior
- the change affects API contract
- the change crosses from “script” to “system”
- the diff is large enough that future-you will want a clean review trail

---

## 4. Recommended Branch Names

Examples:
- `feature/aoi-fastapi-service`
- `feature/aoi-yolo-baseline`
- `feature/aoi-batch-inference`
- `docs/aoi-roadmap-refresh`
- `refactor/infer-helper-cleanup`

---

## 5. Recommended Upcoming Branch Usage

### Next likely branch
When implementing Phase 2 API:

Use:
`feature/aoi-fastapi-service`

Suggested flow:
1. create branch
2. implement API
3. test locally
4. review JSON contract
5. merge into `main`

### Why a branch is recommended here
Phase 2 is the first true “systemization” step.
It affects:
- serving behavior
- integration direction
- demo story

That is worth a review checkpoint.

---

## 6. Suggested Commands

### Create next feature branch
```bash
git checkout -b feature/aoi-fastapi-service
```

### After finishing work
```bash
git status
git add .
git commit -m "Phase 2: add FastAPI service for AOI inference"
git push -u origin feature/aoi-fastapi-service
```

### Later merge approach
If working solo, merge after review:
```bash
git checkout main
git pull
git merge feature/aoi-fastapi-service
git push
```

---

## 7. Practical Guidance

Use `main` for:
- stable, demoable state

Use feature branches for:
- active implementation
- risky or nontrivial changes

Use PR-style review even if solo when:
- you are changing architecture
- you may need rollback
- you want a clean change story for future demo/interview explanation
