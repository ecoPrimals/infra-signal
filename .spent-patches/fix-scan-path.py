#!/usr/bin/env python3
"""Fix scan_sweep_sort.json path and data extraction in signal-relay.py."""

FILE = "/opt/membrane/signal-relay.py"

with open(FILE) as f:
    c = f.read()

# Fix scan path
c = c.replace(
    '/var/www/hud/feeds/scan_sweep_sort.json',
    '/opt/ecoPrimals/hud/site/public/detroit-data/scan_sweep_sort.json'
)

# Fix the data extraction — sort classes are nested under sort.summary.detroit_entities
c = c.replace(
    'scan.get("sort_classes", {})',
    'scan.get("sort", {}).get("summary", {}).get("detroit_entities", {})'
)

with open(FILE, "w") as f:
    f.write(c)

print("OK: fixed scan path and extraction")
