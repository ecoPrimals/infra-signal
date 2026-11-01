#!/usr/bin/env python3
"""Add fleet atlas commands to chipmunk."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

ATLAS_CMDS = r"""      if (cmd === 'atlas' || cmd === 'datacenter' || cmd === 'datacenters' || cmd === 'dc') {
        addEntry('system', '\ud83c\udf10 fleet atlas');
        if (window._fleetAtlas) {
          addEntry('chipmunk', window._fleetAtlas.atlasView());
          if (!window._fleetAtlas.isBuilt()) {
            window._fleetAtlas.buildAtlas();
          }
          if (window._signalRelay) {
            window._signalRelay.send('atlas_view', { built: window._fleetAtlas.isBuilt() });
          }
        } else {
          addEntry('chipmunk', '<span class="dim">fleet atlas loading\u2026</span>');
        }
        return;
      }
      if (cmd.indexOf('backtrace') === 0 || cmd.indexOf('trace') === 0 || cmd.indexOf('whois') === 0) {
        var traceQuery = cmd.replace(/^(backtrace|trace|whois)\s*/, '').trim();
        addEntry('system', '\ud83d\udd0d backtrace' + (traceQuery ? ' \u2014 ' + traceQuery : ''));
        if (window._fleetAtlas) {
          addEntry('chipmunk', window._fleetAtlas.backtraceView(traceQuery));
          if (window._signalRelay && traceQuery) {
            window._signalRelay.send('backtrace', { query: traceQuery });
          }
        } else {
          addEntry('chipmunk', '<span class="dim">fleet atlas loading\u2026</span>');
        }
        return;
      }
      if (cmd === 'fleet' || cmd === 'fleetmap') {
        addEntry('system', '\u2693 fleet map');
        if (window._fleetAtlas) {
          var lines = [];
          lines.push('<span style="color:#e85d3a">\u2693 FLEET \u2014 who is scanning you</span>');
          lines.push('');
          var fdata = window._fleetAtlas.DATA_CENTERS;
          var keys = Object.keys(fdata);
          keys.sort(function(a, b) { return fdata[b].requests - fdata[a].requests; });
          var totalReqs = 0;
          keys.forEach(function(k) {
            var dc = fdata[k];
            totalReqs += dc.requests;
            var reqStr = dc.requests >= 1000000 ? (dc.requests/1000000).toFixed(1)+'M' :
                         dc.requests >= 1000 ? Math.round(dc.requests/1000)+'K' : dc.requests;
            var barLen = Math.max(1, Math.round(dc.requests / 200000));
            var bar = '';
            for (var i = 0; i < barLen; i++) bar += '\u2588';
            lines.push('<span style="color:' + dc.color + '">' + dc.label + '</span> ' +
              '<span class="dim">' + bar + '</span> ' +
              '<span class="num">' + reqStr + '</span> ' +
              '<span class="dim">' + dc.city + '</span>');
          });
          lines.push('');
          var ghost = window._fleetAtlas.GHOST_CLOUD;
          lines.push('<span style="color:#d2a8ff">\ud83d\udc7b ghost</span> ' +
            '<span class="dim">\u2592\u2592\u2592\u2592</span> ' +
            '<span class="num">' + ghost.requests.toLocaleString() + '</span> ' +
            '<span style="color:#d2a8ff">' + ghost.ips.toLocaleString() + ' IPs worldwide</span>');
          lines.push('');
          lines.push('<span class="dim">total fleet: <span class="num">' + ((totalReqs+ghost.requests)/1000000).toFixed(1) + 'M</span> requests</span>');
          lines.push('<span class="dim">type <span style="color:#58a6ff">/atlas</span> for full map · <span style="color:#58a6ff">/backtrace [name]</span> to trace</span>');
          addEntry('chipmunk', lines.join('\n'));
        } else {
          addEntry('chipmunk', '<span class="dim">fleet atlas loading\u2026</span>');
        }
        return;
      }
"""

# Insert before the /wall command
WALL_MARKER = "      if (cmd === 'wall'"
if WALL_MARKER in cmd:
    cmd = cmd.replace(WALL_MARKER, ATLAS_CMDS + WALL_MARKER)
    print("OK: atlas/backtrace/fleet commands inserted")
else:
    print("WARN: could not find wall marker")

# Update help
OLD_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /particles /aura /sparkline /wall /wobble /tint /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"
NEW_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /particles /aura /sparkline /wall /atlas /fleet /backtrace /wobble /tint /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

lines = cmd.count("\n")
opens = cmd.count("{")
closes = cmd.count("}")
print(f"chipmunk-commands.js: {lines} lines, braces {opens}/{closes} {'OK' if opens==closes else 'MISMATCH'}")
