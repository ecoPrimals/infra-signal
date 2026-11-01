#!/usr/bin/env python3
"""Flavor layer 3: particles, aura, contagion, history, HUD tinting."""

# ═══ 1. EXTEND cosmic-flavor.js — particles, aura, contagion, history, tinting ═══

FLAVOR_FILE = "/opt/ecoPrimals/hud/site/public/js/cosmic-flavor.js"
with open(FLAVOR_FILE) as f:
    fv = f.read()

LAYER3_BLOCK = r"""
  // ═══ FLAVOR PARTICLES — drift up (purple) and down (green) in cosmic view ═══

  var _particles = [];
  var _particlesActive = false;
  var _particleGroup = null;
  var MAX_PARTICLES = 60;

  function _createParticle(svg, cx, cy) {
    var s = Math.random();
    var color = flavorHex(s);
    var x = cx + (Math.random() - 0.5) * 280;
    var y = cy + (Math.random() - 0.5) * 200;
    var speed = (s - 0.5) * 0.3;
    var drift = (Math.random() - 0.5) * 0.1;
    var size = 0.5 + Math.random() * 1.5;
    var opacity = 0.1 + Math.random() * 0.3;
    var life = 200 + Math.random() * 400;

    var c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    c.setAttribute('r', size.toFixed(1));
    c.setAttribute('fill', color);
    c.setAttribute('opacity', opacity.toFixed(2));
    c.setAttribute('cx', x.toFixed(1));
    c.setAttribute('cy', y.toFixed(1));

    return { el: c, x: x, y: y, vx: drift, vy: -speed, life: life, age: 0, s: s };
  }

  function startParticles() {
    if (_particlesActive) return;
    _particlesActive = true;

    var cv = window._cosmicView;
    if (!cv || !cv.getSvg || !cv.isVisible()) return;
    var svg = cv.getSvg();
    if (!svg) return;

    var dims = cv.dims || { cx: 450, cy: 320 };

    _particleGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    _particleGroup.setAttribute('id', 'flavor-particles');
    _particleGroup.setAttribute('opacity', '0.6');
    svg.appendChild(_particleGroup);

    for (var i = 0; i < MAX_PARTICLES; i++) {
      var p = _createParticle(svg, dims.cx, dims.cy);
      _particleGroup.appendChild(p.el);
      _particles.push(p);
    }

    _particleLoop();
  }

  function stopParticles() {
    _particlesActive = false;
    if (_particleGroup && _particleGroup.parentNode) {
      _particleGroup.parentNode.removeChild(_particleGroup);
    }
    _particleGroup = null;
    _particles = [];
  }

  function _particleLoop() {
    if (!_particlesActive) return;

    var cv = window._cosmicView;
    if (!cv || !cv.isVisible()) { requestAnimationFrame(_particleLoop); return; }
    var dims = cv.dims || { cx: 450, cy: 320 };

    for (var i = 0; i < _particles.length; i++) {
      var p = _particles[i];
      p.age++;
      p.x += p.vx;
      p.y += p.vy;

      var fade = 1 - (p.age / p.life);
      if (fade <= 0 || p.y < dims.cy - 350 || p.y > dims.cy + 350) {
        if (_particleGroup) _particleGroup.removeChild(p.el);
        var np = _createParticle(null, dims.cx, dims.cy);
        if (_particleGroup) _particleGroup.appendChild(np.el);
        _particles[i] = np;
        continue;
      }

      p.el.setAttribute('cx', p.x.toFixed(1));
      p.el.setAttribute('cy', p.y.toFixed(1));
      p.el.setAttribute('opacity', (fade * 0.3).toFixed(2));
    }

    requestAnimationFrame(_particleLoop);
  }

  // ═══ FLAVOR AURA — strangeness ring around "you are here" position ═══

  function flavorAura() {
    var yah = window._youAreHere;
    if (!yah || !yah.observe) return null;
    var self = yah.observe();
    if (!self) return null;

    var catS = CAT_STRANGENESS[self.category] || 0.5;
    var depthFactor = Math.min(1, self.depth * 2);
    var aura = catS * 0.6 + depthFactor * 0.2 + (self.breadth > 5 ? 0.1 : 0) + (self.dwellMin > 5 ? 0.1 : 0);
    aura = Math.max(0, Math.min(1, aura));

    var fc = flavorHex(aura);
    var label = aura < 0.3 ? 'green aura \u2014 familiar ground' :
                aura < 0.5 ? 'balanced aura' :
                aura < 0.7 ? 'shifting purple' :
                'deep purple aura \u2014 strange territory';

    return {
      strangeness: aura,
      color: fc,
      label: label,
      bar: flavorBar(aura),
      category: self.category,
      epitope: self.epitope,
      depth: self.depth,
      breadth: self.breadth,
    };
  }

  // ═══ FLAVOR CONTAGION — visiting a surface shifts your hand's flavor ═══

  var _contagionHistory = [];
  var MAX_CONTAGION = 20;

  function contagion(surfaceKey) {
    var s = surfaceStrangeness(surfaceKey);
    _contagionHistory.push({ surface: surfaceKey, strangeness: s, ts: Date.now() });
    if (_contagionHistory.length > MAX_CONTAGION) _contagionHistory.shift();

    var cc = window._cosmicCards;
    if (cc && cc.hand().length > 0) {
      var hand = cc.hand();
      var closest = null, minDist = 2;
      hand.forEach(function(c) {
        var cs = cardStrangeness(c);
        var dist = Math.abs(cs - s);
        if (dist < minDist) { minDist = dist; closest = c; }
      });
      if (closest) {
        closest._contagion = s;
        closest._contagionFrom = surfaceKey;
      }
    }

    return { surface: surfaceKey, strangeness: s };
  }

  function contagionTrail() {
    if (_contagionHistory.length === 0) return 'no contagion trail yet';
    var lines = ['<span style="color:#bc8cff">CONTAGION TRAIL</span> \u2014 surfaces touched, flavor left behind'];
    _contagionHistory.forEach(function(c) {
      var age = Math.round((Date.now() - c.ts) / 60000);
      lines.push('  ' + flavorBar(c.strangeness) + ' ' + c.surface + ' (' + (c.strangeness * 100).toFixed(0) + '%) ' + age + 'm ago');
    });
    var avg = 0;
    _contagionHistory.forEach(function(c) { avg += c.strangeness; });
    avg /= _contagionHistory.length;
    lines.push('\naverage trail: ' + flavorBar(avg) + ' <span style="color:' + flavorHex(avg) + '">' + (avg * 100).toFixed(1) + '%</span>');
    return lines.join('\n');
  }

  // ═══ STRANGENESS HISTORY — sparkline over heartbeat cycles ═══

  var _strangenessHistory = [];
  var MAX_HISTORY = 60;

  function recordStrangeness(value) {
    _strangenessHistory.push({ value: value, ts: Date.now() });
    if (_strangenessHistory.length > MAX_HISTORY) _strangenessHistory.shift();
  }

  function strangenessSparkline() {
    if (_strangenessHistory.length < 2) return '<span class="dim">not enough data for sparkline</span>';

    var chars = ['\u2581', '\u2582', '\u2583', '\u2584', '\u2585', '\u2586', '\u2587', '\u2588'];
    var min = 1, max = 0;
    _strangenessHistory.forEach(function(h) {
      if (h.value < min) min = h.value;
      if (h.value > max) max = h.value;
    });
    var range = max - min || 0.01;

    var spark = '';
    _strangenessHistory.forEach(function(h) {
      var idx = Math.round(((h.value - min) / range) * (chars.length - 1));
      var color = flavorHex(h.value);
      spark += '<span style="color:' + color + '">' + chars[idx] + '</span>';
    });

    var latest = _strangenessHistory[_strangenessHistory.length - 1].value;
    var first = _strangenessHistory[0].value;
    var trend = latest > first + 0.05 ? '\u2197 drifting purple' :
                latest < first - 0.05 ? '\u2198 settling green' : '\u2192 stable';

    return spark + '\n<span class="dim">' + _strangenessHistory.length + ' readings \u00b7 ' + trend + '</span>';
  }

  // Poll heartbeat for strangeness history
  function _pollStrangeness() {
    if (!window._signalRelay) return;
    window._signalRelay.pulse().then(function(p) {
      if (p && p.heartbeat && p.heartbeat.strangeness !== undefined) {
        recordStrangeness(p.heartbeat.strangeness);
      }
    }).catch(function() {});
  }
  setInterval(_pollStrangeness, 30000);
  setTimeout(_pollStrangeness, 5000);

  // ═══ HUD TINTING — shift the page itself by membrane strangeness ═══

  var _tintActive = false;

  function startTinting() {
    _tintActive = true;
    _tintLoop();
  }

  function stopTinting() {
    _tintActive = false;
    document.documentElement.style.removeProperty('--flavor-hue');
    var cards = document.querySelectorAll('.card-panel, .investigate-card, .entity-card');
    for (var i = 0; i < cards.length; i++) {
      cards[i].style.removeProperty('border-color');
    }
  }

  function _tintLoop() {
    if (!_tintActive) return;

    var s = _feedStrangeness.membrane;
    if (s === undefined) s = 0.5;

    var hue = Math.round(120 + s * 180);
    document.documentElement.style.setProperty('--flavor-hue', hue);

    var borderColor = flavorHex(s);
    var memStatus = document.querySelector('.membrane-status, .hud-live');
    if (memStatus) {
      memStatus.style.borderLeftColor = borderColor;
    }

    var footerEl = document.querySelector('.hud-footer, footer');
    if (footerEl) {
      footerEl.style.borderTopColor = borderColor;
    }

    setTimeout(_tintLoop, 10000);
  }

"""

