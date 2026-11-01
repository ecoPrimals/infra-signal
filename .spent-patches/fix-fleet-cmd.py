#!/usr/bin/env python3
"""Fix fleet command to use fleet atlas."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

OLD = r"""      if (cmd === 'fleet' || cmd === 'ghost' || cmd === 'bots') {
        addEntry('system', '\ud83d\udc7e fleet');
        if (window._chipmunkMind && window._chipmunkMind.showFleet) {
          window._chipmunkMind.showFleet();
        } else {
          addEntry('chipmunk', '<span class="dim">fleet loading\u2026</span>');
        }
        return;
      }"""

NEW = r"""      if (cmd === 'ghost' || cmd === 'bots') {
        addEntry('system', '\ud83d\udc7e fleet');
        if (window._fleetAtlas) {
          addEntry('chipmunk', window._fleetAtlas.backtraceView('ghost'));
        } else if (window._chipmunkMind && window._chipmunkMind.showFleet) {
          window._chipmunkMind.showFleet();
        } else {
          addEntry('chipmunk', '<span class="dim">fleet loading\u2026</span>');
        }
        return;
      }"""

if OLD in cmd:
    cmd = cmd.replace(OLD, NEW)
    print("OK: old fleet command updated, ghost/bots now use atlas")
else:
    print("WARN: could not find old fleet command")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

opens = cmd.count("{")
closes = cmd.count("}")
print(f"braces {opens}/{closes} {'OK' if opens == closes else 'MISMATCH'}")
