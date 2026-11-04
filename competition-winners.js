
document.addEventListener("DOMContentLoaded", function () {
  // Only run on individual competition-season pages.
  const match = window.location.pathname.match(
    /\/competitions\/[a-z0-9-]+-\d{4}-\d{2}\.html$/
  );
  if (!match) return;

  const main = document.querySelector("main");
  const heading = main?.querySelector("h1");
  if (!heading) return;

  let winnerLink = null;

  // League competitions: use the champions in the final table.
  const finalTable = main.querySelector("table.league-table");
  if (finalTable) {
    const rows = finalTable.querySelectorAll("tbody tr");
    for (const row of rows) {
      const position = row.querySelector("td.pos");
      const club = row.querySelector("td.club a");

      if (position?.textContent.trim() === "1" && club) {
        winnerLink = club;
        break;
      }
    }
  }

  // Knockout competitions: use the winner of the final tie.
  if (!winnerLink) {
    const bracket = main.querySelector("svg.knockout-svg");
    if (bracket) {
      const cards = [...bracket.querySelectorAll("g.tie-card")];
      const finalCard = cards.reduce((rightmost, card) => {
        const x = Number(card.querySelector("rect.tie-box")?.getAttribute("x"));
        const previousX = Number(
          rightmost?.querySelector("rect.tie-box")?.getAttribute("x")
        );
        return !rightmost || x > previousX ? card : rightmost;
      }, null);

      winnerLink = finalCard?.querySelector("a:has(text.team.winner)") || null;
    }
  }

  if (!winnerLink) return;

  const name = winnerLink.querySelector("text")?.textContent.trim()
    || winnerLink.textContent.trim();
  const href = winnerLink.getAttribute("href");
  if (!name || !href) return;

  const clubSlug = href.split("/").pop().replace(/\.html$/, "");
  const crestPath = "../clubs/crests/" + clubSlug + ".png";

  const panel = document.createElement("section");
  panel.className = "competition-winner-panel";

  const crest = document.createElement("img");
  crest.src = crestPath;
  crest.alt = name + " crest";
  crest.className = "competition-winner-crest";
  crest.onerror = function () { crest.style.display = "none"; };

  const info = document.createElement("div");
  const label = document.createElement("div");
  label.className = "competition-winner-label";
  label.textContent = finalTable ? "LEAGUE CHAMPIONS" : "CUP WINNERS";

  const link = document.createElement("a");
  link.className = "competition-winner-name";
  link.href = "../clubs/" + clubSlug + ".html";
  link.textContent = name.replace(/\s*\(p\)$/, "");

  info.append(label, link);
  panel.append(crest, info);

  const switcher = main.querySelector(".season-switcher");
  (switcher || heading).insertAdjacentElement("afterend", panel);
});
