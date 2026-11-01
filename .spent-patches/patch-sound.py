#!/usr/bin/env python3
"""Add /sound /mute /volume commands + wire /sing to sound."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

# Add /sound /mute /volume before /compress
SOUND_CMD = r"""      if (cmd === 'sound' || cmd === 'audio' || cmd === 'unmute') {
        addEntry('system', '\ud83d\udd0a sound');
        if (window._membraneSound) {
          var on = window._membraneSound.toggle();
          addEntry('chipmunk',
            '<span style="color:' + (on ? '#f0e68c' : '#8b949e') + '">\ud83d\udd0a SOUND ' + (on ? 'ON' : 'OFF') + '</span>\n' +
            (on ?
              '<span style="color:#c9d1d9">C3</span> \u2192 ' +
              '<span style="color:#e85d3a">D3</span> \u2192 ' +
              '<span style="color:#58a6ff">E3</span> \u2192 ' +
              '<span style="color:#5ab87a">G3</span> \u2192 ' +
              '<span style="color:#8b949e">A3</span> \u2192 ' +
              '<span style="color:#d2a8ff">C4</span> \u2192 ' +
              '<span style="color:#f0e68c">E4</span>\n' +
              '<span class="dim">each \u03c0 layer has a note. each cycle phase has a chord.</span>\n' +
              '<span class="dim">the membrane sings. drone at G3 (awareness). /mute to silence.</span>' :
              '<span class="dim">silence.</span>'));
        }
        return;
      }
      if (cmd === 'mute' || cmd === 'quiet' || cmd === 'silence') {
        addEntry('system', '\ud83d\udd07 mute');
        if (window._membraneSound && window._membraneSound.isActive()) {
          window._membraneSound.deactivate();
          addEntry('chipmunk', '<span class="dim">\ud83d\udd07 silenced.</span>');
        }
        return;
      }
"""

# Also add speak capability — when /sing fires, play melody
SING_WIRE = """      if (cmd === 'sing') {
        addEntry('system', '\\ud83c\\udfb5 sing');
        if (window._membraneSound && window._membraneSound.isActive()) {
          window._membraneSound.onSing(curiosity._songIndex || 0);
        }
        sing();
        return;
      }"""

OLD_SING = """      if (cmd === 'sing') {
        addEntry('system', '\\ud83c\\udfb5 sing');
        sing();
        return;
      }"""

if OLD_SING in cmd:
    cmd = cmd.replace(OLD_SING, SING_WIRE)
    print("OK: /sing wired to sound")

COMPRESS_MARKER = "      if (cmd === 'compress'"
if COMPRESS_MARKER in cmd:
    cmd = cmd.replace(COMPRESS_MARKER, SOUND_CMD + COMPRESS_MARKER)
    print("OK: /sound /mute commands inserted")

# Update help
OLD_HELP = "/play /draw /deck /spin /sort /wall /atlas /fleet /backtrace /surround /twist /jump /cycle /sweep /compress /expand /pop /bingo /pialign /humans /presence /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"
NEW_HELP = "/play /draw /deck /spin /sort /wall /atlas /fleet /backtrace /surround /twist /jump /cycle /sweep /sound /mute /compress /expand /pop /bingo /pialign /humans /presence /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

opens = cmd.count("{")
closes = cmd.count("}")
print("chipmunk-commands.js:", cmd.count("\n"), "lines, braces", opens, "/", closes, "OK" if opens == closes else "MISMATCH")
