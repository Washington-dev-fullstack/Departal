/* Página inicial: vitrine, manifesto, gôndola de ofertas, elevador e busca de presentes. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  function vitrine() {
    const s = $(".vitrine");
    const gl = window.THREE ? D.vitrine(s) : (s.classList.add("sem-gl"), null);
    const n = D.diasParaNatal();
    $(".vitrine__dias").textContent = n;
    $(".vitrine__rotulo").textContent = n === 1 ? "dia para o Natal" : "dias para o Natal";
    $(".vitrine__dica").textContent = D.fino ? "Passe o mouse no vidro" : "Passe o dedo no vidro";

    if (!D.reduzir) {
      const tl = gsap.timeline({
        scrollTrigger: { trigger: s, pin: true, start: "top top", end: "+=130%", scrub: 0.5, onUpdate: (st) => gl && gl.progresso(st.progress) }
      });
      tl.to(".vitrine__letras", { scale: 1.24, opacity: 0, duration: 0.5, ease: "power1.in", transformOrigin: "30% 70%" }, 0.04)
        /* Os filhos somem na rolagem; o pai fica com a entrada, e uma animação não grava o valor da outra */
        .to(".vitrine__contagem > *", { opacity: 0, duration: 0.2 }, 0)
        .to({}, { duration: 0.46 });

      gsap.set(".vitrine__linha > span", { yPercent: 108 });
      gsap.set([".vitrine__lide", ".vitrine__acoes", ".vitrine__contagem", ".vitrine__dica"], { autoAlpha: 0, y: 14 });
      D.abertura.then(() => {
        gsap.timeline({ delay: 0.1 })
          .to(".vitrine__linha > span", { yPercent: 0, duration: 1, ease: "chega", stagger: 0.14 }, 0)
          .to(".vitrine__linha .folha", { backgroundPosition: "62% 0", duration: 2.2, ease: "sine.inOut" }, 0.2)
          .to([".vitrine__lide", ".vitrine__acoes"], { autoAlpha: 1, y: 0, duration: 0.6, ease: "chega", stagger: 0.12 }, 0.5)
          .to(".vitrine__contagem", { autoAlpha: 1, y: 0, duration: 0.6, ease: "chega" }, 0.8)
          .to(".vitrine__dica", { autoAlpha: 1, y: 0, duration: 0.5, ease: "chega" }, 1)
          .call(() => gl && gl.demonstrar(), null, 1.05);
      });
    }
  }

  function faixa() {
    const dados = ["Embalagem de Natal grátis", "Entrega expressa em até 2 dias úteis", "Troca grátis"];
    const trilho = $(".faixa__trilho");
    const uma = dados.map((t) => "<span>" + t + "</span>").join("");
    trilho.innerHTML = '<div class="faixa__grupo">' + uma + uma + '</div><div class="faixa__grupo" aria-hidden="true">' + uma + uma + "</div>";
  }

  function manifesto() {
    const p = $(".manifesto__frase");
    if (D.reduzir) return;
    SplitText.create(p, {
      type: "words",
      wordsClass: "palavra",
      autoSplit: true,
      onSplit(self) {
        gsap.set(self.words, { opacity: 0.16 });
        return gsap.to(self.words, {
          opacity: 1,
          stagger: 0.05,
          ease: "none",
          scrollTrigger: { trigger: p, start: "top 72%", end: "bottom 46%", scrub: 0.4 }
        });
      }
    });
    gsap.to(".carimbo__roda", { rotation: 360, duration: 22, ease: "none", repeat: -1 });
  }

  function ofertas() {
    const ordem = D.produtos.filter((p) => p.de).sort((a, b) => D.desconto(b) - D.desconto(a)).slice(0, 8);
    const trilho = D.prateleira(".gondola__trilho", ordem);
    trilho.classList.remove("prateleira");
    D.$$(".produto", trilho).forEach((el) => el.classList.add("aceso"));
    const mm = gsap.matchMedia();
    mm.add("(min-width: 900px) and (min-height: 560px) and (prefers-reduced-motion: no-preference)", () => {
      const area = $(".gondola__area");
      gsap.to(trilho, {
        x: () => -(trilho.scrollWidth - area.clientWidth),
        ease: "none",
        scrollTrigger: {
          trigger: ".gondola",
          pin: true,
          start: "top top",
          end: () => "+=" + Math.max(400, trilho.scrollWidth - area.clientWidth),
          scrub: 0.5,
          invalidateOnRefresh: true,
          onUpdate(st) {
            const n = Math.min(ordem.length, Math.round(st.progress * (ordem.length - 1)) + 1);
            const v = $(".gondola__visor");
            if (v) v.textContent = String(n).padStart(2, "0") + "/" + String(ordem.length).padStart(2, "0");
          }
        }
      });
    });
  }

  /* Elevador: rolar sobe os andares, com visor, ambiente e foto trocando */
  function elevador() {
    const area = $(".elevador");
    const andares = D.andares.slice().reverse();
    const botoes = $(".elevador__botoes");
    botoes.innerHTML = andares.slice().reverse().map((a) => '<button class="elevador__botao" type="button" data-n="' + a.n + '" aria-label="Ver ' + a.nome + '"><span>' + a.n + "</span></button>").join("");
    const cenas = $(".elevador__cenas");
    cenas.innerHTML = andares
      .map(
        (a) =>
          '<article class="elevador__cena" data-n="' + a.n + '">' +
          '<img src="' + D.foto(a.capa) + '" alt="" width="800" height="800" loading="lazy">' +
          '<div class="elevador__txt"><p class="elevador__num num-led">' + a.n + "</p>" +
          '<h3 class="titulo t-2">' + a.nome + "</h3><p class=\"lide\">" + a.frase + "</p>" +
          '<a class="btn btn--vidro" href="' + a.pagina + '">Ir para ' + a.nome + "</a></div></article>"
      )
      .join("");

    const mm = gsap.matchMedia();
    mm.add("(min-width: 900px) and (prefers-reduced-motion: no-preference)", () => {
      const lista = $$(".elevador__cena");
      const cores = { 1: "#0e2c20", 2: "#3a0a17", 3: "#2c0b14", 4: "#0b0d14", 5: "#0e2f20", 6: "#0c1636" };
      gsap.set(lista, { autoAlpha: 0 });
      gsap.set(lista[0], { autoAlpha: 1 });
      const visor = $(".elevador__visor span:last-child");
      const seta = $(".elevador__seta");
      const nome = $(".elevador__nome");
      let atual = 0;
      function ir(i) {
        if (i === atual) return;
        const para = lista[i];
        const de = lista[atual];
        const sobe = i > atual;
        seta.textContent = sobe ? "▲" : "▼";
        gsap.to(de, { autoAlpha: 0, duration: 0.38, overwrite: true });
        gsap.to($("img", de), { yPercent: sobe ? 9 : -9, duration: 0.5, overwrite: true });
        gsap.fromTo(para, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.46, delay: 0.1, overwrite: true });
        gsap.fromTo($("img", para), { yPercent: sobe ? -9 : 9, scale: 0.94 }, { yPercent: 0, scale: 1, duration: 0.7, ease: "chega", overwrite: true });
        gsap.fromTo($(".elevador__txt", para).children, { y: sobe ? 16 : -16, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "chega", stagger: 0.04, overwrite: true });
        gsap.to(area, { "--fundo-andar": cores[andares[i].n], duration: 0.7, overwrite: true });
        visor.textContent = andares[i].n;
        nome.textContent = andares[i].nome;
        $$(".elevador__botao").forEach((b) => b.setAttribute("aria-current", Number(b.dataset.n) === andares[i].n));
        atual = i;
      }
      $$(".elevador__botao")[5].setAttribute("aria-current", "true");
      const st = ScrollTrigger.create({
        trigger: area,
        pin: true,
        start: "top top",
        end: "+=" + innerHeight * 3.4,
        onUpdate: (s) => ir(Math.min(5, Math.floor(s.progress * 6)))
      });
      botoes.addEventListener("click", (e) => {
        const b = e.target.closest(".elevador__botao");
        if (!b) return;
        const i = andares.findIndex((a) => a.n === Number(b.dataset.n));
        scrollTo({ top: st.start + (st.end - st.start) * ((i + 0.5) / 6), behavior: "smooth" });
      });
    });
  }

  /* Busca de presentes por orçamento e interesse */
  function encontre() {
    const faixa = $("#orcamento");
    const valor = $(".busca__valor");
    const conta = $(".busca__conta");
    const grade = $(".busca__grade");
    const chips = $(".busca__chips");
    const opcoes = [["criancas", "Para crianças"], ["mao-na-massa", "Mão na massa"], ["cozinha", "Para a cozinha"], ["cuidados", "Cuidados pessoais"], ["familia", "Para a família"], ["casa", "Para a casa"], ["surpresa", "Um mimo surpresa"]];
    chips.innerHTML = opcoes.map(([v, t]) => '<button class="filtro" type="button" data-v="' + v + '" aria-pressed="false">' + t + "</button>").join("");
    const candidatos = D.produtos.filter((p) => p.interesse);
    D.prateleira(grade, candidatos);
    const escolhidos = new Set();

    function pinta() {
      const pct = ((faixa.value - faixa.min) / (faixa.max - faixa.min)) * 100;
      faixa.style.setProperty("--pct", pct + "%");
      valor.textContent = D.moeda(Number(faixa.value)).replace(",00", "");
    }
    function filtrar(animar) {
      const teto = Number(faixa.value);
      const itens = $$(".produto", grade);
      const estado = animar && !D.reduzir ? Flip.getState(itens) : null;
      const passa = (p) => p.preco <= teto && (!escolhidos.size || p.interesse.some((i) => escolhidos.has(i)));
      const lista = candidatos.filter(passa).sort((a, b) => b.preco - a.preco).slice(0, 8);
      const ids = new Set(lista.map((p) => p.id));
      itens.forEach((el) => {
        el.hidden = !ids.has(el.dataset.id);
        el.classList.add("aceso");
      });
      lista.forEach((p) => grade.append(itens.find((el) => el.dataset.id === p.id)));
      const total = candidatos.filter(passa).length;
      conta.textContent = total === 0 ? "Nada nessa faixa ainda. Suba um pouco o valor ou tire um interesse." : total === 1 ? "1 presente para você" : total + " presentes para você" + (total > 8 ? ", os 8 melhores abaixo" : "");
      if (estado) {
        Flip.from(estado, {
          duration: 0.5,
          absolute: true,
          scale: true,
          ease: "loja",
          onEnter: (els) => gsap.fromTo(els, { opacity: 0, scale: 0.92 }, { opacity: 1, scale: 1, duration: 0.4, delay: 0.08 }),
          onLeave: (els) => gsap.to(els, { opacity: 0, scale: 0.92, duration: 0.2 }),
          onComplete: () => ScrollTrigger.refresh()
        });
      } else ScrollTrigger.refresh();
    }
    let espera = 0;
    faixa.addEventListener("input", () => {
      pinta();
      clearTimeout(espera);
      espera = setTimeout(() => filtrar(true), 110);
    });
    chips.addEventListener("click", (e) => {
      const b = e.target.closest(".filtro");
      if (!b) return;
      const on = b.getAttribute("aria-pressed") !== "true";
      b.setAttribute("aria-pressed", on);
      on ? escolhidos.add(b.dataset.v) : escolhidos.delete(b.dataset.v);
      filtrar(true);
    });
    pinta();
    filtrar(false);
  }

  function servicos() {
    if (D.reduzir) return;
    gsap.fromTo(".servicos__fita path", { drawSVG: "0%" }, {
      drawSVG: "100%",
      ease: "none",
      scrollTrigger: { trigger: ".servicos", start: "top 72%", end: "bottom 62%", scrub: 0.6 }
    });
  }

  function novidades() {
    const f = $(".novidades__form");
    f.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!f.reportValidity()) return;
      $(".novidades__ok").textContent = "Cadastro simulado: este site é uma demonstração e nenhum e-mail foi guardado.";
      f.reset();
    });
  }

  D.aoIniciar(() => {
    vitrine();
    faixa();
    manifesto();
    ofertas();
    elevador();
    encontre();
    servicos();
    novidades();
    if (location.hash) {
      addEventListener("load", () => {
        const alvo = $(location.hash);
        ScrollTrigger.refresh();
        if (alvo) alvo.scrollIntoView();
      });
    }
  });
})();
