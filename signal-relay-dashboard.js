// signal-relay-dashboard.js — live relay dashboard for signal.primals.eco
// Shows relay pulse, event stream, heartbeat status, feed status.
// Loaded after signal-relay.js on signal page.
(function() {
  'use strict';

  var relay = window._signalRelay;
  if (!relay) return;

  var _el = null;
  var _pollTimer = null;
  var _eventLog = [];
  var MAX_LOG = 50;

  function mount() {
    var anchor = document.querySelector('.site-main') || document.querySelector('main') || document.body;
    if (!anchor) return;

    _el = document.createElement('section');
    _el.id = 'relay-dashboard';
    _el.innerHTML = [
      '<hr>',
      '<h2 id="relay-dashboard-h">Signal Relay \u2014 Central Nervous System</h2>',
      '<div style="background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:1.5em;margin:1em 0">',
      '  <div style="display:flex;gap:2em;flex-wrap:wrap;margin-bottom:1em">',
      '    <div id="relay-pulse" style="flex:1;min-width:200px">',
      '      <div style="color:#8b949e;text-transform:uppercase;font-size:.8em;margin-bottom:.5em">Relay Pulse</div>',
      '      <div id="relay-status" style="font-family:monospace;font-size:1.1em;color:#3fb950">connecting...</div>',
      '    </div>',
      '    <div id="relay-heartbeat" style="flex:1;min-width:200px">',
      '      <div style="color:#8b949e;text-transform:uppercase;font-size:.8em;margin-bottom:.5em">Chipmunk Heartbeat</div>',
      '      <div id="relay-hb-status" style="font-family:monospace;font-size:1.1em;color:#f0e68c">\u2026</div>',
      '    </div>',
      '    <div id="relay-sources" style="flex:1;min-width:200px">',
      '      <div style="color:#8b949e;text-transform:uppercase;font-size:.8em;margin-bottom:.5em">Sources</div>',
      '      <div id="relay-src-list" style="font-family:monospace;font-size:.9em;color:#c9d1d9">\u2026</div>',
      '    </div>',
      '    <div id="relay-flavor" style="flex:1;min-width:200px">',
      '      <div style="color:#8b949e;text-transform:uppercase;font-size:.8em;margin-bottom:.5em">\u2728 Membrane Flavor</div>',
      '      <div id="relay-strangeness" style="font-family:monospace;font-size:1.1em;color:#bc8cff">\u2026</div>',
      '    </div>',
      '  </div>',
      '  <div style="color:#8b949e;text-transform:uppercase;font-size:.8em;margin-bottom:.5em">Event Stream</div>',
      '  <div id="relay-event-stream" style="background:#161b22;border:1px solid #21262d;border-radius:4px;max-height:300px;overflow-y:auto;padding:.8em;font-family:monospace;font-size:.85em;line-height:1.6;color:#8b949e">',
      '    waiting for events\u2026',
      '  </div>',
      '</div>',
    ].join('\n');

    var insertBefore = document.getElementById('the-button');
    if (insertBefore) {
      insertBefore.parentNode.insertBefore(_el, insertBefore);
    } else {
      var firstHr = anchor.querySelector('hr');
      if (firstHr) {
        firstHr.parentNode.insertBefore(_el, firstHr);
      } else {
        anchor.appendChild(_el);
      }
    }
  }

  function updatePulse() {
    relay.pulse().then(function(p) {
      if (!p) return;

      var statusEl = document.getElementById('relay-status');
      if (statusEl) {
        var dot = p.up ? '\u25cf' : '\u25cb';
        statusEl.innerHTML = '<span style="color:' + (p.up ? '#3fb950' : '#f85149') + '">' + dot + '</span> ' +
          (p.up ? 'ONLINE' : 'OFFLINE') +
          ' \u00b7 ' + (p.events_today || 0) + ' events today';
      }

      var hbEl = document.getElementById('relay-hb-status');
      if (hbEl && p.heartbeat) {
        var hb = p.heartbeat;
        var piWake = (hb.pi_wake / Math.PI).toFixed(2);
        var stateColors = { awake:'#3fb950', drowsy:'#f0e68c', resting:'#f0883e', asleep:'#6e7681' };
        hbEl.innerHTML = '<span style="color:' + (stateColors[hb.state] || '#8b949e') + '">\u2665 ' + hb.state + '</span>' +
          ' \u00b7 energy=' + (hb.energy || 0).toFixed(3) +
          ' \u00b7 piWake=' + piWake + '\u03c0' +
          ' \u00b7 cycle=' + (hb.cycle || 0);
      }

      // Flavor strangeness gauge
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
            flavorBar += '<span style="color:#f0e68c">\u25c6</span>';
          } else {
            flavorBar += '<span style="color:rgb(' + r + ',' + g + ',' + b + ')">\u2500</span>';
          }
        }
        var label = s < 0.3 ? 'familiar' : s < 0.5 ? 'balanced' : s < 0.7 ? 'shifting' : 'strange';
        var fc = s < 0.3 ? '#3fb950' : s < 0.5 ? '#58a6ff' : s < 0.7 ? '#bc8cff' : '#a371f7';
        flavorEl.innerHTML = flavorBar + '<br><span style="color:' + fc + '">' + label + '</span> ' + (s * 100).toFixed(1) + '%';
      }

      var srcEl = document.getElementById('relay-src-list');
      if (srcEl && p.sources) {
        var srcLines = Object.keys(p.sources).map(function(k) {
          return k + ': ' + p.sources[k];
        });
        srcEl.textContent = srcLines.join(' \u00b7 ') || 'none';
      }
    });
  }

  function updateStream() {
    fetch('/signal/stream', { cache: 'no-store' })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (!data || !data.events) return;

        var streamEl = document.getElementById('relay-event-stream');
        if (!streamEl) return;

        _eventLog = data.events.slice(-MAX_LOG);

        var html = _eventLog.map(function(ev) {
          var ts = ev.ts ? ev.ts.substring(11, 19) : '??:??:??';
          var typeColors = {
            heartbeat: '#6e7681',
            surface_visit: '#3fb950',
            scene_transition: '#a371f7',
            discovery: '#f0e68c',
            combat: '#e85d3a',
            card_draw: '#58a6ff',
            card_play: '#f0883e',
            territory_claim: '#3fb950',
            npc_interaction: '#bc8cff',
            ability_unlock: '#d29922',
            test: '#484f58',
            flavor_spin: '#a371f7',
            flavor_sort: '#bc8cff',
            flavor_search: '#a371f7',
            flavor_spectrum: '#bc8cff',
            sing: '#f0e68c',
            pollinate: '#3fb950',
          };
          var color = typeColors[ev.type] || '#8b949e';

          var detail = '';
          if (ev.data) {
            if (ev.data.content) detail = ' \u2014 ' + ev.data.content.substring(0, 80);
            else if (ev.data.surface) detail = ' \u2014 ' + ev.data.surface;
            else if (ev.data.msg) detail = ' \u2014 ' + ev.data.msg;
            else if (ev.data.action) detail = ' \u2014 ' + ev.data.action;
          }

          return '<span style="color:#484f58">' + ts + '</span> ' +
            '<span style="color:' + color + '">[' + ev.type + ']</span> ' +
            '<span style="color:#8b949e">' + (ev.source || '?') + '</span>' +
            detail;
        }).reverse().join('\n');

        streamEl.innerHTML = html || 'no events yet';
      }).catch(function() {});
  }

  function startPolling() {
    updatePulse();
    updateStream();
    _pollTimer = setInterval(function() {
      updatePulse();
      updateStream();
    }, 5000);
  }

  mount();
  setTimeout(startPolling, 1000);
})();
