#!/usr/bin/env python3
"""Add /compress /expand /bingo /pop commands."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

BINGO_CMD = r"""      if (cmd === 'compress' || cmd === 'squeeze') {
        addEntry('system', '\u2588 compress');
        if (window._bingoCompress) {
          var lvl = window._bingoCompress.compress();
          var labels = ['full', 'half', '1/\u03c0', 'tight'];
          var counts = [342, 174, 106, 33];
          addEntry('chipmunk',
            '<span style="color:' + (['#c9d1d9','#e85d3a','#58a6ff','#5ab87a'][lvl]) + '">\u2588 COMPRESS \u2192 ' + labels[lvl] + ' (x=' + [1.0,0.5,0.318,0.1][lvl] + ')</span>\n' +
            '<span class="dim">' + counts[lvl] + '/342 entities survive. squirrel shakes the rest out.</span>\n' +
            '<span class="dim">surround squeezes. dots vanish. /expand to reverse.</span>');
        }
        return;
      }
      if (cmd === 'expand' || cmd === 'unsqueeze') {
        addEntry('system', '\u2591 expand');
        if (window._bingoCompress) {
          var lvl = window._bingoCompress.expand();
          if (lvl >= 0) {
            var labels = ['full', 'half', '1/\u03c0', 'tight'];
            var counts = [342, 174, 106, 33];
            addEntry('chipmunk',
              '<span style="color:#5ab87a">\u2591 EXPAND \u2192 ' + labels[lvl] + '</span>\n' +
              '<span class="dim">' + counts[lvl] + '/342 entities. dots return. surround grows.</span>');
          } else {
            addEntry('chipmunk', '<span class="dim">fully expanded. sieve removed.</span>');
          }
        }
        return;
      }
      if (cmd === 'pop' || cmd === 'compressandpop') {
        addEntry('system', '\u2727 compress \u2192 pop');
        if (window._bingoCompress) {
          window._bingoCompress.compressAndPop();
          addEntry('chipmunk',
            '<span style="color:#f0e68c">\u2727 COMPRESS \u2192 POP</span>\n' +
            '<span style="color:#c9d1d9">full(342)</span> \u2192 ' +
            '<span style="color:#e85d3a">half(174)</span> \u2192 ' +
            '<span style="color:#58a6ff">1/\u03c0(106)</span> \u2192 ' +
            '<span style="color:#5ab87a">tight(33)</span> \u2192 ' +
            '<span style="color:#f0e68c">POP!</span> \u2192 expand back\n' +
            '<span class="dim">squeeze as tight as we can. see what survives. then reverse.</span>\n' +
            '<span class="dim">squirrel shakes dots out at each level. 24.4:1 compression ratio.</span>');
        }
        return;
      }
      if (cmd === 'bingo' || cmd === 'sieve') {
        addEntry('system', '\u25a6 bingo sieve');
        if (window._bingoCompress) {
          var view = window._bingoCompress.bingoView();
          addEntry('chipmunk',
            '<span style="color:#d2a8ff">\u25a6 BINGO CUBE \u2014 Attention \u00d7 Curiosity \u00d7 Interaction</span>\n' +
            '<pre style="font-size:10px;line-height:1.3;color:#c9d1d9">' + view + '</pre>\n' +
            '<span class="dim">/compress to squeeze. /pop for the full cycle. /expand to reverse.</span>');
        }
        return;
      }
"""

CYCLE_MARKER = "      if (cmd === 'cycle'"
if CYCLE_MARKER in cmd:
    cmd = cmd.replace(CYCLE_MARKER, BINGO_CMD + CYCLE_MARKER)
    print("OK: /compress /expand /pop /bingo commands inserted")

# Update help
OLD_HELP = "/play /draw /deck /spin /sort /flavor /wall /atlas /fleet /backtrace /surround /twist /jump /cycle /sweep /pialign /humans /presence /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"
NEW_HELP = "/play /draw /deck /spin /sort /wall /atlas /fleet /backtrace /surround /twist /jump /cycle /sweep /compress /expand /pop /bingo /pialign /humans /presence /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

opens = cmd.count("{")
closes = cmd.count("}")
print("chipmunk-commands.js:", cmd.count("\n"), "lines, braces", opens, "/", closes, "OK" if opens == closes else "MISMATCH")
