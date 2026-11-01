#!/usr/bin/env python3
"""Deep flavor integration — dynamic strangeness, orbit wobble, combat scaling, spectrum."""

import json, os

# ═══ 1. PATCH COSMIC-FLAVOR.JS — add dynamic strangeness from live feeds ═══

FLAVOR_FILE = "/opt/ecoPrimals/hud/site/public/js/cosmic-flavor.js"
with open(FLAVOR_FILE) as f:
    fv = f.read()

# Add dynamic feed scoring before the EXPORT block
DYNAMIC_BLOCK = r"""
  // ═══ DYNAMIC STRANGENESS FROM LIVE DATA ═══

  var _feedStrangeness = {};

  function updateFromFeeds() {
    var cs = window._cosmicSurfaces;
    if (!cs || !cs.feeds) return;
    var feeds = cs.feeds();

    // Scan sweep sort — entities with sort classes get real-time scores
    if (feeds.scan) {
      var scan = feeds.scan;
      var sortCounts = { self: 0, partial: 0, null: 0, 'non-self': 0 };
      if (scan.sort_classes) {
        for (var cls in scan.sort_classes) {
          sortCounts[cls] = scan.sort_classes[cls] || 0;
        }
      }
      var total = sortCounts.self + sortCounts.partial + sortCounts['null'] + sortCounts['non-self'];
      if (total > 0) {
        _feedStrangeness.membrane = (
          sortCounts['non-self'] * 0.9 +
          sortCounts['null'] * 0.65 +
          sortCounts.partial * 0.45 +
          sortCounts.self * 0.05
        ) / total;
      }
    }

    // Topology — connection density affects strangeness
    if (feeds.topology) {
      var topo = feeds.topology;
      var edges = topo.total_edges || 0;
      var nodes = topo.total_nodes || 1;
      var density = edges / (nodes * (nodes - 1) / 2 || 1);
      _feedStrangeness.topology = Math.min(1, density * 5);
    }

    // Human data — S/N ratio affects strangeness
    if (feeds.human) {
      var human = feeds.human;
      var sn = (human.energy && human.energy.signal_to_noise) || 1;
      _feedStrangeness.signalNoise = Math.max(0, 1 - (sn / 1000));
    }

    return _feedStrangeness;
  }

  function feedStrangeness() { return _feedStrangeness; }

  function liveCardStrangeness(card) {
    var base = cardStrangeness(card);
    var memS = _feedStrangeness.membrane || 0.5;
    return base * 0.7 + memS * 0.3;
  }

  // ═══ SPECTRUM VIEW — live gradient visualization ═══

  function spectrumView() {
    updateFromFeeds();
    var lines = [
      '<span style="color:#a371f7">\u2b06 THE SPECTRUM</span> \u2014 live strangeness across the membrane',
      '',
    ];

    // Build a 40-character gradient bar
    var bar = '';
    for (var i = 0; i < 40; i++) {
      var s = i / 39;
      bar += '<span style="color:' + flavorHex(s) + '">\u2588</span>';
    }
    lines.push(bar);
    lines.push('<span style="color:#3fb950">GREEN</span>' + ' '.repeat(28) + '<span style="color:#a371f7">PURPLE</span>');
    lines.push('');

    // Live feed strangeness
    lines.push('<span style="color:#bc8cff">LIVE FEED READINGS</span>');
    var feedKeys = Object.keys(_feedStrangeness);
    if (feedKeys.length === 0) {
      lines.push('  <span class="dim">no feed data yet \u2014 /draw to pull</span>');
    } else {
      feedKeys.sort(function(a, b) { return (_feedStrangeness[b] || 0) - (_feedStrangeness[a] || 0); });
      feedKeys.forEach(function(k) {
        var s = _feedStrangeness[k];
        lines.push('  ' + flavorBar(s) + ' ' + k + ' <span style="color:' + flavorHex(s) + '">' + (s * 100).toFixed(1) + '%</span>');
      });
    }

    // Current hand strangeness
    var cc = window._cosmicCards;
    if (cc && cc.hand().length > 0) {
      var hand = cc.hand();
      var avgS = 0;
      hand.forEach(function(c) { avgS += cardStrangeness(c); });
      avgS /= hand.length;
      lines.push('\n<span style="color:#bc8cff">HAND STRANGENESS</span>');
      lines.push('  ' + flavorBar(avgS) + ' average: <span style="color:' + flavorHex(avgS) + '">' + (avgS * 100).toFixed(1) + '%</span> across ' + hand.length + ' cards');

      var minS = 1, maxS = 0, minC = null, maxC = null;
      hand.forEach(function(c) {
        var s = cardStrangeness(c);
        if (s < minS) { minS = s; minC = c; }
        if (s > maxS) { maxS = s; maxC = c; }
      });
      if (minC) lines.push('  <span style="color:#3fb950">\u2b07 greenest:</span> ' + minC.name + ' (' + (minS * 100).toFixed(0) + '%)');
      if (maxC) lines.push('  <span style="color:#a371f7">\u2b06 purplest:</span> ' + maxC.name + ' (' + (maxS * 100).toFixed(0) + '%)');
    }

    // Overall membrane strangeness
    var memS = _feedStrangeness.membrane;
    if (memS !== undefined) {
      lines.push('\n<span style="color:#bc8cff">MEMBRANE BALANCE</span>');
      var pos = Math.round(memS * 38);
      var gauge = '';
      for (var j = 0; j < 40; j++) {
        if (j === pos) {
          gauge += '<span style="color:#f0e68c">\u25c6</span>';
        } else {
          gauge += '<span style="color:' + flavorHex(j / 39) + '">\u2500</span>';
        }
      }
      lines.push('  ' + gauge);
      var label = memS < 0.3 ? 'mostly familiar' : memS < 0.5 ? 'balanced' : memS < 0.7 ? 'shifting strange' : 'deeply purple';
      lines.push('  <span style="color:' + flavorHex(memS) + '">' + label + '</span> (' + (memS * 100).toFixed(1) + '% strangeness)');
    }

    lines.push('');
    lines.push('<span style="color:#3fb950">\u2b07 GREEN</span> \u2014 base, familiar, common, nearby');
    lines.push('<span class="dim">/purple to search up \u00b7 /green to search down \u00b7 /spin to rotate</span>');

    return lines.join('\n');
  }

  // ═══ ORBIT WOBBLE — planets drift by strangeness ═══

  var _wobbleActive = false;
  var _wobblePhase = 0;

  function startOrbitWobble() {
    if (_wobbleActive) return;
    _wobbleActive = true;
    _wobblePhase = 0;
    _wobbleLoop();
  }

  function stopOrbitWobble() {
    _wobbleActive = false;
  }

  function _wobbleLoop() {
    if (!_wobbleActive) return;
    _wobblePhase += 0.02;

    var cv = window._cosmicView;
    if (!cv || !cv.getSvg || !cv.isVisible()) {
      requestAnimationFrame(_wobbleLoop);
      return;
    }
    var svg = cv.getSvg();
    if (!svg) { requestAnimationFrame(_wobbleLoop); return; }

    var surfEls = svg.querySelectorAll('circle[data-surface][data-orbit-r]');
    for (var i = 0; i < surfEls.length; i++) {
      var el = surfEls[i];
      var surfName = el.getAttribute('data-surface');
      var baseR = parseFloat(el.getAttribute('data-orbit-r'));
      var s = surfaceStrangeness(surfName);

      // Wobble: purple things drift outward, green things drift inward
      var wobble = Math.sin(_wobblePhase + s * 6.28) * (s - 0.5) * 4;
      el.setAttribute('data-orbit-r', (baseR + wobble).toFixed(1));
    }

    requestAnimationFrame(_wobbleLoop);
  }

"""

