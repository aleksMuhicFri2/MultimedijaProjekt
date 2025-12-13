export function parseSloveniaSvg(svgText) {
  const parser = new DOMParser();
  const svgDoc = parser.parseFromString(svgText, "image/svg+xml");

  return Array.from(svgDoc.querySelectorAll("g[id^='obc_']")).map((gEl) => {
    const rawId = gEl.getAttribute("id");
    const code = rawId.replace("obc_", "").padStart(3, "0");

    const dList = Array.from(
      gEl.querySelectorAll("path"),
      (p) => p.getAttribute("d")
    ).filter(Boolean);

    return { code, dList };
  });
}
