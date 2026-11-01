#!/usr/bin/env python3
"""Insert flavor/spin/sort commands into chipmunk-commands.js on golgi."""

FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"

NEW_COMMANDS = r"""      // ═══ FLAVOR / SPIN / SORT COMMANDS ═══
      if (cmd === 'flavor' || cmd === 'flavour' || cmd === 'strangeness') {
        addEntry('system', '\u2728 flavor map');
        if (window._cosmicFlavor) {
          addEntry('chipmunk', window._cosmicFlavor.flavorMapView());
        } else {
          addEntry('chipmunk', '<span class="dim">flavor engine loading\u2026</span>');
        }
        return;
      }
      if (cmd === 'spin') {
        addEntry('system', '\u27f3 spin');
        if (window._cosmicFlavor) {
          var p = window._cosmicFlavor.spin();
          addEntry('chipmunk',
            '<span style="color:#a371f7">\u27f3 SPIN</span> perspective: <span style="color:#f0e68c">' + p.name + '</span>\n' +
            p.desc + '\n' +
            window._cosmicFlavor.sortedHandView());
        } else {
          addEntry('chipmunk', '<span class="dim">flavor engine loading\u2026</span>');
        }
        return;
      }
      if (cmd === 'sort' || cmd === 'sorted') {
        addEntry('system', '\u2195 sort');
        if (window._cosmicFlavor) {
          addEntry('chipmunk', window._cosmicFlavor.sortedHandView());
        } else if (window._chipmunkMind && window._chipmunkMind.showSortDeck) {
          window._chipmunkMind.showSortDeck();
        } else {
          addEntry('chipmunk', '<span class="dim">sort loading\u2026</span>');
        }
        return;
      }
      if (cmd === 'purple' || cmd === 'strange') {
        addEntry('system', '\u2b06 purple search');
        if (window._cosmicFlavor && window._cosmicCards) {
          window._cosmicCards.refreshFeeds().then(function() {
            var drawn = window._cosmicCards.draw(3);
            var all = drawn.concat(window._cosmicCards.hand());
            var sorted = all.sort(function(a, b) {
              return window._cosmicFlavor.cardStrangeness(b) - window._cosmicFlavor.cardStrangeness(a);
            });
            var top = sorted.slice(0, 5);
            var lines = ['<span style="color:#a371f7">\u2b06 SEARCHING FOR PURPLE</span> \u2014 the strangest things in the membrane'];
            top.forEach(function(c) {
              var s = window._cosmicFlavor.cardStrangeness(c);
              lines.push('  ' + window._cosmicFlavor.flavorBar(s) + ' ' + window._cosmicCards.cardLine(c) + ' <span class="dim">(' + (s*100).toFixed(0) + '% strange)</span>');
            });
            lines.push('\n<span class="dim">/spin to change perspective \u00b7 /flavor for full map</span>');
            addEntry('chipmunk', lines.join('\n'));
          });
        }
        return;
      }
      if (cmd === 'green' || cmd === 'base' || cmd === 'home' || cmd === 'nearby') {
        addEntry('system', '\u2b07 green search');
        if (window._cosmicFlavor && window._cosmicCards) {
          window._cosmicCards.refreshFeeds().then(function() {
            var drawn = window._cosmicCards.draw(2);
            var all = drawn.concat(window._cosmicCards.hand());
            var sorted = all.sort(function(a, b) {
              return window._cosmicFlavor.cardStrangeness(a) - window._cosmicFlavor.cardStrangeness(b);
            });
            var top = sorted.slice(0, 5);
            var lines = ['<span style="color:#3fb950">\u2b07 SEARCHING FOR GREEN</span> \u2014 the most familiar, base, nearby'];
            top.forEach(function(c) {
              var s = window._cosmicFlavor.cardStrangeness(c);
              lines.push('  ' + window._cosmicFlavor.flavorBar(s) + ' ' + window._cosmicCards.cardLine(c) + ' <span class="dim">(' + (s*100).toFixed(0) + '% strange)</span>');
            });
            lines.push('\n<span class="dim">/spin to change perspective \u00b7 /flavor for full map</span>');
            addEntry('chipmunk', lines.join('\n'));
          });
        }
        return;
      }
      if (cmd === 'flavorview' || cmd === 'flavortoggle') {
        addEntry('system', '\u2728 flavor view');
        if (window._cosmicFlavor && window._cosmicView) {
          window._cosmicView.show();
          var active = window._cosmicFlavor.toggleFlavor();
          addEntry('chipmunk',
            '<span style="color:' + (active ? '#a371f7' : '#3fb950') + '">\u2728 flavor overlay ' + (active ? 'ON' : 'OFF') + '</span>\n' +
            '<span class="dim">planets colored by strangeness: purple=unknown, green=familiar</span>');
        }
        return;
      }
"""

with open(FILE) as f:
    content = f.read()

# Insert before the relay commands
target = "      // \u2550\u2550\u2550 SIGNAL RELAY COMMANDS \u2550\u2550\u2550"
idx = content.find(target)
if idx < 0:
    print("ERROR: could not find SIGNAL RELAY COMMANDS marker")
    exit(1)

content = content[:idx] + NEW_COMMANDS + content[idx:]

# Update help text
old_help = "/play /draw /deck /cards /strategy /battle /relay /signal /cosmos /surfaces /gates /discover /parlor /scene /go /talk /ability /sing /pollinate /explore /trail"
new_help = "/play /draw /deck /spin /sort /flavor /purple /green /strategy /battle /relay /signal /cosmos /surfaces /parlor /scene /go /talk /explore /trail"
content = content.replace(old_help, new_help)

with open(FILE, "w") as f:
    f.write(content)

lines = content.count("\n")
print(f"OK: {lines} lines total")
