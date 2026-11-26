# Friday: Data Contracts

These are the shapes of the data that moves between Friday's parts. They're defined in [`engine/src/friday_engine/contracts/`](../engine/src/friday_engine/contracts/) with Pydantic.

Every example on this page is checked by `engine/tests/test_schema_docs.py`, so if the code changes and an example stops being valid, the tests fail.

## Rules that apply to everything

- **Unknown fields are rejected**, not ignored. A message carrying `page_text` or `verdict` where it doesn't belong is an error.
- **No type coercion.** `"0.5"` isn't accepted where a number is expected.
- **Objects are immutable.** A change, such as marking a finding as benign, creates a new object.
- **Timestamps must include a timezone.**
- **Sizes are bounded**: text lengths, the number of signals, and the number of evidence entries. A hostile page can't make Friday store megabytes.

## Vocabularies

| Field | Allowed values | Notes |
|---|---|---|
| `verdict` | `not_detected`, `unknown`, `suspicious` | There's no `safe` and no `malicious`. URL checks can't prove either |
| `severity` | `none`, `low`, `medium`, `high` | How bad it would be if the finding is right |
| `confidence` | `low`, `medium`, `high` | How sure Friday is. Always shown separately from severity |
| intel `status` | `hit`, `miss`, `error`, `disabled` | `miss` and `error` never mean "safe" |
| `user_feedback` | `none`, `benign`, `incorrect` | |
| `action` | `mark_benign`, `delete_finding`, `open_guidance` | The complete allowlist. None of them touch files, processes or settings |

## Finding

The result of checking one URL. These rules hold for every finding:

- `suspicious` needs at least one signal or an intel hit, and a severity other than `none`.
- `not_detected` must have severity `none`, and can't sit alongside an intel hit.
- At least one limitation is always listed.
- Signal ids are unique within a finding.
- URL subjects never contain a `#fragment`.

<!-- example: Finding -->
```json
{
  "id": "6f1c2b9e-3d4a-4f8e-9b7a-2c5d1e0f3a41",
  "created_at": "2026-11-26T09:15:02+05:30",
  "subject": {
    "kind": "url",
    "value_redacted": "http://192.0.2.10/login?user",
    "host": "192.0.2.10"
  },
  "verdict": "suspicious",
  "severity": "medium",
  "confidence": "low",
  "signals": [
    {
      "id": "url.ip_literal_host",
      "title": "The address is a raw IP instead of a domain name",
      "evidence": { "host": "192.0.2.10" },
      "weight": 0.4,
      "rule_version": "1.0.0"
    }
  ],
  "intel": [{ "provider": "example_feed", "status": "disabled" }],
  "limitations": ["Only the URL was checked, not the page content."],
  "rule_set_version": "0.1.0",
  "user_feedback": "none"
}
```

In `value_redacted`, the query string keeps parameter **names** only (`?user`), not their values.

A URL that couldn't be parsed produces `unknown`, not an error and not `not_detected`:

<!-- example: Finding -->
```json
{
  "id": "0b8e7c55-1a2f-4c3d-8e9f-a1b2c3d4e5f6",
  "created_at": "2026-11-26T09:16:40+05:30",
  "subject": { "kind": "url", "value_redacted": "http://[::1" },
  "verdict": "unknown",
  "severity": "none",
  "confidence": "low",
  "signals": [],
  "intel": [],
  "limitations": ["The URL could not be parsed, so no checks ran."],
  "rule_set_version": "0.1.0"
}
```

## Signal

One thing a rule noticed.

| Field | Rule |
|---|---|
| `id` | Dotted lowercase, e.g. `url.idn_mixed_script` |
| `evidence` | Flat map of up to 32 entries. Values are strings (up to 2048 chars), numbers or booleans. No nesting |
| `weight` | Greater than 0, at most 1 |
| `rule_version` | `MAJOR.MINOR.PATCH` |

## IntelResult

Records every lookup, **including the ones that didn't happen**, so the UI can say "reputation lookup was off" rather than leave people guessing. A real lookup must record exactly what was sent and when.

<!-- example: IntelResult -->
```json
{
  "provider": "example_feed",
  "status": "error",
  "indicator_sent": "192.0.2.10",
  "fetched_at": "2026-11-26T09:15:03+05:30"
}
```

## Explanation

What the local AI model is allowed to return. It has **no verdict, severity or action field**: the model can describe a finding but has no way to change one. Every fact has to cite at least one signal id, and `assert_grounded_in(finding)` rejects ids that aren't in the finding.

<!-- example: Explanation -->
```json
{
  "finding_id": "6f1c2b9e-3d4a-4f8e-9b7a-2c5d1e0f3a41",
  "model": "qwen3:8b",
  "facts": [
    {
      "text": "The link goes to a bare IP address rather than a named website.",
      "signal_ids": ["url.ip_literal_host"]
    }
  ],
  "uncertainty": ["Only the address was checked. The page itself may be harmless."],
  "recommendations": ["Avoid typing a password on this page unless you expected it."],
  "generated_at": "2026-11-26T09:20:00+05:30"
}
```

## ActionRequest

The only way Friday does anything for you. Each request starts as `proposed`, and only these transitions are allowed:

```text
proposed ──> approved ──> done
    │            └──────> failed
    └──────> declined
```

`decided_at` is set when the request leaves `proposed`. Params are fixed per action. `open_guidance` takes a `guide_id` from Friday's own list of vendor help pages, **never a URL**.

<!-- example: ActionRequest -->
```json
{
  "id": "9a8b7c6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d",
  "finding_id": "6f1c2b9e-3d4a-4f8e-9b7a-2c5d1e0f3a41",
  "action": "open_guidance",
  "params": { "guide_id": "macos_firewall" },
  "status": "approved",
  "created_at": "2026-11-26T09:21:00+05:30",
  "decided_at": "2026-11-26T09:21:30+05:30"
}
```
