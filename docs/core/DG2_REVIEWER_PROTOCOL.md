# DG-2 Reviewer Protocol

_Last updated: 2026-06-02._
**Status: governance protocol for the DG-2 expert-review process.**
This document defines reviewer-level vocabulary and procedure for the
DG-2 gold-dataset review. It is **portfolio-scale**: it formalises the
solo-reviewer workflow used today and names the conditions under which
that workflow would need to evolve to be "promotion-grade." It does
**not** claim to implement an industrial fab-grade inspection process
(KLA / AMAT-style tool-and-process flows are out of scope). It does
**not** modify code, contracts, labels, or any other tracked spec.

---

## 1. Purpose & scope

### 1.1 Purpose

To give a single tracked answer to "what is a reviewer allowed to assert
about a DG-2 image, and how does an assertion turn into something that
could later support DG-1 v0 → v1 promotion or G4 baseline lock?"
Without this, in-progress observations risk being either over-read (as
findings) or under-read (as private notes).

### 1.2 Scope

- Applies to the DG-2 gold-dataset expert review (per
  `B_PROJECT_BRIEF.md` §9.2 / §9.4 and
  `B8_3_V1_VS_V2_ANALYSIS.md` §7.1).
- Defines reviewer-action vocabulary (§2), reviewer protocol (§3),
  current-status anchor (§4), the future requirements that would convert
  the current working-review into a promotion-grade process (§5 / §6),
  and what is intentionally **not** in scope (§7).
- Uses the same status tags as the other DG / B8.3 docs:
  **[implemented]**, **[in progress]**, **[planned]**, **[gated]**,
  **[deferred]**.

### 1.3 What this doc explicitly does NOT do

- Does **not** change any GT label, manifest, or dataset file.
- Does **not** promote any in-progress working artifact into the tracked
  governance set; in particular it does **not** promote
  `outputs/DG2_P1_REVIEW_OBSERVATIONS_DRAFT.md` or
  `outputs/DG2_EXPERT_REVIEW_EXTENSION_DRAFT.md`.
- Does **not** un-gate the Enhancement Track or any other gate.
- Does **not** add or modify the locked AOI JSON contract, the §4.3
  detection schema, or any code path.
- Does **not** claim alignment with KLA / AMAT / vendor-specific fab
  inspection processes. The protocol below is portfolio-scale governance
  hygiene, not a fab-deployable methodology.

---

## 2. Reviewer-action vocabulary

A reviewer assertion about an image can be one of three things, in
ascending scope. Names below are normative.

### 2.1 Suspect-label flag

**Definition:** the reviewer judges that an image's existing GT label
*may* be wrong, but is **not yet committing** to a specific alternative
label and is **not** proposing a change to the class taxonomy.

**Required record (portfolio-scale):**
- short justification (1–2 sentences) referencing visible morphology;
- one or more candidate alternative classes from the existing 7-class
  ontology, marked as candidates not as decisions.

**Effect:** none on labels, manifests, or the model. The image is
recorded as warranting a closer look; it does **not** count as a
re-label and it does **not** count as a taxonomy change.

**Example shape (no real assertion here):** "Image XXXX shows feature Y;
GT class A may be incorrect; candidate alternatives: B or C."

### 2.2 Label-change candidate

**Definition:** the reviewer proposes that a specific image's GT label
should change to a specific different existing class. Scope is exactly
one image. The class **ontology** is unchanged.

**Required record (portfolio-scale):**
- the new candidate label (one of the existing 7 classes);
- a written justification referencing DG-1 §10.2 cues and/or external
  literature, in the reviewer's own words;
- explicit "not yet authorised" framing: a label-change candidate is a
  *proposal* until it clears the gate in §3.4.

**Effect:** none on the on-disk label until the gate clears. The
candidate exists only in the working review memo.

### 2.3 Taxonomy-change candidate

**Definition:** the reviewer judges that the underlying class boundaries
need revision — for example, that a single class encompasses
morphologically distinct sub-types, or that two existing classes overlap
without an adjudicable boundary. Scope is multi-image and ontology-level.