# Insert before the export block
export_marker = "  // \u2550\u2550\u2550 EXPORT \u2550\u2550\u2550"
if export_marker in fv:
    fv = fv.replace(export_marker, LAYER3_BLOCK + "\n" + export_marker)
    print("OK: layer 3 block inserted")
else:
    print("ERROR: could not find EXPORT marker")

# Add new exports
OLD_EXP = """    // wobble
    startOrbitWobble: startOrbitWobble,
    stopOrbitWobble: stopOrbitWobble,
  };"""

NEW_EXP = """    // wobble
    startOrbitWobble: startOrbitWobble,
    stopOrbitWobble: stopOrbitWobble,
    // particles
    startParticles: startParticles,
    stopParticles: stopParticles,
    // aura
    flavorAura: flavorAura,
    // contagion
    contagion: contagion,
    contagionTrail: contagionTrail,
    // history
    recordStrangeness: recordStrangeness,
    strangenessSparkline: strangenessSparkline,
    // tinting
    startTinting: startTinting,
    stopTinting: stopTinting,
  };"""

if OLD_EXP in fv:
    fv = fv.replace(OLD_EXP, NEW_EXP)
    print("OK: new exports added")
else:
    print("ERROR: could not find old exports")

with open(FLAVOR_FILE, "w") as f:
    f.write(fv)
