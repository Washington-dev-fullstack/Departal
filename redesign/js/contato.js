/* Contato: placa de neon e quadro da semana com o horário real, pedido de orçamento vindo da oficina,
   envio simulado que vira carta e perguntas frequentes. */
(function () {
  const D = window.Departal;
  const { $, $$ } = D;

  /* Domingo a sábado, no horário de Brasília: [abre, fecha] */
  const HORARIO = [[10, 16], [9, 18], [9, 18], [9, 18], [9, 18], [9, 18], [9, 18]];
  const SEMANA = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const relogio = new Intl.DateTimeFormat("en-US", { timeZone: "America/Sao_Paulo", weekday: "short", hour: "numeric", minute: "numeric", hourCycle: "h23" });

  function situacao() {
    const p = Object.fromEntries(relogio.formatToParts(new Date()).map((x) => [x.type, x.value]));
    const dia = SEMANA.indexOf(p.weekday);
    const hora = Number(p.hour) + Number(p.minute) / 60;
    const [abre, fecha] = HORARIO[dia];
    const aberto = hora >= abre && hora < fecha;
    const txt = aberto
      ? "Aberto agora, até as " + fecha + "h"
      : hora < abre
        ? "Fechado agora. Abrimos hoje às " + abre + "h"
        : "Fechado agora. Abrimos amanhã às " + HORARIO[(dia + 1) % 7][0] + "h";
    return { dia, aberto, txt };
  }

  /* A placa desce pelo cordão e fica balançando como um pêndulo */
  function balancar(placa) {
    const pend = D.pendulo($(".placa__balanco", placa), { area: placa.closest(".capa"), alvo: $(".placa__quadro", placa) });
    gsap.from(placa, { y: () => -innerHeight * 0.5, duration: 1.2, ease: "chega", delay: 0.1, onComplete: () => pend.empurrar(20) });
  }

  /* Placa de porta: dourada com a loja aberta, vermelha com ela fechada. Se o estado muda com a página aberta, o neon pisca e troca */
  function placa() {
    const el = $(".placa");
    if (!el) return () => {};
    const neon = $(".placa__neon", el);
    let estado = null;
    const escrever = (aberto) => {
      const t = aberto ? "Aberto" : "Fechado";
      neon.textContent = t;
      neon.dataset.texto = t;
      el.dataset.aberto = aberto;
    };
    if (!D.reduzir) {
      balancar(el);
      gsap.fromTo(el, { "--acesa": 0 }, { "--acesa": 1, duration: 1.1, ease: "pisca", delay: 1 });
    }
    return (aberto) => {
      if (estado === aberto) return;
      const primeira = estado === null;
      estado = aberto;
      if (primeira || D.reduzir) return escrever(aberto);
      gsap.timeline()
        .to(el, { "--acesa": 0, duration: 0.25, ease: "power1.in" })
        .add(() => escrever(aberto))
        .to(el, { "--acesa": 1, duration: 0.9, ease: "pisca" });
    };
  }

  /* Quadro da semana: acende a coluna de hoje */
  let marcado = -1;
  function marcarHoje(dia) {
    const tabela = $(".semana");
    if (!tabela || dia === marcado) return;
    marcado = dia;
    $$(".hoje", tabela).forEach((c) => c.classList.remove("hoje"));
    $$(".semana__hoje", tabela).forEach((s) => s.remove());
    const th = $$("thead th", tabela)[dia];
    th.classList.add("hoje");
    th.insertAdjacentHTML("beforeend", '<span class="so-leitor semana__hoje">, hoje</span>');
    $$("tbody tr", tabela).forEach((tr) => $$("td", tr)[dia].classList.add("hoje"));
  }

  function agora() {
    const el = $(".agora");
    const trocarPlaca = placa();
    const atualizar = () => {
      const s = situacao();
      el.dataset.aberto = s.aberto;
      if (el.textContent !== s.txt) el.textContent = s.txt;
      trocarPlaca(s.aberto);
      marcarHoje(s.dia);
    };
    atualizar();
    setInterval(atualizar, 60000);
  }

  function formulario() {
    const f = $(".contato__form");
    const corpo = $(".contato__corpo", f);
    const aviso = $(".contato__aviso", f);
    const status = $(".contato__status", f);
    const carta = $(".contato__carta", f);
    const titulo = $("h3", carta);
    const pecas = {
      envelope: $(".carta", carta),
      folha: $(".carta__folha", carta),
      fundo: $(".carta__aba--fundo", carta),
      frente: $(".carta__aba--frente", carta),
      selo: $(".carta__selo", carta),
      textos: $$(".contato__carta > :not(svg)", f)
    };
    $(".carta__selo", carta).insertAdjacentHTML("beforeend", D.gorro.replace("<svg ", '<svg x="106" y="146" width="28" height="20" '));

    try {
      const pedido = JSON.parse(D.sessao.ler("dp-orcamento") || "null");
      if (pedido) {
        f.elements.assunto.value = pedido.assunto;
        f.elements.mensagem.value = pedido.mensagem;
        aviso.hidden = false;
      }
    } catch (e) {
      /* pedido ilegível: o formulário segue em branco */
    }
    D.sessao.tirar("dp-orcamento");

    const fecharCarta = () => {
      gsap.killTweensOf([corpo, carta, ...Object.values(pecas).flat()]);
      gsap.set([corpo, carta, ...Object.values(pecas).flat()], { clearProps: "all" });
      carta.hidden = true;
      corpo.inert = false;
      status.textContent = "";
    };

    /* no celular o painel é alto e o botão fica lá embaixo: traz a carta para o meio da tela se ela ficou fora */
    const mostrarNaTela = () => {
      const r = pecas.envelope.getBoundingClientRect();
      const fim = $("button", carta).getBoundingClientRect().bottom;
      if (r.top < 70 || fim > innerHeight) {
        scrollBy({ top: (r.top + fim) / 2 - innerHeight / 2, behavior: D.reduzir ? "auto" : "smooth" });
      }
    };

    const abrirCarta = () => {
      corpo.inert = true;
      carta.hidden = false;
      mostrarNaTela();
      const { envelope, folha, fundo, frente, selo, textos } = pecas;
      /* a carta entra aberta: folha por cima, aba de trás levantada, aba da frente e selo ainda escondidos */
      gsap.set(fundo, { scaleY: 1, transformOrigin: "50% 100%" });
      gsap.set(frente, { transformOrigin: "50% 0%" });
      gsap.set(selo, { transformOrigin: "50% 50%" });
      if (D.reduzir) {
        gsap.set(corpo, { opacity: 0 });
        gsap.set(folha, { y: 108 });
        gsap.set(fundo, { scaleY: 0 });
        titulo.focus({ preventScroll: true });
        return;
      }
      gsap.set(textos, { opacity: 0 });
      gsap.set(frente, { scaleY: 0 });
      gsap.set(selo, { scale: 0 });
      gsap.set(folha, { y: 8 });
      titulo.focus({ preventScroll: true });
      gsap.timeline()
        .to(corpo, { opacity: 0, duration: 0.3, ease: "power1.out" })
        .fromTo(envelope, { y: 26, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "chega" }, "<")
        .to(folha, { y: 108, duration: 0.65, ease: "power2.inOut" }, "+=0.05")
        .to(fundo, { scaleY: 0, duration: 0.18, ease: "power2.in" })
        .to(frente, { scaleY: 1, duration: 0.26, ease: "power2.out" })
        .fromTo(selo, { scale: 0, rotation: -25 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.4)" })
        .fromTo(textos, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "chega" }, "-=0.2");
    };

    f.addEventListener("submit", (e) => {
      e.preventDefault();
      aviso.hidden = true;
      f.reset();
      status.textContent = "Envio simulado: este site é uma demonstração e nenhuma mensagem foi enviada.";
      abrirCarta();
    });
    $("button", carta).addEventListener("click", () => {
      fecharCarta();
      f.elements.nome.focus();
    });
  }

  /* Perguntas frequentes: abre uma por vez, com a resposta deslizando */
  function duvidas() {
    const itens = $$(".duvida");
    if (!itens.length || D.reduzir) return;
    const fechar = (d) => {
      const r = $(".duvida__resposta", d);
      d.classList.add("fechando");
      gsap.fromTo(r, { height: r.offsetHeight }, {
        height: 0,
        duration: 0.3,
        ease: "power2.in",
        overwrite: true,
        onComplete: () => {
          d.open = false;
          d.classList.remove("fechando");
          gsap.set(r, { clearProps: "height" });
        }
      });
    };
    const abrir = (d) => {
      const r = $(".duvida__resposta", d);
      /* se ela ainda estava fechando, volta a abrir de onde parou */
      const de = d.open ? r.offsetHeight : 0;
      d.classList.remove("fechando");
      d.open = true;
      gsap.fromTo(r, { height: de }, { height: () => r.scrollHeight, duration: 0.42, ease: "loja", overwrite: true, clearProps: "height" });
    };
    itens.forEach((d) => {
      $("summary", d).addEventListener("click", (e) => {
        e.preventDefault();
        if (d.open && !d.classList.contains("fechando")) return fechar(d);
        itens.forEach((o) => o !== d && o.open && !o.classList.contains("fechando") && fechar(o));
        abrir(d);
      });
    });
  }

  D.aoIniciar(() => {
    agora();
    formulario();
    duvidas();
  });
})();
