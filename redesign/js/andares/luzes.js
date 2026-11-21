/* Andar 4: varal de lâmpadas com interruptor e os 8 modos do pisca-pisca, e a economia do LED em números. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  /* [cor acesa, halo, vidro apagado] */
  const CORES = [
    ["#ff3b4f", "rgba(255, 59, 79, 0.42)", "#4a1018"],
    ["#ffc23d", "rgba(255, 194, 61, 0.42)", "#4a3a12"],
    ["#3ddc84", "rgba(61, 220, 132, 0.38)", "#123a24"],
    ["#4aa8ff", "rgba(74, 168, 255, 0.42)", "#122a48"],
    ["#ff7ad9", "rgba(255, 122, 217, 0.4)", "#48183c"]
  ];
  const MODOS = ["Combinação", "Em ondas", "Sequencial", "Acende devagar", "Perseguição", "Esmaecer lento", "Cintilante", "Fixo"];
  const BAIXO = 0.06;

  function varal() {
    const raiz = document.documentElement;
    const capa = $(".capa--luzes");
    const area = $(".varal", capa);
    const svg = $(".varal__fio", area);
    const fio = $("path", svg);
    const caixa = $(".varal__lampadas", area);
    const chave = $(".interruptor", capa);
    const estado = $(".interruptor__estado", capa);
    const visor = $(".controle__visor", capa);
    const nome = $(".controle__nome", capa);
    let lampadas = [];
    let luzes = [];
    let ligado = false;
    let modo = 0;
    let atual = null;
    let ciclo = null;
    let largura = 0;

    /* Fio em vãos curvos entre ganchos; as lâmpadas ficam distribuídas pelo comprimento */
    function montar() {
      largura = area.clientWidth;
      const h = area.clientHeight;
      svg.setAttribute("viewBox", "0 0 " + largura + " " + h);
      const vaos = largura < 700 ? 2 : 3;
      const passo = (largura + 40) / vaos;
      let d = "M-20 8";
      for (let k = 0; k < vaos; k++) {
        const x0 = -20 + passo * k;
        d += " Q" + (x0 + passo / 2) + " " + h * 0.92 + " " + (x0 + passo) + " 8";
      }
      fio.setAttribute("d", d);
      const total = fio.getTotalLength();
      const n = Math.max(12, Math.round(largura / (largura < 700 ? 30 : 44)));
      caixa.innerHTML = Array.from({ length: n }, (_, i) => {
        const [cor, halo, apagada] = CORES[i % CORES.length];
        return '<span class="lampada" style="--cor:' + cor + ";--halo:" + halo + ";--apagada:" + apagada + '"><span class="lampada__luz"></span></span>';
      }).join("");
      lampadas = $$(".lampada", caixa);
      luzes = $$(".lampada__luz", caixa);
      lampadas.forEach((l, i) => {
        const p = fio.getPointAtLength((total * (i + 0.5)) / n);
        l.base = gsap.utils.random(-10, 10);
        gsap.set(l, { x: p.x, y: p.y - 2, rotation: l.base });
      });
    }

    /* Como num controlador de verdade, as lâmpadas pares e ímpares são dois canais */
    const canal = (par) => luzes.filter((_, i) => i % 2 === par);
    const PADROES = [
      null,
      () => gsap.fromTo(luzes, { opacity: BAIXO }, { opacity: 1, duration: 1.7, ease: "vaievem", stagger: { each: 0.08, repeat: -1 } }),
      () =>
        gsap.timeline({ repeat: -1 })
          .set(canal(0), { opacity: 1 }, 0)
          .set(canal(1), { opacity: BAIXO }, 0)
          .set(canal(0), { opacity: BAIXO }, 0.55)
          .set(canal(1), { opacity: 1 }, 0.55)
          .set(luzes, { opacity: 1 }, 1.1)
          .set(luzes, { opacity: BAIXO }, 1.65)
          .to({}, { duration: 0.35 }, 1.65),
      () => gsap.fromTo(luzes, { opacity: BAIXO }, { opacity: 1, duration: 1.5, ease: "sine.inOut", repeat: -1, yoyo: true }),
      () => gsap.fromTo(luzes, { opacity: BAIXO }, { opacity: 1, duration: 0.34, ease: "vaievem", stagger: { each: 0.055, repeat: -1, repeatDelay: Math.max(0.2, luzes.length * 0.0275 - 0.34) } }),
      () =>
        gsap.timeline({ repeat: -1, defaults: { duration: 1.8, ease: "sine.inOut" } })
          .fromTo(canal(0), { opacity: 1 }, { opacity: BAIXO }, 0)
          .fromTo(canal(1), { opacity: BAIXO }, { opacity: 1 }, 0)
          .to(canal(0), { opacity: 1 }, 1.8)
          .to(canal(1), { opacity: BAIXO }, 1.8),
      () => gsap.fromTo(luzes, { opacity: 1 }, { opacity: 0.1, duration: 0.18, ease: "vaievem", stagger: { each: 0.09, from: "random", repeat: -1, repeatDelay: 1.6 } }),
      () => gsap.to(luzes, { opacity: 1, duration: 0.3 })
    ];

    function parar() {
      if (ciclo) ciclo.kill();
      if (atual) atual.kill();
      ciclo = atual = null;
      gsap.killTweensOf(luzes);
    }
    /* Combinação passa pelos outros efeitos, um de cada vez */
    function rodar() {
      parar();
      if (D.reduzir) return gsap.set(luzes, { opacity: 1 });
      if (modo !== 0) return (atual = PADROES[modo]());
      let k = 1;
      const proximo = () => {
        if (atual) atual.kill();
        gsap.killTweensOf(luzes);
        atual = PADROES[k]();
        k = (k % 6) + 1;
        ciclo = gsap.delayedCall(3.4, proximo);
      };
      proximo();
    }
    function acender(animar) {
      ligado = true;
      raiz.classList.remove("apagado");
      chave.setAttribute("aria-checked", "true");
      estado.textContent = "Luzes acesas";
      parar();
      if (!animar || D.reduzir) return rodar();
      gsap.fromTo(luzes, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "pisca", stagger: 0.035, onComplete: rodar });
    }
    function apagar() {
      ligado = false;
      raiz.classList.add("apagado");
      chave.setAttribute("aria-checked", "false");
      estado.textContent = "Luzes apagadas";
      parar();
      gsap.to(luzes, { opacity: 0, duration: D.reduzir ? 0 : 0.3, stagger: D.reduzir ? 0 : { each: 0.008, from: "end" } });
    }

    chave.addEventListener("click", () => (ligado ? apagar() : acender(true)));
    $(".controle__modo", capa).addEventListener("click", () => {
      modo = (modo + 1) % MODOS.length;
      visor.textContent = modo + 1;
      nome.textContent = MODOS[modo];
      if (!D.reduzir) gsap.fromTo(visor, { opacity: 0.3 }, { opacity: 1, duration: 0.3, ease: "pisca" });
      ligado ? rodar() : acender(true);
    });

    /* A mão que passa perto balança as lâmpadas; empurrar para a direita gira no sentido anti-horário */
    let antes = null;
    capa.addEventListener("pointermove", (e) => {
      if (D.reduzir) return;
      const v = antes === null ? 0 : e.clientX - antes;
      antes = e.clientX;
      const r = area.getBoundingClientRect();
      if (e.clientY < r.top || e.clientY > r.bottom + 20 || Math.abs(v) < 2) return;
      lampadas.forEach((l) => {
        if (Math.abs(r.left + gsap.getProperty(l, "x") - e.clientX) > 46) return;
        gsap.to(l, {
          rotation: l.base + gsap.utils.clamp(-38, 38, -v * 1.4),
          duration: 0.16,
          ease: "power2.out",
          overwrite: true,
          onComplete: () => gsap.to(l, { rotation: l.base, duration: 2, ease: "elastic.out(1, 0.18)" })
        });
      });
    }, { passive: true });
    capa.addEventListener("pointerleave", () => (antes = null));

    let espera = 0;
    addEventListener("resize", () => {
      if (Math.abs(area.clientWidth - largura) < 2) return;
      clearTimeout(espera);
      espera = setTimeout(() => {
        parar();
        montar();
        if (ligado) {
          gsap.set(luzes, { opacity: 1 });
          rodar();
        }
      }, 160);
    });

    montar();
    /* Com movimento reduzido as lâmpadas ficam fixas, então o controle de modos sai de cena */
    if (D.reduzir) {
      $(".controle__modo", capa).hidden = true;
      $(".controle__nota", capa).textContent = "Seu sistema pede menos movimento, então as luzes ficam fixas. Os 8 modos estão no nosso Pisca-Pisca 200 Lâmpadas.";
      return acender(false);
    }
    /* A loja chega apagada e acende logo depois que as portas abrem */
    apagar();
    gsap.delayedCall(0.9, () => acender(true));
  }

  function economia() {
    $$(".economia__valor[data-ate]").forEach((el) => {
      const ate = Number(el.dataset.ate);
      const escrever = (v) => (el.textContent = Math.round(v).toLocaleString("pt-BR") + (el.dataset.sufixo || ""));
      if (D.reduzir) return;
      const o = { v: 0 };
      escrever(0);
      gsap.to(o, { v: ate, duration: 1.8, ease: "power3.out", onUpdate: () => escrever(o.v), scrollTrigger: { trigger: el, start: "top 88%", once: true } });
    });
  }

  D.aoIniciar(() => {
    varal();
    economia();
  });
})();
