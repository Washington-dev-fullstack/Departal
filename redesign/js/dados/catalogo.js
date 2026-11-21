/* Catálogo único da loja. Todas as páginas leem daqui. Descontos são sempre calculados a partir dos preços. */
window.Departal = window.Departal || {};

Departal.andares = [
  { n: 6, id: "presepios", nome: "Presépios", pagina: "presepios.html", capa: "presepio-tradicional", frase: "O nascimento em Belém, entalhado, pintado e iluminado." },
  { n: 5, id: "guirlandas", nome: "Guirlandas", pagina: "guirlandas.html", capa: "guirlanda-tradicional", frase: "A primeira coisa que quem chega vê." },
  { n: 4, id: "luzes", nome: "Luzes", pagina: "luzes.html", capa: "rena-led", frase: "Da árvore à fachada, tudo aceso." },
  { n: 3, id: "roupas", nome: "Roupas", pagina: "roupas.html", capa: "pijama", frase: "Pijamas combinando, vestidos de festa e meias." },
  { n: 2, id: "presentes", nome: "Presentes", pagina: "presentes.html", capa: "caixa-presentes", frase: "Um presente para cada pessoa da sua lista." },
  { n: 1, id: "decoracao", nome: "Decoração", pagina: "decoracao.html", capa: "arvore-180", frase: "Árvores, enfeites e tudo o que transforma a sala." }
];

