/* Sobre: enfeites pendurados que balançam, vitrine da memória, crachás e carimbo. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  /* Cada enfeite é um pêndulo amortecido: a brisa mantém um balanço leve e o ponteiro dá empurrões */
  function pendentes() {
    const capa = $(".capa--sobre");
    const els = $$(".pendente", capa);
    if (!els.length || D.reduzir) return;
    const itens = els.map((el, i) => ({
      el,
      img: $("img", el),
      a: 0,
      v: 0,
      w: 4,
      amp: 1.1 + (i % 3) * 0.45,
      ritmo: 0.31 + i * 0.047,
      fase: i * 1.9,
      dentro: false,
      girar: gsap.quickSetter(el, "rotation", "deg")
    }));

    /* fio mais longo balança mais devagar, como um pêndulo de verdade */
    const medir = () => itens.forEach((it) => {
      const L = it.el.offsetHeight * 0.82;
      it.w = 2 * Math.PI * gsap.utils.clamp(0.42, 1.0, 0.95 * Math.sqrt(150 / Math.max(L, 60)));
    });
    medir();
    addEventListener("resize", medir);

    let ativo = true;
    let t = 0;
    ScrollTrigger.create({ trigger: capa, start: "top bottom", end: "bottom top", onToggle: (s) => (ativo = s.isActive) });
    gsap.ticker.add((tempo, delta) => {
      if (!ativo) return;
      const dt = Math.min(delta, 50) / 1000;
      t += dt;
      itens.forEach((it) => {
        const alvo = it.amp * Math.sin(t * it.ritmo * 2 * Math.PI + it.fase);
        const acel = -it.w * it.w * (it.a - alvo) - 2 * 0.07 * it.w * it.v;
        it.v += acel * dt;
        it.a = gsap.utils.clamp(-28, 28, it.a + it.v * dt);
        it.girar(it.a);
      });
    });

    /* o empurrão vem da velocidade do ponteiro no instante em que ele cruza o enfeite */
    let ux = 0;
    let ut = 0;
    capa.addEventListener("pointermove", (e) => {
      const dt = Math.max(8, e.timeStamp - ut) / 1000;
      const vx = ut ? (e.clientX - ux) / dt : 0;
      ux = e.clientX;
      ut = e.timeStamp;
      itens.forEach((it) => {
        const r = it.img.getBoundingClientRect();
        const dentro = e.clientX > r.left - 8 && e.clientX < r.right + 8 && e.clientY > r.top - 8 && e.clientY < r.bottom + 8;
        if (dentro && !it.dentro) it.v += gsap.utils.clamp(-110, 110, -vx * 0.06);
        it.dentro = dentro;
      });
    }, { passive: true });
    capa.addEventListener("pointerleave", () => {
      ut = 0;
      itens.forEach((it) => (it.dentro = false));
    });

    /* chegada: os enfeites descem pelos fios e ficam balançando */
    gsap.from(els, {
      y: () => -innerHeight * 0.45,
      duration: 1.3,
      ease: "chega",
      stagger: 0.11,
      delay: 0.15,
      onStart() {
        itens.forEach((it, i) => gsap.delayedCall(0.15 + i * 0.11 + 0.75, () => (it.v += (i % 2 ? 1 : -1) * (26 + i * 5))));
      }
    });
  }

  /* Hoje: os seis andares em janelas, montados a partir dos dados da loja */
  function montarPredio() {
    const lista = $(".predio__andares");
    if (!lista) return;
    $(".predio__letreiro").innerHTML = D.letreiroSVG() + '<span class="predio__chapeu">' + D.gorro + "</span>";
    lista.innerHTML = D.andares.map((a) =>
      '<li class="predio__janela"><img src="' + D.foto(a.capa) + '" alt="" width="800" height="800" loading="lazy">' +
      '<span class="num-led" aria-hidden="true">' + a.n + '</span><span class="predio__nome"><span class="so-leitor">' + a.n + "º andar, </span>" + a.nome + "</span></li>"
    ).join("");
  }

  let aceso = false;
  function acender() {
    if (aceso) return;
    aceso = true;
    const janelas = $$(".predio__janela").reverse();
    if (D.reduzir) return janelas.forEach((j) => j.style.setProperty("--luz", 1));
    gsap.to(janelas, { "--luz": 1, duration: 0.5, ease: "pisca", stagger: 0.16, delay: 0.2 });
  }

  /* A vitrine da memória troca de quadro conforme o parágrafo que está sendo lido */
  function memoria() {
    const quadros = $$(".memoria__quadro");
    const marcas = $$(".memoria__linha li");
    if (!quadros.length) return;
    montarPredio();
    let atual = 0;
    const mostrar = (i) => {
      if (i === 2) acender();
      if (i === atual) return;
      atual = i;
      quadros.forEach((q, k) => q.classList.toggle("ativo", k === i));
      marcas.forEach((m, k) => m.classList.toggle("ativo", k === i));
    };
    gsap.matchMedia().add({ largo: "(min-width: 900px)", estreito: "(max-width: 899px)" }, (ctx) => {
      if (ctx.conditions.largo) {
        $$(".historia__texto p[data-quadro]").forEach((p) => {
          ScrollTrigger.create({ trigger: p, start: "top 58%", end: "bottom 58%", onToggle: (s) => s.isActive && mostrar(Number(p.dataset.quadro)) });
        });
        return;
      }
      /* na faixa de cartões todos ficam visíveis; o prédio acende quando o cartão dele entra na tela */
      const predio = $(".predio");
      if (!("IntersectionObserver" in window)) return acender();
      const io = new IntersectionObserver((es) => {
        if (es.some((e) => e.isIntersecting)) {
          acender();
          io.disconnect();
        }
      }, { threshold: 0.6 });
      io.observe(predio);
      return () => io.disconnect();
    });
  }

  /* Crachás balançam na presilha quando o ponteiro passa */
  function crachas() {
    $$(".cracha__marca").forEach((m) => (m.innerHTML = D.letreiroSVG() + '<span class="cracha__chapeu">' + D.gorro + "</span>"));
    if (!D.fino || D.reduzir) return;
    $$(".cracha").forEach((c) => {
      c.addEventListener("pointerenter", (e) => {
        const r = c.getBoundingClientRect();
        const lado = e.clientX < r.left + r.width / 2 ? -1 : 1;
        gsap.fromTo(c, { rotation: lado * 3.5 }, { rotation: 0, duration: 1.8, ease: "elastic.out(1, 0.22)", overwrite: true });
      });
    });
  }

  function carimbo() {
    const g = $(".compromisso .carimbo__gorro");
    if (!g) return;
    g.innerHTML = D.gorro;
    if (!D.reduzir) gsap.to(".compromisso .carimbo__roda", { rotation: 360, duration: 24, ease: "none", repeat: -1 });
  }

  D.aoIniciar(() => {
    pendentes();
    memoria();
    crachas();
    carimbo();
  });
})();
