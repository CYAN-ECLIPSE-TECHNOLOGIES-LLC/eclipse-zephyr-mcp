# Eclipse Zephyr MCP

**Powered by Cyan Eclipse Technologies** — https://cetech.ai

**Eclipse Zephyr — the Bluesky adapter: the family's open-protocol reference implementation, using the AT Protocol's sanctioned records and services while keeping CETech's review-first and engagement limits fully in force.**

## Why this exists

Zephyr's purpose is disciplinary as much as commercial (§17): it proves the family core can use a fully open surface without importing the platform's openness as an excuse to abandon approval, caps, or receipts. The least gated platform gets no weaker house rules merely because the protocol permits more.

## Status — honest labels

v0.1.0, phase **S2 public-read adapter**. **Reads are REAL and live**: the tools call the AT Protocol public API (`public.api.bsky.app`, no auth) and were smoke-verified live from this VM on 2026-10-25 (profile, author feed, and search for `@bsky.app` all returned live data). **There is no posting surface** — Zephyr posting requires an owner Bluesky account and an approved, hash-bound pack (Wave 2); it does not exist in this code, and a test asserts the write-tool names are absent. Local stdio, Python stdlib only. **No certification claimed — bench pending.**

Environment note: this VM's egress proxy intermittently truncates large chunked keep-alive bodies and resets connections in bursts. The transport therefore sends `Connection: close` + gzip and retries transient failures (bounded); a read that still fails returns a named error **and is receipted as an error** — failures are never silently swallowed or dressed up as data.

## Tools (5)

| Tool | What it does |
|---|---|
| `profile_read` | One public profile (`app.bsky.actor.getProfile`): DID, handle, display name, description, follower/follows/post counts — normalized, source endpoint named. |
| `actor_search` | Public account search (`app.bsky.actor.searchActors`): normalized profile summaries. Discovery only — no follow or engagement action exists. |
| `author_feed_read` | A named account's recent original posts (`app.bsky.feed.getAuthorFeed`, `posts_no_replies`): text, timestamps, the protocol's own like/repost/reply counts, media presence and alt-bearing embed type — per-post provenance. |
| `post_thread_read` | One post thread (`app.bsky.feed.getPostThread`): root + direct replies. |
| `receipt_list` | The append-only, hash-chained receipt ledger — **every read, success or failure** — with chain verification. |

## Rate discipline + analytics honesty

- Minimum interval between live calls, a per-process live-call budget, bounded retries on transient failures only (4xx never retries).
- No native view metric is invented: custom feeds and labelers change what "the feed" means, so every figure carries its source endpoint and the envelope says so (§6/§17).
- Engagement, when a future owner-enabled `COMMUNITY_API_PILOT` is ever approved, remains bound by the core's playbook caps and logging (§5) — default is `COMMUNITY_PREP`, and v0.1 ships no engagement surface at all.

## Run it

```bash
python3 server.py            # MCP over stdio, stdlib only, no dependencies
python3 smoke.py             # LIVE smoke: real public reads for @bsky.app
python3 -m unittest discover tests   # 6 tests, fully offline (fixture transports)
```

State (receipts) persists in `data/state.json` (override with `ECLIPSE_ZEPHYR_STATE`). `data/` is gitignored.

### Fixtures

`fixtures/profile_bsky_app.json` is a **real captured** public-API response (2026-10-25) used as the profile normalization fixture. `fixtures/author_feed_sample.json` and `fixtures/search_actors_sample.json` are **synthetic** samples shaped like the real lexicon responses, labeled as such in-file.

## Roadmap (per spec §21)

- **Wave 2 (owner-gated):** an owner Bluesky account → `bsky_identity_probe`, `bsky_record_stage` (approved packs only), `bsky_thread_verify`, `bsky_label_preflight`. Reposts/follows are state changes with social meaning — they enter through the engagement plan's scope, never as free analytics actions.

## License / attribution

A Cyan Eclipse Technologies product. The "Powered by Cyan Eclipse Technologies" attribution travels with it.
