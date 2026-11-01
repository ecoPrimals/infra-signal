#!/usr/bin/env python3
"""Add flavor strangeness gauge to signal relay dashboard."""

FILE = "/opt/ecoPrimals/signal/site/public/js/signal-relay-dashboard.js"

with open(FILE) as f:
    content = f.read()

# Add strangeness gauge panel
OLD_SOURCES = """      '    <div id="relay-sources" style="flex:1;min-width:200px">',
      '      <div style="color:#8b949e;text-transform:uppercase;font-size:.8em;margin-bottom:.5em">Sources</div>',
      '      <div id="relay-src-list" style="font-family:monospace;font-size:.9em;color:#c9d1d9">\\u2026</div>',
      '    </div>',"""

NEW_SOURCES = """      '    <div id="relay-sources" style="flex:1;min-width:200px">',
      '      <div style="color:#8b949e;text-transform:uppercase;font-size:.8em;margin-bottom:.5em">Sources</div>',
      '      <div id="relay-src-list" style="font-family:monospace;font-size:.9em;color:#c9d1d9">\\u2026</div>',
      '    </div>',
      '    <div id="relay-flavor" style="flex:1;min-width:200px">',
      '      <div style="color:#8b949e;text-transform:uppercase;font-size:.8em;margin-bottom:.5em">\\u2728 Membrane Flavor</div>',
      '      <div id="relay-strangeness" style="font-family:monospace;font-size:1.1em;color:#bc8cff">\\u2026</div>',
      '    </div>',"""

if OLD_SOURCES in content:
    content = content.replace(OLD_SOURCES, NEW_SOURCES)
    print("OK: strangeness gauge HTML added")
else:
    print("ERROR: could not find sources panel")

# Add strangeness rendering to updatePulse
OLD_SRC_UPDATE = """      var srcEl = document.getElementById('relay-src-list');"""

NEW_SRC_UPDATE = """      // Flavor strangeness gauge
      var flavorEl = document.getElementById('relay-strangeness');
      if (flavorEl && p.heartbeat) {
        var s = p.heartbeat.strangeness || 0.5;
        var barWidth = 20;
        var flavorBar = '';
        for (var fi = 0; fi < barWidth; fi++) {
          var frac = fi / (barWidth - 1);
          var r = Math.round(63 + (163 - 63) * frac);
          var g = Math.round(185 + (113 - 185) * frac);
          var b = Math.round(80 + (247 - 80) * frac);
          if (Math.abs(frac - s) < (1 / barWidth)) {
            flavorBar += '<span style="color:#f0e68c">\\u25c6</span>';
          } else {
            flavorBar += '<span style="color:rgb(' + r + ',' + g + ',' + b + ')">\\u2500</span>';
          }
        }
        var label = s < 0.3 ? 'familiar' : s < 0.5 ? 'balanced' : s < 0.7 ? 'shifting' : 'strange';
        var fc = s < 0.3 ? '#3fb950' : s < 0.5 ? '#58a6ff' : s < 0.7 ? '#bc8cff' : '#a371f7';
        flavorEl.innerHTML = flavorBar + '<br><span style="color:' + fc + '">' + label + '</span> ' + (s * 100).toFixed(1) + '%';
      }

      var srcEl = document.getElementById('relay-src-list');"""

if OLD_SRC_UPDATE in content:
    content = content.replace(OLD_SRC_UPDATE, NEW_SRC_UPDATE)
    print("OK: strangeness gauge rendering added")
else:
    print("ERROR: could not find src update")

# Add flavor event types to color map
OLD_TYPE_COLORS = """            test: '#484f58',"""
NEW_TYPE_COLORS = """            test: '#484f58',
            flavor_spin: '#a371f7',
            flavor_sort: '#bc8cff',
            flavor_search: '#a371f7',
            flavor_spectrum: '#bc8cff',"""

if OLD_TYPE_COLORS in content:
    content = content.replace(OLD_TYPE_COLORS, NEW_TYPE_COLORS)
    print("OK: flavor event colors added")
else:
    print("WARN: could not find type colors")

with open(FILE, "w") as f:
    f.write(content)

print(f"signal-relay-dashboard.js: {content.count(chr(10))} lines")
