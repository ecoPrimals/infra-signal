#!/usr/bin/env python3
"""Add /cycle /sweep commands for color-sort-sweep-align-twist cycle."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

# Add /cycle /sweep before /pialign
CYCLE_CMD = r"""      if (cmd === 'cycle' || cmd === 'colorcycle' || cmd === 'css') {
        addEntry('system', '\u21bb color-sort-sweep cycle');
        if (window._fleetSurround) {
          var cycling = window._fleetSurround.toggleCycle();
          addEntry('chipmunk',
            '<span style="color:' + (cycling ? '#f0e68c' : '#8b949e') + '">\u21bb CYCLE ' + (cycling ? 'ON' : 'OFF') + '</span>\n' +
            (cycling ?
              '<span style="color:#c9d1d9">\u2460 color</span> \u2192 ' +
              '<span style="color:#e85d3a">\u2461 sort</span> \u2192 ' +
              '<span style="color:#58a6ff">\u2462 sweep</span> \u2192 ' +
              '<span style="color:#5ab87a">\u2463 align</span> \u2192 ' +
              '<span style="color:#d2a8ff">\u2464 twist</span> \u2192 ' +
              '<span style="color:#f0e68c">repeat</span>\n' +
              '<span class="dim">live data \u2192 flash dots \u2192 sweep gradient \u2192 slide to \u03c0 depth \u2192 flip. every 6s.</span>' :
              '<span class="dim">cycle stopped. dots hold position.</span>'));
        }
        return;
      }
      if (cmd === 'sweep' || cmd === 'colorsweep') {
        addEntry('system', '\u2248 color sweep');
        if (window._fleetSurround && window._fleetSurround.isActive()) {
          window._fleetSurround.sweepColors();
          addEntry('chipmunk',
            '<span style="color:#ffffff">\u2248 SWEEP</span>\n' +
            '<span class="dim">flash \u2192 settle. each dot finds its \u03c0 color.</span>');
        }
        return;
      }
"""

PI_MARKER = "      if (cmd === 'pialign'"
if PI_MARKER in cmd:
    cmd = cmd.replace(PI_MARKER, CYCLE_CMD + PI_MARKER)
    print("OK: /cycle /sweep commands inserted")

# Update help
OLD_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /wall /atlas /fleet /backtrace /surround /twist /jump /pialign /humans /presence /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"
NEW_HELP = "/play /draw /deck /spin /sort /flavor /wall /atlas /fleet /backtrace /surround /twist /jump /cycle /sweep /pialign /humans /presence /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

opens = cmd.count("{")
closes = cmd.count("}")
print("chipmunk-commands.js:", cmd.count("\n"), "lines, braces", opens, "/", closes, "OK" if opens == closes else "MISMATCH")
