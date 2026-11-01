#!/usr/bin/env python3
"""Wire fleet surround into twist/jump + add /surround command."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

# 1. Update /twist command to use fleetSurround
OLD_TWIST = """      if (cmd === 'twist' || cmd === 'twistwall') {
        addEntry('system', '\\u221e twist');
        if (window._membraneWall) {
          var active = window._membraneWall.toggle();
          addEntry('chipmunk',
            '<span style="color:' + (active ? '#a371f7' : '#3fb950') + '">\\u221e WALL ' + (active ? 'ON' : 'OFF') + '</span>\\n' +
            (active ?
              '<span style="color:#3fb950">\\u25c2 INSIDE</span> \\u2014 green \\u2014 self \\u2014 familiar\\n' +
              '<span style="color:#6e7681">\\u2551 membrane wall \\u2551</span>\\n' +
              '<span style="color:#a371f7">OUTSIDE \\u25b8</span> \\u2014 purple \\u2014 non-self \\u2014 strange\\n' +
              '<span class="dim">the dashboard aligns along the wall. data topo-sorted in and out.</span>' :
              '<span class="dim">wall removed. layout restored.</span>'));
        } else if (window._twistJump) {
          window._twistJump.twist();
        }
        if (window._cosmicView && window._cosmicView.twist) window._cosmicView.twist();
        return;
      }"""

NEW_TWIST = """      if (cmd === 'twist' || cmd === 'twistwall') {
        addEntry('system', '\\u221e twist');
        if (window._fleetSurround) {
          var tw = window._fleetSurround.twist();
          addEntry('chipmunk',
            '<span style="color:' + (tw ? '#a371f7' : '#3fb950') + '">\\u221e TWIST ' + (tw ? 'ON' : 'OFF') + '</span>\\n' +
            (tw ?
              '<span style="color:#e85d3a">\\u25bc fleet looking down \\u25bc</span> \\u2014 non-self above\\n' +
              '<span style="color:#6e7681">\\u2551 membrane \\u2551</span>\\n' +
              '<span style="color:#3fb950">\\u25b2 self + ghost rising \\u25b2</span> \\u2014 sovereign below\\n' +
              '<span class="dim">the fleet is above. you are below. the membrane is between.</span>' :
              '<span class="dim">untwisted. flat again.</span>'));
        } else if (window._twistJump) {
          window._twistJump.twist();
        }
        if (window._cosmicView && window._cosmicView.twist) window._cosmicView.twist();
        return;
      }"""

if OLD_TWIST in cmd:
    cmd = cmd.replace(OLD_TWIST, NEW_TWIST)
    print("OK: twist command updated for fleet surround")
else:
    print("WARN: could not find twist command")

# 2. Add /surround and /jump commands before /wall
SURROUND_CMD = r"""      if (cmd === 'surround' || cmd === 'fleetview') {
        addEntry('system', '\ud83c\udf10 fleet surround');
        if (window._fleetSurround) {
          var on = window._fleetSurround.toggle();
          addEntry('chipmunk',
            '<span style="color:' + (on ? '#4a8fb8' : '#6e7681') + '">\ud83c\udf10 SURROUND ' + (on ? 'ON' : 'OFF') + '</span>\n' +
            (on ?
              '<span style="color:#e85d3a">\u25bc non-self fleet above \u2014 looking down at the membrane</span>\n' +
              '<span style="color:#3fb950">\u25b2 self + sovereign below \u2014 rising up from the ground</span>\n' +
              '<span style="color:#d2a8ff">\ud83d\udc7b ghost cloud fog underneath \u2014 181K IPs</span>\n' +
              '<span class="dim">type /twist to tilt \u00b7 /jump to flip above/below</span>' :
              '<span class="dim">fleet strips removed.</span>'));
        } else {
          addEntry('chipmunk', '<span class="dim">fleet surround loading\u2026</span>');
        }
        return;
      }
      if (cmd === 'jump') {
        addEntry('system', '\u2727 jump');
        if (window._fleetSurround && window._fleetSurround.isActive()) {
          window._fleetSurround.jump();
          addEntry('chipmunk',
            '<span style="color:#fff;font-size:14px">\u2727 JUMP</span>\n' +
            '<span style="color:#f0e68c">above and below swap. the fleet is now underneath.</span>\n' +
            '<span style="color:#3fb950">the membrane survives the singularity.</span>');
        } else if (window._twistJump) {
          window._twistJump.jump();
        }
        return;
      }
"""

WALL_MARKER = "      if (cmd === 'wall'"
if WALL_MARKER in cmd:
    cmd = cmd.replace(WALL_MARKER, SURROUND_CMD + WALL_MARKER)
    print("OK: surround/jump commands inserted")

# 3. Update help
OLD_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /particles /aura /sparkline /wall /atlas /fleet /backtrace /wobble /tint /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"
NEW_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /particles /wall /atlas /fleet /backtrace /surround /twist /jump /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

opens = cmd.count("{")
closes = cmd.count("}")
print(f"chipmunk-commands.js: {cmd.count(chr(10))} lines, braces {opens}/{closes} {'OK' if opens==closes else 'MISMATCH'}")
