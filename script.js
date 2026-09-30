/* BellMitchell — smooth scroll and glide-in sections.
   Content is fully visible without JS; every animation only sets its starting
   state once GSAP has loaded, and reduced-motion users get the static page. */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  $$("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));

  /* ---------- Mobile menu ---------- */
  const menuBtn = $(".menu-btn");
  const menu = $("#nav-menu");
  let lenis = null;
  const setMenu = (open) => {
    menuBtn.setAttribute("aria-expanded", String(open));
    menu.classList.toggle("is-open", open);
    document.body.style.overflow = open ? "hidden" : "";
    if (lenis) open ? lenis.stop() : lenis.start();
  };
  menuBtn.addEventListener("click", () => setMenu(menuBtn.getAttribute("aria-expanded") !== "true"));
  menu.addEventListener("click", (e) => e.target.closest("a") && setMenu(false));
  addEventListener("keydown", (e) => {
    if (e.key === "Escape" && menu.classList.contains("is-open")) { setMenu(false); menuBtn.focus(); }
  });

  /* ---------- Contact form (opens the visitor's email app) ---------- */
  const form = $("[data-form]");
  const rules = {
    name: (v) => (v.trim() ? "" : "Please tell us your name."),
    email: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()) ? "" : "Please enter an email address like name@business.com."),
    message: (v) => (v.trim().length >= 10 ? "" : "A sentence or two about what you need helps us reply properly."),
  };
  const check = (field) => {
    const msg = rules[field.name]?.(field.value) ?? "";
    field.setAttribute("aria-invalid", msg ? "true" : "false");
    const err = document.getElementById(field.getAttribute("aria-describedby"));
    if (err) err.textContent = msg;
    return !msg;
  };
  $$("input, textarea", form).forEach((f) => f.addEventListener("blur", () => f.value && check(f)));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const fields = $$("[required]", form);
    const bad = fields.filter((f) => !check(f));
    if (bad.length) { bad[0].focus(); return; }
    const d = Object.fromEntries(new FormData(form));
    const body = `${d.message}\n\n— ${d.name}${d.business ? `, ${d.business}` : ""}\n${d.email}`;
    location.href = `mailto:hello@bellmitchell.com?subject=${encodeURIComponent(`New project enquiry from ${d.business || d.name}`)}&body=${encodeURIComponent(body)}`;
    $(".form-status", form).textContent = "Thanks! Your email app should open with your message ready to send.";
  });

  /* ---------- Marquee: duplicate lists so the loop is seamless ---------- */
  $$(".marquee-row").forEach((row) => {
    const list = $("ul", row);
    const copy = list.cloneNode(true);
    copy.setAttribute("aria-hidden", "true");
    row.append(copy);
  });

  const gsap = window.gsap;
  const ST = window.ScrollTrigger;
  if (!gsap || !ST) return;
  gsap.registerPlugin(ST);

  /* ---------- Nav state + progress (kept even with reduced motion) ---------- */
  const nav = $("[data-nav]");
  const hero = $(".hero");
  let lastY = 0;
  ST.create({
    start: 0, end: "max",
    onUpdate: (self) => {
      const y = self.scroll();
      nav.classList.toggle("is-solid", y > 60);
      nav.classList.toggle("is-hidden", y > lastY && y > hero.offsetHeight && !menu.classList.contains("is-open"));
      lastY = y;
      $(".progress span").style.transform = `scaleX(${self.progress})`;
    },
  });
  $$("main section[id]").forEach((sec) => {
    const link = $(`.nav-links a[href="#${sec.id}"]`);
    if (!link) return;
    ST.create({
      trigger: sec, start: "top 50%", end: "bottom 50%",
      onToggle: (self) => link.classList.toggle("is-active", self.isActive),
    });
  });

  if (reduce) return;

  /* ---------- Smooth scroll ---------- */
  if (window.Lenis) {
    lenis = new Lenis({ lerp: 0.09, wheelMultiplier: 0.95 });
    lenis.on("scroll", ST.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
    $$('a[href^="#"]').forEach((a) =>
      a.addEventListener("click", (e) => {
        const id = a.getAttribute("href");
        const target = id === "#top" ? 0 : $(id);
        if (target === null) return;
        e.preventDefault();
        lenis.scrollTo(target, { offset: 0, duration: 1.6 });
        if (target) target.setAttribute("tabindex", "-1"), target.focus({ preventScroll: true });
      })
    );
  }

  const ease = "expo.out";

  /* ---------- Hero intro ---------- */
  gsap.timeline({ defaults: { ease } })
    .from(".scene .layer", { scale: 1.12, duration: 2.4, stagger: 0.06 }, 0)
    .from(".l-sun", { yPercent: 12, duration: 2.6 }, 0)
    .from(".l-village", { xPercent: -8, duration: 2.2 }, 0.1)
    .from(".l-chapel", { xPercent: 8, duration: 2.2 }, 0.1)
    .from(".hero-title .line > span", { yPercent: 110, rotate: 3, duration: 1.6, stagger: 0.12 }, 0.35)
    .from(".hero-copy .eyebrow", { y: 20, autoAlpha: 0, duration: 1.2 }, 0.6)
    .from(".hero-cta", { y: 40, autoAlpha: 0, duration: 1.4 }, 0.9);

  /* ---------- Hero parallax: fly through the gap as the sun sets ---------- */
  gsap.timeline({ scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: 0.6 } })
    .to(".l-back", { scale: 1.12, yPercent: 6, ease: "none" }, 0)
    .to(".l-sun", { yPercent: 16, ease: "none" }, 0)
    .to(".l-boat", { scale: 1.25, yPercent: 10, ease: "none" }, 0)
    .to(".l-chapel", { xPercent: 14, scale: 1.2, ease: "none" }, 0)
    .to(".l-village", { xPercent: -14, scale: 1.2, ease: "none" }, 0)
    .to(".l-flowers", { scale: 1.35, yPercent: -8, ease: "none" }, 0)
    .to(".hero-copy", { yPercent: -28, autoAlpha: 0, ease: "none" }, 0)
    .to(".scroll-hint", { autoAlpha: 0, duration: 0.2 }, 0);

  /* ---------- About: panel rises, words light up as you read ---------- */
  gsap.from(".about", {
    yPercent: 8, rotate: -1.2, transformOrigin: "0% 0%", ease: "none",
    scrollTrigger: { trigger: ".about", start: "top bottom", end: "top 30%", scrub: 0.8 },
  });
  const lead = $("[data-words]");
  lead.innerHTML = lead.textContent.trim().split(/\s+/).map((w) => `<span class="w">${w}</span>`).join(" ");
  gsap.fromTo($$(".w", lead), { opacity: 0.14 }, {
    opacity: 1, stagger: 0.1, ease: "none",
    scrollTrigger: { trigger: lead, start: "top 80%", end: "bottom 45%", scrub: true },
  });

  /* ---------- Section headings: words slide up out of a mask ---------- */
  $$("[data-split]").forEach((h) => {
    h.setAttribute("aria-label", h.textContent.trim());
    h.innerHTML = h.textContent.trim().split(/\s+/)
      .map((w) => `<span aria-hidden="true" style="display:inline-block;overflow:hidden;padding-bottom:.1em;margin-bottom:-.1em;vertical-align:top"><span style="display:inline-block">${w}</span></span>`)
      .join(" ");
    gsap.from($$("span > span", h), {
      yPercent: 115, rotate: 4, duration: 1.3, ease, stagger: 0.06,
      scrollTrigger: { trigger: h, start: "top 85%" },
    });
  });

  /* ---------- Generic glide-in ---------- */
  ST.batch("[data-glide]", {
    start: "top 88%",
    once: true,
    onEnter: (els) => gsap.fromTo(els,
      { y: 70, rotate: 2, autoAlpha: 0, transformOrigin: "0% 100%" },
      { y: 0, rotate: 0, autoAlpha: 1, duration: 1.3, ease, stagger: 0.09, overwrite: true }),
  });
  // hide them up front (after the batch is registered) so there's no flash
  gsap.set($$("[data-glide]").filter((el) => el.getBoundingClientRect().top > innerHeight), { autoAlpha: 0 });

  /* ---------- Services: cards glide up and stack ---------- */
  const cards = $$(".card");
  cards.forEach((card, i) => {
    gsap.from(card, {
      y: 160, rotate: i % 2 ? -3 : 3, ease: "none",
      scrollTrigger: { trigger: card, start: "top bottom", end: "top 55%", scrub: 0.8 },
    });
    const next = cards[i + 1];
    if (next) {
      gsap.fromTo(card, { scale: 1, filter: "brightness(1)" }, {
        scale: 0.93, filter: "brightness(0.82)", ease: "none",
        scrollTrigger: { trigger: next, start: "top bottom", end: "top 30%", scrub: true },
      });
    }
  });

  /* ---------- Work: pinned horizontal glide on larger screens ---------- */
  const mm = gsap.matchMedia();
  mm.add("(min-width: 768px)", () => {
    const track = $("[data-track]");
    const distance = () => track.scrollWidth - innerWidth;
    const tween = gsap.to(track, {
      x: () => -distance(), ease: "none",
      scrollTrigger: {
        trigger: ".work-pin", start: "top top", end: () => `+=${distance()}`,
        pin: true, scrub: 0.8, invalidateOnRefresh: true, anticipatePin: 1,
      },
    });
    $$(".project", track).forEach((p, i) => {
      gsap.from(p, {
        y: i % 2 ? 90 : -40, rotate: i % 2 ? 3 : -2, ease: "none",
        scrollTrigger: { trigger: p, containerAnimation: tween, start: "left right", end: "left 65%", scrub: true },
      });
    });
  });
  mm.add("(max-width: 767px)", () => {
    $$(".project").forEach((p) =>
      gsap.from(p, { y: 80, rotate: 2, autoAlpha: 0, duration: 1.2, ease, scrollTrigger: { trigger: p, start: "top 90%" } })
    );
  });

  /* ---------- Clients marquee: drifts, speeds up with scroll ---------- */
  const rows = $$(".marquee-row");
  const offsets = rows.map(() => 0);
  let boost = 0;
  let paused = false;
  const marquee = $("[data-marquee]");
  let hovered = false;
  let stopped = false;
  const toggle = $("[data-marquee-toggle]");
  const sync = () => (paused = hovered || stopped);
  marquee.addEventListener("mouseenter", () => { hovered = true; sync(); });
  marquee.addEventListener("mouseleave", () => { hovered = false; sync(); });
  toggle.addEventListener("click", () => {
    stopped = !stopped;
    toggle.setAttribute("aria-pressed", String(stopped));
    toggle.textContent = stopped ? "Play motion" : "Pause motion";
    sync();
  });
  ST.create({
    trigger: marquee, start: "top bottom", end: "bottom top",
    onUpdate: (self) => (boost = Math.min(Math.abs(self.getVelocity()) / 300, 8)),
  });
  gsap.ticker.add((_, dt) => {
    boost *= 0.94;
    if (paused) return;
    rows.forEach((row, i) => {
      const half = row.scrollWidth / 2;
      offsets[i] = (offsets[i] + (0.04 + boost * 0.05) * dt) % half;
      const x = i % 2 ? offsets[i] - half : -offsets[i];
      row.style.transform = `translate3d(${x}px,0,0)`;
    });
  });

  /* ---------- Process: draw the sun's path ---------- */
  const draw = $(".sun-path .draw");
  if (draw) {
    const len = draw.getTotalLength();
    gsap.fromTo(draw, { strokeDasharray: len, strokeDashoffset: len }, {
      strokeDashoffset: 0, ease: "none",
      scrollTrigger: { trigger: ".path-wrap", start: "top 75%", end: "bottom 60%", scrub: 0.6 },
    });
  }

  /* ---------- Contact: sunset rises in ---------- */
  gsap.from(".contact", {
    backgroundPosition: "0 200px", ease: "none",
    scrollTrigger: { trigger: ".contact", start: "top bottom", end: "top top", scrub: true },
  });
  gsap.from(".footer-mark", {
    yPercent: 60, ease: "none",
    scrollTrigger: { trigger: ".footer", start: "top bottom", end: "bottom bottom", scrub: true },
  });

  addEventListener("load", () => ST.refresh());
})();
