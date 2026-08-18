if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const targets = document.querySelectorAll(".reveal");

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  targets.forEach((target) => {
    target.classList.add("reveal-ready");
    io.observe(target);
  });
}

document.querySelectorAll('a[href^="http"]').forEach((link) => {
  if (link.hostname !== window.location.hostname) {
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  }
});

const navToggle = document.getElementById("nav-toggle");
const navLinks = document.getElementById("navlinks");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    const open = navLinks.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  });
}
