function sendEvent(payload) {
  const body = JSON.stringify(payload);
  if (navigator.sendBeacon) {
    navigator.sendBeacon("/api/track", new Blob([body], { type: "application/json" }));
  } else {
    fetch("/api/track", { method: "POST", body, headers: { "Content-Type": "application/json" }, keepalive: true });
  }
}

sendEvent({ type: "pageview", path: location.pathname });

document.addEventListener("click", (event) => {
  const link = event.target.closest("a[href]");
  if (!link) return;

  const href = link.getAttribute("href");
  sendEvent({ type: "click", path: location.pathname, target: href });
});