print(f"cosmic-flavor.js: {fv.count(chr(10))} lines")


# ═══ 2. ADD COMMANDS — /particles /aura /contagion /sparkline /tint ═══

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

NEW_CMDS = r"""      if (cmd === 'particles' || cmd === 'particle' || cmd === 'dust') {
        addEntry('system', '\u2728 flavor particles');
        if (window._cosmicFlavor && window._cosmicView) {
          window._cosmicView.show();
          window._cosmicFlavor.startParticles();
          addEntry('chipmunk',
            '<span style="color:#a371f7">\u2728 FLAVOR PARTICLES ON</span>\n' +
            '<span class="dim">purple drifts up, green settles down\n' +
            'the membrane breathes in color</span>');
        }
        return;
      }
      if (cmd === 'aura') {
        addEntry('system', '\u25c9 flavor aura');
        if (window._cosmicFlavor) {
          var a = window._cosmicFlavor.flavorAura();
          if (a) {
            addEntry('chipmunk',
              '\u25c9 ' + a.bar + '\n' +
              '<span style="color:' + a.color + '">' + a.label + '</span> (' + (a.strangeness * 100).toFixed(1) + '%)\n' +
              'you are <span style="color:' + a.color + '">' + a.epitope + '</span> in ' + a.category +
              ' \u00b7 depth=' + a.depth.toFixed(3) + ' \u00b7 breadth=' + a.breadth +
              '\n<span class="dim">your aura is the flavor of where you stand</span>');
          } else {
            addEntry('chipmunk', '<span class="dim">no position data yet \u2014 browse a surface first</span>');
          }
        }
        return;
      }
      if (cmd === 'contagion' || cmd === 'trail' || cmd === 'touched') {
        addEntry('system', '\u2022 contagion trail');
        if (window._cosmicFlavor) {
          addEntry('chipmunk', window._cosmicFlavor.contagionTrail());
        }
        return;
      }
      if (cmd === 'sparkline' || cmd === 'history' || cmd === 'trend') {
        addEntry('system', '\u2581\u2583\u2585\u2587 sparkline');
        if (window._cosmicFlavor) {
          window._cosmicFlavor.updateFromFeeds();
          var spark = window._cosmicFlavor.strangenessSparkline();
          addEntry('chipmunk',
            '<span style="color:#bc8cff">STRANGENESS OVER TIME</span>\n' + spark);
        }
        return;
      }
      if (cmd === 'tint' || cmd === 'tinting') {
        addEntry('system', '\u2728 tint');
        if (window._cosmicFlavor) {
          window._cosmicFlavor.startTinting();
          addEntry('chipmunk',
            '<span style="color:#a371f7">\u2728 HUD TINTING ON</span>\n' +
            '<span class="dim">the page shifts color by membrane strangeness</span>');
        }
        return;
      }
"""

# Insert before the spectrum commands
spectrum_marker = r"""      if (cmd === 'spectrum' || cmd === 'gradient') {"""
if spectrum_marker in cmd:
    cmd = cmd.replace(spectrum_marker, NEW_CMDS + spectrum_marker)
    print("OK: particle/aura/contagion/sparkline/tint commands added")
