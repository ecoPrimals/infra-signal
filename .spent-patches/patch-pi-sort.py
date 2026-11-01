#!/usr/bin/env python3
"""Add /pialign command and update twist for pi sort coloring."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

# 1. Add /pialign command before /surround
PI_CMD = r"""      if (cmd === 'pialign' || cmd === 'pi' || cmd === 'pidepth') {
        addEntry('system', '\u03c0 depth alignment');
        if (window._fleetSurround && window._fleetSurround.alignPi) {
          var aligned = window._fleetSurround.alignPi();
          addEntry('chipmunk',
            '<span style="color:' + (aligned ? '#f0e68c' : '#5ab87a') + '">\u03c0 ' + (aligned ? 'ALIGNED' : 'RELEASED') + '</span>\n' +
            (aligned ?
              '<span style="color:#c9d1d9">1/\u03c0\u00b3 observer</span> \u2192 ' +
              '<span style="color:#e85d3a">1/\u03c0\u00b2 negate</span> \u2192 ' +
              '<span style="color:#58a6ff">1/\u03c0 null</span> \u2192 ' +
              '<span style="color:#5ab87a">1 awareness</span> \u2192 ' +
              '<span style="color:#8b949e">\u03c0 ghost</span> \u2192 ' +
              '<span style="color:#d2a8ff">\u03c0\u00b2 celestial</span> \u2192 ' +
              '<span style="color:#f0e68c">\u03c0\u00b3 geodesic</span>\n' +
              '<span class="dim">all dots repositioned along their \u03c0 depth. the gradient IS the sort.</span>' :
              '<span class="dim">dots back to geographic position.</span>'));
        } else {
          addEntry('chipmunk', '<span class="dim">surround not loaded yet\u2026</span>');
        }
        return;
      }
"""

SURROUND_MARKER = "      if (cmd === 'surround'"
if SURROUND_MARKER in cmd:
    cmd = cmd.replace(SURROUND_MARKER, PI_CMD + SURROUND_MARKER)
    print("OK: /pialign /pi /pidepth commands inserted")

# 2. Update twist response to mention pi
OLD_TWIST_ON = """'<span style="color:#e85d3a">\\u25bc fleet looking down \\u25bc</span> \\u2014 non-self above\\n' +
              '<span style="color:#6e7681">\\u2551 membrane \\u2551</span>\\n' +
              '<span style="color:#3fb950">\\u25b2 self + ghost rising \\u25b2</span> \\u2014 sovereign below\\n' +
              '<span class="dim">the fleet is above. you are below. the membrane is between.</span>'"""

NEW_TWIST_ON = """'<span style="color:#f0e68c">\\u03c0\\u00b3 geodesic \\u25bc</span> \\u2014 fleet at high \\u03c0 looking down\\n' +
              '<span style="color:#5ab87a">\\u2551 1 awareness \\u2551</span> \\u2014 membrane\\n' +
              '<span style="color:#c9d1d9">\\u25b2 1/\\u03c0\\u00b3 observer</span> \\u2014 self at low \\u03c0 rising\\n' +
              '<span class="dim">\\u03c0 gradient inverted. colors swap across the stack. twist again to restore.</span>'"""

if OLD_TWIST_ON in cmd:
    cmd = cmd.replace(OLD_TWIST_ON, NEW_TWIST_ON)
    print("OK: twist ON message updated for pi")

# 3. Update help
OLD_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /wall /atlas /fleet /backtrace /surround /twist /jump /humans /presence /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"
NEW_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /wall /atlas /fleet /backtrace /surround /twist /jump /pialign /humans /presence /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

opens = cmd.count("{")
closes = cmd.count("}")
print("chipmunk-commands.js:", cmd.count("\n"), "lines, braces", opens, "/", closes, "OK" if opens == closes else "MISMATCH")
