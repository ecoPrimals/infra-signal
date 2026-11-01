#!/usr/bin/env python3
"""Wire human-surround into chipmunk commands and fleet-surround."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

# 1. Add /humans /presence command before /surround
HUMANS_CMD = r"""      if (cmd === 'humans' || cmd === 'presence' || cmd === 'epitopes') {
        addEntry('system', '\ud83e\uddd1 human presence');
        if (window._humanSurround) {
          var view = window._humanSurround.humanView();
          addEntry('chipmunk',
            '<span style="color:#58a6ff">\ud83e\uddd1 HUMAN MEMBRANE SORT</span>\n' +
            '<pre style="font-size:10px;line-height:1.3;color:#c9d1d9">' + view + '</pre>\n' +
            '<span class="dim">the squirrel sorts humans too. visitors arrive outside, get absorbed inside.</span>');
        } else {
          addEntry('chipmunk', '<span class="dim">human surround loading\u2026</span>');
        }
        return;
      }
"""

SURROUND_MARKER = "      if (cmd === 'surround'"
if SURROUND_MARKER in cmd:
    cmd = cmd.replace(SURROUND_MARKER, HUMANS_CMD + SURROUND_MARKER)
    print("OK: /humans /presence commands inserted")

# 2. Update /surround to toggle human-surround too
OLD_SURROUND_TOGGLE = "var on = window._fleetSurround.toggle();"
NEW_SURROUND_TOGGLE = """var on = window._fleetSurround.toggle();
          if (window._humanSurround) { if (on) window._humanSurround.activate(); else window._humanSurround.deactivate(); }"""

if OLD_SURROUND_TOGGLE in cmd:
    cmd = cmd.replace(OLD_SURROUND_TOGGLE, NEW_SURROUND_TOGGLE)
    print("OK: /surround now toggles human-surround too")

# 3. Add human info to surround ON message
OLD_SURROUND_ON = """'<span style="color:#e85d3a">\\u25bc non-self fleet above \\u2014 looking down at the membrane</span>\\n' +
              '<span style="color:#3fb950">\\u25b2 self + sovereign below \\u2014 rising up from the ground</span>\\n' +
              '<span style="color:#d2a8ff">\\ud83d\\udc7b ghost cloud fog underneath \\u2014 181K IPs</span>\\n' +
              '<span class="dim">type /twist to tilt \\u00b7 /jump to flip above/below</span>'"""

NEW_SURROUND_ON = """'<span style="color:#e85d3a">\\u25bc non-self fleet above \\u2014 looking down at the membrane</span>\\n' +
              '<span style="color:#3fb950">\\u25b2 self + sovereign below \\u2014 rising up from the ground</span>\\n' +
              '<span style="color:#58a6ff">\\u25c2 humans arriving left \\u2014 visitors, readers, observers</span>\\n' +
              '<span style="color:#f0e68c">humans absorbed right \\u25b8 \\u2014 coders, investigators, explorers</span>\\n' +
              '<span style="color:#d2a8ff">\\ud83d\\udc7b ghost fog + epitope transitions crossing the wall</span>\\n' +
              '<span class="dim">/twist /jump /humans /presence \\u2014 the squirrel sorts both fleet AND humans</span>'"""

if OLD_SURROUND_ON in cmd:
    cmd = cmd.replace(OLD_SURROUND_ON, NEW_SURROUND_ON)
    print("OK: surround ON message updated with human info")

# 4. Update help
OLD_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /particles /wall /atlas /fleet /backtrace /surround /twist /jump /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"
NEW_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /wall /atlas /fleet /backtrace /surround /twist /jump /humans /presence /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

opens = cmd.count("{")
closes = cmd.count("}")
print("chipmunk-commands.js:", cmd.count("\n"), "lines, braces", opens, "/", closes, "OK" if opens == closes else "MISMATCH")
