/* Andar 3: o provador abre a cortina, o guia de tamanhos calcula a medida e a entrega mostra o último dia para pedir. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  /* As duas metades franzem para os lados: a escala comprime as dobras do veludo */
  function provador() {
    if (D.reduzir) return;
    gsap.timeline({ scrollTrigger: { trigger: ".provador__cabine", start: "top 72%", end: "top 18%", scrub: 0.7 } })
      .to(".provador__cortina--e", { scaleX: 0.1, ease: "power2.inOut" }, 0)
      .to(".provador__cortina--d", { scaleX: 0.1, ease: "power2.inOut" }, 0);
  }

  function medidas() {
    const abas = $$('.medidas__abas [role="tab"]');
    const marca = $(".medidas__marca");
    const mover = (b, animar) => gsap.to(marca, { x: b.offsetLeft, width: b.offsetWidth, duration: animar && !D.reduzir ? 0.4 : 0, ease: "chega" });
    const escolher = (b, focar) => {
      abas.forEach((a) => {
        const sim = a === b;
        a.setAttribute("aria-selected", sim);
        a.tabIndex = sim ? 0 : -1;
        $("#" + a.getAttribute("aria-controls")).hidden = !sim;
      });
      mover(b, true);
      if (focar) b.focus();
    };
    abas.forEach((a, i) => {
      a.addEventListener("click", () => escolher(a));
      a.addEventListener("keydown", (e) => {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        e.preventDefault();
        escolher(abas[(i + (e.key === "ArrowRight" ? 1 : abas.length - 1)) % abas.length], true);
      });
    });
    const ajustar = () => mover($('.medidas__abas [aria-selected="true"]'), false);
    ajustar();
    addEventListener("resize", ajustar);
    if (document.fonts) document.fonts.ready.then(ajustar);

    const AVISOS = {
      adultos: { menor: "Para menos de 84 cm de busto, escolha o P.", maior: "Acima de 100 cm, fale com a gente: temos tamanhos especiais.", achou: (n) => "Seu tamanho é " + n + "." },
      criancas: { menor: "Para menos de 92 cm de altura, escolha o 2 a 4 anos.", maior: "Acima de 128 cm, confira a tabela de adultos.", achou: (n) => "O tamanho indicado é " + n + "." }
    };
    $$("[data-calc]").forEach((campo) => {
      const painel = campo.closest('[role="tabpanel"]');
      const linhas = $$("tbody tr", painel);
      const resposta = $(".medidas__resposta", painel);
      const aviso = AVISOS[campo.dataset.calc];
      campo.addEventListener("input", () => {
        linhas.forEach((l) => l.classList.remove("na-medida"));
        if (campo.value === "") return (resposta.textContent = "");
        const v = Number(campo.value);
        const servem = linhas.filter((l) => v >= Number(l.dataset.de) && v <= Number(l.dataset.ate));
        if (!servem.length) return (resposta.textContent = v < Number(linhas[0].dataset.de) ? aviso.menor : aviso.maior);
        const escolhida = servem[servem.length - 1];
        escolhida.classList.add("na-medida");
        resposta.textContent = aviso.achou(escolhida.dataset.nome) + (servem.length > 1 ? " Entre dois tamanhos, prefira o maior." : "");
      });
    });
  }

  /* Entrega em até 2 dias úteis: o último pedido que chega até 24 de dezembro */
  function entrega() {
    const el = $(".entrega__prazo");
    const agora = new Date();
    const hoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
    const limite = new Date(agora.getFullYear(), 11, 24);
    for (let uteis = 0; uteis < 2; ) {
      limite.setDate(limite.getDate() - 1);
      if (limite.getDay() !== 0 && limite.getDay() !== 6) uteis++;
    }
    if (hoje > limite) return;
    const dia = new Intl.DateTimeFormat("pt-BR", { weekday: "long", day: "numeric", month: "long" }).format(limite);
    el.innerHTML = "Peça até <strong>" + dia + "</strong> e receba antes do Natal. A entrega é em até 2 dias úteis.";
  }

  D.aoIniciar(() => {
    provador();
    medidas();
    entrega();
  });
})();
