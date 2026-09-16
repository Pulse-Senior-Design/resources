# Pulse First Advisor Meeting

**Date:** Friday, September 11, 2026  
**Attendees:** Jeffrey Gundler, Jacob Cohen, Sujal Choukse, and Yatharth Bajaj  
**Meeting cadence:** Monday, Wednesday, and Friday  
**Record status:** Reconstructed on September 14, 2026, from team recollection and project records

## Purpose

The team introduced Pulse and confirmed Jeffrey Gundler as the advisor for both project semesters. The team also reviewed the farm data-collection use case and the first release scope.

## Decisions

- Focus the first release on farm, water, and environmental sensor data.
- Use the three purchased ESP32-S3 boards for the first hardware tests.
- Use the LoRa-capable ESP32-S3 as the first field device.
- Start with one test sensor and a custom Pulse sensor driver.
- Prove the desktop data path before the team adds full hardware support.
- Keep the Node, Edge, Hub, and shared protocol modules separate.
- Use persistent identities and trusted peers from the start.
- Test direct SX1262 support before the team selects a serial RNode fallback.
- Limit the shared equipment budget to $1,000.
- Split approved equipment costs among the three team members.

## Action Items

| Owner | Action | Due date |
|---|---|---|
| Jacob Cohen | Update the architecture and shared protocol plan. | September 14, 2026 |
| Sujal Choukse | Record the hardware inventory and define the test sensor driver needs. | September 16, 2026 |
| Yatharth Bajaj | Update the course records and prepare the advisor submission. | September 16, 2026 |
| All team members | Confirm the LoRa test method and required radio hardware. | September 18, 2026 |
| All team members | Record equipment purchases against the $1,000 budget. | Ongoing |

## Open Questions

- Which test sensor will the first custom driver support?
- Which LoRa settings and United States frequency plan will the first test use?
- What sample rate and outage period must the farm deployment support?
- Does the farm deployment require a powered relay device?

## Advisor Contract Decision

The team reports that Jeffrey Gundler approved the project and team contract through Slack. He requested no contract changes.

Attach the original Slack message or a screenshot as the approval evidence. Ask the advisor to approve version 1.0 again if its content differs from the reviewed version.