**Required record (portfolio-scale):**
- the specific class(es) involved;
- the proposed ontology change in plain language (e.g., "split class X
  into X-a and X-b on cue Z");
- ≥ 2 image-level examples supporting the change (more is better; small
  N is acknowledged);
- explicit "not yet authorised" framing: a taxonomy-change candidate is
  the heaviest reviewer action and never automatically promotes.

**Effect:** none on labels, manifest, DG-1 §10.2 spec, or downstream
artifacts until the gate in §3.5 clears. The candidate exists only in
the working review memo and, eventually, in a discussion log.

### 2.4 What none of these three categories is

A reviewer assertion in any of the three categories is **not**:
- a fix proposal for the model;
- a request for retraining, augmentation, focal-loss, or threshold
  change;
- an edit to `B_PROJECT_BRIEF.md` §10 (DG-1 v0 spec);
- a change to `src/b_yolo/dg2_review_candidates.py` or any candidate
  vocabulary;
- a change to the locked AOI JSON contract.

Reviewer assertions remain governance observations until and unless a
gate clears.

---

## 3. Reviewer protocol

### 3.1 Inputs

- The image and its existing label, from
  `data/processed/roboflow_wafer_yolo/test/{images,labels}/`
  (read-only).
- The relevant priority bucket in
  `results/b8_3_dg2_review_image_summary_v1.csv` (working artifact,
  never committed).
- The DG-1 v0 ontology in `B_PROJECT_BRIEF.md` §10.2 as the cue
  reference.
- Optionally: external literature, dataset documentation
  (e.g., the Roboflow Universe listing), or any review aids under
  `outputs/dg2_review_batch_a/` and similar working directories.

### 3.2 Output destination

- All reviewer outputs land in the per-batch working memo under
  `outputs/` (currently `outputs/DG2_P1_REVIEW_OBSERVATIONS_DRAFT.md`
  for the P1 pass and `outputs/DG2_EXPERT_REVIEW_EXTENSION_DRAFT.md`
  for the Batch A extension).
- The `[REVIEWER]` slots in those memos are the canonical fill-in
  locations.
- The memos remain **working review**, not tracked artifacts.

### 3.3 Per-image action — making a suspect-label flag

1. Confirm the image is on the priority list for the relevant batch.
2. Record morphology, GT-vs-prediction split, and the 1–2 sentence
   reason for suspicion. Reference DG-1 §10.2 cues where possible.
3. Name one or more candidate alternative classes from the existing
   7-class ontology. Mark them as candidates, not decisions.
4. Stop. No label is changed.

### 3.4 Per-image action — promoting a flag to a label-change candidate

A suspect-label flag can be **rewritten** as a label-change candidate
only when:
1. one specific alternative class is named (not multiple);
2. the justification cites DG-1 §10.2 cues *or* external literature
   *or* a documented morphology-class mapping; and
3. the candidate has been re-read by the same reviewer after at least
   one calendar day (single-rater consistency check — see §5).

A label-change candidate does **not** convert into an on-disk label
change inside this protocol. The on-disk change is a separate, later
governance decision and is out of scope for this document.

### 3.5 Cross-image action — proposing a taxonomy-change candidate

A taxonomy-change candidate may be raised only when:
1. ≥ 2 image-level examples are recorded supporting the proposed
   boundary change;
2. the cue under which the existing class fails to discriminate is
   stated in plain language;
3. an explicit acknowledgement is recorded that small-N evidence
   (typically N = 2–10) is a hypothesis, not a finding.

A taxonomy-change candidate does **not** convert into a DG-1 §10.2
spec edit inside this protocol. Any such edit is gated separately by
`B_PROJECT_BRIEF.md` §10.9 and is out of scope here.

### 3.6 What clearance / non-clearance looks like

Because the current reviewer is a single person (see §4), no
multi-rater clearance step exists today. The §3.4 / §3.5 procedures
above are deliberately structured so that the reviewer's own act of
re-reading and recording the candidate is the lightest possible
substitute for multi-rater clearance — adequate at portfolio scale,
inadequate for promotion-grade (see §5).

---

## 4. Current DG-2 status anchor

- **Current state:** DG-2 expert review is **working-review only**.
- **What that means concretely:**
  - No image's on-disk label has been changed by any reviewer action.
  - No DG-2 sub-curation or relabeling pass has been declared complete.
  - No taxonomy-change candidate has been promoted into a DG-1 spec
    edit.
  - The per-batch working memos under `outputs/` are the record of
    reviewer activity to date.
- **What that does NOT mean:**
  - That the reviewer activity is unimportant. It is the input to any
    later promotion-grade pass.
  - That suspect-label flags or label-change candidates may be acted on
    informally. The §3 protocol applies to every reviewer assertion.
- **Cross-reference:** `B8_3_CLOSEOUT_STATUS.md` §3 records B8.3 as
  *not yet fully closed*; the DG-2 status here is consistent with that.

---

## 5. Future promotion-grade requirements (planned, not current blockers)

The current single-reviewer working review is sufficient for portfolio
governance. It is **not** sufficient to call DG-2 "promotion-grade." The
following are the future requirements that would convert the current
state into promotion-grade. Each is **[planned]**, not currently a
blocker.

### 5.1 Inter-annotator agreement (IAA)

- **Why:** independent agreement between ≥ 2 annotators is the
  conventional way to demonstrate that a class boundary is reproducibly
  applicable, not idiosyncratic to one reviewer. Standard metrics are
  Cohen's kappa (two annotators, categorical) and Krippendorff's alpha
  (any number of annotators, mixed levels of measurement).
- **AOI repo positioning:** the existing DG track lists IAA under
  **DG-8** (`B_PROJECT_BRIEF.md` §9.2): "*Pre-label seed (YOLO
  inference), audit log, IAA (Cohen's Kappa / Krippendorff's Alpha).
  Low IAA = spec ambiguity, not human error.*" This document does not
  change DG-8's scope; it ties DG-8 to the promotion-grade gate.
