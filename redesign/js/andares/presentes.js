/* Andar 2: faixas de preço com etiquetas penduradas e a tag do embrulho com o nome de quem vai ganhar. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  /* Empurrar para a direita gira no sentido anti-horário: a ponta de baixo vai junto com a mão */
  function patamares() {
    $$(".patamar__lista").forEach((ul) => D.prateleira(ul, D.produtos.filter((p) => p.faixa === ul.dataset.faixa)));
    if (D.reduzir) return;
    const pendentes = $$(".patamar__pendente");
    gsap.timeline({ scrollTrigger: { trigger: ".patamares", start: "top 78%", once: true } })
      .from(".patamares__fita", { scaleX: 0, duration: 0.9, ease: "power3.inOut" })
      .from(pendentes, { rotation: (i) => [-18, 14, -12][i], opacity: 0, duration: 2, ease: "elastic.out(1, 0.28)", stagger: 0.12 }, 0.35);
    pendentes.forEach((el) => {
      el.addEventListener("pointerenter", (e) => {
        const r = el.getBoundingClientRect();
        const daEsquerda = e.clientX < r.left + r.width / 2;
        gsap.fromTo(el, { rotation: daEsquerda ? -7 : 7 }, { rotation: 0, duration: 1.8, ease: "elastic.out(1, 0.22)", overwrite: true });
      });
    });
  }

  function tag() {
    const campo = $("#nome-tag");
    const nome = $(".tag__nome");
    const tag = $(".tag");
    const REPOUSO = -9;
    gsap.set(tag, { rotation: REPOUSO });
    const balancar = (forca) => {
      if (D.reduzir) return;
      gsap.fromTo(tag, { rotation: REPOUSO + forca }, { rotation: REPOUSO, duration: 2.4, ease: "elastic.out(1, 0.2)", overwrite: true });
    };
    /* O nome encolhe quando não cabe no cartão */
    const caber = () => {
      nome.classList.remove("tag__nome--longo");
      nome.classList.toggle("tag__nome--longo", nome.scrollWidth > nome.clientWidth);
    };
    if (document.fonts) document.fonts.ready.then(caber);
    campo.addEventListener("input", () => {
      const v = campo.value.trim();
      nome.textContent = v || "você";
      caber();
      balancar(v.length % 2 ? 5 : -5);
    });
    if (D.reduzir) return;
    gsap.from(tag, { rotation: REPOUSO - 46, duration: 2.6, ease: "elastic.out(1, 0.22)", scrollTrigger: { trigger: ".embrulho", start: "top 62%", once: true } });
    let antes = null;
    const palco = $(".embrulho__palco");
    palco.addEventListener("pointermove", (e) => {
      if (antes !== null) {
        const v = e.clientX - antes;
        if (Math.abs(v) > 12) balancar(gsap.utils.clamp(-18, 18, -v * 0.6));
      }
      antes = e.clientX;
    }, { passive: true });
    palco.addEventListener("pointerleave", () => (antes = null));
  }

  /* As dicas aplicam o filtro da prateleira principal e levam até ela */
  function dicas() {
    $$("[data-filtro]").forEach((b) =>
      b.addEventListener("click", () => {
        const f = $('.andar__filtros .filtro[data-v="' + b.dataset.filtro + '"]');
        if (f && f.getAttribute("aria-pressed") !== "true") f.click();
        $("#produtos").scrollIntoView({ behavior: D.reduzir ? "auto" : "smooth" });
      })
    );
  }

  D.aoIniciar(() => {
    patamares();
    tag();
    dicas();
  });
})();
