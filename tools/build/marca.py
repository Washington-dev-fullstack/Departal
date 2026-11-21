# Marca da Departal para o site novo:
#  - letras do letreiro em vetor (Montserrat, a mesma família do logo), uma a uma, para acender em sequência;
#  - guirlanda recortada do logo original (PNG do cliente), sem as letras vermelhas;
#  - favicon "DE" com o gorro.
import json
import os

import numpy as np
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..", "..")
SITE = os.path.join(RAIZ, "redesign")
os.makedirs(os.path.join(SITE, "images", "marca"), exist_ok=True)

fonte = TTFont(os.path.join(AQUI, "node_modules", "@fontsource", "montserrat", "files", "montserrat-latin-800-normal.woff2"))
gs = fonte.getGlyphSet()
cmap = fonte.getBestCmap()
upem = fonte["head"].unitsPerEm
ALTURA = 700  # altura de capitular usada nas contas

# ajustes de entreletra medidos no logo original
AJUSTE = {"DE": -8, "EP": -8, "PA": -46, "AR": -22, "RT": -30, "TA": -52, "AL": -20}
letras = []
x = 0.0
palavra = "DEPARTAL"
for i, ch in enumerate(palavra):
    g = cmap[ord(ch)]
    pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
    gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, ALTURA)))
    b = BoundsPen(gs)
    gs[g].draw(b)
    letras.append({"ch": ch, "d": pen.getCommands(), "x0": round(x + b.bounds[0], 1), "x1": round(x + b.bounds[2], 1)})
    x += gs[g].width
    if i + 1 < len(palavra):
        x += AJUSTE.get(ch + palavra[i + 1], 0)
largura = round(letras[-1]["x1"] + 4)

js = "/* Gerado por tools/build/marca.py. Letras do letreiro em vetor. */\nwindow.Departal = window.Departal || {};\nDepartal.letreiro = " + json.dumps({"largura": largura, "altura": ALTURA, "letras": letras}, ensure_ascii=False, separators=(",", ":")) + ";\n"
with open(os.path.join(SITE, "js", "dados", "letreiro.js"), "w", encoding="utf-8") as f:
    f.write(js)
print("letreiro", largura, len(js))

# guirlanda: tudo o que não é o vermelho chapado das letras
im = Image.open(os.path.join(RAIZ, "images", "logo - site.png")).convert("RGBA")
a = np.array(im).astype(np.int16)
vermelho = (np.abs(a[..., 0] - 190) < 22) & (np.abs(a[..., 1] - 22) < 20) & (np.abs(a[..., 2] - 34) < 22)
linha_letras = 840  # acima daqui não há guirlanda, só letras e o topo dos laços
alfa = a[..., 3].copy()
alfa[vermelho & (np.arange(a.shape[0])[:, None] < 990)] = 0
# sobra apenas a região da guirlanda, com os laços que sobem sobre as letras
alfa[: linha_letras - 170] = 0
limpa = Image.fromarray(np.dstack([a[..., 0], a[..., 1], a[..., 2], alfa]).astype(np.uint8), "RGBA")
# remove a franja vermelha fina deixada pelas letras
bb = limpa.getbbox()
limpa = limpa.crop(bb)
limpa.thumbnail((2400, 2400), Image.LANCZOS)
limpa.save(os.path.join(SITE, "images", "marca", "guirlanda.webp"), quality=86, method=6)
print("guirlanda", limpa.size, bb)
