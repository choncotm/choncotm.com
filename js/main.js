if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const targets = document.querySelectorAll(".reveal");

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        entry.target.classList.toggle("is-visible", entry.isIntersecting);
      });
    },
    { threshold: 0.15 }
  );

  targets.forEach((target) => {
    target.classList.add("reveal-ready");
    io.observe(target);
  });
}
