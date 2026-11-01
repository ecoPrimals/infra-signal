#!/usr/bin/env python3
"""Add relay events to spin, purple, green commands."""

FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"

with open(FILE) as f:
    content = f.read()

changes = 0

# Add relay to spin command
OLD_SPIN = r"""          var p = window._cosmicFlavor.spin();
          addEntry('chipmunk',"""
NEW_SPIN = r"""          var p = window._cosmicFlavor.spin();
          if (window._signalRelay) {
            window._signalRelay.send('flavor_spin', { perspective: p.name, desc: p.desc });
          }
          addEntry('chipmunk',"""

if OLD_SPIN in content:
    content = content.replace(OLD_SPIN, NEW_SPIN)
    changes += 1
    print("OK: spin relay added")

# Add relay to purple search
OLD_PURPLE = r"""            var lines = ['<span style="color:#a371f7">\u2b06 SEARCHING FOR PURPLE</span> \u2014 the strangest things in the membrane'];"""
NEW_PURPLE = r"""            if (window._signalRelay) {
              window._signalRelay.send('flavor_search', { direction: 'purple', count: top.length });
            }
            var lines = ['<span style="color:#a371f7">\u2b06 SEARCHING FOR PURPLE</span> \u2014 the strangest things in the membrane'];"""

if OLD_PURPLE in content:
    content = content.replace(OLD_PURPLE, NEW_PURPLE)
    changes += 1
    print("OK: purple relay added")

# Add relay to green search
OLD_GREEN = r"""            var lines = ['<span style="color:#3fb950">\u2b07 SEARCHING FOR GREEN</span> \u2014 the most familiar, base, nearby'];"""
NEW_GREEN = r"""            if (window._signalRelay) {
              window._signalRelay.send('flavor_search', { direction: 'green', count: top.length });
            }
            var lines = ['<span style="color:#3fb950">\u2b07 SEARCHING FOR GREEN</span> \u2014 the most familiar, base, nearby'];"""

if OLD_GREEN in content:
    content = content.replace(OLD_GREEN, NEW_GREEN)
    changes += 1
    print("OK: green relay added")

if changes > 0:
    with open(FILE, "w") as f:
        f.write(content)
    print(f"Total changes: {changes}")
else:
    print("No changes made")
