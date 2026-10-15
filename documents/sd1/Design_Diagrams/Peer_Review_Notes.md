# Pulse - Peer Design Review Notes

**Team:** Jacob Cohen, Sujal Choukse, Yatharth Bajaj. **Recorded:** October 14, 2026.

**Reviewers:** Sahil, Team Street Smart; Mohammad, EpistemicRAG. We combined both reviews below. Must-fix items are due with the D2 submission on October 14; Week 8 is the course milestone specified for the optional suggestions.

### Feedback from Sahil - Team Street Smart

Sahil highlighted the four-category edge-case coverage, named handlers, error paths in Figures 2-4, figure legends, and clearly stated design limits.

| ID | Criterion | Issue and source | Action / resolution | Owner | Priority | Due |
| --- | --- | --- | --- | --- | --- | --- |
| PR-01 | Risk | 128 records cannot hold three sensors' one-hour backlog. Street Smart. | Applied: sensor-derived capacity; 183 minimum and 256 reference records. Section 2.3; R-1. | Jacob Cohen | must-fix | Oct 14, 2026 |
| PR-02 | Feasibility | ESP32 recovery needs a real clock source. Street Smart. | Applied: battery-backed DS3231 RTC, bench UTC provisioning, boot checks. Section 2.3; EC-54; R-10. | Sujal Choukse | must-fix | Oct 14, 2026 |
| PR-03 | Completeness | Invalid trusted envelopes retry for an hour. Street Smart. | Applied: owned ACK and signed FAILED for permanent rejection, not a new REJECTED enum. Sections 2.3/2.5; EC-57; R-9. | Yatharth Bajaj | must-fix | Oct 14, 2026 |
| PR-04 | Risk | Backlogged retries exceed one LoRa window. Street Smart. | Applied: one radio scheduler, EDF, inter-frame spacing, airtime gate, expiry recheck. Section 2.3; Figure 3; EC-58; R-7. | Jacob Cohen | must-fix | Oct 14, 2026 |
| PR-05 | Feasibility | 383 wrapper bytes do not fit a 255-byte radio payload. Street Smart. | Applied: TCP-only 383 cap; LoRa profile budget plus complete encoded payload <=255. Section 2.4; EC-20; R-7. | Jacob Cohen | must-fix | Oct 14, 2026 |
| PR-06 | Clarity | Airtime and remote-bind references are missing/wrong. Street Smart. | Applied: visible gate in Figures 2/3; NFR-07 cites EC-58; NFR-02 cites new remote-bind EC-59. | Jacob Cohen | must-fix | Oct 14, 2026 |
| PR-07 | Clarity | Draft assignment labels were unclear; figures were out of order and review notes/decision markers were missing. Street Smart. | Applied: label D2 as Assignment 7 within the Assignment 4 collection; order Figures 1-4; add part 6 and rationale markers. | Yatharth Bajaj | must-fix | Oct 14, 2026 |
| PR-08 | Completeness | Backups, multiple Hubs, UDP have no requirement. Street Smart. | Applied early (Oct 14): remove all three optional runtime features; one Hub/TCP baseline. Sections 2.2/2.4/2.5 and part 4; R-4/8. | All team members | worth considering | Week 8 |
| PR-09 | Clarity | Stopped sensors are absent from HEALTH. Street Smart. | Applied early (Oct 14): typed sensor reports, stopped reason, disconnected/stale states. Sections 2.2/2.3; EC-60; R-2. | Yatharth Bajaj | worth considering | Week 8 |
| PR-10 | Risk | No low-disk warning; sensor-count assumption unclear. Street Smart. | Applied early (Oct 14): warning/critical thresholds and HEALTH; size both D1's 10 sensors and new 30-sensor case. Section 2.5; EC-56; R-8. | Yatharth Bajaj | worth considering | Week 8 |

### Feedback from Mohammad - EpistemicRAG

Mohammad praised the repository organization, project vision, core modules, and functional breakdown. He asked for more quantitative hardware and latency limits, explicit disruption recovery, and concrete API schemas. We assigned an owner and a submission deadline to each action.

| ID | Criterion | Issue and source | Action / resolution | Owner | Priority | Due |
| --- | --- | --- | --- | --- | --- | --- |
| MR-01 | Feasibility | Hardware/resources and heavy-load latency need explicit budgets. EpistemicRAG. | Applied: resource/latency table, rate/capacity calculations, and a radio overload rejection rule. Section 2.8; R-1/7. | Jacob Cohen | must-fix | Oct 14, 2026 |
| MR-02 | Risk | Network and dependency delays need concrete recovery rules. EpistemicRAG. | Applied: backoff and held samples, paced retry, storage rollback, terminal rejection, clock fault handling. Sections 2.2-2.5; EC-08/28/54/57/58. | Yatharth Bajaj | must-fix | Oct 14, 2026 |
| MR-03 | Clarity | Module integration needs explicit request/error schemas. EpistemicRAG. | Applied: version-2 health/report/ACK contracts, policy version, types, ownership, errors, and compatibility rules. Sections 2.2-2.5; EC-61; R-9. | Jacob Cohen | must-fix | Oct 14, 2026 |

### Review summary

**Most feedback:** Risk and clarity tied, with four action items each. Feasibility had three and completeness had two. The main concerns were whether backlog and radio limits could satisfy the delivery promise, and whether the diagrams and contracts described the same behavior. All seven Street Smart must-fix items and the three EpistemicRAG action items have corresponding design changes above; we applied the three Week 8 suggestions early, on October 14.

### Top two issues we raised while reviewing Street Smart

1. **Risk - unblurred images in the unresolved-location cache.** Street Smart states that photos are blurred before storage, but its unresolved-location path saves a detection locally before blurring. Faces and license plates could reach the worker's disk. We suggested storing metadata only and extracting the image from the video later, or blurring the image before saving it.
2. **Completeness - contradictory detection counts.** One section keeps the top 10 detections per frame, while the pipeline selects only the highest-confidence box and the database permits one detection per frame. A frame with two potholes could lose one without warning. We asked the team to choose one design: explicitly keep one detection and state the limitation, or support several and update the database key and related sections.

**Review-driven decisions:** R-1, R-2, R-4, R-7, R-8, R-9, and R-10 are marked in part 5. D0 is unchanged. D1 has editorial corrections; D2 records the revised capacity, carrier limits, and rejection policy.