# Insert before the export block
export_marker = "  // \u2550\u2550\u2550 EXPORT \u2550\u2550\u2550"
if export_marker in fv:
    fv = fv.replace(export_marker, DYNAMIC_BLOCK + "\n" + export_marker)
    print("OK: dynamic strangeness block inserted")
else:
    print("ERROR: could not find EXPORT marker")

# Add new exports
OLD_EXPORTS = """    PERSPECTIVES: PERSPECTIVES,
  };"""
NEW_EXPORTS = """    PERSPECTIVES: PERSPECTIVES,
    // dynamic
    updateFromFeeds: updateFromFeeds,
    feedStrangeness: feedStrangeness,
    liveCardStrangeness: liveCardStrangeness,
    spectrumView: spectrumView,
    // wobble
    startOrbitWobble: startOrbitWobble,
    stopOrbitWobble: stopOrbitWobble,
  };"""

if OLD_EXPORTS in fv:
    fv = fv.replace(OLD_EXPORTS, NEW_EXPORTS)
    print("OK: new exports added")
else:
    print("ERROR: could not find old exports")

with open(FLAVOR_FILE, "w") as f:
    f.write(fv)

print(f"cosmic-flavor.js: {fv.count(chr(10))} lines")


# ═══ 2. PATCH COMBAT — scale difficulty by strangeness ═══

