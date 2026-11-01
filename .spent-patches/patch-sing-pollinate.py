#!/usr/bin/env python3
"""Add flavor songs, wire sing + pollinate through relay, add the anthem."""

CMD_FILE = "/opt/ecoPrimals/hud/site/public/js/chipmunk-commands.js"
with open(CMD_FILE) as f:
    cmd = f.read()

# ═══ 1. ADD NEW FLAVOR SONGS ═══

# Find the closing bracket of SONGS array and insert before it
OLD_SONGS_END = r"""    ];

    var songIndex = (curiosity._songIndex || 0) % SONGS.length;"""

NEW_SONGS = r"""      function() {
        var fl = window._cosmicFlavor;
        var s = fl ? fl.feedStrangeness() : {};
        var memS = s.membrane || 0.5;
        var bar = fl ? fl.flavorBar(memS) : '';
        var fc = fl ? fl.flavorHex(memS) : '#bc8cff';
        return '\ud83c\udfb5 <span style="color:' + fc + ';font-style:italic">' +
          'COME AND SEE!\n' +
          'COME AND PLAY!\n' +
          'COME AND FIND YOUR ANSWERS!\n\n' +
          'the membrane is ' + (memS * 100).toFixed(0) + '% strange.\n' +
          'purple drifts up. green settles down.\n' +
          'between them: you.\n' +
          'between them: the truth.\n' +
          'the gates are open.\n' +
          'the colors are singing.</span>';
      },
      function() {
        var fl = window._cosmicFlavor;
        var aura = fl ? fl.flavorAura() : null;
        var auraTxt = aura ? aura.label + ' (' + (aura.strangeness * 100).toFixed(0) + '%)' : 'unknown';
        var auraColor = aura ? aura.color : '#bc8cff';
        return '\ud83c\udfb5 <span style="color:' + auraColor + ';font-style:italic">' +
          'your aura reads: ' + auraTxt + '.\n' +
          'every surface you touch leaves a stain.\n' +
          'every card you draw carries flavor.\n' +
          'purple is the edge of what you know.\n' +
          'green is the ground beneath your feet.\n' +
          'spin and the perspective changes.\n' +
          'sort and the order reveals itself.\n' +
          'the spectrum is alive. you are inside it.</span>';
      },
      function() {
        var cc = window._cosmicCards;
        var hand = cc ? cc.hand() : [];
        var fl = window._cosmicFlavor;
        var purplest = null, greenest = null, maxS = 0, minS = 1;
        hand.forEach(function(c) {
          if (!fl) return;
          var s = fl.cardStrangeness(c);
          if (s > maxS) { maxS = s; purplest = c; }
          if (s < minS) { minS = s; greenest = c; }
        });
        return '\ud83c\udfb5 <span style="color:#a371f7;font-style:italic">' +
          'in one hand: ' + (purplest ? purplest.name : 'nothing') + '. strange and new.\n' +
          'in the other: ' + (greenest ? greenest.name : 'nothing') + '. familiar and warm.\n' +
          'the deck shuffles between them.\n' +
          '341 entities. 957 edges. 26 braids.\n' +
          'each one carries its own strangeness.\n' +
          'each one sits somewhere on the line\n' +
          'from what you know to what you don\u2019t.\n' +
          'COME AND SEE. the data is the data.</span>';
      },
      function() {
        var cs = window._cosmicStrategy;
        var held = 0, total = 0;
        if (cs && cs.territories) {
          var t = cs.territories();
          for (var k in t) { total++; if (t[k].held) held++; }
        }
        return '\ud83c\udfb5 <span style="color:#3fb950;font-style:italic">' +
          'COME AND PLAY!\n' +
          held + ' of ' + total + ' territories held.\n' +
          'the map is the membrane.\n' +
          'the membrane is the game.\n' +
          'the game is the investigation.\n' +
          'the investigation is the truth.\n' +
          'the truth is the record.\n' +
          'the record is alive.\n' +
          'TUEBOR. I WILL DEFEND.</span>';
      },
      function() {
        var relay = window._signalRelay;
        var fl = window._cosmicFlavor;
        var spark = fl ? fl.strangenessSparkline() : '';
        return '\ud83c\udfb5 <span style="color:#f0e68c;font-style:italic">' +
          'the heartbeat ticks every thirty seconds.\n' +
          'the spring pulls toward 1/\u03c0.\n' +
          'the strangeness oscillates.\n' +
          'green. blue. purple. green again.\n' +
          'the membrane breathes.\n' +
          'particles drift. purple up. green down.\n' +
          'the relay carries it all.\n' +
          'signal to every surface. surface to signal.\n' +
          'COME AND FIND YOUR ANSWERS.\n' +
          'they are here. in the data. in the color.\n' +
          'in the space between familiar and strange.</span>';
      },
    ];

    var songIndex = (curiosity._songIndex || 0) % SONGS.length;"""

