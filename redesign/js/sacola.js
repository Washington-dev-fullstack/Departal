/* Sacola: lista guardada no navegador, gaveta de vidro e pedido simulado. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;
  const CHAVE = "dp-sacola";
  const estado = { itens: D.ler(CHAVE, []), embrulho: D.ler("dp-embrulho", true) };
  let aberta = false;
  let antes = null;
  let raiz, lista, rodape, tl;

  const salvar = () => {
    D.gravar(CHAVE, estado.itens);
    D.gravar("dp-embrulho", estado.embrulho);
  };
  const totalItens = () => estado.itens.reduce((s, i) => s + i.qtd, 0);
  const subtotal = () => estado.itens.reduce((s, i) => s + D.produto(i.id).preco * i.qtd, 0);

  function atualizarContador(pulso) {
    const c = $(".nav__conta");
    if (!c) return;
    const n = totalItens();
    c.textContent = n;
    c.hidden = n === 0;
    if (pulso && !D.reduzir) gsap.fromTo($(".nav__sacola"), { scale: 1 }, { scale: 1.16, duration: 0.14, yoyo: true, repeat: 1, ease: "sine.inOut" });
  }

  function linha(i, idx) {
    const p = D.produto(i.id);
    return (
      '<li class="item" data-i="' + idx + '">' +
      '<img src="' + D.foto(p.id) + '" alt="" width="84" height="84">' +
      '<div class="item__txt"><h3>' + p.nome + "</h3>" + (i.tam ? '<p class="suave">Tamanho ' + i.tam + "</p>" : "") +
      '<div class="item__baixo"><div class="passo" role="group" aria-label="Quantidade de ' + p.nome + '">' +
      '<button type="button" data-acao="menos" aria-label="Diminuir quantidade">' + D.icones.menos + "</button>" +
      '<output aria-live="polite">' + i.qtd + "</output>" +
      '<button type="button" data-acao="mais" aria-label="Aumentar quantidade">' + D.icones.mais + "</button></div>" +
      "<strong>" + D.moeda(p.preco * i.qtd) + "</strong></div></div>" +
      '<button class="item__tirar" type="button" data-acao="tirar" aria-label="Remover ' + p.nome + ' da sacola">' + D.icones.lixeira + "</button></li>"
    );
  }

  function desenhar() {
    if (!raiz) return;
    if (!estado.itens.length) {
      lista.innerHTML = '<li class="sacola__vazia"><p class="t-4">Sua sacola está vazia</p><p class="suave">Comece pelas ofertas da vitrine.</p><a class="btn btn--pequeno" href="index.html#ofertas">Ver ofertas</a></li>';
      rodape.hidden = true;
      return;
    }
    lista.innerHTML = estado.itens.map(linha).join("");
    rodape.hidden = false;
    $(".sacola__subtotal", rodape).textContent = D.moeda(subtotal());
    $(".sacola__embrulho input", rodape).checked = estado.embrulho;
  }

  function montar() {
    raiz = document.createElement("div");
    raiz.className = "sacola";
    raiz.setAttribute("role", "dialog");
    raiz.setAttribute("aria-modal", "true");
    raiz.setAttribute("aria-label", "Sacola");
    raiz.innerHTML =
      '<div class="sacola__veu"></div><div class="sacola__caixa">' +
      '<div class="sacola__topo"><h2 class="t-3">Sua sacola</h2><button class="painel__fechar" type="button" aria-label="Fechar sacola">' + D.icones.fechar + "</button></div>" +
      '<ul class="sacola__lista"></ul>' +
      '<div class="sacola__rodape" hidden>' +
      '<label class="sacola__embrulho"><input type="checkbox"><span class="troca-chave" aria-hidden="true"></span><span>Embalagem de Natal grátis<small>Papel premium, tag personalizada e laço vermelho</small></span></label>' +
      '<p class="sacola__total"><span>Subtotal</span><strong class="sacola__subtotal"></strong></p>' +
      '<button class="btn sacola__finalizar" type="button">Finalizar compra</button>' +
      "</div></div>";
    document.body.append(raiz);
    lista = $(".sacola__lista", raiz);
    rodape = $(".sacola__rodape", raiz);
    const caixa = $(".sacola__caixa", raiz);
    const veu = $(".sacola__veu", raiz);
    gsap.set(caixa, { x: "102%" });
    tl = gsap.timeline({ paused: true, defaults: { ease: "chega" } })
      .set(raiz, { visibility: "visible" })
      .to(veu, { opacity: 1, duration: 0.3, ease: "none" }, 0)
      .to(caixa, { x: 0, duration: 0.5 }, 0);

    $(".painel__fechar", raiz).addEventListener("click", fechar);
    veu.addEventListener("click", fechar);
    $(".nav__sacola").addEventListener("click", abrir);
    $(".sacola__embrulho input", raiz).addEventListener("change", (e) => {
      estado.embrulho = e.target.checked;
      salvar();
    });
    $(".sacola__finalizar", raiz).addEventListener("click", resumo);
    lista.addEventListener("click", (e) => {
      const b = e.target.closest("[data-acao]");
      if (!b) return;
      const i = Number(b.closest(".item").dataset.i);
      if (b.dataset.acao === "mais") estado.itens[i].qtd++;
      if (b.dataset.acao === "menos") estado.itens[i].qtd--;
      if (b.dataset.acao === "tirar" || estado.itens[i].qtd < 1) estado.itens.splice(i, 1);
      salvar();
      desenhar();
      atualizarContador();
    });
    addEventListener("keydown", (e) => {
      if (aberta && e.key === "Escape") fechar();
    });
    desenhar();
    atualizarContador();
  }

  function abrir() {
    aberta = true;
    antes = document.activeElement;
    document.documentElement.style.overflow = "hidden";
    D.reduzir ? tl.progress(1) : tl.timeScale(1).play();
    $(".painel__fechar", raiz).focus({ preventScroll: true });
  }
  function fechar() {
    aberta = false;
    document.documentElement.style.overflow = "";
    D.reduzir ? tl.progress(0) : tl.timeScale(1.4).reverse();
    if (antes) antes.focus({ preventScroll: true });
  }

  /* Pedido simulado: nada é cobrado nem enviado */
  function resumo() {
    const soma = D.moeda(subtotal());
    const numero = "DP-" + String(Date.now()).slice(-6);
    lista.innerHTML =
      '<li class="sacola__fim">' +
      '<span class="sacola__ok" aria-hidden="true"><svg viewBox="0 0 64 64" fill="none"><circle class="ok-a" cx="32" cy="32" r="29" stroke="currentColor" stroke-width="2"/><path class="ok-b" d="m19 33 9 9 18-20" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></span>' +
      '<p class="t-3">Pedido simulado</p>' +
      "<p>Número <strong>" + numero + "</strong>, total de <strong>" + soma + "</strong>" + (estado.embrulho ? ", com embalagem de Natal" : "") + ".</p>" +
      '<p class="suave">Este site é uma demonstração: nenhum pagamento foi feito e nada será entregue.</p>' +
      '<button class="btn btn--vidro" type="button" data-fim>Continuar na loja</button></li>';
    rodape.hidden = true;
    estado.itens = [];
    salvar();
    atualizarContador();
    if (!D.reduzir) {
      gsap.from(".ok-a", { drawSVG: 0, duration: 0.6 });
      gsap.from(".ok-b", { drawSVG: 0, duration: 0.4, delay: 0.4, ease: "chega" });
    }
    $("[data-fim]", lista).addEventListener("click", () => {
      fechar();
      desenhar();
    });
  }

  /* A foto do produto voa em arco até a sacola */
  function voar(origem) {
    const alvo = $(".nav__sacola");
    if (!origem || !alvo || D.reduzir) return;
    const a = origem.getBoundingClientRect();
    const b = alvo.getBoundingClientRect();
    const c = origem.cloneNode();
    c.removeAttribute("loading");
    c.removeAttribute("data-flip-id");
    c.className = "voo";
    Object.assign(c.style, { left: a.left + "px", top: a.top + "px", width: a.width + "px", height: a.height + "px" });
    document.body.append(c);
    const dx = b.left + b.width / 2 - (a.left + a.width / 2);
    const dy = b.top + b.height / 2 - (a.top + a.height / 2);
    const tl2 = gsap.timeline({ onComplete: () => c.remove() });
    tl2.to(c, { x: dx, duration: 0.74, ease: "power1.inOut" }, 0)
      .to(c, { y: dy, duration: 0.74, ease: "back.in(1.4)" }, 0)
      .to(c, { scale: 0.08, rotation: 16, duration: 0.74, ease: "power2.in" }, 0)
      .to(c, { opacity: 0, duration: 0.12 }, 0.64);
  }

  D.sacola = {
    adicionar(id, tam, foto) {
      const i = estado.itens.find((x) => x.id === id && (x.tam || null) === (tam || null));
      if (i) i.qtd++;
      else estado.itens.push({ id, tam: tam || null, qtd: 1 });
      salvar();
      desenhar();
      voar(foto);
      setTimeout(() => atualizarContador(true), D.reduzir ? 0 : 620);
    },
    abrir
  };

  D.aoIniciar(montar);
})();
