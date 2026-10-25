#!/usr/bin/env python3
"""Smoke: drive server.py over real stdio with a temp state file, then
attempt LIVE public reads (profile + author feed for bsky.app, plus a
search). Live results are labeled LIVE with real figures; if the VM
egress blocks a call, the smoke prints the named error and marks that
leg [verify] — it never fabricates a result."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent


def call(proc, rid, name, args):
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": rid,
                                 "method": "tools/call",
                                 "params": {"name": name,
                                            "arguments": args}}) + "\n")
    proc.stdin.flush()
    resp = json.loads(proc.stdout.readline())
    result = resp["result"]
    text = result["content"][0]["text"]
    return json.loads(text), bool(result.get("isError"))


def main():
    with tempfile.TemporaryDirectory() as td:
        # Inherit the full environment: this VM reaches the internet
        # through an egress proxy named in env vars; a stripped env
        # makes live reads fail for harness reasons, not product ones.
        env = {**os.environ,
               "ECLIPSE_ZEPHYR_STATE": str(Path(td) / "state.json")}
        proc = subprocess.Popen([sys.executable, str(ROOT / "server.py")],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                text=True, env=env)
        try:
            proc.stdin.write(json.dumps(
                {"jsonrpc": "2.0", "id": 0, "method": "initialize",
                 "params": {"protocolVersion": "2025-03-26"}}) + "\n")
            proc.stdin.flush()
            init = json.loads(proc.stdout.readline())
            print("server:", init["result"]["serverInfo"])
            rid = 1
            out, err = call(proc, rid, "profile_read",
                            {"actor": "bsky.app"})
            rid += 1
            if err:
                print("profile_read bsky.app: [verify] live leg failed:",
                      out["error"])
            else:
                p = out["profile"]
                print(f"LIVE profile_read: {p['display_name']} "
                      f"(@{p['handle']}) followers={p['followers_count']} "
                      f"posts={p['posts_count']} did={p['did']}")
            out, err = call(proc, rid, "author_feed_read",
                            {"actor": "bsky.app", "limit": 5})
            rid += 1
            if err:
                print("author_feed_read bsky.app: [verify] live leg "
                      "failed:", out["error"])
            else:
                print(f"LIVE author_feed_read: {out['count']} posts; "
                      f"newest: {out['posts'][0]['text'][:80]!r}")
            out, err = call(proc, rid, "actor_search",
                            {"query": "bluesky", "limit": 3})
            rid += 1
            if err:
                print("actor_search: [verify] live leg failed:",
                      out["error"])
            else:
                print("LIVE actor_search 'bluesky':",
                      [a["handle"] for a in out["actors"]])
            rec, _ = call(proc, rid, "receipt_list", {})
            print("receipts:", rec["count"], "chain valid:",
                  rec["chain_valid"],
                  "| statuses:", [r["detail"]["status"]
                                   for r in rec["receipts"]])
        finally:
            proc.stdin.close()
            proc.wait(timeout=10)


if __name__ == "__main__":
    main()
