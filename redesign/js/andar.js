/* Andares: prateleira principal com filtros, prateleiras extras e guias passo a passo. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  /* O fio liga o centro do primeiro número ao do último, na horizontal ou na vertical */
  function medirFio(lista) {
    const nums = $$(".etapa__num", lista);
    const base = lista.getBoundingClientRect();
    const a = nums[0].getBoundingClientRect();
    const b = nums[nums.length - 1].getBoundingClientRect();
    Object.assign($(".etapas__fio", lista).style, {
      left: a.left + a.width / 2 - base.left - 1 + "px",
      top: a.top + a.height / 2 - base.top - 1 + "px",
      width: Math.max(2, b.left - a.left) + "px",
      height: Math.max(2, b.top - a.top) + "px"
    });
  }

  /* O fio do guia acende cada etapa conforme a página desce */
  function etapas(lista) {
    const fio = $(".etapas__fio i", lista);
    const itens = $$(".etapa", lista);
    const medir = () => medirFio(lista);
    medir();
    addEventListener("resize", medir);
    if (document.fonts) document.fonts.ready.then(medir);
    if (D.reduzir) {
      itens.forEach((e) => e.classList.add("acesa"));
      return;
    }
    gsap.matchMedia().add({ largo: "(min-width: 861px)", estreito: "(max-width: 860px)" }, (ctx) => {
      const largo = ctx.conditions.largo;
      gsap.fromTo(fio, largo ? { scaleX: 0, scaleY: 1 } : { scaleX: 1, scaleY: 0 }, {
        scaleX: 1,
        scaleY: 1,
        ease: "none",
        scrollTrigger: {
          trigger: lista,
          start: "top 72%",
          end: largo ? "top 34%" : "bottom 62%",
          scrub: 0.5,
          onUpdate: (st) => itens.forEach((e, i) => e.classList.toggle("acesa", st.progress >= i / (itens.length - 1) - 0.02))
        }
      });
    });
  }

  /* A peça da capa: acende sob o feixe de luz, ou desce pelo fio e fica balançando */
  function pecaDaCapa() {
    const peca = $(".capa__peca");
    if (!peca || D.reduzir) return;
    const img = $("img", peca);
    const balanco = $(".capa__balanco", peca);
    if (balanco) {
      const pend = D.pendulo(balanco, { area: peca.closest(".capa"), alvo: img, forca: 0.05, limite: 16, comprimento: () => img.offsetTop + img.offsetHeight * 0.5 });
      gsap.from(balanco, { y: () => -innerHeight * 0.6, duration: 1.3, ease: "chega", delay: 0.15, onComplete: () => pend.empurrar(-24) });
      return;
    }
    gsap.timeline({ delay: 0.25 })
      .fromTo(peca, { "--luz": 0 }, { "--luz": 1, duration: 1, ease: "pisca" })
      .from(img, { y: 22, opacity: 0, duration: 1, ease: "chega" }, 0.15);
  }

  D.aoIniciar(() => {
    const n = Number(document.documentElement.dataset.andar);
    const a = D.andares.find((x) => x.n === n);
    const grade = D.prateleira(".andar__grade", D.doAndar(a.id));
    const barra = $(".andar__filtros");
    if (D.filtros[a.id]) D.ligarFiltros(barra, grade, D.filtros[a.id], (p, v) => (p.filtros || []).includes(v));
    else barra.remove();
    $$(".andar__extras").forEach((ul) => D.prateleira(ul, D.doAndar(a.id, ul.dataset.secao)));
    $$(".etapas").forEach(etapas);
    pecaDaCapa();
  });
})();
