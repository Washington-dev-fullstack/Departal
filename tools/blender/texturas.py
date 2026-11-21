# Gera as estampas usadas nos produtos 3D. Roda no Python do sistema: python texturas.py
import math
import os
import random

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(AQUI, "tex")
FONTES = os.path.join(AQUI, "..", "build", "node_modules", "@fontsource-variable")
os.makedirs(TEX, exist_ok=True)

VINHO = (86, 12, 28)
VERMELHO = (178, 18, 38)
VERMELHO_ESC = (120, 10, 26)
VERDE = (16, 74, 52)
VERDE_ESC = (10, 44, 32)
OURO = (216, 170, 92)
CREME = (240, 230, 210)
BRANCO = (244, 240, 232)
PRETO = (20, 18, 18)


def fonte(tam):
    ttf = os.path.join(TEX, "fraunces.ttf")
    if not os.path.exists(ttf):
        f = TTFont(os.path.join(FONTES, "fraunces", "files", "fraunces-latin-full-normal.woff2"))
        f.flavor = None
        f.save(ttf)
    return ImageFont.truetype(ttf, tam)


def peso(fnt, valor=700):
    try:
        fnt.set_variation_by_axes([144, valor, 100, 0][: len(fnt.get_variation_axes())])
    except Exception:
        pass
    return fnt


def salvar(im, nome):
    im.save(os.path.join(TEX, nome))


