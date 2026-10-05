# Outreach state inside the blueprint

Per unit, next to `icp.md`, `competitors.md` and `pricing.md`:

| File | Written by | What |
|---|---|---|
| `offering/<slug>/prospects.csv` | `/prospects` (rows) · `/outreach log` (status, cadence, next touch) | One row per prospect |
| `offering/<slug>/prospects-runs.md` | `/prospects` | ICP FINAL used per run, counts, discarded companies (excluded next time) |
| `offering/<slug>/drafts/<key>/` | `/outreach` | `touch-N.md`, `linkedin-N.md`: what was generated, as generated |

Company-wide, under `offering/_shared/`:

| File | Written by | What |
|---|---|---|
| `events.csv` | `/prospects` (`added`) · `/outreach` (`draft_created`) · `/outreach log` (the rest) | One row per event, any unit |
| `suppression.csv` | `/outreach log` (BAJA, bounce, do-not-contact) | Append only. Removing someone is a new row with `reason=reactivated`, never a deletion |

All of it is gitignored with the rest of `offering/`.

## `prospects.csv`

| Column | Values |
|---|---|
| `key` | slug of email → else `<company>-<contact>` → else `<company>`; `[a-z0-9.-]`, max 80. Dedup key |
| `campaign` | slug of the campaign this prospect is in right now, or **empty**: in the pool, written to by nobody. **One active campaign at most.** Closing a campaign clears it for whoever did not convert. Assigned only by `/campaign`, never by `/prospects` |
| `email_status` | `public` (published, page in `email_source`) · `none` (searched, nothing published) · `unsearchable` (site could not be read). Never merged. No inferred addresses |
| `signal_confidence` | `high` · `medium` · `low`, from the verifier |
| `findings` | 3-5 observed facts, ` · ` separated, each with its URL |
| `status` | `lead` → `contacted` → `replied` → `meeting` → `proposal` → `won` \| `lost`; plus `do_not_contact` |
| `channel` | `email` · `linkedin` · `none` |
| `cadence` | `none` · `email-3` · `linkedin-3` |
| `next_touch_on` | date of the next touch, or empty |
| `source` | `prospects` · `manual` · `referral` |

## `events.csv`

Columns: `ts,unit,campaign,key,type,channel,touch,summary,by`. **Write the row at that exact
width.** A short row does not fail, it shifts every field after the gap and the tracker lies from
then on; `tools/linkedin.py` checks the header before appending and refuses if it differs.

`type`: `added` · `draft_created` · `sent` · `reply` · `bounce` · `status_change` ·
`suppressed` · `note`. Only a person (via `/outreach log`) or the tool that performed the action
writes `sent`, `reply`, `bounce`: generating a draft never counts as sending.

`campaign` records which campaign it happened under. The history is still the **person's**:
suppression, and everything already sent to them, follow them into whatever campaign they enter
next. That is why a second contact needs a new angle.
