/* Andar 1: a árvore se monta enquanto a página desce, na ordem certa de decorar. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  function montagem() {
    const s = $(".montagem");
    const passos = $$(".montagem__passo");
    const [arvore, luzes, bolas, enfeites, estrela] = $$(".montagem__camada");
    const brilho = $(".montagem__brilho");
    let atual = -1;
    const marcar = (i) => {
      if (i === atual) return;
      atual = i;
      passos.forEach((p, k) => {
        p.classList.toggle("feito", k < i);
        if (k === i) p.setAttribute("aria-current", "step");
        else p.removeAttribute("aria-current");
      });
    };

    if (D.reduzir) {
      s.classList.add("montagem--pronta");
      gsap.set(brilho, { opacity: 1 });
      return;
    }

    marcar(0);
    gsap.set([luzes, bolas, enfeites, estrela], { opacity: 0 });
    gsap.set(arvore, { filter: "brightness(0.3) saturate(0.6)" });
    gsap.timeline({
      defaults: { ease: "none" },
      scrollTrigger: {
        trigger: s,
        pin: true,
        start: "top top",
        end: () => "+=" + innerHeight * 2.6,
        scrub: 0.6,
        invalidateOnRefresh: true,
        onUpdate: (st) => marcar(Math.min(4, Math.floor(st.progress * 5)))
      }
    })
      .to(arvore, { filter: "brightness(1) saturate(1)", duration: 0.6 }, 0.15)
      .to(luzes, { opacity: 1, duration: 0.6, ease: "pisca" }, 1.15)
      .to(brilho, { opacity: 1, duration: 0.6 }, 1.2)
      .fromTo(bolas, { y: -60 }, { opacity: 1, y: 0, duration: 0.7, ease: "back.out(1.5)" }, 2.1)
      .fromTo(enfeites, { scale: 0.94 }, { opacity: 1, scale: 1, duration: 0.6, ease: "back.out(2)" }, 3.1)
      .fromTo(estrela, { y: -140, rotation: -50, transformOrigin: "50% 9%" }, { opacity: 1, y: 0, rotation: 0, duration: 0.7, ease: "back.out(1.3)" }, 4.05)
      .to({}, { duration: 0.2 });
  }

  D.aoIniciar(montagem);
})();
