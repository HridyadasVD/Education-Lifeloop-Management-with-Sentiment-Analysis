(function () {
  const toggle = document.querySelector("[data-nav-toggle]");
  const links = document.querySelector("[data-nav-links]");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("is-open");
    });
  }

  const revealItems = document.querySelectorAll(
    ".course-card, .exam-card, .path-card, .stat-card, .path-step, .reveal"
  );

  if (!("IntersectionObserver" in window) || revealItems.length === 0) {
    revealItems.forEach(function (el) {
      el.classList.add("is-visible");
    });
    return;
  }

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  revealItems.forEach(function (el, index) {
    el.style.transitionDelay = Math.min(index * 0.05, 0.35) + "s";
    observer.observe(el);
  });
})();