def xadrez(nome, fundo, fx, fy, linha, tam=1024, malha=256):
    """Tartã: duas faixas cruzadas em transparência mais fios finos, com trama."""
    im = Image.new("RGB", (tam, tam), fundo)
    cam = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    for k in range(0, tam, malha):
        d.rectangle((k + malha * 0.12, 0, k + malha * 0.5, tam), fill=(*fx, 150))
        d.rectangle((0, k + malha * 0.12, tam, k + malha * 0.5), fill=(*fy, 150))
    im.paste(cam, (0, 0), cam)
    d = ImageDraw.Draw(im)
    for k in range(0, tam, malha):
        x = k + malha * 0.78
        d.rectangle((x, 0, x + 6, tam), fill=linha)
        d.rectangle((0, x, tam, x + 6), fill=linha)
    p = im.load()
    for y in range(tam):
        for x in range(tam):
            t = 0.93 + 0.07 * (((x // 2) + (y // 2)) % 2)
            r, g, b = p[x, y]
            p[x, y] = (int(r * t), int(g * t), int(b * t))
    salvar(im, nome)


def coracao(d, cx, cy, r, cor):
    pts = []
    for i in range(60):
        t = i / 60 * math.tau
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * r / 16, cy - y * r / 16))
    d.polygon(pts, fill=cor)


def coracoes():
    """A estampa do seu pijama original: vinho com corações brancos."""
    s = 3
    tam = 1024
    im = Image.new("RGB", (tam * s, tam * s), VINHO)
    d = ImageDraw.Draw(im)
    passo = 170
    for j in range(7):
        for i in range(7):
            x = (i * passo + (passo / 2 if j % 2 else 0)) * s
            y = j * passo * s
            for ox in (0, tam * s):
                for oy in (0, tam * s):
                    coracao(d, x + ox - tam * s, y + oy - tam * s, 40 * s, BRANCO)
    salvar(im.resize((tam, tam), Image.LANCZOS), "coracoes.png")


def estrela_pts(cx, cy, r, ri, n=5, giro=-math.pi / 2):
    return [(cx + (r if i % 2 == 0 else ri) * math.cos(giro + i * math.pi / n), cy + (r if i % 2 == 0 else ri) * math.sin(giro + i * math.pi / n)) for i in range(n * 2)]


def estrelas_bola():
    """Estrelas douradas sobre vermelho para a bola natalina."""
    tam = 2048
    im = Image.new("RGB", (tam, tam // 2), VERMELHO)
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for j in range(5):
        y = (j + 0.5) / 5 * tam / 2
        n = [6, 10, 12, 10, 6][j]
        for i in range(n):
            x = (i + 0.5 * (j % 2)) / n * tam
            d.polygon(estrela_pts(x, y, rnd.uniform(44, 58), 22), fill=OURO)
    salvar(im, "estrelas-bola.png")


def malha_rena(nome, fundo, frente, faixa):
    """Tricô natalino: gráfico em pontos com renas, flocos e faixas."""
    pontos = 96
    im = Image.new("RGB", (pontos, pontos), fundo)
    p = im.load()

    def ponto(x, y, c):
        p[x % pontos, y % pontos] = c

    for x in range(pontos):
        for y in (0, 1, 22, 23, 48, 49, 70, 71):
            ponto(x, y, faixa)
        for y in (6, 17, 54, 65):
            if (x // 2) % 2 == 0:
                ponto(x, y, frente)
    floco = ["...X...", ".X.X.X.", "..XXX..", "XXXXXXX", "..XXX..", ".X.X.X.", "...X..."]
    arvore = ["...X...", "..XXX..", ".XXXXX.", "..XXX..", ".XXXXX.", "XXXXXXX", "...X..."]
    for k in range(0, pontos, 16):
        for j, lin in enumerate(floco):
            for i, c in enumerate(lin):
                if c == "X":
                    ponto(k + i + 4, 8 + j, frente)
        for j, lin in enumerate(arvore):
            for i, c in enumerate(lin):
                if c == "X":
                    ponto(k + i + 12, 56 + j, frente)
    for k in range(0, pontos, 12):
        for j in range(5):
            for i in range(5):
                if (i + j) % 2 == 0:
                    ponto(k + i + 1, 34 + j, frente)
    grande = im.resize((1024, 1024), Image.NEAREST)
    fios = Image.new("L", (1024, 1024), 255)
    df = ImageDraw.Draw(fios)
    for k in range(0, 1024, 11):
        df.line((0, k, 1024, k), fill=214, width=2)
        df.line((k, 0, k, 1024), fill=226, width=1)
    grande = Image.composite(grande, Image.eval(grande, lambda v: int(v * 0.72)), fios)
    salvar(grande.filter(ImageFilter.GaussianBlur(1.1)), nome)


def listras_meia():
    im = Image.new("RGB", (1024, 1024), BRANCO)
    d = ImageDraw.Draw(im)
    cores = [VERMELHO, BRANCO, VERDE, BRANCO]
    for i in range(0, 1024, 64):
        d.rectangle((0, i, 1024, i + 64), fill=cores[(i // 64) % 4])
    salvar(im, "listras-meia.png")


def camiseta():
    tam = 2048
    im = Image.new("RGB", (tam, tam), VERMELHO)
    d = ImageDraw.Draw(im)
    f = peso(fonte(250), 800)
    for txt, y in (("Feliz", 780), ("Natal", 1040)):
        l = d.textlength(txt, font=f)
        d.text(((tam - l) / 2, y), txt, font=f, fill=CREME)
    d.polygon(estrela_pts(tam / 2, 640, 80, 32), fill=OURO)
    salvar(im, "camiseta.png")


def capa_jogo():
    """Tampa do jogo Noite Feliz, ilustração própria."""
    tam = 1400
    im = Image.new("RGB", (tam, tam), (12, 34, 62))
    d = ImageDraw.Draw(im)
    for y in range(tam):
        t = y / tam
        d.line((0, y, tam, y), fill=(int(10 + 34 * t), int(20 + 40 * t), int(52 + 58 * t)))
    rnd = random.Random(3)
    for _ in range(340):
        x, y, r = rnd.uniform(0, tam), rnd.uniform(0, tam * 0.7), rnd.uniform(1.5, 5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 240, 214))
    d.polygon(estrela_pts(tam * 0.5, tam * 0.2, 96, 36, 4), fill=(255, 228, 176))
    d.ellipse((tam * 0.5 - 200, tam * 0.2 - 200, tam * 0.5 + 200, tam * 0.2 + 200), outline=(255, 228, 176), width=3)
    d.ellipse((-tam * 0.3, tam * 0.74, tam * 0.9, tam * 1.3), fill=(236, 240, 246))
    d.ellipse((tam * 0.3, tam * 0.78, tam * 1.3, tam * 1.3), fill=(214, 222, 234))
    for x, h in ((0.16, 330), (0.32, 240), (0.86, 370), (0.72, 230)):
        cx = tam * x
        base = tam * 0.83
        for k in range(3):
            lar = h * (0.42 - k * 0.09)
            top = base - h * (0.5 + k * 0.24)
            d.polygon([(cx, top), (cx - lar, base - k * h * 0.2), (cx + lar, base - k * h * 0.2)], fill=(14, 72, 52))
    d.rectangle((tam * 0.44, tam * 0.66, tam * 0.58, tam * 0.8), fill=(150, 26, 40))
    d.polygon([(tam * 0.41, tam * 0.67), (tam * 0.51, tam * 0.58), (tam * 0.61, tam * 0.67)], fill=(92, 18, 30))
    d.rectangle((tam * 0.49, tam * 0.71, tam * 0.53, tam * 0.75), fill=(255, 214, 140))
    f = peso(fonte(170), 800)
    l = d.textlength("Noite Feliz", font=f)
    d.text(((tam - l) / 2, tam * 0.32), "Noite Feliz", font=f, fill=(255, 236, 196))
    f2 = fonte(54)
    l = d.textlength("o jogo de tabuleiro da família", font=f2)
    d.text(((tam - l) / 2, tam * 0.47), "o jogo de tabuleiro da família", font=f2, fill=(226, 222, 212))
    salvar(im, "capa-jogo.png")


def tabuleiro():
    tam = 1400
    im = Image.new("RGB", (tam, tam), (242, 234, 214))
    d = ImageDraw.Draw(im)
    cores = [VERMELHO, VERDE, OURO, (240, 240, 236)]
    n = 11
    c = tam / n
    idx = 0
    for i in range(n):
        for lado, (x, y) in enumerate(((i, 0), (n - 1, i), (n - 1 - i, n - 1), (0, n - 1 - i))):
            d.rectangle((x * c + 5, y * c + 5, (x + 1) * c - 5, (y + 1) * c - 5), fill=cores[idx % 4])
            idx += 1
    d.polygon(estrela_pts(tam / 2, tam / 2, 300, 118), fill=VERMELHO)
    f = peso(fonte(100), 800)
    l = d.textlength("Noite Feliz", font=f)
    d.text(((tam - l) / 2, tam * 0.71), "Noite Feliz", font=f, fill=VERDE)
    salvar(im, "tabuleiro.png")


def rotulo(nome, texto, sub, fundo, cor, larg=1024, alt=512):
    im = Image.new("RGB", (larg, alt), fundo)
    d = ImageDraw.Draw(im)
    f = peso(fonte(int(alt * 0.3)), 700)
    l = d.textlength(texto, font=f)
    d.text(((larg - l) / 2, alt * 0.2), texto, font=f, fill=cor)
    if sub:
        f2 = fonte(int(alt * 0.11))
        l = d.textlength(sub, font=f2)
        d.text(((larg - l) / 2, alt * 0.66), sub, font=f2, fill=cor)
    d.rectangle((26, 26, larg - 26, alt - 26), outline=cor, width=4)
    salvar(im, nome)


def papel_presente(nome, fundo, cor, tipo):
    tam = 1024
    im = Image.new("RGB", (tam * 2, tam * 2), fundo)
    d = ImageDraw.Draw(im)
    passo = 300
    for j in range(8):
        for i in range(8):
            x = (i * passo + (passo / 2 if j % 2 else 0))
            y = j * passo
            if tipo == "estrela":
                d.polygon(estrela_pts(x, y, 70, 28), fill=cor)
            elif tipo == "bolinha":
                d.ellipse((x - 44, y - 44, x + 44, y + 44), fill=cor)
            else:
                for a in range(6):
                    v = a * math.pi / 3
                    d.line((x, y, x + 74 * math.cos(v), y + 74 * math.sin(v)), fill=cor, width=12)
    salvar(im.resize((tam, tam), Image.LANCZOS), nome)


def caneca():
    larg, alt = 2048, 700
    im = Image.new("RGB", (larg, alt), (168, 16, 34))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 200, larg, 500), fill=BRANCO)
    for y in (186, 500):
        d.rectangle((0, y, larg, y + 14), fill=OURO)
    n = 9
    for i in range(n):
        x = (i + 0.5) / n * larg
        cor = VERDE if i % 2 else (168, 16, 34)
        if i % 2:
            for k in range(3):
                lar = 86 - k * 22
                d.polygon([(x, 236 + k * 62), (x - lar, 320 + k * 62), (x + lar, 320 + k * 62)], fill=cor)
        else:
            d.polygon(estrela_pts(x, 350, 92, 36, 6, 0), fill=cor)
    salvar(im, "caneca.png")


def placa():
    rotulo("placa-feliz-natal.png", "Feliz Natal", "", (232, 216, 182), (118, 28, 26), 1024, 400)
    rotulo("placa-familia.png", "Família Silva", "", (232, 216, 182), (118, 28, 26), 1024, 400)


xadrez("xadrez-vermelho.png", VERMELHO, VERDE_ESC, VERDE_ESC, (236, 214, 150))
xadrez("xadrez-verde.png", VERDE, VERMELHO_ESC, VERMELHO_ESC, (236, 214, 150))
xadrez("xadrez-vinho.png", (40, 16, 20), (150, 18, 34), (150, 18, 34), (226, 206, 150))
coracoes()
estrelas_bola()
malha_rena("trico-vermelho.png", VERMELHO, BRANCO, OURO)
malha_rena("trico-verde.png", VERDE, BRANCO, VERMELHO)
malha_rena("trico-creme.png", CREME, VERMELHO, VERDE)
listras_meia()
camiseta()
capa_jogo()
tabuleiro()
rotulo("rotulo-chocolate.png", "Artesanal", "chocolate 70%", (112, 16, 28), (240, 214, 160))
rotulo("rotulo-creme.png", "Pinho e canela", "creme corporal", (240, 230, 210), (120, 22, 30))
rotulo("rotulo-frasco.png", "Noite de Natal", "essência", (240, 230, 210), (20, 62, 46))
papel_presente("papel-estrela.png", VERDE, OURO, "estrela")
papel_presente("papel-floco.png", VERMELHO, CREME, "floco")
papel_presente("papel-bolinha.png", (28, 24, 26), OURO, "bolinha")
papel_presente("papel-ouro.png", (210, 164, 88), (246, 216, 150), "estrela")
caneca()
placa()
print(sorted(os.listdir(TEX)))
