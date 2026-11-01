#!/usr/bin/env python3
"""Add /wall command and deploy membrane-wall.js."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

WALL_CMDS = r"""      if (cmd === 'wall' || cmd === 'membrane' || cmd === 'align') {
        addEntry('system', '\u2551 membrane wall');
        if (window._membraneWall) {
          addEntry('chipmunk', window._membraneWall.wallView());
          if (window._signalRelay) {
            window._signalRelay.send('wall_view', { active: window._membraneWall.isActive() });
          }
        } else {
          addEntry('chipmunk', '<span class="dim">wall engine loading\u2026</span>');
        }
        return;
      }
      if (cmd === 'twist' || cmd === 'twistwall') {
        addEntry('system', '\u221e twist');
        if (window._membraneWall) {
          var active = window._membraneWall.toggle();
          addEntry('chipmunk',
            '<span style="color:' + (active ? '#a371f7' : '#3fb950') + '">\u221e WALL ' + (active ? 'ON' : 'OFF') + '</span>\n' +
            (active ?
              '<span style="color:#3fb950">\u25c2 INSIDE</span> \u2014 green \u2014 self \u2014 familiar\n' +
              '<span style="color:#6e7681">\u2551 membrane wall \u2551</span>\n' +
              '<span style="color:#a371f7">OUTSIDE \u25b8</span> \u2014 purple \u2014 non-self \u2014 strange\n' +
              '<span class="dim">the dashboard aligns along the wall. data topo-sorted in and out.</span>' :
              '<span class="dim">wall removed. layout restored.</span>'));
        } else if (window._twistJump) {
          window._twistJump.twist();
        }
        if (window._cosmicView && window._cosmicView.twist) window._cosmicView.twist();
        return;
      }
"""

# Insert before the existing twist command (which we'll keep as fallback)
OLD_TWIST = """      if (cmd === 'twist') {
        addEntry('system', '\\u221e twist');
        if (window._twistJump) window._twistJump.twist();
        if (window._cosmicView && window._cosmicView.twist) window._cosmicView.twist();
        return;
      }"""

if OLD_TWIST in cmd:
    cmd = cmd.replace(OLD_TWIST, WALL_CMDS)
    print("OK: wall/twist commands replaced")
else:
    print("WARN: could not find old twist command")
    # Try inserting before jump instead
    jump_marker = """      if (cmd === 'jump'"""
    if jump_marker in cmd:
        cmd = cmd.replace(jump_marker, WALL_CMDS + jump_marker)
        print("OK: wall commands inserted before jump")

# Update help
OLD_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /particles /aura /sparkline /wobble /tint /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore /trail"
NEW_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /particles /aura /sparkline /wall /wobble /tint /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

lines = cmd.count("\n")
opens = cmd.count("{")
closes = cmd.count("}")
print(f"chipmunk-commands.js: {lines} lines, braces {opens}/{closes} {'OK' if opens==closes else 'MISMATCH'}")
