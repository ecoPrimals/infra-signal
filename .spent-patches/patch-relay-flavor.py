#!/usr/bin/env python3
"""Add flavor strangeness scoring to signal-relay.py heartbeat."""

FILE = "/opt/membrane/signal-relay.py"

with open(FILE) as f:
    content = f.read()

# Add strangeness computation to heartbeat state
OLD_STATE = '''    h["actions_fired"] += 1

            pw = h["pi_wake"]'''

NEW_STATE = '''    h["actions_fired"] += 1

            # Compute membrane strangeness from scan data
            strangeness = 0.5
            try:
                scan_path = "/var/www/hud/feeds/scan_sweep_sort.json"
                if os.path.exists(scan_path):
                    with open(scan_path) as sf:
                        scan = json.load(sf)
                    sc = scan.get("sort_classes", {})
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

            pw = h["pi_wake"]'''

if OLD_STATE in content:
    content = content.replace(OLD_STATE, NEW_STATE)
    print("OK: strangeness computation added to heartbeat")
else:
    print("ERROR: could not find state marker")

# Add strangeness to heartbeat event data
OLD_EVENT_DATA = '''                    "wake_level": chipmunk.get("wake_level") if chipmunk else None,'''
NEW_EVENT_DATA = '''                    "wake_level": chipmunk.get("wake_level") if chipmunk else None,
                    "strangeness": h.get("strangeness", 0.5),'''

if OLD_EVENT_DATA in content:
    content = content.replace(OLD_EVENT_DATA, NEW_EVENT_DATA)
    print("OK: strangeness added to heartbeat event data")
else:
    print("ERROR: could not find event data marker")

# Add strangeness to pulse response
OLD_PULSE = '''            "state": _heartbeat_state["state"],'''
NEW_PULSE = '''            "state": _heartbeat_state["state"],
            "strangeness": _heartbeat_state.get("strangeness", 0.5),'''

if OLD_PULSE in content:
    content = content.replace(OLD_PULSE, NEW_PULSE, 1)
    print("OK: strangeness added to pulse response")
else:
    print("WARN: could not find pulse marker")

# Add strangeness to initial heartbeat state
OLD_INIT = '''"actions_fired": 0,'''
NEW_INIT = '''"actions_fired": 0, "strangeness": 0.5,'''

if OLD_INIT in content:
    content = content.replace(OLD_INIT, NEW_INIT)
    print("OK: strangeness added to initial state")

# Add flavor commentary to observations
OLD_OBS_RETURN = '''    return ". ".join(parts) + "." if parts else None'''
NEW_OBS_RETURN = '''    # Add strangeness reading
    if _heartbeat_state.get("strangeness") is not None:
        s = _heartbeat_state["strangeness"]
        if s > 0.7:
            parts.append("membrane deeply purple \u2014 strange and new")
        elif s > 0.5:
            parts.append("shifting strange")
        elif s > 0.3:
            parts.append("balanced green-purple")
        else:
            parts.append("membrane green \u2014 familiar ground")
    return ". ".join(parts) + "." if parts else None'''

if OLD_OBS_RETURN in content:
    content = content.replace(OLD_OBS_RETURN, NEW_OBS_RETURN)
    print("OK: flavor commentary added to observations")
else:
    print("WARN: could not find observation return")

# Need to add os import if not present
if "import os" not in content:
    content = content.replace("import json", "import json, os")
    print("OK: added os import")

with open(FILE, "w") as f:
    f.write(content)

print(f"signal-relay.py: {content.count(chr(10))} lines")