Departal.produtos = [
  /* Andar 1: decoração */
  { id: "arvore-180", andar: "decoracao", nome: "Árvore de Natal Artificial 1,80 m", desc: "Árvore premium com ramos realistas e iluminação integrada.", preco: 299.9, selo: "Mais vendido", spec: [["medida", "1,80 m"], ["led", "Luzes integradas"]] },
  { id: "arvore-kit", andar: "decoracao", nome: "Árvore de Natal e Kit", desc: "Árvore pequena com um kit de enfeites completo.", preco: 126.63, de: 180.9, selo: "Promoção de ouro", spec: [["pecas", "Árvore + enfeites"]] },
  { id: "pinhas", andar: "decoracao", nome: "Conjunto de Pinhas", desc: "20 pinhas decorativas para a sua árvore de Natal.", preco: 79.9, spec: [["pecas", "20 pinhas"]] },
  { id: "enfeites", andar: "decoracao", nome: "Enfeites para Árvore de Natal", desc: "Enfeites para pendurar na sua árvore de Natal.", preco: 8.9, spec: [["pecas", "Para pendurar"]] },
  { id: "festao", andar: "decoracao", nome: "Festive Festão", desc: "Festão brilhante para contornar a sua árvore de Natal.", preco: 19.99, spec: [["medida", "200 × 10 cm"]] },
  { id: "bolas-estrelas", andar: "decoracao", nome: "Conjunto de Bolas Natalinas com Estrelas", desc: "Bolas com estrelas douradas, perfeitas para a sua casa.", preco: 17.99, spec: [["pecas", "Conjunto"]] },
  { id: "kit-decoracao", andar: "decoracao", secao: "ofertas", nome: "Kit Decoração Natal Completo", desc: "Inclui árvore, enfeites, luzes e guirlanda: tudo o que você precisa para o Natal.", preco: 449.9, de: 599.9, spec: [["pecas", "4 itens"], ["led", "Luzes inclusas"]] },
  { id: "lacinhos", andar: "decoracao", secao: "ofertas", nome: "Lacinhos", desc: "Conjunto com 20 lacinhos vermelhos para decorar todo o exterior da casa.", preco: 10.9, de: 17.9, spec: [["pecas", "20 lacinhos"]] },
  { id: "mini-arvore", andar: "decoracao", secao: "ofertas", nome: "Mini Árvore de Natal com Pinhas", desc: "Pequena, mas elegante. Por tempo ultra limitado, está a troco de bala.", preco: 123.2, de: 257.9, spec: [["pinho", "Com pinhas"]] },

  /* Andar 2: presentes */
  { id: "caixa-presentes", andar: "presentes", nome: "Caixa de Presentes Premium", desc: "4 itens surpresa selecionados.", preco: 34, de: 49.99, filtros: ["familia"], interesse: ["surpresa"], spec: [["pecas", "4 itens surpresa"]] },
  { id: "kit-construcao", andar: "presentes", nome: "Kit de Construção Criativa", desc: "Blocos de montar coloridos para desenvolver a criatividade das crianças.", preco: 89.9, selo: "Educativo", filtros: ["criancas"], interesse: ["criancas"], spec: [["pecas", "200 peças"]] },
  { id: "kit-churrasco", andar: "presentes", nome: "Kit Churrasco Premium", desc: "Faca, garfo, espeto e acessórios em aço inox.", preco: 159.9, de: 199.9, filtros: ["mao-na-massa"], interesse: ["cozinha"], spec: [["pecas", "8 peças"], ["metal", "Aço inox"]] },
  { id: "kit-cosmeticos", andar: "presentes", nome: "Kit Cosméticos Natalino Premium", desc: "Perfume, cremes e essências com fragrância especial de Natal.", preco: 129.9, selo: "Mais vendido", filtros: ["cuidados"], interesse: ["cuidados"], spec: [["aroma", "Fragrância de Natal"]] },
  { id: "jogo-noite-feliz", andar: "presentes", nome: "Jogo de Tabuleiro “Noite Feliz”", desc: "Diversão garantida para toda a família nas festas de fim de ano.", preco: 79.9, filtros: ["familia", "criancas"], interesse: ["familia", "criancas"], spec: [["pessoas", "Para a família"]] },
  { id: "urso-pelucia", andar: "presentes", nome: "Urso de Pelúcia Gigante", desc: "O companheiro perfeito para as noites de inverno, super fofinho.", preco: 119.9, de: 149.9, filtros: ["criancas"], interesse: ["criancas"], spec: [["medida", "1,5 m"]] },
  { id: "kit-ferramentas", andar: "presentes", nome: "Kit Ferramentas", desc: "Perfeito para pequenos reparos em casa, com qualidade profissional.", preco: 189.9, filtros: ["mao-na-massa"], interesse: ["mao-na-massa"], spec: [["pecas", "32 peças"]] },
  { id: "caneca", andar: "presentes", secao: "faixa", faixa: "ate-50", nome: "Caneca Natalina", desc: "Para o chocolate quente da noite de Natal.", preco: 29.9, interesse: ["cozinha", "surpresa"] },
  { id: "chocolate", andar: "presentes", secao: "faixa", faixa: "ate-50", nome: "Chocolate Artesanal", desc: "Barra de chocolate artesanal embrulhada para presente.", preco: 24.9, interesse: ["cozinha", "surpresa"] },
  { id: "par-meias", andar: "presentes", secao: "faixa", faixa: "ate-150", nome: "Par de Meias Natalina", desc: "Meias de tricô com estampa natalina.", preco: 64.9, interesse: ["familia", "surpresa"] },
  { id: "cestinha", andar: "presentes", secao: "faixa", faixa: "ate-150", nome: "Cestinha de Natal", desc: "Cesta com mimos, fita de cetim e ramos de pinho.", preco: 54.5, interesse: ["familia", "surpresa"] },
  { id: "floratta-gold", andar: "presentes", secao: "faixa", faixa: "acima-150", nome: "Floratta Gold", desc: "Perfume dourado para presentear.", preco: 160, interesse: ["cuidados"] },
  { id: "sonhos-natal", andar: "presentes", secao: "faixa", faixa: "acima-150", nome: "Sonhos de Natal", desc: "Nosso presente mais especial, em caixa dourada com laço de cetim.", preco: 250.9, interesse: ["familia", "surpresa"] },

  /* Andar 3: roupas */
  { id: "pijama", andar: "roupas", nome: "Pijama Natalino Unisex", desc: "Conjunto para dormir: blusa de corações e calça xadrez.", preco: 57.54, de: 95.9, tamanhos: ["P", "M", "G", "GG"], filtros: ["adultos"], interesse: ["familia"], spec: [["tecido", "Blusa + calça"]] },
  { id: "pijama-premium", andar: "roupas", nome: "Pijama Natalino Premium", desc: "Conforto e estilo para as noites de Natal, disponível em vários tamanhos.", preco: 89.9, selo: "Conforto", tamanhos: ["P", "M", "G", "GG"], filtros: ["adultos"], interesse: ["familia"], spec: [["tecido", "Blusa + calça"]] },
  { id: "vestido-infantil", andar: "roupas", nome: "Vestido Natalino Infantil", desc: "Perfeito para a festa da escola e a ceia de Natal, de 2 a 12 anos.", preco: 59.9, de: 79.9, tamanhos: ["2-4", "6-8", "10-12"], filtros: ["criancas"], interesse: ["criancas"], spec: [["tecido", "Veludo"]] },
  { id: "conjunto-familiar", andar: "roupas", nome: "Conjunto Familiar Matching", desc: "Pijamas combinando para adultos e crianças: a família toda igual.", preco: 249.9, selo: "Família", filtros: ["familia"], interesse: ["familia"], spec: [["pessoas", "Kit família"]] },
  { id: "camiseta", andar: "roupas", nome: "Camiseta “Feliz Natal”", desc: "Estilo casual para os dias festivos, 100% algodão.", preco: 49.9, tamanhos: ["P", "M", "G", "GG"], filtros: ["adultos"], spec: [["tecido", "100% algodão"]] },
  { id: "kit-meias", andar: "roupas", nome: "Kit Meias Natalinas", desc: "Meias temáticas para presentear ou usar na noite de Natal.", preco: 34.9, de: 45.9, filtros: ["acessorios"], interesse: ["surpresa"], spec: [["pecas", "3 pares"]] },
  { id: "conjunto-noel", andar: "roupas", nome: "Conjunto Infantil Papai Noel", desc: "Fantasia completa para as crianças, com gorro e cinto.", preco: 99.9, tamanhos: ["3-4", "5-6", "7-8"], filtros: ["criancas"], interesse: ["criancas"], spec: [["pecas", "Gorro e cinto"]] },
  { id: "look-feminino", andar: "roupas", secao: "looks", nome: "Look Festivo Feminino", desc: "Vestido vermelho com acessórios dourados.", preco: 189.9, filtros: ["adultos"], tamanhos: ["P", "M", "G", "GG"], interesse: ["cuidados"] },
  { id: "look-familiar", andar: "roupas", secao: "looks", nome: "Look Familiar Completo", desc: "Pijamas combinando para 4 pessoas.", preco: 329.9, filtros: ["familia"], interesse: ["familia"] },

  /* Andar 4: luzes */
  { id: "fita-led", andar: "luzes", nome: "Fita LED Colorida 10 m", desc: "Com controle remoto e 16 cores, impermeável para uso interno e externo.", preco: 89.9, selo: "Mais vendida", filtros: ["led", "arvore"], interesse: ["casa"], spec: [["medida", "10 metros"], ["cor", "16 cores"], ["controle", "Controle"]] },
  { id: "rena-led", andar: "luzes", nome: "Rena LED 1,2 m", desc: "Decoração externa com iluminação quente, perfeita para o jardim.", preco: 129.9, de: 159.9, filtros: ["exterior", "figuras"], interesse: ["casa"], spec: [["led", "LED quente"], ["agua", "Impermeável"], ["medida", "1,2 metro"]] },
  { id: "pisca-pisca", andar: "luzes", nome: "Pisca-Pisca 200 Lâmpadas", desc: "Luzes intermitentes multicoloridas com 8 modos de funcionamento.", preco: 49.9, selo: "Clássico", filtros: ["arvore"], interesse: ["casa"], spec: [["led", "200 lâmpadas"], ["modos", "8 modos"], ["cabo", "10 m de cabo"]] },
  { id: "cortina-led", andar: "luzes", nome: "Cortina de LED 300 LEDs", desc: "Perfeita para janelas e varandas, com efeito de chuva de luzes.", preco: 119.9, filtros: ["exterior", "led"], interesse: ["casa"], spec: [["led", "300 LEDs"], ["medida", "3 × 2 metros"], ["controle", "Controle"]] },
  { id: "boneco-neve-led", andar: "luzes", nome: "Boneco de Neve LED 80 cm", desc: "Decoração interna com iluminação suave e sensor de movimento.", preco: 79.9, de: 99.9, filtros: ["figuras"], interesse: ["criancas", "casa"], spec: [["medida", "80 cm"], ["sensor", "Sensor"], ["led", "LED branco"]] },
  { id: "leds-arvore", andar: "luzes", nome: "LEDs para Árvore 500 Pontos", desc: "Iluminação profissional para árvores grandes, em branco quente.", preco: 189.9, filtros: ["arvore", "led"], interesse: ["casa"], spec: [["led", "500 LEDs"], ["cor", "Branco quente"], ["cabo", "15 m de cabo"]] },
  { id: "kit-externa", andar: "luzes", secao: "kits", nome: "Kit Iluminação Externa Completo", desc: "Inclui cortina LED, 2 renas, fachada e controlador.", preco: 399.9, filtros: ["exterior"], interesse: ["casa"], spec: [["casa", "Para toda a casa"], ["agua", "À prova d’água"], ["controle", "Controle único"]] },
  { id: "kit-arvore-premium", andar: "luzes", secao: "kits", nome: "Kit Árvore Premium", desc: "LEDs, pisca-pisca, ponto central e controlador RGB.", preco: 249.9, de: 299.9, filtros: ["arvore"], interesse: ["casa"], spec: [["pinho", "Árvore completa"], ["cor", "Cores RGB"], ["controle", "Controle por app"]] },

  /* Andar 5: guirlandas */
  { id: "guirlanda-tradicional", andar: "guirlandas", nome: "Guirlanda Tradicional 60 cm", desc: "Pinho natural, frutas vermelhas e laço de cetim, com aroma de canela.", preco: 79.9, selo: "Tradicional", filtros: ["porta"], interesse: ["casa"], spec: [["medida", "60 cm"], ["laco", "Laço incluso"], ["pinho", "Pinho natural"]] },
  { id: "guirlanda-led", andar: "guirlandas", nome: "Guirlanda LED 50 cm", desc: "50 pontos de luz dourada e bateria inclusa, com duração de 30 dias.", preco: 99.9, de: 129.9, filtros: ["porta", "luminosa"], interesse: ["casa"], spec: [["led", "50 LEDs"], ["bateria", "Bateria inclusa"], ["medida", "50 cm"]] },
  { id: "guirlanda-mini", andar: "guirlandas", nome: "Mini Guirlanda 25 cm", desc: "Perfeita para centro de mesa, com pinhas douradas e frutas cristalizadas.", preco: 39.9, selo: "Mesa", filtros: ["mesa"], interesse: ["casa"], spec: [["medida", "25 cm"], ["brilho", "Dourada"], ["casa", "Interior"]] },
  { id: "guirlanda-rustica", andar: "guirlandas", nome: "Guirlanda Rústica 70 cm", desc: "Estilo country com ramos secos, pinhas e corda natural.", preco: 89.9, filtros: ["parede"], interesse: ["casa"], spec: [["medida", "70 cm"], ["madeira", "Rústica"], ["pinho", "Natural"]] },
  { id: "guirlanda-rgb", andar: "guirlandas", nome: "Guirlanda RGB 45 cm", desc: "LEDs de 16 cores, com controle remoto e timer automático.", preco: 119.9, de: 149.9, filtros: ["luminosa"], interesse: ["casa"], spec: [["cor", "16 cores"], ["relogio", "Timer"], ["controle", "Controle"]] },
  { id: "guirlanda-premium", andar: "guirlandas", nome: "Guirlanda Premium 80 cm", desc: "Material sintético premium, resistente ao clima e com aroma artificial.", preco: 159.9, filtros: ["parede", "porta"], interesse: ["casa"], spec: [["medida", "80 cm"], ["agua", "Exterior"], ["brilho", "Premium"]] },
  { id: "kit-entrada", andar: "guirlandas", secao: "kits", nome: "Kit Entrada Principal", desc: "Guirlanda 70 cm, laço premium, sino decorativo e placa “Feliz Natal”.", preco: 199.9, filtros: ["porta"], interesse: ["casa"], spec: [["casa", "Porta principal"], ["laco", "Acessórios inclusos"], ["agua", "Resistente"]] },
  { id: "kit-luminosas", andar: "guirlandas", secao: "kits", nome: "Kit Guirlandas Luminosas", desc: "3 guirlandas LED para porta, parede e mesa, com pilhas e controle universal.", preco: 279.9, de: 349.9, filtros: ["luminosa"], interesse: ["casa"], spec: [["led", "3 guirlandas LED"], ["bateria", "Pilhas inclusas"], ["controle", "Controle único"]] },

  /* Andar 6: presépios */
  { id: "presepio-tradicional", andar: "presepios", nome: "Presépio Tradicional 12 Peças", desc: "Conjunto completo em madeira entalhada: família sagrada, animais e reis magos.", preco: 189.9, selo: "Clássico", filtros: ["tradicional"], interesse: ["familia"], spec: [["pecas", "12 peças"], ["madeira", "Madeira"], ["medida", "40 cm"]] },
  { id: "presepio-led", andar: "presepios", nome: "Presépio LED com Estrela", desc: "Iluminação suave e estrela piscante, com efeito noturno realista.", preco: 129.9, de: 159.9, filtros: ["luminoso"], interesse: ["familia"], spec: [["led", "LED"], ["estrela", "Estrela"], ["pecas", "8 peças"]] },
  { id: "presepio-ceramica", andar: "presepios", nome: "Presépio Cerâmica Pintado à Mão", desc: "Peças únicas pintadas manualmente, com detalhes em ouro e prata.", preco: 299.9, selo: "Exclusivo", filtros: ["artesanal"], interesse: ["familia"], spec: [["brilho", "Artesanal"], ["casa", "Cerâmica"], ["pecas", "10 peças"]] },
  { id: "presepio-minimalista", andar: "presepios", nome: "Presépio Minimalista Aço", desc: "Design contemporâneo em aço inox, perfeito para decoração moderna.", preco: 219.9, filtros: ["moderno"], interesse: ["casa"], spec: [["brilho", "Moderno"], ["metal", "Aço inox"], ["pecas", "6 peças"]] },
  { id: "vila-led", andar: "presepios", nome: "Presépio Vila Completa LED", desc: "Com casinhas, poço e árvores iluminadas: cenário completo de Belém.", preco: 329.9, de: 399.9, filtros: ["luminoso"], interesse: ["familia"], spec: [["casa", "Vila"], ["led", "LED"], ["pecas", "15 peças"]] },
  { id: "presepio-barro", andar: "presepios", nome: "Presépio Barro Nordestino", desc: "Arte popular brasileira: peças em barro cozido com pigmentos naturais.", preco: 179.9, filtros: ["artesanal"], interesse: ["familia"], spec: [["brilho", "Nordestino"], ["casa", "Barro"], ["pecas", "9 peças"]] },
  { id: "kit-familia-sagrada", andar: "presepios", secao: "kits", nome: "Kit Família Sagrada Premium", desc: "Presépio 12 peças, manjedoura iluminada, estrela e musgo decorativo.", preco: 459.9, filtros: ["tradicional"], interesse: ["familia"], spec: [["pessoas", "Família completa"], ["led", "Iluminação"], ["pinho", "Acessórios"]] },
  { id: "kit-belem", andar: "presepios", secao: "kits", nome: "Kit Belém Completo", desc: "Vila iluminada, 20 personagens, animais e paisagem desértica.", preco: 599.9, de: 699.9, filtros: ["luminoso"], interesse: ["familia"], spec: [["casa", "Vila completa"], ["pecas", "20 peças"], ["pinho", "Cenário"]] }
];

Departal.filtros = {
  presentes: [["todos", "Todos os presentes"], ["criancas", "Para crianças"], ["mao-na-massa", "Mão na massa"], ["cuidados", "Cuidados pessoais"], ["familia", "Para a família"]],
  roupas: [["todos", "Todas as roupas"], ["adultos", "Para adultos"], ["criancas", "Para crianças"], ["familia", "Conjuntos familiares"], ["acessorios", "Acessórios"]],
  luzes: [["todos", "Todas as luzes"], ["arvore", "Para árvore"], ["exterior", "Exterior"], ["led", "LEDs"], ["figuras", "Figuras luminosas"]],
  guirlandas: [["todos", "Todas as guirlandas"], ["porta", "Para porta"], ["parede", "Para parede"], ["mesa", "Para mesa"], ["luminosa", "Com luzes"]],
  presepios: [["todos", "Todos os presépios"], ["tradicional", "Tradicionais"], ["moderno", "Modernos"], ["luminoso", "Com luzes"], ["artesanal", "Artesanais"]]
};