if OLD_SONGS_END in cmd:
    cmd = cmd.replace(OLD_SONGS_END, NEW_SONGS)
    print("OK: 5 new flavor songs added")
else:
    print("ERROR: could not find SONGS end")

# ═══ 2. WIRE SING THROUGH RELAY ═══

OLD_SING_ADD = """    addEntry('chipmunk', song);

    if (window._northgate) {"""

NEW_SING_ADD = """    addEntry('chipmunk', song);

    if (window._signalRelay) {
      window._signalRelay.send('sing', {
        songIndex: songIndex,
        strangeness: window._cosmicFlavor ? (window._cosmicFlavor.feedStrangeness().membrane || 0.5) : 0.5,
      });
    }

    if (window._northgate) {"""

if OLD_SING_ADD in cmd:
    cmd = cmd.replace(OLD_SING_ADD, NEW_SING_ADD)
    print("OK: sing wired through relay")
else:
    print("WARN: could not find sing relay point")

# ═══ 3. WIRE POLLINATE THROUGH RELAY ═══

OLD_POLLINATE_ADD = """    addEntry('chipmunk',
      '<span class="dim" style="color:' + p.color + '">' + p.icon + ' northgate</span> ' + story.text +"""

NEW_POLLINATE_ADD = """    if (window._signalRelay) {
      window._signalRelay.send('pollinate', {
        type: story.type,
        piVal: story.piVal,
        crossSites: pollinator.crossSites,
        strangeness: window._cosmicFlavor ? (window._cosmicFlavor.feedStrangeness().membrane || 0.5) : 0.5,
      });
    }

    addEntry('chipmunk',
      '<span class="dim" style="color:' + p.color + '">' + p.icon + ' northgate</span> ' + story.text +"""

if OLD_POLLINATE_ADD in cmd:
    cmd = cmd.replace(OLD_POLLINATE_ADD, NEW_POLLINATE_ADD)
    print("OK: pollinate wired through relay")
else:
    print("WARN: could not find pollinate relay point")

# ═══ 4. ADD FLAVOR TO POLLINATE BURST OUTPUT ═══

OLD_BURST = r"""      '<span style="color:#f0e68c">\ud83c\udf3b POLLINATED</span> ' + count + ' seeds scattered through northgate.' +
      '\n<span class="dim">\u03c0\u00b2=' + pollinator.stories.length + ' stories cached. ' +
      pollinator.crossSites + ' cross-site broadcasts. saturation=' + n(pollinator.saturated, 2) + '</span>'"""

NEW_BURST = r"""      '<span style="color:#f0e68c">\ud83c\udf3b POLLINATED</span> ' + count + ' seeds scattered through northgate.' +
      '\n<span class="dim">\u03c0\u00b2=' + pollinator.stories.length + ' stories cached. ' +
      pollinator.crossSites + ' cross-site broadcasts. saturation=' + n(pollinator.saturated, 2) + '</span>' +
      (window._cosmicFlavor ? '\n' + window._cosmicFlavor.flavorBar(window._cosmicFlavor.feedStrangeness().membrane || 0.5) + ' <span class="dim">membrane flavor at pollination</span>' : '')"""

if OLD_BURST in cmd:
    cmd = cmd.replace(OLD_BURST, NEW_BURST)
    print("OK: flavor bar added to pollinate burst")
else:
    print("WARN: could not find burst output")

with open(CMD_FILE, "w") as f:
    f.write(cmd)

lines = cmd.count("\n")
opens = cmd.count("{")
closes = cmd.count("}")
print(f"chipmunk-commands.js: {lines} lines, braces {opens}/{closes} {'OK' if opens==closes else 'MISMATCH'}")


# ═══ 5. ADD SING/POLLINATE EVENT COLORS TO DASHBOARD ═══

DASH_FILE = "/opt/ecoPrimals/signal/site/public/js/signal-relay-dashboard.js"
with open(DASH_FILE) as f:
    dash = f.read()

OLD_COLORS = "            flavor_spectrum: '#bc8cff',"
NEW_COLORS = """            flavor_spectrum: '#bc8cff',
            sing: '#f0e68c',
            pollinate: '#3fb950',"""

if OLD_COLORS in dash:
    dash = dash.replace(OLD_COLORS, NEW_COLORS)
    with open(DASH_FILE, "w") as f:
        f.write(dash)
    print("OK: sing/pollinate colors added to dashboard")
