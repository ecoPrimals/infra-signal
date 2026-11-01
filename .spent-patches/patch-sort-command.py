#!/usr/bin/env python3
"""Patch the old sort command to use flavor sort when available."""

FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"

with open(FILE) as f:
    content = f.read()

OLD = r"""      if (cmd === 'sort') {
        if (window._chipmunkMind && window._chipmunkMind.toggleSortDeck) {
          window._chipmunkMind.toggleSortDeck();
        }
        return;
      }"""

NEW = r"""      if (cmd === 'sort') {
        if (window._cosmicFlavor) {
          addEntry('system', '\u2195 sort');
          addEntry('chipmunk', window._cosmicFlavor.sortedHandView());
          if (window._signalRelay) {
            var p = window._cosmicFlavor.currentPerspective();
            window._signalRelay.send('flavor_sort', { perspective: p.name });
          }
        } else if (window._chipmunkMind && window._chipmunkMind.toggleSortDeck) {
          window._chipmunkMind.toggleSortDeck();
        }
        return;
      }"""

if OLD in content:
    content = content.replace(OLD, NEW)
    with open(FILE, "w") as f:
        f.write(content)
    print("OK: sort command updated")
else:
    print("ERROR: could not find old sort command")
