/* Navegação, painel do elevador, portas de vidro, abertura e rodapé. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  const andarAtual = () => {
    const v = document.documentElement.dataset.andar;
    return v ? Number(v) : 0;
  };
  const nomeDoAndar = (n) => {
    if (!n) return "Térreo";
    const a = D.andares.find((x) => x.n === n);
    return a ? a.nome : "Térreo";
  };
  const seta = (de, para) => (para >= de ? "▲" : "▼");
  const rotulo = (n) => (n ? String(n) : "T");

  const paginaAtual = () => {
    const f = location.pathname.split("/").pop();
    return f === "" ? "index.html" : f;
  };

  function montarNav() {
    const n = andarAtual();
    const pag = paginaAtual();
    const inicio = pag === "index.html";
    const links = [
      [inicio ? "#ofertas" : "index.html#ofertas", "Ofertas"],
      [inicio ? "#encontre" : "index.html#encontre", "Encontre um presente"],
      ["sobre.html", "Sobre"],
      ["contato.html", "Contato"]
    ];
    const nav = document.createElement("header");
    nav.className = "nav";
    nav.innerHTML =
      '<a class="nav__logo" href="index.html" aria-label="Departal, página inicial">' + D.letreiroSVG() + '<span class="nav__chapeu">' + D.gorro + "</span></a>" +
      '<nav class="nav__links" aria-label="Principal">' + links.map(([h, t]) => '<a href="' + h + '"' + (h === pag ? ' aria-current="page"' : "") + ">" + t + "</a>").join("") + "</nav>" +
      '<button class="nav__sacola" type="button" aria-label="Abrir sacola">' + D.icones.sacola + '<span class="nav__conta" hidden>0</span></button>' +
      '<button class="nav__andar" type="button" aria-haspopup="dialog" aria-expanded="false"><span class="nav__visor num-led">' + rotulo(n) + "</span><span>Andares</span></button>";
    document.body.prepend(nav);

    const pular = document.createElement("a");
    pular.className = "pular";
    pular.href = "#conteudo";
    pular.textContent = "Pular para o conteúdo";
    document.body.prepend(pular);
  }

  function montarPainel() {
    const n = andarAtual();
    const p = document.createElement("div");
    p.className = "painel";
    p.setAttribute("role", "dialog");
    p.setAttribute("aria-modal", "true");
    p.setAttribute("aria-label", "Andares da loja");
    const linha = (num, nome, frase, href, foto) =>
      '<a class="painel__andar" href="' + href + '" data-para="' + num + '" data-nome="' + nome + '"' + (num === n ? ' aria-current="page"' : "") + ">" +
      '<span class="painel__botao">' + rotulo(num) + "</span>" +
      '<span class="painel__nome"><strong>' + nome + "</strong><span>" + frase + "</span></span>" +
      (foto ? '<img class="painel__mini" src="' + D.foto(foto) + '" alt="" width="62" height="62" loading="lazy">' : "<span></span>") +
      "</a>";
    p.innerHTML =
      '<div class="painel__veu"></div>' +
      '<div class="painel__caixa">' +
      '<div class="painel__topo"><div class="painel__visor num-led"><span class="painel__seta">' + seta(0, n) + '</span><span class="painel__txt">' + rotulo(n) + " " + nomeDoAndar(n) + "</span></div>" +
      '<button class="painel__fechar" type="button" aria-label="Fechar andares">' + D.icones.fechar + "</button></div>" +
      '<nav class="painel__lista" aria-label="Andares">' +
      D.andares.map((a) => linha(a.n, a.nome, a.frase, a.pagina, a.capa)).join("") +
      linha(0, "Térreo", "A vitrine e as ofertas da semana.", "index.html", "kit-decoracao") +
      "</nav>" +
      '<div class="painel__extras"><a href="index.html#ofertas">Ofertas</a><a href="index.html#encontre">Encontre um presente</a><a href="sobre.html">Sobre</a><a href="contato.html">Contato</a></div>' +
      "</div>";
    document.body.append(p);

    const veu = $(".painel__veu", p);
    const caixa = $(".painel__caixa", p);
    const txt = $(".painel__txt", p);
    const setaEl = $(".painel__seta", p);
    const abrirBtn = $(".nav__andar");
    const linhas = $$(".painel__andar", p);
    const padrao = rotulo(n) + " " + nomeDoAndar(n);

    const tl = gsap.timeline({ paused: true, defaults: { ease: "chega" } });
    tl.set(p, { visibility: "visible" })
      .to(veu, { opacity: 1, duration: 0.32, ease: "none" }, 0)
      .to(caixa, { x: 0, xPercent: -102 * 0, duration: 0.5 }, 0)
      .from(linhas, { x: 26, opacity: 0, duration: 0.34, stagger: 0.03 }, 0.1);
    gsap.set(caixa, { x: "102%" });

    let aberto = false;
    let antes = null;
    function abrir() {
      aberto = true;
      antes = document.activeElement;
      abrirBtn.setAttribute("aria-expanded", "true");
      document.documentElement.style.overflow = "hidden";
      D.reduzir ? tl.progress(1) : tl.timeScale(1).play();
      $(".painel__fechar", p).focus({ preventScroll: true });
    }
    function fechar() {
      aberto = false;
      abrirBtn.setAttribute("aria-expanded", "false");
      document.documentElement.style.overflow = "";
      D.reduzir ? tl.progress(0) : tl.timeScale(1.5).reverse();
      if (antes) antes.focus({ preventScroll: true });
    }
    abrirBtn.addEventListener("click", abrir);
    $(".painel__fechar", p).addEventListener("click", fechar);
    veu.addEventListener("click", fechar);
    D.fecharPainel = () => aberto && fechar();

    addEventListener("keydown", (e) => {
      if (!aberto) return;
      if (e.key === "Escape") fechar();
      if (e.key === "Tab") {
        const foco = $$("a, button", caixa).filter((f) => f.offsetParent !== null);
        const a = foco[0];
        const z = foco[foco.length - 1];
        if (e.shiftKey && document.activeElement === a) {
          e.preventDefault();
          z.focus();
        } else if (!e.shiftKey && document.activeElement === z) {
          e.preventDefault();
          a.focus();
        }
      }
    });

    const mostrar = (t, de, para) => {
      setaEl.textContent = seta(de, para);
      if (D.reduzir) txt.textContent = t;
      else gsap.to(txt, { duration: 0.32, scrambleText: { text: t, chars: "0123456789", speed: 1 }, overwrite: true, ease: "none" });
    };
    linhas.forEach((l) => {
      const ver = () => mostrar(rotulo(Number(l.dataset.para)) + " " + l.dataset.nome, n, Number(l.dataset.para));
      l.addEventListener("pointerenter", ver);
      l.addEventListener("focus", ver);
      l.addEventListener("pointerleave", () => mostrar(padrao, 0, n));
    });
  }

  /* Portas de vidro entre as páginas */
  function montarPortas() {
    const p = document.createElement("div");
    p.className = "portas";
    p.setAttribute("aria-hidden", "true");
    p.innerHTML = '<div class="porta porta--e"></div><div class="porta porta--d"></div><div class="portas__flash"></div><div class="portas__visor num-led"><span class="seta"></span><span class="txt"></span></div>';
    document.body.append(p);
    const e = $(".porta--e", p);
    const d = $(".porta--d", p);
    const visor = $(".portas__visor", p);
    const txt = $(".txt", p);
    const s = $(".seta", p);
    const flash = $(".portas__flash", p);

    function fecharEIr(href, alvo) {
      const de = andarAtual();
      D.sessao.gravar("dp-porta", String(alvo));
      D.sessao.gravar("dp-de", String(de));
      p.classList.add("ativa");
      if (D.reduzir) {
        location.href = href;
        return;
      }
      gsap.set(p, { visibility: "visible" });
      gsap.set(e, { xPercent: -100 });
      gsap.set(d, { xPercent: 100 });
      s.textContent = seta(de, alvo);
      txt.textContent = rotulo(de);
      const tl = gsap.timeline({ onComplete: () => (location.href = href) });
      tl.to([e, d], { xPercent: 0, duration: 0.52, ease: "power3.inOut" }, 0).to(visor, { opacity: 1, duration: 0.2 }, 0.3);
      const passos = Math.abs(alvo - de);
      const dir = alvo >= de ? 1 : -1;
      for (let k = 1; k <= passos; k++) {
        tl.call(() => (txt.textContent = rotulo(de + dir * k)), null, 0.42 + (k * 0.26) / Math.max(1, passos));
      }
      tl.to({}, { duration: 0.1 });
    }
    D.irPara = (href) => {
      const url = new URL(href, location.href);
      const andar = D.andares.find((x) => x.pagina === url.pathname.split("/").pop());
      fecharEIr(url.href, andar ? andar.n : 0);
    };

    function abrirChegada() {
      const raiz = document.documentElement;
      const alvo = D.sessao.ler("dp-porta");
      D.sessao.tirar("dp-porta");
      D.sessao.tirar("dp-de");
      if (alvo === null) {
        raiz.classList.remove("portas-fechadas");
        return false;
      }
      if (D.reduzir) {
        raiz.classList.remove("portas-fechadas");
        return true;
      }
      gsap.set(p, { visibility: "visible" });
      gsap.set(visor, { opacity: 1 });
      s.textContent = "";
      txt.textContent = rotulo(Number(alvo)) + " " + nomeDoAndar(Number(alvo));
      raiz.classList.remove("portas-fechadas");
      gsap.timeline({ delay: 0.16, onComplete: () => gsap.set(p, { visibility: "hidden" }) })
        .to(visor, { opacity: 0, duration: 0.22 }, 0.18)
        .to(flash, { opacity: 1, duration: 0.2, ease: "none" }, 0.22)
        .to([e], { xPercent: -100, duration: 0.82, ease: "power3.inOut" }, 0.3)
        .to([d], { xPercent: 100, duration: 0.82, ease: "power3.inOut" }, 0.3)
        .to(flash, { opacity: 0, duration: 0.5, ease: "none" }, 0.52);
      return true;
    }

    addEventListener("pageshow", (ev) => {
      if (ev.persisted) {
        gsap.set(p, { visibility: "hidden" });
        gsap.set([e, d], { xPercent: 0 });
        gsap.set(flash, { opacity: 0 });
        p.classList.remove("ativa");
        document.documentElement.classList.remove("portas-fechadas");
      }
    });

    document.addEventListener("click", (ev) => {
      const a = ev.target.closest("a[href]");
      if (!a || ev.defaultPrevented || a.target || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey || ev.button) return;
      const bruto = a.getAttribute("href");
      if (/^(mailto|tel):/.test(bruto)) return;
      const url = new URL(a.href, location.href);
      const mesma = url.pathname === location.pathname;
      if (mesma && url.hash) {
        const dest = $(url.hash);
        if (dest) {
          ev.preventDefault();
          if (D.fecharPainel) D.fecharPainel();
          dest.scrollIntoView({ behavior: D.reduzir ? "auto" : "smooth" });
        }
        return;
      }
      if (!/\.html$/.test(url.pathname) || url.protocol !== location.protocol) return;
      ev.preventDefault();
      const nome = url.pathname.split("/").pop();
      const andar = D.andares.find((x) => x.pagina === nome);
      fecharEIr(a.href, andar ? andar.n : 0);
    });
    return abrirChegada;
  }

  /* Abertura: o letreiro acende letra por letra na primeira visita */
  function abertura() {
    if (D.reduzir || D.sessao.ler("dp-visto")) return Promise.resolve();
    D.sessao.gravar("dp-visto", "1");
    return new Promise((pronto) => {
      const a = document.createElement("div");
      a.className = "abertura";
      a.setAttribute("aria-hidden", "true");
      a.innerHTML = '<div class="abertura__sinal">' + D.letreiroSVG() + '<span class="abertura__chapeu">' + D.gorro + "</span></div>";
      document.body.append(a);
      const letras = $$("path", a).filter((x) => !x.closest(".abertura__chapeu"));
      const chapeu = $(".abertura__chapeu", a);
      const brilho = "drop-shadow(0 0 6px rgba(232,40,63,.9)) drop-shadow(0 0 26px rgba(232,40,63,.55))";
      const tl = gsap.timeline({
        onComplete: () => {
          a.remove();
        }
      });
      letras.forEach((l, i) => {
        const t = 0.1 + i * 0.1;
        tl.to(l, { fill: "#e8283f", duration: 0.05, ease: "none" }, t)
          .to(l, { fill: "#5a1420", duration: 0.04, ease: "none" }, t + 0.06)
          .to(l, { fill: "#e8283f", duration: 0.05, ease: "none" }, t + 0.11);
      });
      tl.to($("svg", a), { filter: brilho, duration: 0.3 }, 0.8);
      tl.fromTo(chapeu, { y: -160, opacity: 0, rotation: -24 }, { y: 0, opacity: 1, rotation: 0, duration: 0.62, ease: "bounce.out" }, 0.9);
      tl.to(chapeu, { rotation: 6, duration: 0.14, ease: "sine.inOut", yoyo: true, repeat: 1 }, 1.5);
      tl.call(pronto, null, 1.72);
      tl.to(a, { opacity: 0, duration: 0.5 }, 1.72);
    });
  }

  function montarRodape() {
    const f = document.createElement("footer");
    f.className = "rodape";
    f.innerHTML =
      '<canvas class="rodape__neve" aria-hidden="true"></canvas>' +
      '<div class="envolve rodape__grade">' +
      '<p class="rodape__carimbo">Uma loja feita por pessoas, para pessoas. Todos merecem celebrar, independentemente do orçamento.</p>' +
      '<div><h2>Andares</h2><ul>' + D.andares.slice().reverse().map((a) => '<li><a href="' + a.pagina + '">' + a.nome + "</a></li>").join("") + "</ul></div>" +
      '<div><h2>Loja</h2><ul><li><a href="index.html#ofertas">Ofertas</a></li><li><a href="index.html#encontre">Encontre um presente</a></li><li><a href="sobre.html">Sobre a Departal</a></li><li><a href="contato.html">Fale com a gente</a></li></ul></div>' +
      '<div><h2>Atendimento</h2><ul><li>Segunda a sábado, 9h às 18h</li><li>Domingo, 10h às 16h</li><li><a href="tel:+5519923666666">(19) 92366-6666</a></li><li><a href="mailto:Departal.org@gmail.com">Departal.org@gmail.com</a></li></ul></div>' +
      "</div>" +
      '<div class="envolve"><div class="rodape__letreiro" aria-hidden="true">' + D.letreiroSVG() + '<img class="rodape__guirlanda" src="images/marca/guirlanda.webp" alt="" width="2400" height="241" loading="lazy"></div>' +
      '<p class="rodape__base"><span>© 2026 Departal</span><span>Site demonstrativo: compras e formulários são simulados.</span></p></div>';
    document.body.append(f);
    neveRodape($(".rodape__neve", f), f);
  }

  function neveRodape(cv, area) {
    if (D.reduzir) return;
    const ctx = cv.getContext("2d");
    let w, h, flocos, ativo = false, raf = 0;
    const criar = () => {
      w = cv.width = area.clientWidth;
      h = cv.height = area.clientHeight;
      flocos = Array.from({ length: Math.min(70, Math.round(w / 18)) }, () => ({ x: Math.random() * w, y: Math.random() * h, r: 0.6 + Math.random() * 1.7, v: 0.25 + Math.random() * 0.6, f: Math.random() * 6 }));
    };
    const quadro = () => {
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "rgba(246,239,226,.72)";
      ctx.beginPath();
      flocos.forEach((f) => {
        f.y += f.v;
        f.f += 0.012;
        f.x += Math.sin(f.f) * 0.3;
        if (f.y > h) f.y = -4;
        ctx.moveTo(f.x + f.r, f.y);
        ctx.arc(f.x, f.y, f.r, 0, 6.283);
      });
      ctx.fill();
      if (ativo) raf = requestAnimationFrame(quadro);
    };
    new IntersectionObserver((es) => {
      ativo = es[0].isIntersecting;
      if (ativo) {
        if (!flocos) criar();
        raf = requestAnimationFrame(quadro);
      } else cancelAnimationFrame(raf);
    }).observe(area);
    addEventListener("resize", () => flocos && criar());
  }

  function ambiente() {
    const g = document.createElement("div");
    g.className = "grao";
    g.setAttribute("aria-hidden", "true");
    document.body.append(g);
    if (D.fino && !D.reduzir) {
      const l = document.createElement("div");
      l.className = "luz-mao";
      l.setAttribute("aria-hidden", "true");
      document.body.append(l);
      const x = gsap.quickTo(l, "x", { duration: 0.9, ease: "power3" });
      const y = gsap.quickTo(l, "y", { duration: 0.9, ease: "power3" });
      addEventListener("pointermove", (e) => {
        x(e.clientX);
        y(e.clientY);
      }, { passive: true });
    }
  }

  D.aoIniciar(() => {
    montarNav();
    montarPainel();
    const chegar = montarPortas();
    montarRodape();
    ambiente();
    const veioDePorta = chegar();
    D.abertura = veioDePorta ? Promise.resolve() : document.body.dataset.pagina === "inicio" ? abertura() : Promise.resolve();
  });
})();
