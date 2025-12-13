
// parses municipality data from svg to build new structure for the html

export function parseSloveniaSvg(svgText) {
  const parser = new DOMParser();
  const svgDoc = parser.parseFromString(svgText, "image/svg+xml");

  return Array.from(svgDoc.querySelectorAll("g[id^='obc_']")).map((gEl) => {
    const rawId = gEl.getAttribute("id");
    const code = rawId?.replace("obc_", "").padStart(3, "0");

    let name = "Unknown";
    const anchor = gEl.closest("a[href]");
    if (anchor) {
      const href = anchor.getAttribute("href");
      const match = href?.match(/Občina[_\s](.+)/i);
      if (match) {
        name = decodeURIComponent(match[1].replace(/_/g, " "));
      }
    }

    const dList = Array.from(
      gEl.querySelectorAll("path"),
      (p) => p.getAttribute("d")
    ).filter(Boolean);

    return { code, name, dList };
  });
}
