#!/usr/bin/env python3
"""Fix client-side scan data extraction in cosmic-flavor.js."""

FILE = "/opt/ecoPrimals/hud/site/public/js/cosmic-flavor.js"

with open(FILE) as f:
    c = f.read()

OLD = """      if (scan.sort_classes) {
        for (var cls in scan.sort_classes) {
          sortCounts[cls] = scan.sort_classes[cls] || 0;
        }
      }"""

NEW = """      var sc = (scan.sort && scan.sort.summary && scan.sort.summary.detroit_entities) || scan.sort_classes || {};
      for (var cls in sc) {
        if (sortCounts.hasOwnProperty(cls)) sortCounts[cls] = sc[cls] || 0;
      }"""

if OLD in c:
    c = c.replace(OLD, NEW)
    with open(FILE, "w") as f:
        f.write(c)
    print("OK: client scan extraction fixed")
else:
    print("ERROR: not found")
