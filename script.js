// Scroll-driven motion. Everything is tied to scroll position, so it moves
// exactly as fast as the visitor scrolls and reverses when they scroll back.
(function () {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const clamp = (v, min = 0, max = 1) => Math.min(max, Math.max(min, v));
  const ease = (t) => 1 - Math.pow(1 - t, 3);

  // Hero: sweep the old website away and reveal the new one
  const hero = document.querySelector(".hero");
  const copy = hero.querySelector(".hero-copy");
  const browser = hero.querySelector(".browser");
  const newSite = hero.querySelector(".new");
  const edge = hero.querySelector(".sweep-edge");
  const oldBits = [...hero.querySelectorAll("[data-old]")];

  function updateHero() {
    const scrolled = -hero.getBoundingClientRect().top;
    const travel = hero.offsetHeight - window.innerHeight;
    // On phones the text scrolls away first and the browser then sticks,
    // so the reveal only starts once the browser has stopped moving
    const start = getComputedStyle(browser).position === "sticky"
      ? copy.offsetTop + copy.offsetHeight - parseFloat(getComputedStyle(browser).top) + 40
      : 0;
    // Reveal runs over 75% of the remaining scroll, then holds
    const p = ease(clamp((scrolled - start) / ((travel - start) * 0.75)));
    const pct = p * 100;

    newSite.style.clipPath = `inset(0 ${100 - pct}% 0 0)`;
    edge.style.left = `${pct}%`;
    edge.style.opacity = p > 0 && p < 1 ? 1 : 0;

    // Each piece of the old site is pushed along and fades as the sweep reaches it
    oldBits.forEach((el, i) => {
      const local = clamp((p - i * 0.06) / 0.5);
      el.style.transform = `translateX(${local * 40}%) rotate(${local * (i % 2 ? 4 : -4)}deg)`;
      el.style.opacity = 1 - local;
    });

    browser.classList.toggle("is-after", p > 0.6);
  }

  // Sections: content sweeps in from the side as it arrives and sweeps away
  // and fades as it leaves the top of the screen
  const sweepers = [...document.querySelectorAll("[data-sweep]")];

  function updateSweepers() {
    const vh = window.innerHeight;
    const distance = Math.min(window.innerWidth * 0.12, 160);
    for (const el of sweepers) {
      const r = el.getBoundingClientRect();
      const dir = el.dataset.sweep === "right" ? 1 : -1;
      const enter = ease(clamp((vh - r.top) / (vh * 0.3)));
      const exit = ease(clamp((vh * 0.3 - r.bottom) / (vh * 0.3)));
      const x = dir * distance * (1 - enter) + dir * distance * 1.5 * exit;
      el.style.transform = `translate3d(${x}px, 0, 0)`;
      el.style.opacity = enter * (1 - exit);
    }
  }

  let ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      updateHero();
      if (!reduceMotion) updateSweepers();
      ticking = false;
    });
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();
})();
