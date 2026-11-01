#!/usr/bin/env python3
"""Patch cardLine in cosmic-cards.js to include flavor pip."""

FILE = "/opt/ecoPrimals/hud/site/public/js/cosmic-cards.js"

with open(FILE) as f:
    content = f.read()

OLD = r"""  function cardLine(card) {
    var rarityMark = { common:'', uncommon:'\u2605', rare:'\u2605\u2605', mythic:'\u2605\u2605\u2605', legendary:'\u2606\u2606\u2606', boss:'\ud83d\udc80' };
    var mark = rarityMark[card.rarity] || '';
    var pt = (card.power !== undefined) ? ' ' + card.power + '/' + card.toughness : '';
    var costStr = card.cost ? ' (' + card.cost + ')' : '';
    return '<span style="color:' + (card.color || '#8b949e') + '">' + (card.icon || '') + card.name + '</span>' +
      pt + costStr + ' ' + mark + ' <span class="dim">[' + card.type + ']</span>';
  }"""

NEW = r"""  function cardLine(card) {
    var rarityMark = { common:'', uncommon:'\u2605', rare:'\u2605\u2605', mythic:'\u2605\u2605\u2605', legendary:'\u2606\u2606\u2606', boss:'\ud83d\udc80' };
    var mark = rarityMark[card.rarity] || '';
    var pt = (card.power !== undefined) ? ' ' + card.power + '/' + card.toughness : '';
    var costStr = card.cost ? ' (' + card.cost + ')' : '';
    var flavorPip = '';
    if (window._cosmicFlavor) {
      var s = window._cosmicFlavor.cardStrangeness(card);
      flavorPip = '<span style="color:' + window._cosmicFlavor.flavorHex(s) + '">\u25cf</span> ';
    }
    return flavorPip + '<span style="color:' + (card.color || '#8b949e') + '">' + (card.icon || '') + card.name + '</span>' +
      pt + costStr + ' ' + mark + ' <span class="dim">[' + card.type + ']</span>';
  }"""

if OLD in content:
    content = content.replace(OLD, NEW)
    with open(FILE, "w") as f:
        f.write(content)
    print("OK: cardLine patched with flavor pip")
else:
    print("ERROR: could not find cardLine")
