# Assumptions Broken by Sensor Input

| Original Assumption | What the Sensor Did | Software Change |
|---|---|---|
| Temperature input always exists | One reading is missing/unavailable | Added missing-value rejection |
| A user supplies a valid number | Sensor streams can contain invalid/unavailable values | Added numeric and finite-value validation |
| Input is always in an expected range | Velxio produced extreme temperatures | Added absolute sensor-range validation |
| Input changes only when a person edits it | Sensor produces a new value every sample | Added repeated CSV replay |
| Input is stable | Sensor readings changed rapidly | Applied spike and normal-band filtering |
| Unit is known because the user typed the value | Sensor data includes a unit field | Added explicit `C` unit validation |
| Input is always current | Old records remain in CSV | Added increasing-timestamp validation |
| Engineering calculation can trust the caller | Sensor values may be noisy or suspicious | Added validation/filtering before `select_coefficient()` |
| Invalid input can be manually corrected before use | No human is guaranteed at every sample | Flagged/rejected values do not reach the engineering calculation |
