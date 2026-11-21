/* Andar 5: a oficina monta a guirlanda em camadas, com laço, luzes, enfeites, placa e aroma. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  const LACOS = { vermelho: "laço vermelho", dourado: "laço dourado", xadrez: "laço xadrez", juta: "laço de juta" };
  const AROMAS = { canela: ["aroma de canela", "#d08a4a"], pinho: ["aroma de pinho", "#7fd19b"], laranja: ["aroma de laranja e cravo", "#ffa04a"], nenhum: [null, null] };

  /* "a, b e c" */
  const juntar = (itens) => (itens.length > 1 ? itens.slice(0, -1).join(", ") + " e " + itens[itens.length - 1] : itens[0]);
  const descrever = (v) =>
    juntar([LACOS[v.laco], v.luzes && "luzes douradas", v.extras && "bolas douradas extras", v.placa && "placa com o nome “" + v.placa + "”", AROMAS[v.aroma][0]].filter(Boolean)) +
    (v.aroma === "nenhum" ? ", sem aroma." : ".");

  /* Partículas sobem da guirlanda na cor do aroma escolhido, só enquanto a oficina está na tela */
  function montarAroma(palco) {
    const caixa = $(".oficina__aroma", palco);
    if (D.reduzir) return () => {};
    caixa.innerHTML = "<span></span>".repeat(14);
    const pontos = $$("span", caixa);
    const tl = gsap.timeline({ paused: true });
    pontos.forEach((p) => {
      const a = Math.random() * Math.PI * 2;
      const r = gsap.utils.random(24, 40);
      const dur = gsap.utils.random(2.6, 4);
      const t0 = gsap.utils.random(0, 3);
      gsap.set(p, { left: 50 + Math.cos(a) * r + "%", top: 50 + Math.sin(a) * r + "%" });
      tl.fromTo(p, { opacity: 0 }, { opacity: 0.8, duration: dur, ease: "vaievem", repeat: -1 }, t0)
        .fromTo(p, { yPercent: 0, xPercent: 0 }, { yPercent: -900, xPercent: gsap.utils.random(-160, 160), duration: dur, ease: "sine.out", repeat: -1 }, t0);
    });
    gsap.set(caixa, { opacity: 0 });
    let cor = null;
    let visivel = false;
    const rodar = () => (cor && visivel ? tl.play() : tl.pause());
    ScrollTrigger.create({ trigger: palco, start: "top bottom", end: "bottom top", onToggle: (st) => { visivel = st.isActive; rodar(); } });
    return (qual) => {
      cor = AROMAS[qual][1];
      if (cor) gsap.to(pontos, { backgroundColor: cor, duration: 0.4 });
      gsap.to(caixa, { opacity: cor ? 1 : 0, duration: 0.4 });
      rodar();
    };
  }

  function oficina() {
    const form = $(".oficina__painel");
    const palco = $(".oficina__palco");
    const luzes = $('[data-camada="luzes"]', palco);
    const extras = $('[data-camada="extras"]', palco);
    const lacos = $$("[data-laco]", palco);
    const placa = $(".oficina__placa", palco);
    const nome = $(".oficina__nome", placa);
    const resumo = $(".oficina__resumo", form);
    const trocarAroma = montarAroma(palco);
    const t = (d) => (D.reduzir ? 0 : d);
    const valor = () => {
      const f = form.elements;
      return { laco: f.laco.value, luzes: f.luzes.checked, extras: f.extras.checked, placa: f.placa.value.trim(), aroma: f.aroma.value };
    };
    let antes = { laco: null, luzes: false, extras: false, placa: "", aroma: "nenhum" };
    /* O nome encolhe quando não cabe na placa */
    const caber = () => {
      nome.classList.remove("oficina__nome--longo");
      nome.classList.toggle("oficina__nome--longo", nome.scrollWidth > nome.clientWidth);
    };
    if (document.fonts) document.fonts.ready.then(caber);

    /* O laço gira a partir do nó; a placa balança a partir do prego */
    gsap.set(lacos, { transformOrigin: "51.2% 77%" });
    gsap.set(placa, { transformOrigin: "50.3% 29%" });

    /* Anima só o que mudou desde a última escolha */
    function aplicar(intro) {
      const v = valor();
      if (v.laco !== antes.laco) {
        lacos.forEach((img) => {
          if (img.dataset.laco === v.laco) gsap.fromTo(img, { opacity: 0, scale: 0.7, rotation: -10 }, { opacity: 1, scale: 1, rotation: 0, duration: t(0.7), delay: intro ? t(0.45) : 0, ease: "back.out(2.2)", overwrite: true });
          else if (img.dataset.laco === antes.laco) gsap.to(img, { opacity: 0, scale: 0.85, duration: t(0.2), overwrite: true });
        });
      }
      if (v.luzes !== antes.luzes) {
        if (v.luzes) gsap.fromTo(luzes, { opacity: 0 }, { opacity: 1, duration: t(0.6), ease: "pisca", overwrite: true });
        else gsap.to(luzes, { opacity: 0, duration: t(0.25), overwrite: true });
      }
      if (v.extras !== antes.extras) {
        if (v.extras) gsap.fromTo(extras, { opacity: 0, yPercent: -3 }, { opacity: 1, yPercent: 0, duration: t(0.6), ease: "back.out(1.6)", overwrite: true });
        else gsap.to(extras, { opacity: 0, yPercent: -1.5, duration: t(0.25), overwrite: true });
      }
      if (v.placa !== antes.placa) {
        nome.textContent = v.placa;
        caber();
        if (v.placa && !antes.placa) gsap.fromTo(placa, { opacity: 0, rotation: 18 }, { opacity: 1, rotation: 0, duration: t(1.6), ease: "elastic.out(1, 0.3)", overwrite: true });
        else if (!v.placa) gsap.to(placa, { opacity: 0, rotation: -8, duration: t(0.3), overwrite: true });
        else if (!D.reduzir) gsap.fromTo(placa, { rotation: v.placa.length % 2 ? 2.5 : -2.5 }, { rotation: 0, duration: 1.4, ease: "elastic.out(1, 0.25)", overwrite: "auto" });
      }
      if (v.aroma !== antes.aroma) trocarAroma(v.aroma);
      resumo.textContent = "Sua guirlanda leva " + descrever(v);
      antes = v;
    }

    form.addEventListener("input", () => aplicar());
    form.addEventListener("change", () => aplicar());
    /* O pedido segue para o Contato já escrito, pela sessão e não pela URL */
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      D.sessao.gravar("dp-orcamento", JSON.stringify({ assunto: "Orçamento de guirlanda", mensagem: "Olá! Gostaria de um orçamento para uma guirlanda com " + descrever(valor()) }));
      D.irPara("contato.html");
    });

    resumo.textContent = "Sua guirlanda leva " + descrever(valor());
    if (D.reduzir) return aplicar();
    /* Na primeira passagem, a guirlanda se monta sozinha com as escolhas iniciais */
    ScrollTrigger.create({ trigger: palco, start: "top 70%", once: true, onEnter: () => aplicar(true) });
  }

  D.aoIniciar(oficina);
})();