GAMEPLAY_FILE = "/opt/ecoPrimals/hud/site/public/js/cosmic-gameplay.js"
with open(GAMEPLAY_FILE) as f:
    gp = f.read()

OLD_COMBAT = r"""      var aRoll = Math.random() * (playerCard.power || 1) + (playerCard.power || 1) * 0.5;
      var dRoll = Math.random() * (enemyCard.toughness || 1) + (enemyCard.toughness || 1) * 0.5;"""

NEW_COMBAT = r"""      var strangeBonus = 0;
      if (window._cosmicFlavor) {
        var eStrange = window._cosmicFlavor.cardStrangeness(enemyCard);
        strangeBonus = eStrange * 2;
      }
      var aRoll = Math.random() * (playerCard.power || 1) + (playerCard.power || 1) * 0.5;
      var dRoll = Math.random() * (enemyCard.toughness || 1) + (enemyCard.toughness || 1) * 0.5 + strangeBonus;"""

if OLD_COMBAT in gp:
    gp = gp.replace(OLD_COMBAT, NEW_COMBAT)
    print("OK: combat scaled by strangeness")
else:
    print("WARN: could not find combat roll code")

with open(GAMEPLAY_FILE, "w") as f:
    f.write(gp)


# ═══ 3. ADD /spectrum COMMAND ═══

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

SPECTRUM_CMD = r"""      if (cmd === 'spectrum' || cmd === 'gradient') {
        addEntry('system', '\u2588 spectrum');
        if (window._cosmicFlavor) {
          window._cosmicFlavor.updateFromFeeds();
          addEntry('chipmunk', window._cosmicFlavor.spectrumView());
          if (window._signalRelay) {
            var fs = window._cosmicFlavor.feedStrangeness();
            window._signalRelay.send('flavor_spectrum', { feeds: fs });
          }
        } else {
          addEntry('chipmunk', '<span class="dim">flavor engine loading\u2026</span>');
        }
        return;
      }
      if (cmd === 'wobble') {
        addEntry('system', '\u223f wobble');
        if (window._cosmicFlavor && window._cosmicView) {
          window._cosmicView.show();
          window._cosmicFlavor.startOrbitWobble();
          addEntry('chipmunk',
            '<span style="color:#a371f7">\u223f ORBIT WOBBLE ON</span>\n' +
            '<span class="dim">purple planets drift outward, green planets drift inward\n' +
            'the membrane breathes by strangeness</span>');
        }
        return;
      }
"""

# Insert before the flavor commands
flavor_marker = "      // \u2550\u2550\u2550 FLAVOR / SPIN / SORT COMMANDS \u2550\u2550\u2550"
if flavor_marker in cmd:
    cmd = cmd.replace(flavor_marker, SPECTRUM_CMD + flavor_marker)
    print("OK: /spectrum and /wobble commands added")
else:
    print("ERROR: could not find FLAVOR marker")

# Update help text
OLD_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /strategy /battle /relay /signal /cosmos /surfaces /parlor /scene /go /talk /explore /trail"
NEW_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /wobble /strategy /battle /relay /cosmos /surfaces /parlor /scene /go /talk /explore /trail"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help text updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

print(f"chipmunk-commands.js: {cmd.count(chr(10))} lines")
