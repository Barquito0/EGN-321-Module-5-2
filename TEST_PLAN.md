# Assignment 5.2 Test Plan

| Test | Scenario | Expected Evidence |
|---|---|---|
| Normal sensor reading | 22 C | ACCEPTED |
| Normal variation | 22 C -> 23 C | Accepted |
| Boundary value | 28 C -> 30 C | 30 C accepted |
| Out-of-range value | 60.1 C | REJECTED; engineering calculation not run |
| Suspicious spike | 19 C -> 25 C | FLAGGED; no coefficient |
| Missing reading | blank temperature | REJECTED |
| Filtering/rejection | 35 C | FLAGGED; no coefficient |
| Unexpected unit | 22 F | REJECTED |
| Stale reading | non-increasing timestamp | REJECTED |
| Successful full flow | 21 C for VX-200 | ACCEPTED; coefficient 1.144 |
| Raw vs accepted traceability | accepted CSV row | raw value and accepted value both logged |
| Rejected-data traceability | 60.1 C | raw value retained, result blank |
| Post-spike stability | 19 -> 25 flagged -> 25 stable | second 25 C accepted |
| Original engineering regression | Module 3.1 lookup/interpolation cases | original logic still passes |

Automated result: **30 tests passed**.
