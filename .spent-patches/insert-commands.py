#!/usr/bin/env python3
"""Insert new game commands into chipmunk-commands.js on golgi."""

FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"

NEW_COMMANDS = r"""      // ═══ SIGNAL RELAY COMMANDS ═══
      if (cmd === 'relay' || cmd === 'stream') {
        addEntry('system', '\ud83d\udce1 relay stream');
        if (window._signalRelay) {
          window._signalRelay.pulse().then(function(p) {
            if (!p) { addEntry('chipmunk', '<span class="dim">relay offline</span>'); return; }
            var hb = p.heartbeat || {};
            addEntry('chipmunk',
              '<span style="color:#3fb950">\ud83d\udce1 SIGNAL RELAY</span> ' + (p.up ? 'ONLINE' : 'OFFLINE') +
              '\nevents today: ' + (p.events_today || 0) +
              '\nsources: ' + JSON.stringify(p.sources || {}) +
              '\n<span style="color:#f0e68c">\u2665 heartbeat</span> energy=' + (hb.energy || 0).toFixed(3) +
              ' piWake=' + ((hb.pi_wake || 0) / Math.PI).toFixed(2) + '\u03c0 ' + (hb.state || '?') +
              ' cycle=' + (hb.cycle || 0) +
              '\n<span class="dim">relay keeps chipmunk alive 24/7 \u2014 no browser needed</span>');
          });
        } else {
          addEntry('chipmunk', '<span class="dim">relay SDK not loaded</span>');
        }
        return;
      }
      if (cmd === 'signal' || cmd === 'pulse') {
        addEntry('system', '\ud83d\udce1 signal pulse');
        if (window._signalRelay) {
          window._signalRelay.pulse().then(function(p) {
            if (!p) { addEntry('chipmunk', '<span class="dim">signal offline</span>'); return; }
            addEntry('chipmunk',
              '<span style="color:#8b949e">\ud83d\udce1 signal.primals.eco</span>\n' +
              'up: ' + p.up + '  events: ' + (p.events_today || 0) +
              '\nlast: ' + (p.last_event || 'none') +
              '\n<span class="dim">POST /signal/send \u00b7 GET /signal/stream \u00b7 GET /signal/pulse</span>');
          });
        }
        return;
      }
      // ═══ CARD GAME COMMANDS ═══
      if (cmd === 'deck' || cmd === 'hand') {
        addEntry('system', '\ud83c\udccf deck');
        if (window._cosmicCards) {
          addEntry('chipmunk', window._cosmicCards.handView());
        } else {
          addEntry('chipmunk', '<span class="dim">card engine loading\u2026</span>');
        }
        return;
      }
      if (cmd === 'draw') {
        addEntry('system', '\ud83c\udccf draw');
        if (window._cosmicCards) {
          window._cosmicCards.refreshFeeds().then(function() {
            var drawn = window._cosmicCards.draw(3);
            if (drawn.length === 0) {
              addEntry('chipmunk', '<span class="dim">hand full (7/7). play a card first.</span>');
            } else {
              var lines = ['<span style="color:#f0e68c">\ud83c\udccf DREW ' + drawn.length + ' CARDS</span>'];
              drawn.forEach(function(c) { lines.push('  ' + window._cosmicCards.cardLine(c)); });
              lines.push('<span class="dim">type /deck to see hand \u00b7 /play <n> to play \u00b7 /cards for all types</span>');
              addEntry('chipmunk', lines.join('\n'));
            }
          });
        }
        return;
      }
      if (cmd.indexOf('play ') === 0) {
        var playIdx = parseInt(cmd.split(' ')[1]);
        addEntry('system', '\ud83c\udccf play ' + playIdx);
        if (window._cosmicCards && !isNaN(playIdx)) {
          var result = window._cosmicCards.play(playIdx);
          if (!result) {
            addEntry('chipmunk', '<span class="dim">invalid card index. type /deck to see hand.</span>');
          } else if (result.error) {
            addEntry('chipmunk', '<span style="color:#f85149">' + result.error + '</span> (mana: ' + result.mana.toFixed(2) + ', cost: ' + result.cost.toFixed(2) + ')');
          } else {
            var encounter = window._cosmicGameplay ? window._cosmicGameplay.encounterFromCard(result.card) : null;
            addEntry('chipmunk',
              '<span style="color:#3fb950">\u25b6 PLAYED: ' + window._cosmicCards.cardLine(result.card) + '</span>' +
              '\nmana: ' + result.mana.toFixed(2) +
              (result.effect ? '\neffect: ' + result.effect : '') +
              (encounter && encounter.msg ? '\n<span style="color:#f0e68c">' + encounter.msg + '</span>' : '') +
              (typeof encounter === 'string' ? '\n<span style="color:#f0e68c">' + encounter + '</span>' : ''));
          }
        }
        return;
      }
      if (cmd === 'cards' || cmd === 'cardlist') {
        addEntry('system', '\ud83c\udccf all cards');
        if (window._cosmicCards) {
          addEntry('chipmunk', window._cosmicCards.allCardsView());
        }
        return;
      }
      // ═══ STRATEGY COMMANDS ═══
      if (cmd === 'strategy' || cmd === 'strat' || cmd === 'map') {
        addEntry('system', '\u2694 strategy');
        if (window._cosmicStrategy) {
          addEntry('chipmunk', window._cosmicStrategy.strategicView());
        } else {
          addEntry('chipmunk', '<span class="dim">strategy engine loading\u2026</span>');
        }
        return;
      }
      if (cmd === 'battle' || cmd === 'combat' || cmd === 'fight') {
        addEntry('system', '\u2694 battle');
        if (window._cosmicStrategy) {
          addEntry('chipmunk', window._cosmicStrategy.battleView());
        } else {
          addEntry('chipmunk', '<span class="dim">strategy engine loading\u2026</span>');
        }
        return;
      }
"""

with open(FILE) as f:
    content = f.read()

target = "      if (cmd === 'cosmos' || cmd === 'earth'"
idx = content.find(target)
if idx < 0:
    print("ERROR: could not find cosmos command")
    exit(1)

content = content[:idx] + NEW_COMMANDS + content[idx:]

old_help = "/play /explore /cosmos /surfaces /gates /discover /parlor /scene /sing /pollinate /wake /rest /sleep /energy /fleet /genome /scan /sieve /sort /trail /geo"
new_help = "/play /draw /deck /cards /strategy /battle /relay /signal /cosmos /surfaces /gates /discover /parlor /scene /go /talk /ability /sing /pollinate /explore /trail"
content = content.replace(old_help, new_help)

with open(FILE, "w") as f:
    f.write(content)

lines = content.count("\n")
print(f"OK: {lines} lines total")
