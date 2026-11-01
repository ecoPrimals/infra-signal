#!/usr/bin/env python3
"""Patch cosmic-strategy.js to include flavor coloring in territory display."""

FILE = "/opt/ecoPrimals/hud/site/public/js/cosmic-strategy.js"

with open(FILE) as f:
    content = f.read()

# Add flavor coloring to territory lines
OLD = r"""      lines.push('  ' + t.name + ' \u2014 ' + status + '  defense ' + (t.defense * 100).toFixed(0) + '%');"""

NEW = r"""      var flavorPip = '';
      if (window._cosmicFlavor) {
        var st = window._cosmicFlavor.surfaceStrangeness(k);
        flavorPip = '<span style="color:' + window._cosmicFlavor.flavorHex(st) + '">\u25cf</span> ';
      }
      lines.push('  ' + flavorPip + t.name + ' \u2014 ' + status + '  defense ' + (t.defense * 100).toFixed(0) + '%');"""

if OLD in content:
    content = content.replace(OLD, NEW)
    with open(FILE, "w") as f:
        f.write(content)
    print("OK: strategy view patched with flavor coloring")
else:
    print("ERROR: could not find territory line")
