/* Andar 6: os Reis Magos caminham até a manjedoura conforme os dias passam, guiados pela estrela. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  const DIAS = 36; /* de 1º de dezembro a 6 de janeiro */
  const NATAL = 23; /* 24 de dezembro, noite de Natal */
  const UM_DIA = 864e5;

  function caminho() {
    const secao = $(".caminho");
    const cena = $(".caminho__cena", secao);
    const svg = $(".caminho__ceu", cena);
    const rastro = $(".caminho__rastro", svg);
    const estrela = $(".caminho__estrela", cena);
    const luz = $(".caminho__luz", cena);
    const reis = $$(".caminho__rei", cena);
    const faixa = $("#dia-reis");
    const data = $(".caminho__data", secao);
    const status = $(".caminho__status", secao);
    const estreito = matchMedia("(max-width: 760px)");

    /* A temporada vai de 1º de dezembro a 6 de janeiro; em janeiro, ela começou no ano anterior */
    const agora = new Date();
    const hoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
    const ano = hoje.getMonth() === 0 && hoje.getDate() <= 6 ? hoje.getFullYear() - 1 : hoje.getFullYear();
    const diaDe = (i) => new Date(ano, 11, 1 + i);
    const desde = Math.round((hoje - diaDe(0)) / UM_DIA);
    const indiceHoje = gsap.utils.clamp(0, DIAS, desde);
    const longo = new Intl.DateTimeFormat("pt-BR", { day: "numeric", month: "long" });
    const porExtenso = (d) => longo.format(d).replace(/^1 de/, "1º de");
    const curto = (d) => String(d.getDate()).padStart(2, "0") + "/" + String(d.getMonth() + 1).padStart(2, "0");

    function frase(i) {
      const d = porExtenso(diaDe(i));
      if (i === 0) return d + ": os Reis Magos partem do Oriente, guiados pela estrela.";
      if (i < NATAL) return d + ": os Reis Magos já fizeram " + Math.round((i / DIAS) * 100) + "% do caminho.";
      if (i === NATAL) return d + ", noite de Natal: o Menino Jesus é colocado na manjedoura.";
      if (i < DIAS) return d + ": o Menino Jesus já está na manjedoura, e os Reis Magos chegam em " + dias(DIAS - i) + ".";
      return d + ", Dia de Reis: os Reis Magos chegam à manjedoura com seus presentes.";
    }
    const dias = (n) => n + (n === 1 ? " dia" : " dias");
    $(".caminho__hoje-txt", secao).textContent =
      "Hoje é " + porExtenso(hoje) +
      (desde < 0 ? ". A caminhada começa em " + dias(-desde) + ", no dia 1º de dezembro. Arraste para ver como ela avança."
        : desde === 0 ? ": a caminhada começa hoje."
        : desde < DIAS ? ": faltam " + dias(DIAS - desde) + " para os Reis Magos chegarem."
        : ", Dia de Reis.");

    /* Céu: estrelinhas em posições relativas, então não dependem do tamanho da cena */
    const sorte = (a, b) => (a + Math.random() * (b - a)).toFixed(1);
    $(".caminho__estrelas", svg).innerHTML = Array.from({ length: 40 }, () => '<circle cx="' + sorte(2, 98) + '%" cy="' + sorte(2, 58) + '%" r="' + sorte(0.6, 1.6) + '" style="animation-delay:-' + sorte(0, 3.6) + 's"/>').join("");

    /* Trajeto em porcentagem da cena: [x, y] de início, controle e fim da curva da estrela */
    const config = () =>
      estreito.matches
        ? { largura: 24, vao: 11, de: -20, ate: 12, curva: [[0.3, 0.22], [0.56, 0.04], [0.77, 0.27]] }
        : { largura: 16, vao: 7.5, de: -2, ate: 27, curva: [[0.3, 0.22], [0.55, -0.02], [0.78, 0.13]] };
    const estado = { t: 0, passo: 0 };
    let c = config();
    let total = 0;
    let luzAcesa = null;

    function desenhar() {
      const t = estado.t;
      const p = rastro.getPointAtLength(t * total);
      gsap.set(estrela, { x: p.x, y: p.y });
      gsap.set(rastro, { drawSVG: "0% " + t * 100 + "%" });
      /* Cada rei balança no próprio ritmo enquanto anda e assenta quando para */
      reis.forEach((r, k) => {
        const balanco = Math.abs(Math.sin((gsap.ticker.time * 2.6 + k * 0.33) * Math.PI));
        gsap.set(r, { xPercent: ((c.de + t * (c.ate - c.de) + k * c.vao) / c.largura) * 100, yPercent: -4 * estado.passo * balanco });
      });
      const acesa = t >= NATAL / DIAS - 0.001;
      if (acesa !== luzAcesa) {
        luzAcesa = acesa;
        gsap.to(luz, { opacity: acesa ? 1 : 0, duration: D.reduzir ? 0 : 0.6 });
      }
    }

    /* A curva é refeita em pixels a cada medida, para a estrela seguir o rastro exato */
    function medir() {
      c = config();
      const w = cena.clientWidth;
      const h = cena.clientHeight;
      svg.setAttribute("viewBox", "0 0 " + w + " " + h);
      const [p0, p1, p2] = c.curva.map(([x, y]) => [x * w, y * h]);
      rastro.setAttribute("d", "M" + p0 + " Q" + p1 + " " + p2);
      total = rastro.getTotalLength();
      desenhar();
    }

    let caminhada = null;
    function irPara(i, animar) {
      const alvo = i / DIAS;
      data.textContent = curto(diaDe(i));
      status.textContent = frase(i);
      faixa.value = i;
      faixa.setAttribute("aria-valuetext", porExtenso(diaDe(i)));
      if (caminhada) caminhada.kill();
      if (!animar || D.reduzir) {
        gsap.killTweensOf(estado);
        estado.t = alvo;
        estado.passo = 0;
        return desenhar();
      }
      gsap.to(estado, { passo: 1, duration: 0.2, overwrite: "auto", onUpdate: desenhar });
      caminhada = gsap.to(estado, {
        t: alvo,
        duration: gsap.utils.clamp(0.4, 3.5, Math.abs(alvo - estado.t) * 6),
        ease: "sine.inOut",
        onUpdate: desenhar,
        onComplete: () => gsap.to(estado, { passo: 0, duration: 0.3, overwrite: "auto", onUpdate: desenhar })
      });
    }

    faixa.addEventListener("input", () => irPara(Number(faixa.value), true));
    faixa.addEventListener("input", () => faixa.classList.remove("convite"), { once: true });
    $(".caminho__hoje", secao).addEventListener("click", () => irPara(indiceHoje, true));
    let espera = 0;
    addEventListener("resize", () => {
      clearTimeout(espera);
      espera = setTimeout(medir, 120);
    });

    medir();
    if (D.reduzir) return irPara(indiceHoje, false);
    irPara(0, false);
    /* Ao chegar na cena, os reis andam até a posição de hoje; antes de dezembro, o controle pisca um convite */
    ScrollTrigger.create({
      trigger: cena,
      start: "top 65%",
      once: true,
      onEnter: () => (indiceHoje > 0 ? irPara(indiceHoje, true) : faixa.classList.add("convite"))
    });
  }

  D.aoIniciar(caminho);
})();
