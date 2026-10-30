(() => {
  const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (motionPreference.matches) return;

  const colors = ["#bd482f", "#17644e", "#d9a739", "#6487c1", "#a079ad"];
  const layer = document.createElement("div");
  layer.className = "confetti";
  layer.setAttribute("aria-hidden", "true");
  const pieceCount = 48;
  let remaining = pieceCount;

  for (let index = 0; index < pieceCount; index += 1) {
    const piece = document.createElement("span");
    piece.className = "confetti-piece";
    piece.style.setProperty("--left", `${Math.random() * 100}%`);
    piece.style.setProperty("--color", colors[index % colors.length]);
    piece.style.setProperty("--drift", `${Math.random() * 160 - 80}px`);
    piece.style.setProperty("--spin", `${Math.random() * 720 - 360}deg`);
    piece.style.setProperty("--duration", `${1600 + Math.random() * 600}ms`);
    piece.style.setProperty("--delay", `${Math.random() * 250}ms`);
    layer.append(piece);
  }

  function finishPiece() {
    remaining -= 1;
    if (remaining === 0) removeLayer();
  }
  function removeLayer() {
    layer.remove();
    motionPreference.removeEventListener("change", removeLayer);
  }
  layer.addEventListener("animationend", finishPiece);
  layer.addEventListener("animationcancel", finishPiece);
  motionPreference.addEventListener("change", removeLayer, { once: true });
  document.body.append(layer);
})();
