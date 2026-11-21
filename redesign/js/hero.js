/* Vitrine em WebGL: bolas de Natal reais atrás de um vidro embaçado que se limpa com a mão. */
(function () {
  const D = window.Departal;

  const FRAG_VIDRO = `
    uniform sampler2D tCena, tMascara, tGotas;
    uniform float uClaro, uAspecto;
    varying vec2 vUv;

    const vec2 TAPS[8] = vec2[8](vec2(.71,.12), vec2(-.33,.63), vec2(-.82,-.21), vec2(.18,-.77), vec2(.42,.86), vec2(-.62,.49), vec2(-.12,-.38), vec2(.93,-.41));

    float acaso(vec2 p) { return fract(52.9829189 * fract(dot(p, vec2(.06711056, .00583715)))); }

    vec3 nevoa(vec2 uv, float lod, float raio) {
      float a = acaso(gl_FragCoord.xy) * 6.2832;
      float s = sin(a), c = cos(a);
      mat2 r = mat2(c, -s, s, c);
      vec3 soma = vec3(0.);
      for (int i = 0; i < 8; i++) {
        vec2 o = r * TAPS[i] * raio;
        soma += textureLod(tCena, uv + o * vec2(1. / uAspecto, 1.), lod).rgb;
      }
      return soma / 8.;
    }

    vec3 aces(vec3 x) { return clamp((x * (2.51 * x + .03)) / (x * (2.43 * x + .59) + .14), 0., 1.); }

    void main() {
      vec2 uv = vUv;
      vec2 q = (uv - .5) * vec2(uAspecto, 1.);
      float canto = smoothstep(.42, 1.02, length((uv - .5) * vec2(1.18, 1.42)));
      vec3 g = texture2D(tGotas, uv * vec2(uAspecto, 1.) * 3.4).rgb;
      float gota = g.b;
      vec2 ref = (g.rg - .5) * gota * .08;

      float m = texture2D(tMascara, uv).r;
      float limpo = max(smoothstep(.22, .62, m) * (1. - canto * .6), uClaro);

      vec3 nitido = textureLod(tCena, uv + ref * .16 * (1. - uClaro), 0.).rgb;
      vec3 fosco = nevoa(uv + ref * .6, 3.3 + canto * 1.3, .011 + canto * .012);
      fosco = fosco * .9 + vec3(.03, .04, .036) + canto * vec3(.07, .085, .08);
      vec3 emGota = textureLod(tCena, uv - ref * 2.4, 1.).rgb * 1.14;
      fosco = mix(fosco, emGota, smoothstep(.34, .72, gota) * .5);

      vec3 cor = mix(fosco, nitido, limpo);
      float borda = smoothstep(.12, .3, m) * (1. - smoothstep(.3, .6, m));
      cor += borda * (1. - uClaro) * vec3(.11, .12, .115);
      cor *= 1. - smoothstep(.56, 1.28, length(q)) * .62;
      gl_FragColor = vec4(pow(aces(cor * 1.08), vec3(1. / 2.2)), 1.);
    }`;

  const VERT_TELA = "varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }";

  const VERT_LUZ = `
    attribute float aTam, aFase, aVel;
    attribute vec3 aCor;
    uniform float uTempo, uEsc;
    varying vec3 vCor;
    void main() {
      vec4 mv = modelViewMatrix * vec4(position, 1.);
      float pisca = aVel > 0. ? .66 + .34 * sin(uTempo * aVel + aFase) : 1.;
      vCor = aCor * pisca;
      gl_PointSize = aTam * uEsc / -mv.z;
      gl_Position = projectionMatrix * mv;
    }`;
  const FRAG_PONTO = `
    varying vec3 vCor;
    void main() {
      vec2 p = gl_PointCoord - .5;
      float d = dot(p, p) * 4.;
      float a = exp(-d * 7.) + exp(-d * 44.) * 1.6;
      gl_FragColor = vec4(vCor * a * (1. - smoothstep(.72, 1., d)), 1.);
    }`;
  const FRAG_DISCO = `
    varying vec3 vCor;
    void main() {
      vec2 p = gl_PointCoord - .5;
      float d = length(p) * 2.;
      float a = (1. - smoothstep(.86, 1., d)) * (.5 + .5 * smoothstep(.5, .94, d));
      gl_FragColor = vec4(vCor * a, 1.);
    }`;
  const VERT_NEVE = `
    attribute float aTam, aFase, aVel;
    uniform float uTempo, uEsc, uAltura;
    varying float vAlfa;
    void main() {
      vec3 p = position;
      p.y = mod(p.y - uTempo * aVel + uAltura, uAltura * 2.) - uAltura;
      p.x += sin(uTempo * .5 + aFase) * .22;
      vec4 mv = modelViewMatrix * vec4(p, 1.);
      vAlfa = smoothstep(-.2, -1.4, mv.z);
      gl_PointSize = aTam * uEsc / -mv.z;
      gl_Position = projectionMatrix * mv;
    }`;
  const FRAG_NEVE = `
    uniform float uForca;
    varying float vAlfa;
    void main() {
      float d = length(gl_PointCoord - .5) * 2.;
      float a = (1. - smoothstep(.2, 1., d)) * vAlfa * uForca;
      gl_FragColor = vec4(vec3(.96, .95, .92), a * .8);
    }`;

  const sorte = (function () {
    let s = 20261225;
    return () => {
      s = (s * 1664525 + 1013904223) >>> 0;
      return s / 4294967296;
    };
  })();

  function tela(w, h, pinta) {
    const c = document.createElement("canvas");
    c.width = w;
    c.height = h;
    pinta(c.getContext("2d"), w, h);
    return c;
  }
  function textura(c, cor) {
    const t = new THREE.CanvasTexture(c);
    if (cor) t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.anisotropy = 4;
    return t;
  }

  function ambiente(renderer) {
    const c = tela(1024, 512, (x, w, h) => {
      const g = x.createLinearGradient(0, 0, 0, h);
      g.addColorStop(0, "#2a1609");
      g.addColorStop(0.5, "#0e0a07");
      g.addColorStop(1, "#050706");
      x.fillStyle = g;
      x.fillRect(0, 0, w, h);
      const janela = (cx, cy, rx, ry, cor) => {
        const r = x.createRadialGradient(0, 0, 0, 0, 0, 1);
        r.addColorStop(0, cor);
        r.addColorStop(1, "rgba(0,0,0,0)");
        x.save();
        x.translate(cx, cy);
        x.scale(rx, ry);
        x.fillStyle = r;
        x.fillRect(-1, -1, 2, 2);
        x.restore();
      };
      x.globalCompositeOperation = "lighter";
      janela(w * 0.74, h * 0.34, 210, 120, "rgba(255,226,180,.95)");
      janela(w * 0.3, h * 0.22, 260, 80, "rgba(255,190,120,.7)");
      janela(w * 0.1, h * 0.56, 150, 150, "rgba(180,20,40,.55)");
      janela(w * 0.52, h * 0.6, 170, 110, "rgba(20,120,80,.42)");
      janela(w * 0.92, h * 0.6, 140, 110, "rgba(230,120,40,.5)");
      /* Luzinhas que aparecem refletidas nas bolas */
      for (let i = 0; i < 300; i++) {
        const px = sorte() * w;
        const py = h * (0.16 + sorte() * 0.56);
        x.fillStyle = sorte() > 0.86 ? "rgba(255,90,90,.9)" : "rgba(255,214,150,.95)";
        x.beginPath();
        x.arc(px, py, 1 + sorte() * 2.4, 0, 6.283);
        x.fill();
      }
      /* Caixilho da vitrine */
      x.globalCompositeOperation = "source-over";
      x.fillStyle = "rgba(4,6,5,.7)";
      for (let i = 0; i < 4; i++) x.fillRect(w * (0.62 + i * 0.08), h * 0.12, 7, h * 0.42);
      x.fillRect(w * 0.58, h * 0.32, w * 0.34, 6);
    });
    const t = textura(c, true);
    t.mapping = THREE.EquirectangularReflectionMapping;
    const pm = new THREE.PMREMGenerator(renderer);
    const env = pm.fromEquirectangular(t).texture;
    pm.dispose();
    t.dispose();
    return env;
  }

  function materiais() {
    const anel = (n, r, x, y) => {
      n.beginPath();
      for (let i = 0; i < 10; i++) {
        const a = -Math.PI / 2 + (i * Math.PI) / 5;
        const q = i % 2 ? r * 0.42 : r;
        n.lineTo(x + Math.cos(a) * q, y + Math.sin(a) * q);
      }
      n.closePath();
      n.fill();
    };
    const listras = tela(1024, 512, (x, w, h) => {
      x.fillStyle = "#f4c26c";
      x.fillRect(0, 0, w, h);
      for (let i = 0; i < 8; i++) {
        const bx = (i * w) / 8;
        x.fillStyle = "#9d0c20";
        x.fillRect(bx + 18, 0, w / 16, h);
        x.fillStyle = "#fff0cf";
        x.fillRect(bx + 18 + w / 16 + 7, 0, 6, h);
      }
    });
    const listrasR = tela(512, 256, (x, w, h) => {
      x.fillStyle = "rgb(0,50,0)";
      x.fillRect(0, 0, w, h);
      x.fillStyle = "rgb(0,150,0)";
      for (let i = 0; i < 8; i++) x.fillRect((i * w) / 8 + 9, 0, w / 16, h);
    });
    const estrelas = tela(1024, 512, (x, w, h) => {
      x.fillStyle = "#0d3b2b";
      x.fillRect(0, 0, w, h);
      x.fillStyle = "#f4c870";
      for (let j = 0; j < 6; j++) {
        for (let i = 0; i < 12; i++) anel(x, 22 + (j % 2) * 8, ((i + (j % 2) * 0.5) * w) / 12 + 20, ((j + 0.5) * h) / 6);
      }
    });
    const brilho = tela(512, 512, (x, w, h) => {
      const d = x.createImageData(w, h);
      for (let i = 0; i < d.data.length; i += 4) {
        const a = sorte() * 6.283;
        const r = sorte() * 0.8;
        d.data[i] = 128 + Math.cos(a) * r * 127;
        d.data[i + 1] = 128 + Math.sin(a) * r * 127;
        d.data[i + 2] = 200;
        d.data[i + 3] = 255;
      }
      x.putImageData(d, 0, 0);
    });
    const std = (o) => new THREE.MeshStandardMaterial(Object.assign({ metalness: 1 }, o));
    const nb = textura(brilho);
    nb.repeat.set(3, 1.5);
    return {
      ouro: std({ color: 0xf1b25a, roughness: 0.13 }),
      rubi: std({ color: 0xc20a24, roughness: 0.12 }),
      prata: std({ color: 0xd8d8dc, roughness: 0.42, normalMap: nb, normalScale: new THREE.Vector2(0.8, 0.8) }),
      listras: std({ map: textura(listras, true), roughnessMap: textura(listrasR), roughness: 1 }),
      estrelas: std({ map: textura(estrelas, true), roughness: 0.2 }),
      ferragem: std({ color: 0xd8ae66, roughness: 0.32 })
    };
  }

  function gotas() {
    const c = tela(512, 512, (x, w, h) => {
      const d = x.createImageData(w, h);
      const p = d.data;
      for (let i = 0; i < p.length; i += 4) {
        p[i] = p[i + 1] = 128;
        p[i + 2] = 0;
        p[i + 3] = 255;
      }
      for (let n = 0; n < 1500; n++) {
        const r = 1.4 + Math.pow(sorte(), 3.4) * 11;
        const cx = sorte() * w;
        const cy = sorte() * h;
        const ri = Math.ceil(r);
        for (let py = -ri; py <= ri; py++) {
          for (let px = -ri; px <= ri; px++) {
            const dd = Math.hypot(px, py / 1.12) / r;
            if (dd > 1) continue;
            const ix = (((Math.floor(cx) + px) % w) + w) % w;
            const iy = (((Math.floor(cy) + py) % h) + h) % h;
            const o = (iy * w + ix) * 4;
            p[o] = 128 + (px / r) * 127;
            p[o + 1] = 128 - (py / r) * 127;
            p[o + 2] = 255 * Math.min(1, (1 - dd) * 3.4);
          }
        }
      }
      x.putImageData(d, 0, 0);
    });
    const t = textura(c);
    t.generateMipmaps = false;
    t.minFilter = THREE.LinearFilter;
    return t;
  }

  function pontos(n, gera, frag, uniforms) {
    const pos = new Float32Array(n * 3);
    const cor = new Float32Array(n * 3);
    const tam = new Float32Array(n);
    const fase = new Float32Array(n);
    const vel = new Float32Array(n);
    for (let i = 0; i < n; i++) {
      const p = gera(i);
      pos.set(p.pos, i * 3);
      cor.set(p.cor, i * 3);
      tam[i] = p.tam;
      fase[i] = sorte() * 6.283;
      vel[i] = p.vel;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    g.setAttribute("aCor", new THREE.BufferAttribute(cor, 3));
    g.setAttribute("aTam", new THREE.BufferAttribute(tam, 1));
    g.setAttribute("aFase", new THREE.BufferAttribute(fase, 1));
    g.setAttribute("aVel", new THREE.BufferAttribute(vel, 1));
    const m = new THREE.ShaderMaterial({ vertexShader: VERT_LUZ, fragmentShader: frag, uniforms, blending: THREE.AdditiveBlending, transparent: true, depthWrite: false });
    const o = new THREE.Points(g, m);
    o.frustumCulled = false;
    return o;
  }

  const BOLAS = [
    { x: 2.5, y: 0.02, z: 0.5, r: 1.08, m: "ouro" },
    { x: 0.42, y: 1.1, z: -0.9, r: 0.62, m: "rubi" },
    { x: 4.12, y: 1.02, z: -0.5, r: 0.72, m: "prata" },
    { x: 3.92, y: -1.5, z: 1.1, r: 0.46, m: "listras" },
    { x: -1.28, y: 1.72, z: -1.3, r: 0.5, m: "estrelas" },
    { x: -3.3, y: 1.94, z: -1.7, r: 0.4, m: "rubi" },
    { x: 1.05, y: -1.34, z: 1.3, r: 0.34, m: "prata" },
    { x: -2.3, y: 0.96, z: -2.7, r: 0.36, m: "ouro" }
  ];
  const TETO = 4.1;
  const CAM_Z = 8.6;

  D.vitrine = function (secao) {
    const cv = D.$(".vitrine__gl", secao);
    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: false, alpha: false, stencil: false, powerPreference: "high-performance" });
    } catch (e) {
      secao.classList.add("sem-gl");
      return null;
    }
    renderer.toneMapping = THREE.NoToneMapping;
    cv.addEventListener("webglcontextlost", () => secao.classList.add("sem-gl"));

    const cena = new THREE.Scene();
    cena.background = new THREE.Color(0x07090a);
    cena.environment = ambiente(renderer);
    cena.environmentIntensity = 1.75;
    const camera = new THREE.PerspectiveCamera(34, 16 / 9, 0.1, 60);
    camera.position.set(0, 0.25, CAM_Z);

    const luz = new THREE.PointLight(0xffd9a0, 46, 30, 2);
    luz.position.set(-1.6, 2.6, 4.2);
    const luz2 = new THREE.PointLight(0xff5a38, 16, 22, 2);
    luz2.position.set(5, -1.4, 2.6);
    cena.add(luz, luz2);

    /* Fundo: a loja acesa, com clarão quente atrás da árvore */
    const fundo = new THREE.Mesh(
      new THREE.PlaneGeometry(44, 26),
      new THREE.MeshBasicMaterial({
        map: textura(
          tela(512, 288, (x, w, h) => {
            x.fillStyle = "#06090a";
            x.fillRect(0, 0, w, h);
            const m = (cx, cy, r, cor) => {
              const g = x.createRadialGradient(cx, cy, 0, cx, cy, r);
              g.addColorStop(0, cor);
              g.addColorStop(1, "rgba(0,0,0,0)");
              x.fillStyle = g;
              x.fillRect(0, 0, w, h);
            };
            x.globalCompositeOperation = "lighter";
            m(w * 0.46, h * 0.62, 190, "rgba(190,96,28,.58)");
            m(w * 0.8, h * 0.4, 170, "rgba(120,12,30,.6)");
            m(w * 0.14, h * 0.5, 180, "rgba(14,74,52,.62)");
          }),
          true
        )
      })
    );
    fundo.position.z = -9;
    cena.add(fundo);

    const tam = { uTempo: { value: 0 }, uEsc: { value: 600 } };
    const QUENTE = [1.6, 0.86, 0.34];
    const arvore = pontos(
      1300,
      () => {
        const t = Math.pow(sorte(), 0.78);
        const y = -3.6 + 8 * t;
        const raio = (1 - t) * 3.5 + 0.04;
        const giro = t * 74 + sorte() * 0.4;
        const especial = sorte();
        const cor = especial > 0.93 ? [1.7, 0.2, 0.16] : especial > 0.87 ? [2, 1.8, 1.4] : QUENTE;
        return {
          pos: [-0.5 + Math.cos(giro) * raio * (0.9 + sorte() * 0.14), y, -5.2 + Math.sin(giro) * raio * 0.86],
          cor,
          tam: 0.16 + sorte() * 0.16,
          vel: 0.8 + sorte() * 2.6
        };
      },
      FRAG_PONTO,
      tam
    );
    cena.add(arvore);
    const CORES = [[0.5, 0.26, 0.09], [0.54, 0.05, 0.05], [0.05, 0.26, 0.15], [0.54, 0.34, 0.14]];
    const discos = pontos(
      56,
      () => ({
        pos: [-10 + sorte() * 20, -4.5 + sorte() * 9.5, -7 + sorte() * 3.6],
        cor: CORES[Math.floor(sorte() * 4)].map((v) => v * (0.3 + sorte() * 0.5)),
        tam: 0.7 + sorte() * 1.5,
        vel: 0.2 + sorte() * 0.5
      }),
      FRAG_DISCO,
      tam
    );
    cena.add(discos);

    /* Bolas penduradas */
    const mats = materiais();
    const esfera = new THREE.SphereGeometry(1, 64, 44);
    const copa = new THREE.CylinderGeometry(0.11, 0.135, 0.17, 24, 1, true);
    const tampa = new THREE.CylinderGeometry(0.125, 0.11, 0.022, 24);
    const argola = new THREE.TorusGeometry(0.06, 0.012, 10, 28);
    const fio = new THREE.CylinderGeometry(0.0055, 0.0055, 1, 6);
    fio.translate(0, -0.5, 0);
    const bolas = BOLAS.map((b, i) => {
      const pivo = new THREE.Group();
      pivo.position.set(b.x, TETO, b.z);
      const L = TETO - b.y;
      const f = new THREE.Mesh(fio, mats.ferragem);
      f.scale.y = L - b.r - 0.14;
      pivo.add(f);
      const corpo = new THREE.Group();
      corpo.position.y = -L;
      const m = new THREE.Mesh(esfera, mats[b.m]);
      m.scale.setScalar(b.r);
      m.rotation.y = i * 1.3;
      corpo.add(m);
      const fer = new THREE.Group();
      fer.position.y = b.r * 0.985;
      fer.scale.setScalar(0.6 + b.r * 0.55);
      const c = new THREE.Mesh(copa, mats.ferragem);
      c.position.y = 0.075;
      const t = new THREE.Mesh(tampa, mats.ferragem);
      t.position.y = 0.17;
      const a = new THREE.Mesh(argola, mats.ferragem);
      a.position.y = 0.235;
      fer.add(c, t, a);
      corpo.add(fer);
      pivo.add(corpo);
      cena.add(pivo);
      return Object.assign({}, b, { pivo, malha: m, L, ax: 0, az: 0, vx: 0, vz: 0, fase: i * 2.1 });
    });

    /* Tela do vidro */
    const mascara = document.createElement("canvas");
    mascara.width = 512;
    mascara.height = 288;
    const mx = mascara.getContext("2d");
    mx.fillStyle = "#000";
    mx.fillRect(0, 0, 512, 288);
    const tMascara = new THREE.CanvasTexture(mascara);
    tMascara.generateMipmaps = false;
    tMascara.minFilter = THREE.LinearFilter;

    let alvo = null;
    const uniVidro = { tCena: { value: null }, tMascara: { value: tMascara }, tGotas: { value: gotas() }, uClaro: { value: 0 }, uAspecto: { value: 1.7 } };
    const tri = new THREE.BufferGeometry();
    tri.setAttribute("position", new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 3, -1, 0, -1, 3, 0]), 3));
    tri.setAttribute("uv", new THREE.BufferAttribute(new Float32Array([0, 0, 2, 0, 0, 2]), 2));
    const quadroVidro = new THREE.Mesh(tri, new THREE.ShaderMaterial({ vertexShader: VERT_TELA, fragmentShader: FRAG_VIDRO, uniforms: uniVidro, depthTest: false, depthWrite: false }));
    quadroVidro.frustumCulled = false;
    const cenaVidro = new THREE.Scene();
    cenaVidro.add(quadroVidro);
    const camVidro = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

    /* Neve do lado de fora do vidro */
    const uniNeve = { uTempo: tam.uTempo, uEsc: tam.uEsc, uAltura: { value: 5 }, uForca: { value: 1 } };
    const cenaNeve = new THREE.Scene();
    (function () {
      const n = 150;
      const pos = new Float32Array(n * 3);
      const t = new Float32Array(n);
      const f = new Float32Array(n);
      const v = new Float32Array(n);
      for (let i = 0; i < n; i++) {
        pos.set([-6 + sorte() * 12, -5 + sorte() * 10, 3.8 + sorte() * 3.6], i * 3);
        t[i] = 0.018 + sorte() * sorte() * 0.052;
        f[i] = sorte() * 6.283;
        v[i] = 0.26 + sorte() * 0.5;
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
      g.setAttribute("aTam", new THREE.BufferAttribute(t, 1));
      g.setAttribute("aFase", new THREE.BufferAttribute(f, 1));
      g.setAttribute("aVel", new THREE.BufferAttribute(v, 1));
      const o = new THREE.Points(g, new THREE.ShaderMaterial({ vertexShader: VERT_NEVE, fragmentShader: FRAG_NEVE, uniforms: uniNeve, transparent: true, depthWrite: false, depthTest: false }));
      o.frustumCulled = false;
      cenaNeve.add(o);
    })();

    /* Tamanho e qualidade adaptativa */
    let w = 1, h = 1;
    let escala = Math.min(devicePixelRatio || 1, 1.5);
    function criarAlvo() {
      if (alvo) alvo.dispose();
      const a = Math.floor(w * escala);
      const b = Math.floor(h * escala);
      alvo = new THREE.WebGLRenderTarget(a, b, {
        type: THREE.HalfFloatType,
        format: THREE.RGBAFormat,
        generateMipmaps: true,
        minFilter: THREE.LinearMipmapLinearFilter,
        magFilter: THREE.LinearFilter,
        samples: 2,
        depthBuffer: true
      });
      uniVidro.tCena.value = alvo.texture;
    }
    function medir() {
      w = secao.clientWidth || innerWidth;
      h = secao.clientHeight || innerHeight;
      renderer.setPixelRatio(escala);
      renderer.setSize(w, h, false);
      criarAlvo();
      const a = w / h;
      camera.aspect = a;
      camera.fov = a < 1 ? 47 : 34;
      camera.updateProjectionMatrix();
      tam.uEsc.value = (h * escala) / (2 * Math.tan((camera.fov * Math.PI) / 360));
      uniVidro.uAspecto.value = a;
      const comprime = a < 1 ? 0.42 : a < 1.45 ? 0.72 : 1;
      bolas.forEach((b) => {
        b.pivo.position.x = b.x * comprime + (a < 1 ? 0.1 : 0);
      });
    }

    /* Vidro embaçado: limpar, escorrer e embaçar de novo */
    let sujo = false;
    const escorridos = [];
    function pincel(x, y, raio, forca) {
      const g = mx.createRadialGradient(x, y, 0, x, y, raio);
      g.addColorStop(0, "rgba(255,255,255," + forca + ")");
      g.addColorStop(0.68, "rgba(255,255,255," + forca * 0.84 + ")");
      g.addColorStop(1, "rgba(255,255,255,0)");
      mx.fillStyle = g;
      mx.beginPath();
      mx.arc(x, y, raio, 0, 6.283);
      mx.fill();
      sujo = true;
    }
    function limpar(x0, y0, x1, y1) {
      const a = [x0 * 512, y0 * 288];
      const b = [x1 * 512, y1 * 288];
      const d = Math.hypot(b[0] - a[0], b[1] - a[1]);
      const n = Math.max(1, Math.ceil(d / 7));
      const raio = Math.max(20, 512 * (w < 700 ? 0.075 : 0.05));
      for (let i = 1; i <= n; i++) pincel(a[0] + ((b[0] - a[0]) * i) / n, a[1] + ((b[1] - a[1]) * i) / n, raio, 0.72);
      if (Math.random() < 0.05 + d * 0.012 && escorridos.length < 18) escorridos.push({ x: b[0] + (Math.random() - 0.5) * raio, y: b[1] + raio * 0.6, v: 14 + Math.random() * 26, r: 1.4 + Math.random() * 1.8, vida: 1.4 + Math.random() * 2.6 });
    }
    let reembacar = 0;
    function atualizarVidro(dt) {
      for (let i = escorridos.length - 1; i >= 0; i--) {
        const e = escorridos[i];
        e.y += e.v * dt;
        e.x += Math.sin(e.y * 0.2) * 0.1;
        e.vida -= dt;
        pincel(e.x, e.y, e.r * 2.2, 0.8);
        if (e.vida <= 0 || e.y > 296) escorridos.splice(i, 1);
      }
      reembacar += dt;
      if (reembacar > 0.14) {
        reembacar = 0;
        mx.fillStyle = "rgba(0,0,0,.016)";
        mx.fillRect(0, 0, 512, 288);
        sujo = true;
      }
      if (sujo) {
        tMascara.needsUpdate = true;
        sujo = false;
      }
    }

    /* Física dos pêndulos */
    let prog = 0;
    let impulso = 0;
    const ponteiro = { x: 0.7, y: 0.5, vx: 0, vy: 0, dentro: false };
    const v = new THREE.Vector3();
    function fisica(dt) {
      const k = dt * 60;
      bolas.forEach((b, i) => {
        v.setFromMatrixPosition(b.malha.matrixWorld).project(camera);
        const px = v.x * 0.5 + 0.5;
        const py = 0.5 - v.y * 0.5;
        const dx = (px - ponteiro.x) * (w / h);
        const dy = py - ponteiro.y;
        const d = Math.hypot(dx, dy);
        const perto = Math.max(0, 1 - d / (0.14 + b.r * 0.2));
        const rigidez = 7 / (b.L + 0.5);
        const vento = Math.sin(tam.uTempo.value * 0.47 + b.fase) * 0.03;
        b.vz += (-rigidez * b.az - 0.6 * b.vz + vento + ponteiro.vx * perto * 26 * (w / h)) * dt;
        b.vx += (-rigidez * b.ax - 0.6 * b.vx + impulso * (0.5 + (i % 3) * 0.3) + ponteiro.vy * perto * 12) * dt;
        b.az += b.vz * dt;
        b.ax += b.vx * dt;
        b.pivo.rotation.z = b.az;
        b.pivo.rotation.x = b.ax;
        b.malha.rotation.y += (0.06 + Math.abs(b.vz) * 0.8) * dt;
      });
      impulso *= Math.pow(0.86, k);
      ponteiro.vx *= Math.pow(0.8, k);
      ponteiro.vy *= Math.pow(0.8, k);
      const alvoX = (ponteiro.x - 0.5) * 0.34;
      const alvoY = 0.25 - (ponteiro.y - 0.5) * 0.18;
      camera.position.x += (alvoX - camera.position.x) * 0.05 * k;
      camera.position.y += (alvoY - camera.position.y) * 0.05 * k;
      const e = prog * prog * (3 - 2 * prog);
      camera.position.z = CAM_Z - e * 6.2;
      camera.lookAt(camera.position.x * 0.4, 0.25 + e * 0.1, -2);
      uniVidro.uClaro.value = Math.min(1, Math.max(0, (prog - 0.1) / 0.5));
      uniNeve.uForca.value = 1 - Math.min(1, prog * 2.4);
    }

    function desenhar() {
      renderer.setRenderTarget(alvo);
      renderer.clear();
      renderer.render(cena, camera);
      renderer.setRenderTarget(null);
      renderer.render(cenaVidro, camVidro);
      renderer.autoClear = false;
      renderer.render(cenaNeve, camera);
      renderer.autoClear = true;
    }

    let raf = 0;
    let ult = 0;
    let rodando = false;
    let lentos = 0;
    function quadro(agora) {
      raf = requestAnimationFrame(quadro);
      const ms = agora - ult;
      ult = agora;
      const dt = Math.min(0.05, ms / 1000);
      tam.uTempo.value += dt;
      fisica(dt);
      atualizarVidro(dt);
      desenhar();
      lentos = ms > 26 ? lentos + 1 : Math.max(0, lentos - 1);
      if (lentos > 30 && escala > 0.6) {
        escala = Math.max(0.6, escala * 0.82);
        lentos = 0;
        medir();
      }
    }
    function ligar() {
      if (rodando || D.reduzir) return;
      rodando = true;
      ult = performance.now();
      raf = requestAnimationFrame(quadro);
    }
    function desligar() {
      rodando = false;
      cancelAnimationFrame(raf);
    }

    medir();
    if (D.reduzir) {
      uniVidro.uClaro.value = 0.62;
      camera.lookAt(0, 0.25, -2);
      cena.updateMatrixWorld();
      desenhar();
    } else {
      new IntersectionObserver((es) => (es[0].isIntersecting ? ligar() : desligar())).observe(secao);
      document.addEventListener("visibilitychange", () => (document.hidden ? desligar() : ScrollTrigger.isInViewport(secao) && ligar()));
    }

    let espera = 0;
    addEventListener("resize", () => {
      clearTimeout(espera);
      espera = setTimeout(() => {
        medir();
        if (D.reduzir) desenhar();
      }, 160);
    });

    let ultimo = null;
    secao.addEventListener("pointermove", (e) => {
      const r = cv.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width;
      const y = (e.clientY - r.top) / r.height;
      if (ultimo) {
        limpar(ultimo.x, ultimo.y, x, y);
        ponteiro.vx = ponteiro.vx * 0.5 + (x - ultimo.x);
        ponteiro.vy = ponteiro.vy * 0.5 + (y - ultimo.y);
        sumir();
      }
      ponteiro.x = x;
      ponteiro.y = y;
      ultimo = { x, y };
    }, { passive: true });
    secao.addEventListener("pointerleave", () => (ultimo = null));
    secao.addEventListener("pointercancel", () => (ultimo = null));

    const dica = D.$(".vitrine__dica", secao);
    let dicaFora = false;
    function sumir() {
      if (dicaFora || !dica || !demoFeita) return;
      dicaFora = true;
      gsap.to(dica, { autoAlpha: 0, duration: 0.5, delay: 0.8 });
    }

    /* Uma passada automática ensina o gesto */
    let demoFeita = false;
    return {
      progresso(p) {
        const dp = p - prog;
        prog = p;
        impulso += dp * 40;
      },
      demonstrar() {
        if (D.reduzir) return;
        const o = { t: 0 };
        let a = null;
        gsap.to(o, {
          t: 1,
          duration: 1.5,
          ease: "sine.inOut",
          onUpdate() {
            const x = 0.56 + o.t * 0.3;
            const y = 0.56 - Math.sin(o.t * Math.PI) * 0.17 + o.t * 0.02;
            if (a) limpar(a.x, a.y, x, y);
            ponteiro.vx = (x - (a ? a.x : x)) * 1.4;
            a = { x, y };
          },
          onComplete: () => (demoFeita = true)
        });
      }
    };
  };
})();