- **Portfolio-scale substitute (today):** single-rater intra-rater
  consistency check at §3.4 / §3.5 — re-reading after a calendar-day
  delay. Acknowledged as a weaker signal than IAA; recorded as a
  deliberate portfolio-scale compromise, not a long-term position.
- **Not a current blocker** for any decision in scope of this protocol.

### 5.2 Adjudication rule

- **Why:** even with IAA, disagreements occur; a written adjudication
  rule (who decides, on what basis) is required before disagreements
  become reproducible decisions.
- **Status:** **[planned]**, no draft today. The current
  single-reviewer setup makes adjudication trivial-by-default (no
  disagreement possible), but a promotion-grade pass would need to spell
  this out.

### 5.3 Versioning of any spec or label change

- **Why:** any label-change or taxonomy-change that *does* land on disk
  must be bound to a specific `dataset_version` and
  `annotation_spec_version`, per DG-7 in `B_PROJECT_BRIEF.md` §9.2 and
  §9.3.
- **Status:** **[gated]** — DG-7 versioning is itself planned, and is a
  hard gate for B9 (`B_PROJECT_BRIEF.md` §9.3). This protocol records
  the dependency; it does not pre-empt DG-7's design.

---

## 6. Future optional signals (deferred, not current task)

These are tools that, if used in the future, would supplement the §3
protocol. None is authorised by this document.

### 6.1 Confident-learning / cleanlab-style suspect-label surfacing

- **What:** model-prediction-based label-noise detection (e.g., the
  `cleanlab` library implements confident-learning estimators that
  flag training-set entries whose model-predicted label probability is
  inconsistent with their stored label).
- **Why it might be useful:** could serve as an automatic **Gate-A
  signal** — a pre-filter that surfaces suspect-label-flag candidates
  for the reviewer to consider, complementing the current
  rule-based candidate generator (`src/b_yolo/dg2_review_candidates.py`,
  held local).
- **Status today:** **[deferred]**. Adding cleanlab or any
  confident-learning tool would require:
  - a new tracked dependency (out of scope here);
  - integration with the existing candidate-generator pipeline (DG-3
    scope, not addressed by this protocol);
  - a documented interpretation rule (a high cleanlab score is *not*
    automatically a label change; it would feed §2.1 suspect-label
    flags, nothing stronger).
- **Not a current task.** This protocol records the candidate signal
  source so it is not invented twice later.

### 6.2 Why §6.1 is not a fix proposal

The protocol explicitly takes no position on whether the cleanlab tool
chain *should* be adopted. The §2 vocabulary already accommodates the
output of such a tool (it would feed suspect-label flags); the §3
protocol already accommodates whatever pre-filter is used; the §5
promotion-grade gates apply regardless of pre-filter choice.

---

## 7. Intentionally NOT in scope

To keep this protocol portfolio-scale and non-overclaiming, the
following are **explicitly excluded** by this document:

- **No KLA / AMAT / vendor-specific fab inspection process claims.**
  The protocol above is portfolio governance hygiene, not a
  fab-deployable methodology, and any reading of it as the latter is
  unsupported.
- **No on-disk label change.** §2.2 / §3.4 produce *candidates*; the
  candidate-to-on-disk-change step is out of scope.
- **No DG-1 §10.2 spec edit.** §2.3 / §3.5 produce *taxonomy-change
  candidates*; the candidate-to-spec-edit step is governed separately
  by `B_PROJECT_BRIEF.md` §10.9.
- **No code change** in `src/b_yolo/dg2_review_candidates.py` or
  elsewhere. The script remains held for a future DG-3 PR.
- **No `outputs/` promotion.** Working review memos stay under
  `outputs/`.
- **No `results/*` change.** Working CSVs stay where they are.
- **No JSON contract change.**
- **No Enhancement Track gate movement.** The chain in
  `B8_3_CLOSEOUT_STATUS.md` §3 and §5 is unchanged.
- **No Phase 4 work.**

---

## Cross-reference index

For navigation only — every reference points to existing tracked
material; no new claims are made.

- DG-1 v0 ontology and §10.2 cues: `B_PROJECT_BRIEF.md` §10.
- DG-1 v0 → v1 promotion gate: `B_PROJECT_BRIEF.md` §10.9.
- DG track definition (DG-1..DG-8 incl. IAA under DG-8):
  `B_PROJECT_BRIEF.md` §9.
- B8.3 closeout chain: `B8_3_V1_VS_V2_ANALYSIS.md` §7,
  `B8_3_CLOSEOUT_STATUS.md` §3 / §5.
- DG-2 pipeline artifact authority: `DG2_REVIEW_PIPELINE_STATUS.md`.
- DG-1 rare-class register (cross-track observations):
  `DG1_RARE_CLASS_FAILURE_ANALYSIS.md`.
- Enhancement Track gating: `B_PROJECT_BRIEF.md` §8.4 / §9.3.
- Locked JSON contract: `AOI_PROJECT_STATE.md` §3,
  `AOI_MASTER_ROADMAP.md` §7.
