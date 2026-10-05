# EGN 321 — Module 5.2
# Feed the Tool: Replace Typed Input with Virtual Sensor Data

## Project Overview

This project connects the virtual temperature sensor from Assignment 5.1 to the **Module 3.1 Valve Lookup and Interpolation Tool**.

This is a direct fit because the original Module 3.1 tool already accepted **operating temperature in degrees Celsius** as a typed input. Assignment 5.2 replaces that typed temperature with measured virtual-sensor data.

Original tool:

https://github.com/Barquito0/EGN-321-Module-3.1

Assignment 5.2 repository:

https://github.com/Barquito0/EGN-321-Module-5-2

## Integration Flow

```text
Velxio NTC Temperature Sensor
        ↓
Raw CSV Reading
        ↓
Sensor Validation
        ↓
Assignment 5.1 Filtering Rule
        ↓
Accepted Celsius Temperature
        ↓
Original Module 3.1 select_coefficient()
        ↓
Exact Lookup or Linear Interpolation
        ↓
Valve Coefficient Result
        ↓
Trace Log
```

The sensor reading never bypasses validation.

## Virtual Sensor Source

Platform: **Velxio**

Shareable project:

https://velxio.dev/project/11c7f38f-9ed9-46c4-811c-63c311344366

Sensor configuration:

- Arduino Uno
- NTC temperature sensor
- sensor OUT -> A0
- VCC -> 5V
- GND -> GND
- unit -> degrees Celsius
- sampling interval -> approximately 1 second

The Assignment 5.1 Arduino code is included at:

```text
data/sensor_code_final_v6.ino
```

A Velxio project copy with the final sketch embedded is included at:

```text
data/arduino-temp-sensor-lab-final.vlx
```

## Existing Engineering Tool Selected

The existing tool is the Module 3.1 **Valve Lookup and Interpolation Tool**.

Its original inputs were:

1. valve family;
2. operating temperature in Celsius.

For this integration, the valve family is held at:

```text
VX-200
```

The manually entered `temperature_c` input is replaced by the virtual NTC sensor reading.

## Original Engineering Logic Preserved

The original Module 3.1 engineering files are preserved:

```text
src/lookup_tables.py
src/interpolation.py
src/selection_tool.py
data/valve_lookup_table.csv
```

The original engineering rule is unchanged:

> **Interpolate inside the evidence. Refuse outside it.**

`select_coefficient()` still:

- verifies the valve family;
- verifies the engineering-data range;
- returns exact table values when available;
- performs linear interpolation between adjacent supported rows;
- refuses extrapolation.

Sensor integration is added **before** the original tool rather than rewriting the lookup/interpolation calculation.

## Sensor Dataset

`data/sensor_readings_raw.csv` contains:

- 101 readings collected from the Velxio simulation;
- one additional clearly labeled simulated missing/unavailable condition;
- sample number;
- timestamp;
- raw ADC value;
- temperature in Celsius;
- unit;
- sensor status;
- source.

The raw sensor values are never overwritten.

## Sensor Validation

Before a sensor temperature can reach `select_coefficient()`, the software checks:

1. **Missing input** — reject.
2. **Numeric validity** — reject nonnumeric, NaN, or infinite values.
3. **Unit** — reject anything other than `C`.
4. **Timestamp / freshness** — reject stale or non-increasing timestamps.
5. **Absolute sensor range** — reject values below 0 C or above 50 C.
6. **Expected normal range** — flag values below 18 C or above 30 C.
7. **Suspicious change** — flag a change greater than 3 C from the previous valid in-range reading.

## Assignment 5.1 Filtering / Rejection Rule

The Assignment 5.1 rule is applied before the engineering lookup:

- reject missing data;
- reject temperatures outside 0-50 C;
- flag temperatures outside 18-30 C;
- flag changes greater than 3 C;
- preserve all raw readings.

A flagged or rejected reading is **not** sent to the valve-selection calculation.

### Accepted

An accepted reading must:

- exist;
- be numeric and finite;
- use unit `C`;
- have a current timestamp;
- fall inside 0-50 C;
- fall inside the expected 18-30 C normal band;
- not be a sudden >3 C change.

### Flagged

A value is flagged and withheld when:

