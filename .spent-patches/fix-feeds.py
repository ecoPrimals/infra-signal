#!/usr/bin/env python3
"""Fix updateFromFeeds to use cosmicSurfaces data methods."""

path = "/opt/ecoPrimals/hud/site/public/js/cosmic-flavor.js"
with open(path) as f:
    code = f.read()

OLD = """  function updateFromFeeds() {
    var cs = window._cosmicSurfaces;
    if (!cs || !cs.feeds) return;
    var feeds = cs.feeds();

    // Scan sweep sort — entities with sort classes get real-time scores
    if (feeds.scan) {
      var scan = feeds.scan;"""

NEW = """  function updateFromFeeds() {
    var cs = window._cosmicSurfaces;
    if (!cs) return;

    // Scan sweep sort — entities with sort classes get real-time scores
    var scanRaw = typeof cs.scanData === 'function' ? cs.scanData() : cs.scanData;
    if (scanRaw) {
      var scan = scanRaw;"""

if OLD in code:
    code = code.replace(OLD, NEW)
    print("OK: scan feed access fixed")
else:
    print("WARN: could not find old scan feed code")

OLD2 = """    // Topology — connection density affects strangeness
    if (feeds.topology) {
      var topo = feeds.topology;"""

NEW2 = """    // Topology — connection density affects strangeness
    var topoRaw = typeof cs.topoData === 'function' ? cs.topoData() : cs.topoData;
    if (topoRaw) {
      var topo = topoRaw;"""

if OLD2 in code:
    code = code.replace(OLD2, NEW2)
    print("OK: topo feed access fixed")

OLD3 = """    // Human data — S/N ratio affects strangeness
    if (feeds.human) {
      var human = feeds.human;"""

NEW3 = """    // Human data — S/N ratio affects strangeness
    var humanRaw = typeof cs.humanData === 'function' ? cs.humanData() : cs.humanData;
    if (humanRaw) {
      var human = humanRaw;"""

if OLD3 in code:
    code = code.replace(OLD3, NEW3)
    print("OK: human feed access fixed")

with open(path, "w") as f:
    f.write(code)

print(f"cosmic-flavor.js: {code.count(chr(10))} lines")
