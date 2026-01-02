# state.json schema & meaning

This file is your **runtime position state** persisted on disk so the bot can remember:
- how many batches have been entered (`entry_count`)
- how much capital has been used (`used_capital`)
- average underlying entry price (`avg_price`)
- whether you are stopped out for the day (`stopped_today`)

> Tip: if `entry_count` is unexpectedly 4 at startup, it usually means you loaded an old `state.json` from a prior run/day.

---

## Top-level

### `long`
State for **LONG direction** (typically using CALL in your setup).

### `short`
State for **SHORT direction** (typically using PUT in your setup).

### `meta`
Meta info for debugging / day-rollover resets (optional but recommended).

---

## Per-side fields (`long` / `short`)

### `direction` (string)
- `"long"` or `"short"`.

### `option_type` (string)
- `"CALL"` or `"PUT"`.

### `strike` (number)
The **strike** you derived from underlying:
- Long CALL: `strike = floor(underlying_price)` (<= ticker price, integer)
- Long PUT:  `strike = ceil(underlying_price)`  (>= ticker price, integer)

### `contracts` (int)
How many option contracts per batch signal (your “Qty” in the title).

### `max_capital` (number)
Max capital budget for this side (e.g. `$3000`).

### `ladder` (array of numbers)
Batch sizing weights. Example `[0.3, 0.2, 0.4, 0.1]` means:
- Batch 1 uses 30% of `max_capital`
- Batch 2 uses 20%
- Batch 3 uses 40%
- Batch 4 uses 10%

### `used_capital` (number)
How much capital has already been allocated (sum of executed batches).

### `entry_count` (int)
How many batches have been **entered** so far.
- `0` = no entry yet
- `1..4` = entered batch #1..#4
- When `entry_count == len(ladder)` you are “fully deployed”.

### `avg_price` (number)
Average **underlying** price used as reference for TP/SL logic.
(If you later decide to use option fill price, rename this field.)

### `size` (number)
Computed position size in shares-equivalent (or your internal sizing unit).
This is not strictly required for notifications, but helpful for risk.

### `stopped_today` (bool)
If `true`, the system should refuse new entries for that side until the next trading day.

---

## `meta` fields

### `trading_day`
The YYYY-MM-DD trading date that this state belongs to.

### `updated_at`
Last updated timestamp (ISO8601).

### `notes`
Free text.
