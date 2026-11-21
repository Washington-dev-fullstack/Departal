/* Núcleo: utilidades compartilhadas por todas as páginas. */
(function () {
  const D = (window.Departal = window.Departal || {});

  gsap.registerPlugin(ScrollTrigger, Flip, CustomEase, SplitText, DrawSVGPlugin, ScrambleTextPlugin);
  CustomEase.create("loja", "0.4,0,0.2,1");
  CustomEase.create("chega", "0.16,1,0.3,1");
  /* Lâmpada ligando: acende, falha e firma */
  CustomEase.create("pisca", "M0,0 L0.16,0.86 L0.24,0.1 L0.38,1 L0.5,0.42 L0.64,1 L1,1");
  /* Vai e volta: o valor sobe e retorna ao ponto de partida no mesmo tween */
  CustomEase.create("vaievem", "M0,0 C0.18,0 0.3,1 0.5,1 0.7,1 0.82,0 1,0");
  gsap.defaults({ ease: "loja", duration: 0.5 });

  D.reduzir = matchMedia("(prefers-reduced-motion: reduce)").matches;
  D.fino = matchMedia("(hover: hover) and (pointer: fine)").matches;
  D.$ = (s, r) => (r || document).querySelector(s);
  D.$$ = (s, r) => Array.from((r || document).querySelectorAll(s));

  const fmt = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
  D.moeda = (v) => fmt.format(v).replace(/ /g, " ");
  D.desconto = (p) => (p.de ? Math.round((1 - p.preco / p.de) * 100) : 0);
  D.produto = (id) => D.produtos.find((p) => p.id === id);
  D.foto = (id) => "images/produtos/" + id + ".webp";

  D.ler = function (chave, padrao) {
    try {
      const v = localStorage.getItem(chave);
      return v === null ? padrao : JSON.parse(v);
    } catch (e) {
      return padrao;
    }
  };
  D.gravar = function (chave, valor) {
    try {
      localStorage.setItem(chave, JSON.stringify(valor));
    } catch (e) {
      /* sem armazenamento: a sacola dura até a página fechar */
    }
  };
  D.sessao = {
    ler(c) {
      try { return sessionStorage.getItem(c); } catch (e) { return null; }
    },
    gravar(c, v) {
      try { sessionStorage.setItem(c, v); } catch (e) { /* segue sem transição */ }
    },
    tirar(c) {
      try { sessionStorage.removeItem(c); } catch (e) { /* idem */ }
    }
  };

  D.diasParaNatal = function () {
    const agora = new Date();
    const hoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
    let natal = new Date(agora.getFullYear(), 11, 25);
    if (hoje > natal) natal = new Date(agora.getFullYear() + 1, 11, 25);
    return Math.round((natal - hoje) / 86400000);
  };

  /* Ícones desenhados para a loja: traço único, sem emojis */
  const i = (corpo) => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + corpo + "</svg>";
  D.icones = {
    sacola: i('<path d="M5 8h14l1 13H4L5 8Z"/><path d="M8.5 10V6.5a3.5 3.5 0 0 1 7 0V10"/>'),
    fechar: i('<path d="M6 6l12 12M18 6 6 18"/>'),
    mais: i('<path d="M12 5v14M5 12h14"/>'),
    menos: i('<path d="M5 12h14"/>'),
    lixeira: i('<path d="M5 7h14M10 7V4.5h4V7M7 7l1 13h8l1-13"/>'),
    medida: i('<path d="M3 16 16 3l5 5L8 21l-5-5Z"/><path d="m7 12 2 2M10 9l2 2M13 6l2 2"/>'),
    led: i('<path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3Z"/><path d="M10 19h4M10.5 22h3"/>'),
    cor: i('<circle cx="12" cy="12" r="9"/><circle cx="8" cy="10" r="1.2"/><circle cx="12" cy="7.5" r="1.2"/><circle cx="16" cy="10" r="1.2"/><path d="M12 21c-1.5-2 0-4 2-4h2.5"/>'),
    controle: i('<rect x="8" y="3" width="8" height="18" rx="2.5"/><path d="M12 7v.01M10 12h4M10 15.5h4"/>'),
    agua: i('<path d="M12 3s6.5 7 6.5 11.5a6.5 6.5 0 0 1-13 0C5.500 10 12 3 12 3Z"/>'),
    modos: i('<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>'),
    cabo: i('<path d="M9 3v5M15 3v5M7 8h10v3a5 5 0 0 1-10 0V8ZM12 16v2a3 3 0 0 0 3 3h3"/>'),
    sensor: i('<circle cx="12" cy="12" r="2"/><path d="M7.800 16.200a6 6 0 0 1 0-8.400M16.200 7.800a6 6 0 0 1 0 8.400M5 19a10 10 0 0 1 0-14M19 5a10 10 0 0 1 0 14"/>'),
    pecas: i('<rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.500"/><rect x="3" y="13" width="8" height="8" rx="1.500"/><rect x="13" y="13" width="8" height="8" rx="1.500"/>'),
    metal: i('<path d="m14 4 6 6-3 3-6-6 3-3ZM11 7l-7 7a2 2 0 0 0 0 3l3 3a2 2 0 0 0 3 0l7-7"/>'),
    aroma: i('<path d="M9 21h6M10 21V11h4v10M12 11V8M8 3c0 2 2 2 2 4M12 3c0 2 2 2 2 4M16 3c0 2 2 2 2 4"/>'),
    pessoas: i('<circle cx="8.500" cy="8" r="3.500"/><path d="M2.500 20c.5-4 3-6 6-6s5.500 2 6 6"/><circle cx="17" cy="9.500" r="2.500"/><path d="M16.500 14.500c2.800.2 4.600 2 5 5"/>'),
    tecido: i('<path d="M8 3 3 7l3 3 2-1.500V21h8V8.500l2 1.500 3-3-5-4c-1 1.500-2.500 2-4 2s-3-.5-4-2Z"/>'),
    casa: i('<path d="m3 11 9-8 9 8M6 9v12h12V9M10 21v-6h4v6"/>'),
    laco: i('<path d="M12 12C9 7 4 6 3 8s0 7 2 7 5-1 7-3ZM12 12c3-5 8-6 9-4s0 7-2 7-5-1-7-3ZM12 12l-3 9M12 12l3 9"/>'),
    pinho: i('<path d="m12 2 4 6h-2.500l4 5.500H15l4 5.500H5l4-5.500H6.500l4-5.500H8l4-6ZM12 19v3"/>'),
    bateria: i('<rect x="3" y="8" width="16" height="9" rx="2"/><path d="M21 11v3M7 11v3M11 11v3"/>'),
    brilho: i('<path d="m12 3 1.800 5.200L19 10l-5.200 1.800L12 17l-1.800-5.200L5 10l5.200-1.800L12 3ZM19 16l.8 2.200L22 19l-2.200.8L19 22l-.8-2.200L16 19l2.200-.8L19 16Z"/>'),
    madeira: i('<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.700 3.600 3 8 3s8-1.300 8-3V6"/><path d="M9 6c0-.8 1.300-1 3-1"/>'),
    relogio: i('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    estrela: i('<path d="m12 3 2.700 5.800 6.300.8-4.600 4.300 1.200 6.200L12 17.100 6.400 20.100l1.200-6.200L3 9.600l6.300-.8L12 3Z"/>'),
    caminhao: i('<path d="M2 7h12v10H2zM14 10h4l4 4v3h-8z"/><circle cx="7" cy="18" r="2"/><circle cx="17.500" cy="18" r="2"/>'),
    troca: i('<path d="M4 9h13l-3-3M20 15H7l3 3"/>'),
    presente: i('<path d="M4 10h16v11H4zM3 7h18v3H3zM12 7v14M12 7S10.500 3 8 3a2 2 0 0 0 0 4h4ZM12 7s1.500-4 4-4a2 2 0 0 1 0 4h-4Z"/>'),
    confere: i('<path d="m5 12.500 4.500 4.500L19 7"/>'),
    etiqueta: i('<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9-9-9Z"/><circle cx="7.500" cy="7.500" r="1.500"/>'),
    pino: i('<path d="M12 21s-6.5-6.1-6.5-11.3a6.5 6.5 0 0 1 13 0C18.5 14.9 12 21 12 21Z"/><circle cx="12" cy="9.6" r="2.4"/>'),
    telefone: i('<path d="M6.6 3.5h2.9l1.6 4.2-2 1.4a11.5 11.5 0 0 0 5.8 5.8l1.4-2 4.2 1.6v2.9a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4.6 5.7a2 2 0 0 1 2-2.2Z"/>'),
    carta: i('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>'),
    musica: i('<path d="M9 18V5l11-2v13"/><circle cx="6.500" cy="18" r="2.500"/><circle cx="17.500" cy="16" r="2.500"/>')
  };

  /* Gorro redesenhado do seu favicon */
  D.gorro = '<svg viewBox="0 0 132 96" aria-hidden="true"><path d="M13 62C16 34 36 9 67 7c23-1 39 15 44 37 2 7 3 13 3 18h-11c-1-14-9-25-20-27 7 9 10 19 8 31-23 9-53 8-78-4Z" fill="#c8102e"/><path d="M60 15c16-3 34 7 41 25-9-12-23-18-41-25Z" fill="#8e0b22"/><path d="M6 58c29 14 62 15 88 2 5-2 8 1 8 6l-1 9c-1 5-4 7-8 8-30 7-60 5-87-7-5-2-6-6-5-11l1-4c0-3 2-4 4-3Z" fill="#f6efe2"/><path d="M12 73c26 11 54 13 82 7-27 9-59 6-85-6l3-1Z" fill="#cfc9ba"/><circle cx="111" cy="73" r="12" fill="#f6efe2"/><circle cx="108" cy="70" r="5" fill="#fff"/></svg>';

  /* Letreiro DEPARTAL em vetor, letra por letra */
  D.letreiroSVG = function () {
    const L = D.letreiro;
    const letras = L.letras.map((l) => '<path d="' + l.d + '"/>').join("");
    return '<svg viewBox="0 0 ' + L.largura + " " + L.altura + '" role="img" aria-label="Departal">' + letras + "</svg>";
  };

  /* Revela os produtos da prateleira como se a luz da vitrine acendesse */
  D.acender = function (raiz) {
    const alvos = D.$$(".acende", raiz || document);
    if (!("IntersectionObserver" in window) || D.reduzir) {
      alvos.forEach((a) => a.classList.add("aceso"));
      return;
    }
    const io = new IntersectionObserver(
      (es) => {
        es.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("aceso");
            io.unobserve(e.target);
          }
        });
      },
      { rootMargin: "0px 0px -6% 0px", threshold: 0.12 }
    );
    alvos.forEach((a) => io.observe(a));
  };

  /* Peças penduradas viram pêndulos amortecidos: a brisa mantém um vaivém leve, o ponteiro que cruza a peça
     dá um empurrão e o fio mais longo balança mais devagar, como um pêndulo de verdade */
  D.pendulo = function (corpo, opcoes) {
    const o = Object.assign({ brisa: 0.7, ritmo: 0.27, forca: 0.035, limite: 14, amortece: 0.06 }, opcoes);
    const girar = gsap.quickSetter(corpo, "rotation", "deg");
    const p = { a: 0, v: 0, w: 4 };
    const medir = () => {
      const L = (o.comprimento ? o.comprimento() : corpo.offsetHeight) * 0.8;
      p.w = 2 * Math.PI * gsap.utils.clamp(0.4, 1, 0.95 * Math.sqrt(150 / Math.max(L, 60)));
    };
    medir();
    addEventListener("resize", medir);

    let ativo = true;
    let t = 0;
    ScrollTrigger.create({ trigger: o.area, start: "top bottom", end: "bottom top", onToggle: (s) => (ativo = s.isActive) });
    gsap.ticker.add((tempo, delta) => {
      if (!ativo) return;
      const dt = Math.min(delta, 50) / 1000;
      t += dt;
      const brisa = o.brisa * Math.sin(t * o.ritmo * 2 * Math.PI);
      p.v += (-p.w * p.w * (p.a - brisa) - 2 * o.amortece * p.w * p.v) * dt;
      p.a = gsap.utils.clamp(-o.limite, o.limite, p.a + p.v * dt);
      girar(p.a);
    });

    let ux = 0;
    let ut = 0;
    let dentro = false;
    o.area.addEventListener("pointermove", (e) => {
      const dt = Math.max(8, e.timeStamp - ut) / 1000;
      const vx = ut ? (e.clientX - ux) / dt : 0;
      ux = e.clientX;
      ut = e.timeStamp;
      const r = o.alvo.getBoundingClientRect();
      const agora = e.clientX > r.left && e.clientX < r.right && e.clientY > r.top && e.clientY < r.bottom;
      if (agora && !dentro) p.v += gsap.utils.clamp(-60, 60, -vx * o.forca);
      dentro = agora;
    }, { passive: true });
    o.area.addEventListener("pointerleave", () => {
      ut = 0;
      dentro = false;
    });
    return { empurrar: (v) => (p.v += v) };
  };

  const prontos = [];
  D.aoIniciar = (fn) => prontos.push(fn);
  D.iniciar = function () {
    D.$$("[data-icone]").forEach((el) => el.insertAdjacentHTML("afterbegin", D.icones[el.dataset.icone]));
    prontos.forEach((fn) => fn());
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => ScrollTrigger.refresh());
    addEventListener("load", () => ScrollTrigger.refresh());
  };
})();
