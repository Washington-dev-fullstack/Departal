/* Prateleiras, cartões de produto, filtros e visão rápida. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  D.doAndar = (id, secao) => D.produtos.filter((p) => p.andar === id && (secao ? p.secao === secao : !p.secao));

  const precoHTML = (p) => '<p class="preco">' + (p.de ? '<s aria-label="Preço anterior ' + D.moeda(p.de) + '">' + D.moeda(p.de) + "</s>" : "") + "<strong>" + D.moeda(p.preco) + "</strong></p>";

  const specHTML = (p) =>
    p.spec ? '<ul class="spec">' + p.spec.map(([ic, txt]) => "<li>" + (D.icones[ic] || "") + txt + "</li>").join("") + "</ul>" : "";

  let grupo = 0;
  const tamanhosHTML = (p) => {
    if (!p.tamanhos) return "";
    const nome = "tam-" + p.id + "-" + ++grupo;
    return (
      '<div class="tam" role="radiogroup" aria-label="Tamanho de ' + p.nome + '">' +
      p.tamanhos.map((t) => '<label><input type="radio" name="' + nome + '" value="' + t + '"><span>' + t + "</span></label>").join("") +
      '</div><p class="tam__aviso" role="status"></p>'
    );
  };

  const etiqueta = (p) => {
    const d = D.desconto(p);
    if (!d && !p.selo) return "";
    return (
      '<span class="etiqueta">' +
      (d ? '<span class="etiqueta__led num-led"><span class="so-leitor">' + d + '% de desconto</span><span aria-hidden="true">-' + d + "%</span></span>" : "") +
      (p.selo ? '<span class="etiqueta__txt">' + p.selo + "</span>" : "") +
      "</span>"
    );
  };

  const botao = (p) =>
    '<button class="btn btn--pequeno produto__add" type="button" data-add="' + p.id + '" aria-label="Adicionar ' + p.nome.replace(/"/g, "") + ' à sacola">' +
    '<span class="rotulo">Adicionar<span class="longo"> à sacola</span></span></button>';

  D.cartao = function (p, i) {
    return (
      '<li class="produto acende" data-id="' + p.id + '" style="--i:' + (i % 4) + '">' +
      '<button class="produto__olhar" type="button" aria-label="Ver detalhes de ' + p.nome.replace(/"/g, "") + '">' +
      '<span class="produto__palco">' + etiqueta(p) +
      '<img class="produto__foto" src="' + D.foto(p.id) + '" alt="" width="800" height="800" loading="lazy" decoding="async"></span></button>' +
      '<div class="produto__info"><h3 class="produto__nome">' + p.nome + "</h3>" +
      '<p class="produto__desc">' + p.desc + "</p>" + specHTML(p) +
      '<div class="produto__base">' + precoHTML(p) + tamanhosHTML(p) + botao(p) + "</div></div></li>"
    );
  };

  D.prateleira = function (alvo, lista) {
    const el = typeof alvo === "string" ? $(alvo) : alvo;
    el.classList.add("prateleira");
    el.innerHTML = lista.map(D.cartao).join("");
    D.acender(el);
    return el;
  };

  /* Adicionar: roupas pedem tamanho antes */
  function adicionar(b) {
    const p = D.produto(b.dataset.add);
    const raiz = b.closest(".produto, .olhar__txt");
    let tam = null;
    if (p.tamanhos) {
      const m = $("input:checked", raiz);
      if (!m) {
        $(".tam__aviso", raiz).textContent = "Escolha um tamanho";
        if (!D.reduzir) gsap.fromTo($(".tam", raiz), { x: -7 }, { x: 0, duration: 0.36, ease: "elastic.out(1.4,0.28)" });
        return;
      }
      tam = m.value;
    }
    const foto = b.closest(".produto") ? $(".produto__foto", raiz) : $(".olhar__foto");
    D.sacola.adicionar(p.id, tam, foto);
    const rotulo = $(".rotulo", b);
    const antes = rotulo.innerHTML;
    b.classList.add("feito");
    rotulo.textContent = "Adicionado";
    b.disabled = true;
    setTimeout(() => {
      b.classList.remove("feito");
      rotulo.innerHTML = antes;
      b.disabled = false;
    }, 1400);
  }

  /* Visão rápida */
  let olhar, tlOlhar, antes;
  function montarOlhar() {
    olhar = document.createElement("div");
    olhar.className = "olhar";
    olhar.setAttribute("role", "dialog");
    olhar.setAttribute("aria-modal", "true");
    olhar.setAttribute("aria-labelledby", "olhar-titulo");
    olhar.innerHTML =
      '<div class="olhar__veu"></div><div class="olhar__caixa">' +
      '<button class="painel__fechar olhar__fechar" type="button" aria-label="Fechar detalhes">' + D.icones.fechar + "</button>" +
      '<div class="olhar__palco"><img class="olhar__foto" alt="" width="800" height="800"></div>' +
      '<div class="olhar__txt"></div></div>';
    document.body.append(olhar);
    $(".olhar__veu", olhar).addEventListener("click", fecharOlhar);
    $(".olhar__fechar", olhar).addEventListener("click", fecharOlhar);
    addEventListener("keydown", (e) => {
      if (olhar.style.visibility !== "visible") return;
      if (e.key === "Escape") fecharOlhar();
      if (e.key === "Tab") {
        const foco = $$("button, input, a", $(".olhar__caixa", olhar)).filter((f) => !f.disabled && f.offsetParent !== null);
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
  }

  function abrirOlhar(id, origem) {
    const p = D.produto(id);
    const andar = D.andares.find((a) => a.id === p.andar);
    const foto = $(".olhar__foto", olhar);
    const caixa = $(".olhar__caixa", olhar);
    const veu = $(".olhar__veu", olhar);
    foto.src = D.foto(p.id);
    foto.alt = p.nome;
    $(".olhar__txt", olhar).innerHTML =
      '<p class="olhar__andar"><span class="num-led">' + andar.n + "</span>" + andar.nome + "</p>" +
      '<h2 class="t-3" id="olhar-titulo">' + p.nome + "</h2>" +
      "<p>" + p.desc + "</p>" + specHTML(p) + precoHTML(p) + tamanhosHTML(p) + botao(p) +
      '<p class="olhar__nota">Embalagem de Natal grátis e troca grátis.</p>';
    antes = origem || document.activeElement;
    document.documentElement.style.overflow = "hidden";
    gsap.set(olhar, { visibility: "visible" });
    if (tlOlhar) tlOlhar.kill();
    if (D.reduzir) {
      gsap.set(veu, { opacity: 1 });
      gsap.set(caixa, { opacity: 1 });
    } else {
      gsap.set(foto, { clearProps: "transform" });
      tlOlhar = gsap.timeline({ defaults: { ease: "chega" } })
        .to(veu, { opacity: 1, duration: 0.3, ease: "none" }, 0)
        .fromTo(caixa, { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.42 }, 0);
      const img = origem && $("img", origem);
      if (img) {
        Flip.fit(foto, img, { scale: true });
        tlOlhar.to(foto, { x: 0, y: 0, scaleX: 1, scaleY: 1, rotation: 0, duration: 0.62 }, 0);
      }
    }
    $(".olhar__fechar", olhar).focus({ preventScroll: true });
  }

  function fecharOlhar() {
    const caixa = $(".olhar__caixa", olhar);
    const veu = $(".olhar__veu", olhar);
    document.documentElement.style.overflow = "";
    if (tlOlhar) tlOlhar.kill();
    const fim = () => gsap.set(olhar, { visibility: "hidden" });
    if (D.reduzir) fim();
    else {
      gsap.to(veu, { opacity: 0, duration: 0.22, ease: "none" });
      gsap.to(caixa, { opacity: 0, y: 16, duration: 0.22, ease: "power2.in", onComplete: fim });
    }
    if (antes) antes.focus({ preventScroll: true });
  }

  /* Filtros com troca animada */
  D.ligarFiltros = function (barra, grade, opcoes, teste) {
    barra.classList.add("filtros");
    barra.setAttribute("role", "group");
    barra.setAttribute("aria-label", "Filtrar produtos");
    barra.innerHTML = opcoes.map(([v, t], i) => '<button class="filtro" type="button" data-v="' + v + '" aria-pressed="' + (i === 0) + '">' + t + "</button>").join("");
    barra.addEventListener("click", (e) => {
      const b = e.target.closest(".filtro");
      if (!b || b.getAttribute("aria-pressed") === "true") return;
      $$(".filtro", barra).forEach((x) => x.setAttribute("aria-pressed", x === b));
      const itens = $$(".produto", grade);
      const estado = D.reduzir ? null : Flip.getState(itens);
      itens.forEach((el) => {
        const ok = b.dataset.v === "todos" || teste(D.produto(el.dataset.id), b.dataset.v);
        el.hidden = !ok;
        if (ok) el.classList.add("aceso");
      });
      if (estado) {
        Flip.from(estado, {
          duration: 0.52,
          ease: "loja",
          absolute: true,
          scale: true,
          onEnter: (els) => gsap.fromTo(els, { opacity: 0, scale: 0.92 }, { opacity: 1, scale: 1, duration: 0.42, delay: 0.1 }),
          onLeave: (els) => gsap.to(els, { opacity: 0, scale: 0.92, duration: 0.22 }),
          onComplete: () => ScrollTrigger.refresh()
        });
      } else ScrollTrigger.refresh();
    });
  };

  /* Inclinação sutil da peça sob o ponteiro */
  function inclinar() {
    const ctl = new WeakMap();
    let ativo = null;
    const pegar = (img) => {
      if (!ctl.has(img)) {
        gsap.set(img, { transformPerspective: 900 });
        ctl.set(img, {
          rx: gsap.quickTo(img, "rotationX", { duration: 0.5, ease: "power3" }),
          ry: gsap.quickTo(img, "rotationY", { duration: 0.5, ease: "power3" }),
          y: gsap.quickTo(img, "y", { duration: 0.5, ease: "power3" })
        });
      }
      return ctl.get(img);
    };
    const soltar = () => {
      if (!ativo) return;
      const c = pegar(ativo);
      c.rx(0);
      c.ry(0);
      c.y(0);
      ativo = null;
    };
    document.addEventListener("pointermove", (e) => {
      const palco = e.target.closest && e.target.closest(".produto__palco");
      if (!palco) return soltar();
      const img = $(".produto__foto", palco);
      if (!img) return;
      if (ativo !== img) soltar();
      ativo = img;
      const r = palco.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      const c = pegar(img);
      c.ry(px * 13);
      c.rx(-py * 8);
      c.y(-9);
    }, { passive: true });
  }

  D.aoIniciar(() => {
    montarOlhar();
    if (D.fino && !D.reduzir) inclinar();
    document.addEventListener("click", (e) => {
      const add = e.target.closest("[data-add]");
      if (add) return adicionar(add);
      const ver = e.target.closest(".produto__olhar");
      if (ver) abrirOlhar(ver.closest(".produto").dataset.id, ver);
    });
    document.addEventListener("change", (e) => {
      if (e.target.matches(".tam input")) {
        const aviso = $(".tam__aviso", e.target.closest(".produto, .olhar__txt"));
        if (aviso) aviso.textContent = "";
      }
    });
  });
})();