- it is inside 0-50 C but outside 18-30 C; or
- it changes by more than 3 C from the previous valid in-range reading.

### Rejected

A value is rejected when:

- it is missing;
- it is invalid/non-finite;
- the unit is wrong;
- the timestamp is stale;
- it is below 0 C or above 50 C.

The program never silently invents a replacement sensor value.

## Missing Input Behavior

For missing/unavailable sensor data, the program:

- preserves the original row;
- records `REJECTED`;
- leaves the accepted temperature blank;
- does not call the engineering calculation;
- leaves the valve coefficient blank;
- records the rejection reason;
- continues to later samples.

It does **not** silently reuse the last valid reading.

## Raw vs. Accepted Values

The generated `sensor_integration_log.csv` keeps the required chain visible:

```text
Raw Sensor Reading
→ Validation Decision
→ Accepted / Flagged / Rejected
→ Accepted Temperature
→ Valve Family
→ Engineering Status
→ Lookup / Interpolation Result
→ Valve Coefficient
→ Reason
```

For the provided dataset:

- processed: **102**
- accepted: **31**
- flagged: **53**
- rejected: **18**
- valve coefficients calculated: **31**

Only accepted sensor readings produce an engineering result.

## Example Successful Flow

One accepted sensor reading:

```text
raw temperature = 21.0 C
validation = ACCEPTED
value used = 21.0 C
valve family = VX-200
engineering method = interpolation
lower point = (10.0 C, 1.10)
upper point = (30.0 C, 1.18)
coefficient = 1.144
```

The original Module 3.1 interpolation logic produces that result.

## Example Rejected Flow

```text
raw temperature = 60.1 C
validation = REJECTED
reason = outside supported 0-50 C sensor range
accepted temperature = none
engineering calculation = NOT_RUN
coefficient = none
```

## Assumptions Broken by Sensor Input

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

A standalone copy of this table is also in `ASSUMPTIONS_BROKEN.md`.

## Testing

Run:

```bash
pytest
```

Current result:

```text
30 passed
```

The suite includes the original Module 3.1 lookup/interpolation tests plus sensor-integration tests for:

- normal reading;
- normal variation;
- boundary value;
- out-of-range value;
- suspicious spike;
- missing reading;
- filtering/rejection;
- unexpected unit;
- stale timestamp;
- valid sensor reading flowing into the original engineering calculation;
- raw vs. accepted-value traceability;
- rejected input producing no engineering result;
- stable reading after a flagged change.

## Running the Integration

From the repository root:

```bash
python replay_sensor.py
```

The script reads:

```text
data/sensor_readings_raw.csv
```

and writes:

```text
sensor_integration_log.csv
```

## Project Structure

```text
.
├── README.md
├── ASSUMPTIONS_BROKEN.md
├── TEST_PLAN.md
├── AI_LOG.md
├── replay_sensor.py
├── sensor_integration_log.csv
├── requirements.txt
├── pytest.ini
├── data/
│   ├── valve_lookup_table.csv
│   ├── sensor_readings_raw.csv
│   ├── sensor_code_final_v6.ino
│   └── arduino-temp-sensor-lab-final.vlx
├── src/
│   ├── __init__.py
│   ├── lookup_tables.py
│   ├── interpolation.py
│   ├── selection_tool.py
│   ├── sensor_validation.py
│   └── sensor_integration.py
└── tests/
    ├── test_interpolation.py
    ├── test_selection_tool.py
    └── test_sensor_integration.py
```

## Required Deliverables Coverage

| Required Deliverable | Location |
|---|---|
| Updated engineering tool | `src/` |
| Virtual sensor source / simulation link | README + Velxio link |
| Sensor dataset | `data/sensor_readings_raw.csv` |
| Sensor integration code | `src/sensor_integration.py` |
| Updated validation logic | `src/sensor_validation.py` |
| Filtering / rejection logic | `src/sensor_validation.py` |
| Raw vs accepted/rejected log | `sensor_integration_log.csv` |
| Normal and failure tests | `tests/` |
| Updated README | `README.md` |
| Assumptions Broken by Sensor Input | README + `ASSUMPTIONS_BROKEN.md` |
| GitHub repository | https://github.com/Barquito0/EGN-321-Module-5-2 |
