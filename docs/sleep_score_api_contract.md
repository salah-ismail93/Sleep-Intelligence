# Sleep Score API Contract

## Version 1 Scope

`POST /sleep_score` returns a transparent, adult-oriented wellness heuristic.
It is not a clinical score, diagnostic result, or validated research
instrument.

The request retains `snore_event_count` and `posture_change_count` for future
research compatibility. Version 1 does not use either field in the score
because validated reference ranges are not yet available.

## Formula

```text
duration_component =
    min(total_sleep_minutes / 420.0, 1.0) * 100.0

efficiency_component =
    sleep_efficiency * 100.0

final_score =
    0.40 * duration_component
    + 0.60 * efficiency_component
```

The implementation clamps `final_score` to `[0.0, 100.0]` and then applies the
standard Python rounding function with one decimal place: `round(score, 1)`.

For `total_sleep_minutes = 420.0` and `sleep_efficiency = 0.85`, the returned
score is `91.0`.

The duration threshold is intended for the adult-oriented Version 1 contract.
Future age-specific or research-validated scoring policies should be introduced
as explicitly versioned changes.
