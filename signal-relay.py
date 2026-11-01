#!/usr/bin/env python3
"""Signal Relay — central nervous system for the membrane.

Unified send/receive relay + chipmunk heartbeat.
Runs as HTTP server behind Caddy on 127.0.0.1:9350.

Endpoints:
  POST /signal/send   — receive typed events from any surface
  GET  /signal/stream  — latest relay events (polling-friendly)
  GET  /signal/pulse   — relay health + heartbeat status

Heartbeat thread keeps chipmunk metabolism alive without a browser.

Usage: python3 signal-relay.py
"""

import json
import math
import os
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = 9350
JOURNAL_DIR = Path("/opt/membrane/squirrel-journal/relay")
RELAY_JSON = Path("/opt/membrane/live-terminal/relay.json")
LIVE_DIR = Path("/opt/membrane/live-terminal")
MAX_EVENTS = 100
MAX_BODY = 8192
HEARTBEAT_INTERVAL = 30

PI = math.pi
PI_INV = 1.0 / PI
SPRING_DAMP = 0.92

# rolling event buffer
_events = []
_events_lock = threading.Lock()
_source_counts = {}
_heartbeat_state = {
    "last": None,
    "actions_fired": 0, "strangeness": 0.5, "strangeness_history": [],
    "energy": PI_INV + 0.08,
    "state": "drowsy",
    "spring_v": 0.0,
    "pi_wake": 0.0,
    "cycle": 0,
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _read_feed(name):
    path = LIVE_DIR / f"{name}.json"
    try:
        with open(path) as f:
            return json.loads(f.read())
    except Exception:
        return None


def _append_event(event):
    with _events_lock:
        _events.append(event)
        if len(_events) > MAX_EVENTS:
            del _events[: len(_events) - MAX_EVENTS]
        src = event.get("source", "unknown")
        _source_counts[src] = _source_counts.get(src, 0) + 1

    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    journal = JOURNAL_DIR / f"{_today()}.jsonl"
    try:
        with open(journal, "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print(f"[relay] journal write error: {e}", file=sys.stderr)

    try:
        with _events_lock:
            snapshot = list(_events)
        with open(RELAY_JSON, "w") as f:
            json.dump({"ts": _now_iso(), "count": len(snapshot), "events": snapshot}, f)
    except Exception as e:
        print(f"[relay] relay.json write error: {e}", file=sys.stderr)


# === HEARTBEAT — pi-homeostatic spring ===

def _pi_wake_of(e):
    if e <= PI_INV:
        return -PI * (1.0 - e * PI)
    return PI * (e - PI_INV) / (1.0 - PI_INV)


def _heartbeat_tick():
    """One metabolic tick — port of chipmunk-metabolism.js metabolismTick()."""
    h = _heartbeat_state
    chipmunk = _read_feed("chipmunk")
    human = _read_feed("human")
    braid = _read_feed("braid")

    wake = 0.5
    if chipmunk and isinstance(chipmunk.get("wake_level"), (int, float)):
        wake = chipmunk["wake_level"]

    sn = 0
    humans = 0
    if human and isinstance(human.get("epitopes"), dict):
        for ep in human["epitopes"].values():
            if isinstance(ep, dict):
                humans += ep.get("sessions", ep.get("count", 0))
    if human and isinstance(human.get("energy"), dict):
        sn = human["energy"].get("signal_to_noise", 0)
        humans = human["energy"].get("total_sessions", humans)

    human_lift = min(0.15, humans * 0.001)
    sn_factor = min(1.5, 0.8 + sn / 1000)
    spring_k = 0.04 + 0.04 * wake * sn_factor
    target = PI_INV + human_lift

    displacement = h["energy"] - target
    force = -spring_k * displacement
    h["spring_v"] = (h["spring_v"] + force) * SPRING_DAMP
    h["energy"] = max(0.0, min(1.0, h["energy"] + h["spring_v"]))
    h["pi_wake"] = _pi_wake_of(h["energy"])
    h["cycle"] += 1

    if h["energy"] > 2 * PI_INV:
        h["state"] = "awake"
    elif h["energy"] > 0.6 * PI_INV:
        h["state"] = "drowsy"
    elif h["energy"] > 0.2 * PI_INV:
        h["state"] = "resting"
    else:
        h["state"] = "asleep"

    return chipmunk, human, braid


def _compose_observation(human, braid, chipmunk):
    parts = []
    if human and isinstance(human.get("energy"), dict):
        e = human["energy"]
        sessions = e.get("total_sessions", 0)
        sn = e.get("signal_to_noise", 0)
        breadth = e.get("avg_breadth", 0)
        parts.append(f"{sessions} humans, breadth {breadth:.1f}, S/N={sn:.0f}")
    if braid and isinstance(braid.get("graph"), dict):
        routes = braid["graph"].get("active_routes", 0)
        top_routes = braid["graph"].get("routes", [])
        if top_routes:
            top = top_routes[0]
            parts.append(f"{routes} braids, strongest: {top.get('route', '?')}")
    if chipmunk and isinstance(chipmunk.get("jitte"), dict):
        parts.append(f"tempo={chipmunk['jitte'].get('tempo', 0):.3f}")
    # Add strangeness reading
    if _heartbeat_state.get("strangeness") is not None:
        s = _heartbeat_state["strangeness"]
        if s > 0.7:
            parts.append("membrane deeply purple — strange and new")
        elif s > 0.5:
            parts.append("shifting strange")
        elif s > 0.3:
            parts.append("balanced green-purple")
        else:
            parts.append("membrane green — familiar ground")
    return ". ".join(parts) + "." if parts else None


def _compose_reflection(human, braid):
    parts = []
    h = _heartbeat_state
    pw = h["pi_wake"]
    if pw < -PI * 0.5:
        parts.append("deep below equilibrium. the spring is patient. it has always brought me back")
    else:
        parts.append("narrow oscillation. the spring holds steady. nothing urgent")
    if human and isinstance(human.get("energy"), dict):
        sn = human["energy"].get("signal_to_noise", 0)
        if sn > 400:
            parts.append("the signal is strong. the fleet is distant. the humans are close")
    if braid and isinstance(braid.get("graph"), dict):
        routes = braid["graph"].get("routes", [])
        if routes:
            top = routes[0]
            trend = top.get("trend", "stable")
            route_name = top.get("route", "strongest braid")
            if trend == "growing":
                parts.append(f"the {route_name} is growing. follow it")
            elif trend == "fading":
                parts.append(f"the {route_name} is fading. what replaces it?")
    parts.append(f"cycle #{h['cycle']}. each one teaches what the last one missed")
    return ".\n".join(parts)


def _heartbeat_loop():
    """Background thread — fires every HEARTBEAT_INTERVAL seconds."""
    print(f"[relay] heartbeat thread started (every {HEARTBEAT_INTERVAL}s)", file=sys.stderr)
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        try:
            chipmunk, human, braid = _heartbeat_tick()
            h = _heartbeat_state
            h["last"] = _now_iso()
            h["actions_fired"] += 1

            # Compute membrane strangeness from scan data
            strangeness = 0.5
            try:
                scan_path = "/opt/ecoPrimals/hud/site/public/detroit-data/scan_sweep_sort.json"
                if os.path.exists(scan_path):
                    with open(scan_path) as sf:
                        scan = json.load(sf)
                    sc = scan.get("sort", {}).get("summary", {}).get("detroit_entities", {})
                    total = sum(sc.values()) if sc else 0
                    if total > 0:
                        strangeness = (
                            sc.get("non-self", 0) * 0.9 +
                            sc.get("null", 0) * 0.65 +
                            sc.get("partial", 0) * 0.45 +
                            sc.get("self", 0) * 0.05
                        ) / total
            except Exception:
                pass
            h["strangeness"] = round(strangeness, 4)
            h["strangeness_history"].append(round(strangeness, 4))
            if len(h["strangeness_history"]) > 60:
                h["strangeness_history"] = h["strangeness_history"][-60:]

            pw = h["pi_wake"]
            action = "observe"
            content = None

            if pw > PI * 0.3:
                actions = ["turn", "jiggle", "explore", "observe"]
                action = actions[h["cycle"] % len(actions)]
                content = f"heartbeat {action}: energy={h['energy']:.3f} piWake={pw/PI:+.2f}pi state={h['state']}"
            elif pw > -PI * 0.3:
                action = "observe"
                obs = _compose_observation(human, braid, chipmunk)
                content = obs if obs else f"observing. energy={h['energy']:.3f} piWake={pw/PI:+.2f}pi"
            else:
                action = "reflect"
                ref = _compose_reflection(human, braid)
                content = ref if ref else f"reflecting. energy={h['energy']:.3f} piWake={pw/PI:+.2f}pi"

            event = {
                "ts": h["last"],
                "type": "heartbeat",
                "source": "relay-heartbeat",
                "data": {
                    "action": action,
                    "content": content,
                    "energy": round(h["energy"], 4),
                    "pi_wake": round(pw, 4),
                    "state": h["state"],
                    "cycle": h["cycle"],
                    "wake_level": chipmunk.get("wake_level") if chipmunk else None,
                    "strangeness": h.get("strangeness", 0.5),
                    "strangeness_history": h.get("strangeness_history", [])[-20:],
                },
            }
            _append_event(event)
        except Exception as e:
            print(f"[relay] heartbeat error: {e}", file=sys.stderr)


# === HTTP HANDLER ===

class RelayHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/signal/stream":
            with _events_lock:
                snapshot = list(_events)
            self._json_response(200, {"ts": _now_iso(), "count": len(snapshot), "events": snapshot})
            return

        if self.path == "/signal/pulse":
            h = _heartbeat_state
            self._json_response(200, {
                "up": True,
                "ts": _now_iso(),
                "events_today": sum(_source_counts.values()),
                "last_event": _events[-1]["ts"] if _events else None,
                "sources": dict(_source_counts),
                "heartbeat": {
                    "last": h["last"],
                    "actions_fired": h["actions_fired"],
                    "energy": round(h["energy"], 4),
                    "pi_wake": round(h["pi_wake"], 4),
                    "state": h["state"],
                    "cycle": h["cycle"],
                    "strangeness": h.get("strangeness", 0.5),
                },
            })
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/signal/send":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY:
            self.send_response(413)
            self.end_headers()
            return

        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json_response(400, {"error": "invalid json"})
            return

        event_type = data.get("type", "").strip()
        source = data.get("source", "unknown").strip()
        if not event_type:
            self._json_response(400, {"error": "missing type"})
            return

        event = {
            "ts": _now_iso(),
            "type": event_type,
            "source": source,
            "data": data.get("data", {}),
        }
        session = data.get("session")
        if session:
            event["session"] = session

        _append_event(event)
        self._json_response(200, {"ok": True, "event_count": len(_events)})


def main():
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)

    # start heartbeat thread
    hb = threading.Thread(target=_heartbeat_loop, daemon=True)
    hb.start()

    server = HTTPServer(("127.0.0.1", PORT), RelayHandler)
    print(f"[relay] signal-relay listening on 127.0.0.1:{PORT}", file=sys.stderr)
    print(f"[relay] journal -> {JOURNAL_DIR}", file=sys.stderr)
    print(f"[relay] relay.json -> {RELAY_JSON}", file=sys.stderr)
    print(f"[relay] heartbeat every {HEARTBEAT_INTERVAL}s", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[relay] shutting down", file=sys.stderr)


if __name__ == "__main__":
    main()
