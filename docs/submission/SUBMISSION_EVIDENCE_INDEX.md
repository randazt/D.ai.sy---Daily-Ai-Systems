# D.AI.S.Y. Submission Evidence Index

This index tracks evidence available for the All Things Agentic submission. It does not claim evidence that has not been captured.

Repository SHA: `8240a5ceb57c8220b3d752505fb2c88fffd01301`

| Area | Status | Evidence | Still Missing |
|---|---|---|---|
| Google Cloud deployment | VERIFIED | Cloud Run service `daisy-backend` is live at `https://daisy-backend-pbhnglpapq-ue.a.run.app`, revision `daisy-backend-00001-k9g`, build `4b3e97f6-baa6-43cb-ae9e-e47b503e3e98`, region `us-east1`. | Final submission screenshot/video capture if required by form. |
| Gemini | VERIFIED | Live planning request returned a structured plan; Cloud Run logs showed `Models.generate_content`. `GEMINI_API_KEY` is supplied from Secret Manager. | None for initial live proof. |
| Google ADK | VERIFIED | Live execution request completed reasoning tasks through the deployed execution path; Cloud Run logs showed `AsyncModels.generate_content`, consistent with the existing ADK reasoning executor path. | Deeper ADK trace screenshots if judges require framework-level proof. |
| Planning | VERIFIED | Planner returned five reasoning tasks for a safe user goal. | None for initial live proof. |
| Execution | VERIFIED | `execute` completed the first reasoning task and returned generated output. | None for initial live proof. |
| Observation | VERIFIED | Public response included `TaskObservation` with `outcome=completed`, `success=true`, and `capability=reasoning`. | None for initial live proof. |
| Decision | VERIFIED | Public response included `TaskDecision` with `decision=continue`. | None for initial live proof. |
| Bounded autonomy | VERIFIED | Continuation was applied exactly once into a second reasoning task; no recursive continuation occurred. | None for initial live proof. |
| CALL-E authority/safety | PARTIAL | This live proof avoided `phone_call`, kept `DAISY_ENABLE_REAL_CALLS=0`, and did not invoke CALL-E. Code/test evidence covers authority boundaries. | Separate intentionally authorized CALL-E runtime demonstration, if required. |
| Tests | VERIFIED | Approved baseline at this SHA has 131 backend tests passing. | Fresh final test run before final submission package. |
| Repository SHA | VERIFIED | Approved deployed SHA is `8240a5ceb57c8220b3d752505fb2c88fffd01301`. | Source hygiene before final submission: unrelated staged root artifacts remain in local status. |
| Official All Things Agentic category | VERIFIED | Official rules were supplied externally for this submission workflow; target category is Taskmaster. | Final form completion and artifact upload. |
| Demo runbook | VERIFIED | `docs/submission/ALL_THINGS_AGENTIC_DEMO_RUNBOOK.md` defines the final under-four-minute recording sequence using the deployed system. | Actual recorded video and preserved screenshots/clips. |
| Evidence still missing | MISSING | Remaining gaps are submission artifacts, not missing source-code capabilities for the reasoning-only All Things Agentic demo. | Final demo video, screenshots/clips, official submission narrative, exact required form fields, and CALL-E runtime proof if required separately. |