else:
    print("ERROR: could not find spectrum marker")

# Update help
OLD_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /wobble /strategy /battle /relay /cosmos /surfaces /parlor /scene /go /talk /explore /trail"
NEW_HELP = "/play /draw /deck /spin /sort /flavor /purple /green /spectrum /particles /aura /sparkline /wobble /tint /strategy /battle /relay /cosmos /parlor /scene /go /talk /explore /trail"

if OLD_HELP in cmd:
    cmd = cmd.replace(OLD_HELP, NEW_HELP)
    print("OK: help text updated")

with open(CMD_FILE, "w") as f:
    f.write(cmd)
print(f"chipmunk-commands.js: {cmd.count(chr(10))} lines")


# ═══ 3. WIRE CONTAGION INTO SURFACE NAVIGATION ═══

SURF_FILE = "/opt/ecoPrimals/hud/site/public/js/cosmic-surfaces.js"
with open(SURF_FILE) as f:
    sf = f.read()

# Find the navigate function's relay send
OLD_NAV = """      window._signalRelay.send('surface_visit', {"""
NEW_NAV = """      if (window._cosmicFlavor) {
        window._cosmicFlavor.contagion(surfaceName);
      }
      window._signalRelay.send('surface_visit', {"""

if OLD_NAV in sf:
    sf = sf.replace(OLD_NAV, NEW_NAV, 1)
    print("OK: contagion wired into surface navigation")
else:
    print("WARN: could not find navigate relay send")

with open(SURF_FILE, "w") as f:
    f.write(sf)


# ═══ 4. ADD FLAVOR AURA TO "YOU ARE HERE" COMMAND ═══

OLD_YAH = r"""            '\n<span class="dim">\ud83d\udd12 only you can see this. computed in your browser. nothing stored on our server.</span>');"""

NEW_YAH = r"""            '\n<span class="dim">\ud83d\udd12 only you can see this. computed in your browser. nothing stored on our server.</span>');
          if (window._cosmicFlavor) {
            var aura = window._cosmicFlavor.flavorAura();
            if (aura) {
              addEntry('chipmunk', '\u25c9 flavor aura: ' + aura.bar + ' <span style="color:' + aura.color + '">' + aura.label + '</span> (' + (aura.strangeness * 100).toFixed(1) + '%)');
            }
          }"""

if OLD_YAH in cmd:
    # We already wrote cmd above, need to re-read
    pass

# Actually let's do it on the file we just wrote
with open(CMD_FILE) as f:
    cmd2 = f.read()

if OLD_YAH in cmd2:
    cmd2 = cmd2.replace(OLD_YAH, NEW_YAH)
    with open(CMD_FILE, "w") as f:
        f.write(cmd2)
    print("OK: flavor aura added to 'you are here' command")
    print(f"chipmunk-commands.js: {cmd2.count(chr(10))} lines (final)")
else:
    print("WARN: could not find you-are-here text marker")


# ═══ 5. ADD STRANGENESS HISTORY TO RELAY ═══

RELAY_FILE = "/opt/membrane/signal-relay.py"
with open(RELAY_FILE) as f:
    rl = f.read()

# Add strangeness history list
OLD_INIT_STATE = '"strangeness": 0.5,'
NEW_INIT_STATE = '"strangeness": 0.5, "strangeness_history": [],'

if OLD_INIT_STATE in rl:
    rl = rl.replace(OLD_INIT_STATE, NEW_INIT_STATE, 1)
    print("OK: strangeness_history added to relay state")

# Record history each heartbeat
OLD_SET_STRANGE = 'h["strangeness"] = round(strangeness, 4)'
NEW_SET_STRANGE = """h["strangeness"] = round(strangeness, 4)
            h["strangeness_history"].append(round(strangeness, 4))
            if len(h["strangeness_history"]) > 60:
                h["strangeness_history"] = h["strangeness_history"][-60:]"""

if OLD_SET_STRANGE in rl:
    rl = rl.replace(OLD_SET_STRANGE, NEW_SET_STRANGE)
    print("OK: strangeness history tracking added")

# Add history to pulse response
OLD_PULSE_STRANGE = '"strangeness": h.get("strangeness", 0.5),'
NEW_PULSE_STRANGE = '"strangeness": h.get("strangeness", 0.5),\n                    "strangeness_history": h.get("strangeness_history", [])[-20:],'

if OLD_PULSE_STRANGE in rl:
    rl = rl.replace(OLD_PULSE_STRANGE, NEW_PULSE_STRANGE, 1)
    print("OK: strangeness history added to pulse")

with open(RELAY_FILE, "w") as f:
    f.write(rl)
print(f"signal-relay.py: {rl.count(chr(10))} lines")
