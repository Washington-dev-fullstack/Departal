# Catálogo 3D da Departal. Cada função monta um produto e devolve as opções de enquadramento.
# Uso: blender -b --factory-startup -P produtos.py -- --so nome1,nome2 --res 800 --amostras 56 --saida pasta
import colorsys
import json
import math
import os
import random
import re
import sys
import time
import traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import bpy
import numpy as np
from mathutils import Vector

import estudio as E
import pecas as P
from estudio import Cores as C

PRODUTOS = {}


def produto(fn):
    PRODUTOS[fn.__name__.replace("_", "-")] = fn
    return fn


def em(loc, fn, rot=(0, 0, 0), esc=1.0):
    """Roda `fn` e coloca tudo o que ela criou num grupo na posição dada."""
    antes = set(bpy.context.scene.objects)
    r = fn()
    novos = [o for o in bpy.context.scene.objects if o not in antes and o.parent is None]
    E.agrupar(novos, loc, rot, esc)
    return r


def chapa(pts, esp, mat, loc=(0, 0, 0), rot=(0, 0, 0), raio=0.0):
    """Peça plana recortada: lâminas, ferramentas, placas."""
    n = len(pts)
    v = [(x, y, 0) for x, y in pts] + [(x, y, esp) for x, y in pts]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    o = E.obj(E.malha("chapa", v, f, mat, suave=False), loc, rot)
    if raio:
        b = o.modifiers.new("b", "BEVEL")
        b.width = raio
        b.segments = 2
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(25)
        b.harden_normals = True
        o.data.shade_smooth()
    return o


def ouro():
    return E.pbr("ouro", C.ouro, 1.0, 0.2)


def fita_ouro():
    return E.pbr("fita-ouro", C.ouro_claro, 0.7, 0.34, Anisotropic=0.4, Sheen_Weight=0.5)


def fita_vermelha():
    return E.cetim("fita-vermelha", C.vermelho_vivo)


def papel(cor=None):
    return E.pbr("papel", cor or C.vermelho, 0.0, 0.3, 0.7)


def aco():
    return E.pbr("aco", C.prata, 1.0, 0.3, Anisotropic=0.5)


def caixa_presente(l, p, a, material, fita, loc=(0, 0, 0), giro=0.0, laco=1.0, cinta=0.16, tampa=True):
    itens = [E.bloco(l, p, a, material, (0, 0, a / 2), raio=0.008)]
    topo = a
    if tampa:
        h = max(a * 0.16, 0.08)
        itens.append(E.bloco(l * 1.03, p * 1.03, h, material, (0, 0, a - h / 2 + 0.02), raio=0.012))
        topo = a + 0.02
    lar = min(l, p) * cinta
    itens.append(E.bloco(l * 1.042, lar, topo + 0.012, fita, (0, 0, (topo + 0.012) / 2), raio=0.002, segs=1))
    itens.append(E.bloco(lar, p * 1.042, topo + 0.012, fita, (0, 0, (topo + 0.012) / 2), raio=0.002, segs=1))
    g = E.agrupar(itens, loc, (0, 0, giro))
    if laco:
        m = min(l, p)
        lc = E.laco(fita, m * 0.24 * laco, m * 0.42 * laco, m * 0.3 * laco, (0, 0, topo + m * 0.05), (math.radians(10), 0, 0))
        lc.parent = g
    return g


def tijolo(nx, ny, mat, loc=(0, 0, 0), giro=0.0, u=0.2, h=0.24):
    """Bloco de montar genérico, com pinos."""
    itens = [E.bloco(nx * u - 0.008, ny * u - 0.008, h, mat, (0, 0, h / 2), raio=0.008)]
    pino = E.torno([(0.0, h), (0.062, h), (0.062, h + 0.042), (0.054, h + 0.05), (0, h + 0.05)], mat, seg=20)
    me = pino.data
    bpy.data.objects.remove(pino)
    for i in range(nx):
        for j in range(ny):
            itens.append(E.obj(me, ((i - (nx - 1) / 2) * u, (j - (ny - 1) / 2) * u, 0)))
    return E.agrupar(itens, loc, (0, 0, giro))


def hsv(h, s=1.0, v=1.0):
    return colorsys.hsv_to_rgb(h % 1, s, v)


def ao_longo(caminho, espaco, suavizar=12):
    """Pontos igualmente espaçados num caminho."""
    c = E._catmull(caminho, suavizar)
    saida = [c[0]]
    resto = 0.0
    for a, b in zip(c, c[1:]):
        L = (b - a).length
        d = espaco - resto
        while d < L:
            saida.append(a + (b - a) * (d / L))
            d += espaco
        resto = (resto + L) % espaco if d - espaco < L else 0.0
    return saida


# ---------------------------------------------------------------- andar 1: decoração

def bolas_na_arvore(pontos, raio, mats, seed=2):
    rnd = random.Random(seed)
    tampa = E.pbr("tampa", C.ouro, 1.0, 0.26)
    for i, p in enumerate(pontos):
        r = raio * rnd.uniform(0.82, 1.14)
        E.bola(r, tuple(p - Vector((0, 0, r * 1.1))), mats[i % len(mats)], tampa, argola=False)


def paleta_bolas():
    return [ouro(), E.glitter("rubi", (0.72, 0.03, 0.05)), E.pbr("bola-v", C.vermelho_vivo, 0.0, 0.14, 1.0), E.pbr("prata", C.prata, 1.0, 0.16), E.listras("listra", C.ouro, (0.56, 0.34, 0.1), 16.0, onda=0.8)]


def caixa_enfeites(loc=(0, 0, 0), giro=0.0, esc=1.0):
    """Bandeja aberta com bolas em divisórias."""
    verm = papel()
    mats = paleta_bolas()
    itens = [E.bloco(1.5, 1.0, 0.14, verm, (0, 0, 0.07), raio=0.01)]
    for b in (-1, 1):
        itens.append(E.bloco(1.56, 0.04, 0.24, verm, (0, b * 0.52, 0.12), raio=0.008))
        itens.append(E.bloco(0.04, 1.08, 0.24, verm, (b * 0.76, 0, 0.12), raio=0.008))
    g = E.agrupar(itens)
    tampa = E.pbr("tampa", C.ouro, 1.0, 0.26)
    for i in range(3):
        for j in range(2):
            b = E.bola(0.21, (-0.5 + i * 0.5, -0.24 + j * 0.48, 0.3), mats[(i * 2 + j) % 5], tampa, argola=False, rot=(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), 0))
            b.parent = g
    g.location, g.rotation_euler, g.scale = loc, (0, 0, giro), (esc, esc, esc)
    return g


@produto
def arvore_180():
    alt, R = 3.3, 1.3
    P.pinheiro(alt, R, seed=1, base_z=0.14)
    pe = E.pbr("pe", (0.03, 0.03, 0.035), 0.8, 0.4)
    E.torno([(0.6, 0.0), (0.6, 0.03), (0.2, 0.08), (0.11, 0.2), (0.1, 0.34), (0.0, 0.34)], pe, seg=48)
    P.pontos_luz(P.pontos_copa(alt, R, 340, seed=4, base_z=0.14, recuo=0.93), 0.02, P.CALIDO, 12.0, "bola")
    return dict(azim=-10, elev=5, lente=120, margem=0.04)


@produto
def arvore_kit():
    alt, R = 2.5, 1.0
    P.pinheiro(alt, R, seed=3, neve=0.45, base_z=0.1)
    bolas_na_arvore(P.pontos_copa(alt, R, 22, seed=7, base_z=0.1, recuo=0.98), 0.1, paleta_bolas())
    E.torno([(0.52, 0.0), (0.5, 0.08), (0.12, 0.13), (0.0, 0.14)], E.pbr("saia", C.vermelho, 0, 0.5), seg=48)
    caixa_enfeites((1.02, -0.72, 0), 0.28, 0.72)
    caixa_presente(0.6, 0.6, 0.42, papel(C.verde), fita_ouro(), (-1.0, -0.62, 0), -0.3)
    return dict(azim=-8, elev=8, lente=110, margem=0.05)


@produto
def pinhas():
    rnd = random.Random(6)
    me = P.pinha_malha(P.mat_pinha())
    neve_m = E.madeira("escama-ouro", (0.86, 0.56, 0.2), (0.3, 0.14, 0.05), 2.2, 0.3, 0.0)
    neve_m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.9
    me2 = P.pinha_malha(neve_m)
    lugares = []
    for camada, n, z in ((0, 11, 0.32), (1, 7, 0.82), (2, 2, 1.26)):
        for i in range(n):
            a = i / n * math.tau + camada * 0.6
            r = (1.75 - camada * 0.72) * math.sqrt((i % 3 + 1) / 3.2)
            lugares.append((r * math.cos(a), r * math.sin(a), z))
    for i, (x, y, z) in enumerate(lugares):
        rot = (rnd.uniform(1.2, 1.9), 0, rnd.uniform(0, math.tau))
        P.pinha(me2 if i % 5 == 0 else me, (x, y, z), rnd.uniform(0.54, 0.66), rot)
    return dict(azim=-14, elev=20, margem=0.06)


def estrela_madeira():
    return E.pbr("estrela-o", C.ouro_claro, 1.0, 0.2, Emission_Color=(0.9, 0.56, 0.2, 1), Emission_Strength=0.5)


def floco(raio, mat, loc=(0, 0, 0), rot=(0, 0, 0)):
    itens = []
    for i in range(6):
        a = i * math.pi / 3
        d = Vector((math.cos(a), 0, math.sin(a)))
        itens.append(E.tubo([(0, 0, 0), tuple(d * raio)], raio * 0.05, mat, suavizar=1, lados=6))
        for t in (0.5, 0.78):
            c = d * (raio * t)
            for s in (-1, 1):
                v = Vector((math.cos(a + s * 1.0), 0, math.sin(a + s * 1.0)))
                itens.append(E.tubo([tuple(c), tuple(c + v * raio * 0.26 * (1.1 - t * 0.6))], raio * 0.04, mat, suavizar=1, lados=6))
    return E.agrupar(itens, loc, rot)


@produto
def enfeites():
    bar = E.pbr("barra", C.ouro, 1.0, 0.3)
    E.tubo([(-2.2, 0, 3.2), (2.2, 0, 3.2)], 0.022, bar, suavizar=1, lados=12)
    fio = E.pbr("linha", (0.8, 0.6, 0.3), 0.5, 0.5)
    itens = [(-1.7, 2.1), (-0.85, 1.75), (0, 2.2), (0.85, 1.7), (1.7, 2.05)]
    for x, z in itens:
        E.tubo([(x, 0, z + 0.34), (x, 0, 3.2)], 0.006, fio, suavizar=1, lados=6)
    E.bola(0.42, (-1.7, 0, 2.05), E.glitter("rubi", (0.72, 0.03, 0.05)))
    P.sino(0.86, loc=(-0.85, 0, 1.25))
    E.estrela(0.56, 0.2, (0, 0, 2.0), mat=estrela_madeira())
    floco(0.52, E.pbr("floco", (0.9, 0.92, 0.96), 1.0, 0.25), (0.85, 0, 1.52))
    bengala = E.listras("bengala", C.vermelho_vivo, C.branco, 22.0, metal=0.0, rugosidade_a=0.22, rugosidade_b=0.22, onda=1.2)
    E.tubo([(1.7, 0, 1.0), (1.7, 0, 2.0), (1.72, 0, 2.22), (1.9, 0, 2.34), (2.08, 0, 2.22), (2.08, 0, 2.08)], 0.085, bengala, lados=18)
    return dict(azim=-6, elev=3, sombra=False, margem=0.06)


@produto
def festao():
    r = np.random.default_rng(3)
    cam = []
    for i in range(320):
        t = i / 319
        a = t * math.tau * 3.1
        R = 1.5 - 0.5 * t + 0.1 * math.sin(a * 2)
        cam.append((R * math.cos(a), R * math.sin(a), 0.3 + t * 0.95 + 0.12 * math.sin(a * 1.7)))
    cam = np.array(cam, np.float32)
    n = 75000
    idx = r.integers(0, len(cam) - 1, n)
    k = r.random((n, 1)).astype(np.float32)
    p = cam[idx] * (1 - k) + cam[idx + 1] * k
    d = r.normal(size=(n, 3)).astype(np.float32)
    cor = np.where(r.random((n, 1)) < 0.74, np.array([[0.62, 0.012, 0.03]], np.float32), np.array([[0.9, 0.6, 0.22]], np.float32)).astype(np.float32)
    mat = P.pelo_mat("tinsel", 1.0, 0.24)
    P.fios_malha(p, d, 0.34, 0.0075, mat, seed=5, cor=cor)
    return dict(azim=-12, elev=30, margem=0.06)


@produto
def bolas_estrelas():
    for (x, y, r, gz) in ((-0.95, 0.15, 0.82, 0.5), (0.95, 0.15, 0.82, -0.4), (0.0, -0.55, 0.96, 0.1)):
        mat = E.imagem_mat("estrelas", "estrelas-bola.png", 0.2, 0.5 / r, 0.3, 1.0, deslocar=(0.5, 0.5, 0.5), projecao="SPHERE")
        E.bola(r, (x, y, r * 1.02), mat, rot=(0.08, -0.1, gz))
    return dict(azim=-4, elev=11)


@produto
def kit_decoracao():
    alt, R = 2.6, 1.05
    P.pinheiro(alt, R, seed=8, base_z=0.08)
    bolas_na_arvore(P.pontos_copa(alt, R, 18, seed=2, base_z=0.08, recuo=0.98), 0.1, paleta_bolas())
    P.pontos_luz(P.pontos_copa(alt, R, 150, seed=3, base_z=0.08, recuo=0.95), 0.016, P.CALIDO, 12.0, "bola")
    E.estrela(0.2, 0.07, (0, 0, alt + 0.2), mat=estrela_madeira())
    E.torno([(0.5, 0.0), (0.48, 0.06), (0.1, 0.1), (0, 0.1)], E.pbr("saia", C.vermelho, 0, 0.5), seg=48)
    rnd = em((1.42, -0.1, 0.62), lambda: P.guirlanda(0.46, 21, 320, 0.28, 0.32), rot=(0.06, 0, -0.16))
    caixa_enfeites((-1.2, -0.72, 0), -0.3, 0.72)
    return dict(azim=-6, elev=7, lente=110, margem=0.05)


@produto
def lacinhos():
    mat = fita_vermelha()
    rnd = random.Random(3)
    for j in range(3):
        for i in range(4):
            E.laco(mat, 0.26, 0.42, 0.36, ((i - 1.5) * 1.02 + rnd.uniform(-0.05, 0.05), (j - 1) * 0.94, 0.1), (math.pi / 2 - 0.1, 0, rnd.uniform(-0.3, 0.3)))
    return dict(azim=-4, elev=58, margem=0.05)


@produto
def mini_arvore():
    alt, R = 1.9, 0.72
    P.pinheiro(alt, R, seed=12, andares=13, base_z=0.5, ramo=0.5)
    me = P.pinha_malha(P.mat_pinha())
    for p in P.pontos_copa(alt, R, 14, seed=4, base_z=0.5, recuo=0.96):
        P.pinha(me, tuple(p - Vector((0, 0, 0.18))), 0.17, (math.pi, 0, 0))
    mad = E.madeira("vaso", (0.42, 0.24, 0.11), (0.14, 0.07, 0.03), 6, 0.6, 0.1)
    for i in range(14):
        a = i / 14 * math.tau
        E.bloco(0.18, 0.05, 0.6, mad, (0.42 * math.cos(a), 0.42 * math.sin(a), 0.3), (0, 0, a + math.pi / 2), raio=0.012)
    for z in (0.12, 0.48):
        E.torno([(0.47, z - 0.03), (0.47, z + 0.03)], E.pbr("aro", C.ouro, 1.0, 0.34), seg=48)
    P.pinha(me, (0.72, -0.34, 0.2), 0.27, (1.45, 0, 0.4))
    P.pinha(me, (-0.74, -0.2, 0.2), 0.27, (1.5, 0, 2.4))
    return dict(azim=-9, elev=7, lente=110, margem=0.05)


# ---------------------------------------------------------------- andar 2: presentes

@produto
def kit_construcao():
    verm = E.pbr("verm", C.vermelho_vivo, 0, 0.26, 0.6)
    verde = E.pbr("verde", (0.03, 0.24, 0.1), 0, 0.26, 0.6)
    amar = E.pbr("amar", (0.9, 0.56, 0.05), 0, 0.26, 0.6)
    bran = E.pbr("bran", (0.86, 0.86, 0.84), 0, 0.26, 0.6)
    azul = E.pbr("azul", (0.03, 0.14, 0.5), 0, 0.26, 0.6)
    h = 0.24
    z = 0.0
    tijolo(2, 2, verm, (0, 0, z))
    z += h
    for nivel, n in enumerate((8, 7, 6, 5, 4, 3, 2)):
        tijolo(n, n, verde, (0, 0, z), giro=0.0)
        z += h
    tijolo(1, 1, amar, (0, 0, z))
    tijolo(4, 2, azul, (-1.3, -0.5, 0), 0.35)
    tijolo(2, 2, amar, (1.25, -0.7, 0), -0.4)
    tijolo(3, 2, verm, (1.4, 0.3, 0), 0.5)
    tijolo(2, 2, bran, (-0.9, -1.1, 0), 0.2)
    tijolo(1, 2, verde, (0.2, -1.25, 0), 0.9)
    tijolo(2, 1, bran, (1.25, 0.25, 0.24), 1.1)
    return dict(azim=-20, elev=24, margem=0.06)


def faca(metal, cabo, c=2.0):
    p = [(-0.09, 0), (0.09, 0), (0.1, c * 0.6), (0.05, c * 0.9), (-0.02, c), (-0.09, c * 0.5)]
    a = chapa(p, 0.016, metal)
    b = E.bloco(0.15, 0.8, 0.075, cabo, (0, -0.4, 0.01), raio=0.03)
    r = [E.torno([(0.018, 0.05), (0.018, 0.058)], metal, seg=16, loc=(0, y, 0)) for y in (-0.2, -0.4, -0.6)]
    return [a, b, *r]


def garfo(metal, cabo, c=2.0):
    p = [(-0.05, 0), (0.05, 0), (0.07, c * 0.5), (0.1, c * 0.62), (0.1, c), (0.065, c * 0.68), (0.03, c * 0.6), (-0.03, c * 0.6), (-0.065, c * 0.68), (-0.1, c), (-0.1, c * 0.62), (-0.07, c * 0.5)]
    return [chapa(p, 0.016, metal), E.bloco(0.15, 0.8, 0.075, cabo, (0, -0.4, 0.01), raio=0.03)]


def espatula(metal, cabo, c=2.0):
    p = [(-0.04, 0), (0.04, 0), (0.05, c * 0.56), (0.26, c * 0.6), (0.26, c), (-0.26, c), (-0.26, c * 0.6), (-0.05, c * 0.56)]
    fenda = E.pbr("fenda", (0.01, 0.01, 0.01), 0, 0.8)
    f = [E.bloco(0.04, c * 0.28, 0.003, fenda, (x, c * 0.8, 0.018)) for x in (-0.14, 0, 0.14)]
    return [chapa(p, 0.016, metal), E.bloco(0.15, 0.8, 0.075, cabo, (0, -0.4, 0.01), raio=0.03), *f]


def pegador(metal, cabo, c=2.2):
    a = chapa([(-0.05, 0), (0.0, 0), (0.17, c), (0.08, c), (-0.05, c * 0.1)], 0.016, metal)
    b = chapa([(0.05, 0), (0.0, 0), (-0.17, c), (-0.08, c), (0.05, c * 0.1)], 0.016, metal)
    return [a, b, E.bloco(0.15, 0.7, 0.08, cabo, (0, -0.32, 0.01), raio=0.03)]


def espeto(metal, c=2.8):
    h = E.tubo([(0, -0.1, 0.02), (0, c, 0.02)], 0.02, metal, suavizar=1, lados=8, raios=lambda t: 0.02 * (1 - t ** 8 * 0.9))
    a = E.tubo([(0, -0.1, 0.02), (0.1, -0.22, 0.02), (0, -0.34, 0.02), (-0.1, -0.22, 0.02)], 0.014, metal, fechado=True, lados=8)
    return [h, a]


@produto
def kit_churrasco():
    mad = E.madeira("tabua", (0.44, 0.24, 0.1), (0.15, 0.07, 0.03), 2.4, 0.48, 0.2)
    cabo = E.madeira("cabo", (0.22, 0.09, 0.035), (0.06, 0.025, 0.012), 8, 0.36, 0.5)
    E.bloco(4.1, 3.5, 0.14, mad, (0, 0, 0.07), raio=0.05)
    m = aco()
    kits = [faca(m, cabo), garfo(m, cabo), espatula(m, cabo), pegador(m, cabo), espeto(m), espeto(m), faca(m, cabo, 1.6), garfo(m, cabo, 1.6)]
    xs = [-1.65, -1.2, -0.68, -0.05, 0.42, 0.74, 1.16, 1.62]
    for x, itens in zip(xs, kits):
        E.agrupar(itens, (x, -0.8, 0.18), (0, 0, 0.0))
    return dict(azim=-5, elev=62, lente=110, margem=0.05)


@produto
def kit_cosmeticos():
    veludo = E.tecido("veludo", C.vinho, 0.55, 0.2, 1.0)
    E.bloco(3.3, 2.2, 0.16, E.pbr("bandeja", C.ouro, 1.0, 0.34), (0, 0, 0.08), raio=0.05)
    E.bloco(3.1, 2.0, 0.04, veludo, (0, 0, 0.17), raio=0.012)
    tampa = E.pbr("tampa", C.ouro, 1.0, 0.2)
    liquido = E.pbr("perfume", (0.62, 0.03, 0.05), 0.0, 0.14, 1.0, Emission_Color=(0.8, 0.04, 0.06, 1), Emission_Strength=0.3)
    # perfume
    E.torno([(0, 0.2), (0.34, 0.2), (0.42, 0.26), (0.46, 0.5), (0.44, 0.92), (0.34, 1.16), (0.13, 1.28), (0.12, 1.36), (0, 1.36)], liquido, seg=64)
    E.torno([(0.13, 1.34), (0.15, 1.36), (0.17, 1.72), (0.13, 1.78), (0, 1.78)], tampa, seg=40)
    # frasco de essência
    rot = E.imagem_mat("rotulo", "rotulo-frasco.png", 0.5, (1, 1, 2.0), projecao="TUBE", deslocar=(0.5, 0.5, -1.16))
    corpo = E.pbr("frasco", C.marfim, 0.0, 0.2, 1.0)
    E.torno([(0, 0.2), (0.3, 0.2), (0.3, 0.6), (0.3, 0.84), (0.09, 1.0), (0.09, 1.08), (0, 1.08)], corpo, seg=56, loc=(-1.0, 0.3, 0))
    E.torno([(0.302, 0.42), (0.302, 0.8)], rot, seg=56, loc=(-1.0, 0.3, 0), rot=(0, 0, 0.5))
    E.torno([(0.09, 1.06), (0.11, 1.08), (0.11, 1.3), (0.09, 1.33), (0, 1.33)], tampa, seg=32, loc=(-1.0, 0.3, 0))
    # potes de creme
    rot2 = E.imagem_mat("rotulo2", "rotulo-creme.png", 0.5, (1, 1, 2.2), projecao="TUBE", deslocar=(0.5, 0.5, -0.5))
    for x, y, z in ((-0.62, -0.6, 1.0), (0.9, -0.5, 1.2)):
        pote = E.pbr("pote", C.vermelho_vivo, 0.0, 0.2, 1.0)
        E.torno([(0, 0.2), (0.42, 0.2), (0.44, 0.24), (0.44, 0.52), (0.4, 0.54), (0, 0.54)], pote, seg=64, loc=(x, y, 0))
        E.torno([(0.42, 0.54), (0.46, 0.55), (0.46, 0.74), (0.42, 0.77), (0, 0.77)], tampa, seg=64, loc=(x, y, 0))
    # tubo
    E.tubo([(1.05, 0.46, 0.2), (1.05, 0.46, 1.0)], 0.3, corpo, suavizar=1, lados=48, raios=lambda t: 0.26 + 0.05 * t)
    E.torno([(0.24, 0.17), (0.26, 0.2), (0.26, 0.42), (0, 0.42)], tampa, seg=40, loc=(1.05, 0.46, 0))
    rnd = random.Random(2)
    malhas = P.ramos_pinho(rnd)
    E.espalhar_ramos(rnd, malhas, 4, lambda i: (Vector((-1.2 + i * 0.1, -0.8, 0.28)), Vector((1, -0.1 + i * 0.2, 0.1)), 0.7))
    return dict(azim=-8, elev=20, margem=0.06)


def dado(l, loc, rot):
    bran = E.pbr("dado", (0.86, 0.84, 0.8), 0, 0.28, 0.6)
    pt = E.pbr("pip", (0.5, 0.02, 0.03), 0, 0.3)
    it = [E.bloco(l, l, l, bran, (0, 0, 0), raio=l * 0.13, segs=4)]
    r = l * 0.08
    for x, y in ((0, 0), (-l * 0.26, -l * 0.26), (l * 0.26, l * 0.26)):
        it.append(E.esfera(r, (x, y, l * 0.5), pt, seg=12, aneis=8, esc=(1, 1, 0.3)))
    for x, z in ((-l * 0.26, -l * 0.26), (l * 0.26, l * 0.26), (-l * 0.26, l * 0.26), (l * 0.26, -l * 0.26)):
        it.append(E.esfera(r, (x, -l * 0.5, z), pt, seg=12, aneis=8, esc=(1, 0.3, 1)))
    return E.agrupar(it, loc, rot)


@produto
def jogo_noite_feliz():
    azul = E.pbr("azul", (0.012, 0.03, 0.09), 0.0, 0.34, 0.5)
    L = 2.5
    capa = E.imagem_mat("capa", "capa-jogo.png", 0.3, 1 / L, verniz=0.8)
    tab = E.imagem_mat("tab", "tabuleiro.png", 0.3, 1 / 2.7, verniz=0.5)
    E.bloco(2.7, 2.7, 0.03, tab, (0.5, 0.25, 0.015), (0, 0, 0.3), raio=0.003)
    giro = -0.14
    E.agrupar([E.bloco(L, L, 0.34, azul, (0, 0, 0.17), raio=0.012), E.bloco(L - 0.03, L - 0.03, 0.002, capa, (0, 0, 0.342))], (-0.32, -0.25, 0.03), (0, 0, giro))
    cores = (C.vermelho_vivo, C.ouro, (0.03, 0.24, 0.1), (0.03, 0.14, 0.5))
    for i, c in enumerate(cores):
        m = E.pbr("peao", c, 0.3 if i == 1 else 0, 0.26, 0.8)
        x, y = 1.32 + 0.2 * (i % 2), -1.1 + i * 0.32
        E.torno([(0.12, 0), (0.12, 0.03), (0.06, 0.06), (0.05, 0.22), (0.075, 0.28), (0.09, 0.36), (0.06, 0.45), (0, 0.47)], m, seg=32, loc=(x, y, 0.03))
    dado(0.28, (1.05, -1.5, 0.14), (0, 0, 0.5))
    dado(0.28, (0.62, -1.7, 0.14), (0, 0, -0.3))
    return dict(azim=-6, elev=38, margem=0.05)


@produto
def urso_pelucia():
    cor = (0.46, 0.25, 0.1)
    corpo = []
    corpo.append(E.esfera(0.7, (0, 0, 0.74), esc=(1.0, 0.86, 1.1), seg=40, aneis=30))
    corpo.append(E.esfera(0.56, (0, -0.02, 1.76), esc=(1.1, 0.96, 0.95), seg=40, aneis=30))
    for s in (-1, 1):
        corpo.append(E.esfera(0.2, (s * 0.49, 0, 2.2), esc=(1, 0.5, 1), seg=24, aneis=18))
        corpo.append(E.tubo([(s * 0.56, -0.05, 1.26), (s * 0.8, -0.24, 1.0), (s * 0.86, -0.5, 0.76)], 0.2, None, lados=20, raios=lambda t: 0.2 + 0.05 * t))
        corpo.append(E.tubo([(s * 0.42, -0.2, 0.32), (s * 0.6, -0.6, 0.3), (s * 0.72, -1.02, 0.3)], 0.27, None, lados=20))
        corpo.append(E.esfera(0.32, (s * 0.74, -1.12, 0.34), esc=(0.95, 0.72, 1.1), seg=24, aneis=18))
    base = P.juntar_remalhar(corpo, 0.03, 10, E.pbr("couro", (cor[0] * 0.6, cor[1] * 0.6, cor[2] * 0.6), 0, 0.9))
    mat = P.pelo_mat("pelo")
    P.pelagem(base, 340000, 0.1, 0.0052, mat, cor, pente=(0, -0.2, -0.9), ruido=0.5)
    claro = (0.8, 0.6, 0.38)
    fuc = E.esfera(0.24, (0, -0.52, 1.64), E.pbr("f", claro, 0, 0.9), seg=28, aneis=20, esc=(1.14, 0.8, 0.82))
    P.pelagem(fuc, 40000, 0.05, 0.0036, mat, claro, pente=(0, -0.3, -0.4), seed=8)
    for s in (-1, 1):
        pad = E.esfera(0.19, (s * 0.74, -1.33, 0.34), E.pbr("p", claro, 0, 0.9), seg=24, aneis=16, esc=(1, 0.3, 1.12))
        P.pelagem(pad, 16000, 0.03, 0.003, mat, claro, pente=(0, 0, -0.2), seed=9)
        E.esfera(0.05, (s * 0.21, -0.56, 1.88), E.pbr("olho", (0.004, 0.004, 0.005), 0, 0.08, 1.0), seg=24, aneis=16)
    E.esfera(0.075, (0, -0.72, 1.7), E.pbr("nariz", (0.012, 0.008, 0.008), 0, 0.2, 1.0), seg=24, aneis=16, esc=(1.25, 0.72, 0.86))
    # cachecol
    xad = E.imagem_mat("cachecol", "xadrez-vermelho.png", 0.7, 3, plano="xz", brilho=0.6)
    pts = [(math.cos(a) * 0.5, math.sin(a) * 0.5 - 0.02, 1.28 + 0.02 * math.sin(a * 2)) for a in [i / 24 * math.tau for i in range(24)]]
    E.tubo(pts, 0.11, xad, suavizar=4, lados=16, fechado=True)
    E.fita([(0.18, -0.5, 1.26), (0.25, -0.66, 1.0), (0.28, -0.72, 0.72)], 0.3, xad, 0.04, eixo=(1, 0.2, 0.2))
    return dict(azim=-6, elev=7, lente=110, margem=0.05)


def chave_boca(esc, mat, loc, rot=(0, 0, 0)):
    p = [(-0.06, 0), (0.06, 0), (0.08, 0.8), (0.16, 0.9), (0.14, 1.06), (0.05, 1.0), (-0.05, 1.0), (-0.14, 1.06), (-0.16, 0.9), (-0.08, 0.8)]
    return chapa([(x * esc, y * esc) for x, y in p], 0.03, mat, loc, rot, 0.006)


def chave_fenda(c, cabo, mat, loc, rot=(0, 0, 0)):
    a = E.torno([(0.016, 0), (0.016, c), (0.03, c + 0.02)], mat, seg=10)
    b = E.torno([(0.03, c), (0.07, c + 0.04), (0.075, c + 0.5), (0.06, c + 0.6), (0, c + 0.61)], cabo, seg=20)
    return E.agrupar([a, b], loc, rot)


@produto
def kit_ferramentas():
    casco = E.pbr("casco", C.vermelho, 0.0, 0.32, 0.6)
    espuma = E.pbr("espuma", (0.02, 0.022, 0.026), 0, 0.85)
    m = E.pbr("cromo", C.prata, 1.0, 0.16)
    cabo = E.pbr("cabo", C.vermelho_vivo, 0, 0.3, 0.8)
    E.bloco(4.6, 3.3, 0.3, casco, (0, 0, 0.15), raio=0.05)
    E.bloco(4.34, 3.04, 0.03, espuma, (0, 0, 0.31), raio=0.01)
    E.agrupar([E.bloco(4.6, 0.26, 0.9, casco, (0, 0, 0.45), raio=0.05)], (0, 1.76, 0.16), (-0.06, 0, 0))
    z = 0.33
    mad = E.madeira("cabo-m", (0.46, 0.26, 0.11), (0.2, 0.1, 0.04), 8, 0.4, 0.3)
    E.bloco(0.16, 2.3, 0.11, mad, (-1.82, -0.2, z + 0.055), raio=0.04)
    E.bloco(0.86, 0.3, 0.24, m, (-1.82, 0.98, z + 0.12), raio=0.03)
    for i, x in enumerate((-1.36, -1.08, -0.8, -0.52)):
        c = 1.0 + i * 0.16
        chave_fenda(c, cabo, m, (x, c - 0.9, z + 0.08), (math.pi / 2, 0, 0))
    for i, x in enumerate((-0.16, 0.14, 0.46, 0.8)):
        chave_boca(1.3 + i * 0.28, m, (x, -1.28, z), (0, 0, 0))
    for j in range(2):
        for i in range(8):
            r = 0.07 + i * 0.008
            E.torno([(r, 0), (r, 0.2), (r * 0.7, 0.2), (r * 0.7, 0.03), (0, 0.03)], m, seg=18, loc=(1.16 + (i % 4) * 0.3, 0.22 + (i // 4) * 0.34 + j * 0.0 - 0.0 + j * 0.74, z))
    chapa([(-0.06, 0), (0.06, 0), (0.12, 0.6), (0.09, 0.94), (0, 1.0), (-0.03, 0.6)], 0.04, m, (1.5, -0.46, z), raio=0.008)
    for s in (-1, 1):
        E.tubo([(1.5 + s * 0.04, -0.44, z + 0.04), (1.5 + s * 0.16, -0.84, z + 0.04), (1.5 + s * 0.2, -1.3, z + 0.04)], 0.05, cabo, lados=10)
    return dict(azim=-5, elev=56, margem=0.05)


@produto
def caneca():
    h, r = 1.5, 0.8
    img = E.imagem_mat("caneca", "caneca.png", 0.2, (1, 1, 1 / h), verniz=1.0, projecao="TUBE", deslocar=(0.5, 0.5, 0))
    int_m = E.pbr("int", (0.82, 0.8, 0.76), 0, 0.2, 1.0)
    E.torno([(0, 0), (r * 0.9, 0), (r, 0.06), (r, h)], img, seg=128)
    E.torno([(r, h), (r - 0.02, h + 0.026), (r - 0.06, h + 0.02), (r - 0.07, h - 0.1), (0, h - 0.1)], int_m, seg=128)
    cal = E.pbr("cal", (0.1, 0.035, 0.014), 0, 0.22, 0.7)
    E.torno([(0, h - 0.16), (r - 0.062, h - 0.16)], cal, seg=128)
    E.tubo([(-r + 0.01, 0, 1.2), (-r - 0.34, 0, 1.2), (-r - 0.54, 0, 0.92), (-r - 0.42, 0, 0.5), (-r + 0.02, 0, 0.32)], 0.08, img, lados=20)
    mar = E.pbr("mar", (0.88, 0.85, 0.8), 0, 0.5)
    rnd = random.Random(5)
    for i in range(8):
        a, q = rnd.uniform(0, math.tau), rnd.uniform(0.1, 0.5)
        E.bloco(0.22, 0.22, 0.2, mar, (q * math.cos(a), q * math.sin(a), h - 0.1), (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 3)), raio=0.06, segs=4)
    P.canela((0.34, 0.2, h + 0.3), (0.5, 0.4, 0.3), 1.2, 0.06)
    return dict(azim=24, elev=16)


@produto
def chocolate():
    cho = E.pbr("cho", (0.075, 0.03, 0.014), 0, 0.26, 0.5)
    nx, ny = 4, 6
    u = 0.42
    E.bloco(nx * u, ny * u, 0.05, cho, (0, 0, 0.025), raio=0.01)
    for i in range(nx):
        for j in range(ny):
            if j < 4 or True:
                E.bloco(u - 0.03, u - 0.03, 0.08, cho, ((i - (nx - 1) / 2) * u, (j - (ny - 1) / 2) * u, 0.09), raio=0.03, segs=3)
    # papel-alumínio dourado e cinta
    laminado = E.pbr("lam", C.ouro, 1.0, 0.28)
    n = laminado.node_tree
    tc = n.nodes.new("ShaderNodeTexCoord")
    rd = n.nodes.new("ShaderNodeTexVoronoi")
    rd.inputs["Scale"].default_value = 9
    rl = n.nodes.new("ShaderNodeBump")
    rl.inputs["Strength"].default_value = 0.55
    n.links.new(tc.outputs["Object"], rd.inputs["Vector"])
    n.links.new(rd.outputs["Distance"], rl.inputs["Height"])
    n.links.new(rl.outputs[0], n.nodes["Principled BSDF"].inputs["Normal"])
    E.bloco(nx * u + 0.08, ny * u * 0.6, 0.2, laminado, (0, -ny * u * 0.2, 0.08), raio=0.03)
    cinta = E.pbr("cinta", C.vermelho, 0, 0.42)
    E.bloco(nx * u + 0.12, ny * u * 0.42, 0.24, cinta, (0, -ny * u * 0.22, 0.1), raio=0.012)
    rot = E.imagem_mat("rot", "rotulo-chocolate.png", 0.42, (1 / (nx * u + 0.1), 1 / (ny * u * 0.4), 1))
    E.bloco(nx * u + 0.1, ny * u * 0.4, 0.002, rot, (0, -ny * u * 0.22, 0.222))
    for x, y, g in ((1.42, -0.44, 0.5), (1.22, 0.42, -0.2)):
        E.agrupar([E.bloco(u - 0.03, u - 0.03, 0.09, cho, (0, 0, 0.05), raio=0.03, segs=3), E.bloco(u, u, 0.04, cho, (0, 0, 0.02), raio=0.01)], (x, y, 0), (0, 0, g))
    return dict(azim=-12, elev=42, margem=0.07)


@produto
def par_meias():
    tric = E.imagem_mat("tric", "trico-vermelho.png", 0.75, 1.0, plano="xz", relevo=0.4, brilho=0.8)
    pun = E.tecido("pun", C.branco, 0.8)
    P.meia(tric, pun, 1.0, (-0.56, 0, 0), (0, 0.06, 0), seed=7)
    P.meia(tric, pun, 1.0, (0.1, -0.2, 0.0), (0, -0.05, 0), seed=9)
    return dict(azim=-3, elev=2, sombra=False, margem=0.06)


def cesto(R=1.1, a=0.9, mat=None):
    v = mat or E.pbr("vime", (0.4, 0.24, 0.1), 0, 0.55)
    it = []
    for k in range(13):
        z = 0.05 + k * a / 12
        fase = k % 2 * math.pi
        rr = R * (0.82 + 0.18 * (k / 12) ** 0.6)
        it.append(E.tubo([(rr * (1 + 0.016 * math.sin(i / 72 * 18 * math.tau + fase)) * math.cos(i / 72 * math.tau), rr * (1 + 0.016 * math.sin(i / 72 * 18 * math.tau + fase)) * math.sin(i / 72 * math.tau), z) for i in range(72)], 0.036, v, suavizar=2, lados=8, fechado=True))
    it.append(E.tubo([(R * 1.01 * math.cos(i / 48 * math.tau), R * 1.01 * math.sin(i / 48 * math.tau), a + 0.06) for i in range(48)], 0.062, v, suavizar=2, lados=10, fechado=True))
    it.append(E.torno([(0, 0.04), (R * 0.84, 0.04), (R * 0.84, 0.0), (0, 0.0)], v, seg=48))
    return it


@produto
def cestinha():
    cesto(1.15, 0.86)
    v = E.pbr("vime2", (0.36, 0.2, 0.08), 0, 0.5)
    E.tubo([(-1.13, 0, 0.9), (-1.0, 0, 1.7), (-0.5, 0, 2.2), (0, 0, 2.34), (0.5, 0, 2.2), (1.0, 0, 1.7), (1.13, 0, 0.9)], 0.05, v, lados=10)
    E.laco(fita_vermelha(), 0.3, 0.5, 0.5, (-0.72, -0.05, 1.96), (0, 0.5, 0))
    xad = E.imagem_mat("forro", "xadrez-vermelho.png", 0.7, 2.0, brilho=0.6)
    E.torno([(0, 0.56), (0.9, 0.6), (1.1, 0.82), (1.17, 0.9), (1.22, 0.8), (1.2, 0.74)], xad, seg=96)
    caixa_presente(0.74, 0.74, 0.7, papel(C.verde), fita_ouro(), (-0.4, 0.2, 0.62), 0.3, 0.8)
    E.torno([(0, 0.6), (0.2, 0.6), (0.24, 0.66), (0.24, 1.2), (0.09, 1.42), (0.09, 1.5), (0, 1.5)], E.pbr("garrafa", (0.03, 0.09, 0.05), 0, 0.12, 1.0), seg=48, loc=(0.42, 0.26, 0.05))
    E.torno([(0.1, 1.52), (0.1, 1.62), (0, 1.62)], ouro(), seg=24, loc=(0.42, 0.26, 0.05))
    E.bola(0.2, (0.3, -0.58, 0.92), ouro(), argola=False)
    E.bola(0.17, (-0.12, -0.72, 0.9), E.glitter("rubi", (0.72, 0.03, 0.05)), argola=False)
    me = P.pinha_malha(P.mat_pinha())
    P.pinha(me, (0.72, -0.34, 0.86), 0.34, (1.3, 0, 0.8))
    rnd = random.Random(2)
    malhas = P.ramos_pinho(rnd)
    E.espalhar_ramos(rnd, malhas, 14, lambda i: (Vector((math.cos(i * 0.9) * 0.9, math.sin(i * 0.9) * 0.9, 0.86)), Vector((math.cos(i * 0.9), math.sin(i * 0.9), 0.3)), 0.55))
    return dict(azim=-8, elev=15, lente=110, margem=0.05)


@produto
def floratta_gold():
    vid = E.vidro("frasco-vid", (0.99, 0.94, 0.82), 0.01, 1.48)
    liq = E.pbr("liq", (0.92, 0.56, 0.14), 0.0, 0.16, 0.8, Emission_Color=(1.0, 0.56, 0.14, 1), Emission_Strength=0.42)
    tamp = E.pbr("tampa-f", C.ouro_claro, 1.0, 0.3)
    E.torno([(0, 0), (0.62, 0), (0.74, 0.05), (0.8, 0.26), (0.8, 1.2), (0.7, 1.5), (0.42, 1.64), (0.18, 1.7), (0, 1.7)], vid, seg=96, esc=(1, 0.52, 1))
    E.torno([(0, 0.1), (0.6, 0.1), (0.7, 0.16), (0.74, 0.3), (0.74, 1.12), (0.64, 1.38), (0.38, 1.52), (0, 1.56)], liq, seg=96, esc=(1, 0.46, 1))
    E.torno([(0.14, 1.68), (0.17, 1.7), (0.17, 1.86), (0.14, 1.88), (0, 1.88)], tamp, seg=48)
    E.torno([(0.28, 1.86), (0.3, 1.88), (0.3, 2.6), (0.26, 2.66), (0, 2.68)], tamp, seg=64)
    E.tubo([(0.2 * math.cos(i / 24 * math.tau), 0.2 * math.sin(i / 24 * math.tau), 1.8) for i in range(24)], 0.025, fita_vermelha(), suavizar=3, lados=10, fechado=True)
    E.laco(fita_vermelha(), 0.16, 0.34, 0.5, (0, -0.2, 1.8), (0.1, 0, 0))
    return dict(azim=-20, elev=8, lente=110, margem=0.08)


@produto
def sonhos_natal():
    pap = E.imagem_mat("pap-ouro", "papel-ouro.png", 0.3, 0.8, metal=0.7, verniz=0.6)
    caixa_presente(2.2, 2.2, 1.5, pap, fita_vermelha(), (0, 0, 0), 0.0, 1.05)
    mats = paleta_bolas()
    tampa = E.pbr("tampa", C.ouro, 1.0, 0.26)
    E.bola(0.34, (-1.4, -0.92, 0.35), mats[0], tampa)
    E.bola(0.26, (1.45, -0.92, 0.27), mats[1], tampa)
    E.bola(0.2, (-0.8, -1.42, 0.2), mats[3], tampa)
    E.estrela(0.3, 0.1, (1.05, -1.42, 0.31), (0, 0, 0.3), estrela_madeira())
    return dict(azim=-14, elev=12, margem=0.06)


@produto
def caixa_presentes():
    pap = papel()
    fo = fita_ouro()
    caixa_presente(2.1, 2.1, 1.1, pap, fo, (0, 0.1, 0), 0.1, 0)
    caixa_presente(1.5, 1.5, 0.9, pap, fo, (-0.1, 0.1, 1.13), -0.25, 0)
    caixa_presente(1.0, 1.0, 0.66, pap, fo, (0.05, 0.1, 2.05), 0.3, 1.1)
    return dict(azim=-12, elev=10, lente=110, margem=0.05)


# ---------------------------------------------------------------- andar 3: roupas

def tecido_img(nome, arquivo, escala=1.2, deslocar=(0.5, 0.5, 0)):
    return E.imagem_mat(nome, arquivo, 0.72, escala, plano="xz", relevo=0.25, brilho=0.7, deslocar=deslocar)


def gola_branca():
    return E.tecido("gola", C.branco, 0.7)


FRENTE = dict(azim=-3, elev=2, sombra=False, margem=0.05)


@produto
def pijama():
    """O pijama da sua foto: blusa vinho com corações e calça xadrez."""
    cor = tecido_img("cor", "coracoes.png", 1.3)
    xad = tecido_img("xad", "xadrez-vermelho.png", 0.9)
    P.calca(xad, 0.8, (0, 0.04, -0.66), cos=E.tecido("cos", C.vinho, 0.7))
    P.camisa(cor, loc=(0, -0.04, 0.2), gola=gola_branca(), seed=3)
    return FRENTE


@produto
def pijama_premium():
    xad = tecido_img("xadv", "xadrez-verde.png", 0.9)
    lapela = E.tecido("lap", C.vinho, 0.6)
    P.calca(xad, 0.8, (0, 0.04, -0.66), cos=E.tecido("cos", (0.008, 0.06, 0.03), 0.7), seed=11)
    P.camisa(xad, loc=(0, -0.04, 0.2), gola=lapela, seed=8)
    P.botoes(5, 0, 0.98, 0.1, y=-0.17)
    return FRENTE


@produto
def vestido_infantil():
    vel = E.tecido("vel", C.vermelho, 0.5, 0.2, 1.0)
    bra = E.pbr("renda", (0.86, 0.84, 0.8), 0, 0.6)
    fo = fita_ouro()
    P.cabide(0.9, (0, 0.08, 0.02))
    E.peca_2d(P.VESTIDO, vel, 0.05, 0.011, 0.016, seed=6)
    E.tubo([(-0.26, -0.11, 0.3), (0, -0.14, 0.27), (0.26, -0.11, 0.3)], 0.032, fo, lados=10)
    E.laco(fo, 0.14, 0.24, 0.26, (0, -0.15, 0.28))
    E.tubo([(-0.17, -0.02, 1.03), (-0.09, -0.06, 0.95), (0, -0.07, 0.92), (0.09, -0.06, 0.95), (0.17, -0.02, 1.03)], 0.028, bra, lados=12)
    pts = [(x, -0.03 - 0.04 * math.cos(x * 2), -1.0 - 0.07 * (1 - (x / 0.72) ** 2)) for x in [i / 16 * 1.42 - 0.71 for i in range(17)]]
    E.tubo(pts, 0.03, bra, lados=12)
    return FRENTE


@produto
def conjunto_familiar():
    xad = tecido_img("xad", "trico-vermelho.png", 1.0)
    gol = gola_branca()
    P.camisa(xad, 1.0, (-0.82, 0.1, 0.1), seed=3, gola=gol)
    P.camisa(xad, 0.92, (0.78, 0.06, 0.04), seed=4, gola=gol)
    P.camisa(xad, 0.66, (-0.34, -0.1, -0.5), seed=5, gola=gol)
    P.camisa(xad, 0.5, (0.42, -0.14, -0.62), seed=6, gola=gol)
    return FRENTE


@produto
def camiseta():
    img = E.imagem_mat("cam", "camiseta.png", 0.74, 0.5, plano="xz", relevo=0.2, brilho=0.6, deslocar=(0.5, 0.36, 0))
    P.cabide(1.0, (0, 0.08, 0.0))
    P.camisa(img, manga=False, gola=E.tecido("rib", C.vermelho, 0.7), seed=9)
    return FRENTE


@produto
def kit_meias():
    a = E.imagem_mat("m1", "trico-verde.png", 0.75, 1.0, plano="xz", relevo=0.4, brilho=0.8)
    b = E.imagem_mat("m2", "listras-meia.png", 0.75, 0.8, plano="xz", relevo=0.4, brilho=0.8)
    c = E.imagem_mat("m3", "xadrez-vermelho.png", 0.75, 0.7, plano="xz", relevo=0.4, brilho=0.8)
    P.meia(a, E.tecido("pu1", C.vermelho, 0.7), 0.92, (-0.82, 0, 0.02), (0, 0.1, 0), seed=7)
    P.meia(b, E.tecido("pu2", C.verde, 0.7), 1.0, (0, -0.06, 0.06), (0, 0, 0), seed=8)
    P.meia(c, E.tecido("pu3", C.branco, 0.7), 0.92, (0.82, 0.02, 0.0), (0, -0.1, 0), seed=9)
    return FRENTE


def gorro(esc=1.0, loc=(0, 0, 0), rot=(0, 0, 0)):
    verm = E.tecido("gorro", C.vermelho_vivo, 0.6)
    plu = E.pbr("plush", (0.88, 0.86, 0.82), 0, 0.9)
    pelo = P.pelo_mat("plush-fios")
    c = E.tubo([(0, 0, 0), (0, 0, 0.42), (0.08, 0, 0.78), (0.34, 0, 1.0), (0.6, 0, 0.94), (0.72, 0, 0.72)], 0.4, verm, lados=32, raios=lambda t: 0.46 * (1 - t) ** 0.9 + 0.014)
    aba = E.torno([(0.5 + 0.11 * math.cos(i / 16 * math.tau), 0.11 * math.sin(i / 16 * math.tau)) for i in range(17)], plu, seg=48)
    pom = E.esfera(0.14, (0.72, 0, 0.64), plu, seg=28, aneis=18)
    f1 = P.pelagem(aba, 36000, 0.05, 0.0034, pelo, (0.9, 0.88, 0.84), pente=(0, 0, -0.2), seed=11)
    f2 = P.pelagem(pom, 12000, 0.06, 0.0034, pelo, (0.9, 0.88, 0.84), pente=(0, 0, -0.1), seed=12)
    return E.agrupar([c, aba, pom, f1, f2], loc, rot, esc)


@produto
def conjunto_noel():
    verm = E.tecido("noel", C.vermelho_vivo, 0.55, 0.2, 1.0)
    bra = E.pbr("branco", (0.88, 0.86, 0.82), 0, 0.9)
    pelo = P.pelo_mat("fios")
    P.calca(verm, 0.76, (0, 0.04, -0.72), seed=14)
    P.camisa(verm, 0.96, (0, -0.02, 0.26), seed=13)
    f = []
    faixa = E.tubo([(-0.42, -0.1, 0.0), (0, -0.14, -0.03), (0.42, -0.1, 0.0)], 0.07, bra, lados=12, suavizar=5)
    f.append(P.pelagem(faixa, 20000, 0.04, 0.0034, pelo, (0.9, 0.88, 0.84), pente=(0, 0, -0.1), seed=2))
    col = E.tubo([(0.02, -0.14, 1.12), (0.0, -0.15, 0.6), (0.0, -0.14, 0.0)], 0.06, bra, lados=12, suavizar=5)
    f.append(P.pelagem(col, 16000, 0.04, 0.0034, pelo, (0.9, 0.88, 0.84), pente=(0, 0, -0.1), seed=3))
    cinto = E.pbr("cinto", (0.01, 0.01, 0.012), 0, 0.3, 0.6)
    E.tubo([(-0.44, -0.12, 0.42), (0, -0.16, 0.4), (0.44, -0.12, 0.42)], 0.05, cinto, lados=12, suavizar=5)
    fiv = ouro()
    E.bloco(0.2, 0.03, 0.18, fiv, (0, -0.2, 0.4), raio=0.01)
    E.bloco(0.12, 0.05, 0.1, cinto, (0, -0.2, 0.4))
    gorro(0.62, (0.72, -0.12, 1.1), (0.1, 0.2, 0))
    return dict(azim=-3, elev=2, sombra=False, margem=0.05)


@produto
def look_feminino():
    vel = E.pbr("cetim-v", C.vermelho_vivo, 0.0, 0.38, Anisotropic=0.5, Sheen_Weight=0.8)
    fo = fita_ouro()
    au = ouro()
    P.cabide(0.9, (-0.2, 0.08, 0.02))
    E.peca_2d(P.VESTIDO, vel, 0.05, 0.011, 0.024, loc=(-0.2, 0, 0), seed=12)
    E.tubo([(-0.46, -0.11, 0.3), (-0.2, -0.14, 0.27), (0.06, -0.11, 0.3)], 0.024, au, lados=10)
    # bolsa-carteira e colar
    E.bloco(0.62, 0.14, 0.38, au, (0.82, -0.05, -0.7), raio=0.05, segs=4)
    E.bloco(0.62, 0.15, 0.17, E.pbr("fecho", C.ouro_claro, 1.0, 0.1), (0.82, -0.05, -0.62), raio=0.04, segs=4)
    E.tubo([(0.56, -0.05, -0.54), (0.5, -0.04, -0.1), (0.82, -0.03, 0.22), (1.14, -0.04, -0.1), (1.08, -0.05, -0.54)], 0.006, au, lados=6)
    ang = [i / 28 * math.pi + math.pi for i in range(29)]
    E.tubo([(-0.2 + 0.2 * math.cos(a), -0.1, 0.96 + 0.3 * math.sin(a)) for a in ang], 0.009, au, lados=6, suavizar=2)
    E.esfera(0.05, (-0.2, -0.13, 0.64), au, seg=20, aneis=14)
    return FRENTE


@produto
def look_familiar():
    cor = tecido_img("cor", "coracoes.png", 1.3)
    xad = tecido_img("xad", "xadrez-vermelho.png", 0.9)
    gol = gola_branca()
    for x, z, e, y in ((-1.34, 0.1, 0.72, 0.12), (1.34, 0.06, 0.68, 0.12), (-0.44, -0.3, 0.5, -0.02), (0.44, -0.4, 0.42, -0.04)):
        P.calca(xad, e * 0.86, (x, y + 0.03, z - 1.18 * e), seed=int(x * 7 + 21))
        P.camisa(cor, e, (x, y, z), seed=int(x * 3 + 13), gola=gol)
    return FRENTE


# ---------------------------------------------------------------- andar 4: luzes

@produto
def fita_led():
    pcb = E.pbr("pcb", (0.86, 0.86, 0.84), 0, 0.3, 0.5)
    giros = []
    for i in range(240):
        t = i / 239
        a = t * math.tau * 7
        r = 0.66 + 0.5 * t
        giros.append((r * math.cos(a), r * math.sin(a), 0.2))
    fim = giros[-1]
    a0 = 7 * math.tau
    rabo = [(fim[0], fim[1], 0.2), (fim[0] + 0.12, fim[1] - 0.5, 0.17), (fim[0] - 0.4, fim[1] - 1.4, 0.04), (fim[0] - 1.2, fim[1] - 1.5, 0.018), (fim[0] - 2.0, fim[1] - 0.9, 0.018), (fim[0] - 2.5, fim[1] - 0.1, 0.018)]
    E.fita(giros, 0.34, pcb, 0.014, suavizar=2, eixo=(0, 0, 1), secoes=2, bojo=0.0)
    E.fita(rabo, 0.34, pcb, 0.014, eixo=(0, 0, 1), secoes=2, bojo=0.0)
    pl = E.pbr("carretel", (0.02, 0.02, 0.022), 0, 0.3, 0.5)
    E.torno([(0.0, 0.0), (1.36, 0.0), (1.36, 0.04), (0.5, 0.04), (0.5, 0.34), (0.0, 0.34)], pl, seg=96)
    E.torno([(0.5, 0.34), (0.55, 0.42), (0.34, 0.42), (0.34, 0.2), (0, 0.2)], pl, seg=64)
    P.pontos_luz(ao_longo(rabo, 0.075), 0.05, [hsv(i / 24) for i in range(24)], 7.0, "bola")
    ctrl = E.pbr("ctrl", (0.86, 0.86, 0.84), 0, 0.26, 0.8)
    E.bloco(0.6, 1.1, 0.07, ctrl, (1.72, -1.08, 0.035), (0, 0, -0.3), raio=0.03, segs=4)
    cor_bot = [hsv(i / 12, 0.9) for i in range(12)]
    grupo = []
    for j in range(4):
        for i in range(3):
            m = E.pbr("b", cor_bot[(i + j * 3) % 12], 0, 0.3)
            grupo.append(E.esfera(0.05, (-0.13 + i * 0.13, -0.3 + j * 0.2, 0.07), m, seg=12, aneis=8, esc=(1, 1, 0.3)))
    E.agrupar(grupo, (1.72, -1.08, 0.0), (0, 0, -0.3))
    return dict(azim=-8, elev=38, margem=0.06, luz=0.5)


def rena_caminhos():
    corpo = [(-1.0, 1.66), (-0.4, 1.72), (0.35, 1.72), (0.55, 1.95), (0.75, 2.35), (0.9, 2.62), (1.1, 2.7), (1.45, 2.52), (1.5, 2.42), (1.35, 2.36), (1.05, 2.36), (0.94, 2.2), (0.88, 1.9), (0.82, 1.55), (0.64, 1.3), (0.6, 0.8), (0.62, 0.0), (0.46, 0.0), (0.44, 0.8), (0.38, 1.22), (0.0, 1.2), (-0.45, 1.25), (-0.55, 0.85), (-0.72, 0.45), (-0.62, 0.0), (-0.78, 0.0), (-0.92, 0.45), (-0.9, 0.85), (-1.02, 1.2), (-1.06, 1.45), (-1.0, 1.66)]
    cam = []
    for y0 in (-0.2, 0.2):
        c = []
        for x, z in corpo:
            k = 1.0 if x < 0.45 or z < 1.8 else max(0.22, 1 - (x - 0.45) * 0.95)
            c.append((x, y0 * k, z))
        cam.append(c)
    for x in (-0.72, -0.2, 0.3):
        a = [i / 14 * math.tau for i in range(15)]
        cam.append([(x, 0.22 * math.cos(t), 1.46 + 0.25 * math.sin(t)) for t in a])
    for s in (-1, 1):
        for base in ([(0.95, 2.72), (0.86, 3.1), (0.62, 3.4), (0.35, 3.55)], [(0.87, 3.05), (1.08, 3.25), (1.12, 3.45)], [(0.7, 3.32), (0.82, 3.55), (0.8, 3.72)], [(0.48, 3.48), (0.46, 3.72)]):
            cam.append([(x, s * (0.07 + (z - 2.7) * 0.2), z) for x, z in base])
        cam.append([(0.88, s * 0.07, 2.64), (0.72, s * 0.22, 2.82), (0.64, s * 0.26, 2.68), (0.84, s * 0.1, 2.58)])
    return cam


def rena(espaco=0.058, raio=0.02, cores=None):
    fio = E.pbr("arame", (0.86, 0.72, 0.5), 1.0, 0.36)
    pts = []
    for c in rena_caminhos():
        E.tubo(c, 0.0085, fio, suavizar=8, lados=6)
        pts += ao_longo(c, espaco, 8)
    P.pontos_luz(pts, raio, cores or P.CALIDO, 13.0, "bola")


@produto
def rena_led():
    rena()
    return dict(azim=14, elev=6, lente=110, margem=0.05, luz=0.35)


@produto
def pisca_pisca():
    rnd = random.Random(8)
    cam = []
    n = 110
    for i in range(n):
        t = i / (n - 1)
        a = t * math.tau * 5.4
        r = 1.5 + 0.3 * math.sin(a * 2.3) - 0.45 * math.sin(t * math.pi)
        cam.append((r * math.cos(a), r * math.sin(a), 0.16 + 0.32 * abs(math.sin(a * 0.9 + t * 3))))
    verde = E.pbr("fio-verde", (0.01, 0.07, 0.03), 0, 0.42)
    E.tubo(cam, 0.02, verde, suavizar=4, lados=8)
    fim = cam[-1]
    ponta = [fim, (fim[0] + 0.5, fim[1] - 0.7, 0.05), (fim[0] + 1.0, fim[1] - 1.3, 0.03)]
    E.tubo(ponta, 0.02, verde, lados=8)
    tom = E.pbr("plug", (0.02, 0.02, 0.022), 0, 0.3)
    E.bloco(0.2, 0.28, 0.13, tom, ponta[-1], (0, 0, -0.6), raio=0.03)
    pts = ao_longo(cam, 0.34, 4)
    P.pontos_luz(pts, 0.078, P.COLORIDO + [(1, 0.06, 0.5)], 7.0, "gota")
    return dict(azim=-10, elev=34, margem=0.05, luz=0.5)


@produto
def cortina_led():
    rnd = random.Random(3)
    fio = E.pbr("fio-b", (0.86, 0.84, 0.8), 0, 0.5)
    E.tubo([(-3, 0, 2.0), (3, 0, 2.0)], 0.018, fio, suavizar=1, lados=8)
    pts = []
    n = 24
    for i in range(n):
        x = -2.9 + i * 5.8 / (n - 1)
        h = 3.3 + 0.6 * math.sin(i * 1.6) + rnd.uniform(-0.3, 0.3)
        y = rnd.uniform(-0.1, 0.1)
        E.tubo([(x, 0, 2.0), (x, y, 2.0 - h)], 0.005, fio, suavizar=1, lados=5)
        for k in range(int(h / 0.26)):
            pts.append(Vector((x + rnd.uniform(-0.02, 0.02), y * (k * 0.26 / h), 2.0 - 0.2 - k * 0.26)))
    P.pontos_luz(pts, 0.042, P.CALIDO, 13.0, "bola")
    return dict(azim=-5, elev=2, sombra=False, margem=0.05, luz=0.5)


@produto
def boneco_neve_led():
    bra = E.lampada_mat("neve-luz", (0.82, 0.88, 1.0), 0.72)
    b = bra.node_tree.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.46
    E.esfera(0.74, (0, 0, 0.72), bra)
    E.esfera(0.54, (0, 0, 1.78), bra)
    E.esfera(0.38, (0, 0, 2.52), bra)
    pre = E.pbr("preto", (0.01, 0.01, 0.012), 0, 0.42)
    E.torno([(0, 2.8), (0.5, 2.8), (0.5, 2.84), (0.3, 2.86), (0.28, 3.36), (0.3, 3.4), (0, 3.4)], pre, seg=64)
    E.torno([(0.285, 2.92), (0.29, 3.04)], fita_vermelha(), seg=64)
    E.tubo([(0, -0.38, 2.5), (0, -0.74, 2.46)], 0.05, E.pbr("cenoura", (0.8, 0.22, 0.03), 0, 0.4), suavizar=1, lados=16, raios=lambda t: 0.055 * (1 - t))
    for x in (-0.13, 0.13):
        E.esfera(0.04, (x, -0.34, 2.62), pre, seg=16, aneis=12)
    for z in (0.5, 1.0):
        E.esfera(0.06, (0, -0.74 if z == 0.5 else -0.68, z), pre, seg=16, aneis=12)
    for z in (1.6, 1.84, 2.08):
        E.esfera(0.05, (0, -0.52, z - 0.1), pre, seg=16, aneis=12)
    xad = E.imagem_mat("cachecol", "xadrez-vermelho.png", 0.7, 3, plano="xz", brilho=0.6)
    E.tubo([(0.4 * math.cos(i / 24 * math.tau), 0.4 * math.sin(i / 24 * math.tau) - 0.02, 2.22) for i in range(24)], 0.1, xad, suavizar=4, lados=14, fechado=True)
    E.fita([(0.2, -0.4, 2.2), (0.26, -0.55, 1.9), (0.3, -0.54, 1.58)], 0.26, xad, 0.04, eixo=(1, 0.1, 0.2))
    gal = E.pbr("galho", (0.08, 0.045, 0.02), 0, 0.7)
    for s in (-1, 1):
        E.tubo([(s * 0.5, 0, 1.9), (s * 0.94, -0.04, 2.14), (s * 1.3, 0, 2.42)], 0.024, gal, lados=8)
        E.tubo([(s * 1.0, -0.02, 2.2), (s * 1.08, 0, 2.48)], 0.016, gal, lados=6)
    return dict(azim=-8, elev=6, lente=110, margem=0.05, luz=0.42)


@produto
def leds_arvore():
    alt, R = 3.2, 1.3
    P.pinheiro(alt, R, seed=5, base_z=0.12, ramo=0.46)
    P.pontos_luz(P.pontos_copa(alt, R, 500, seed=6, base_z=0.12, recuo=0.97), 0.02, P.CALIDO, 13.0, "bola")
    return dict(azim=-7, elev=5, lente=120, margem=0.05, luz=0.28)


@produto
def kit_externa():
    fio = E.pbr("fio-b", (0.86, 0.84, 0.8), 0, 0.5)
    pts = []
    rnd = random.Random(3)
    E.tubo([(-3.0, 1.6, 3.5), (3.0, 1.6, 3.5)], 0.016, fio, suavizar=1, lados=8)
    for i in range(32):
        x = -2.9 + i * 5.8 / 31
        h = 2.0 + 0.5 * math.sin(i * 1.3)
        for k in range(int(h / 0.24)):
            pts.append(Vector((x, 1.6, 3.4 - k * 0.24)))
    P.pontos_luz(pts, 0.04, [(1.0, 0.82, 0.56)], 11.0, "bola")
    em((-1.3, 0, 0), lambda: rena(0.07, 0.024), rot=(0, 0, -0.5), esc=0.84)
    em((1.5, -0.2, 0), lambda: rena(0.07, 0.024), rot=(0, 0, 3.6), esc=0.84)
    ctrl = E.pbr("ctrl", (0.02, 0.02, 0.022), 0, 0.28, 0.6)
    E.bloco(0.5, 0.34, 0.18, ctrl, (0.1, -1.3, 0.09), (0, 0, 0.2), raio=0.03)
    E.esfera(0.04, (0.06, -1.42, 0.14), E.luz_mat("led-c", (0.1, 1, 0.3), 10), seg=12, aneis=8)
    return dict(azim=-4, elev=8, lente=110, margem=0.05, luz=0.3)


@produto
def kit_arvore_premium():
    alt, R = 3.0, 1.2
    P.pinheiro(alt, R, seed=9, base_z=0.14)
    pe = E.pbr("pe", (0.03, 0.03, 0.035), 0.8, 0.4)
    E.torno([(0.56, 0.0), (0.56, 0.03), (0.2, 0.08), (0.1, 0.2), (0.0, 0.2)], pe, seg=48)
    P.pontos_luz(P.pontos_copa(alt, R, 340, seed=6, base_z=0.14, recuo=0.96), 0.024, P.COLORIDO + [(1, 0.2, 0.7)], 12.0, "bola")
    E.estrela(0.32, 0.1, (0, 0, alt + 0.36), mat=E.luz_mat("estrela-luz", (1.0, 0.68, 0.26), 2.4))
    ctrl = E.pbr("ctrl", (0.02, 0.02, 0.022), 0, 0.28, 0.6)
    E.bloco(0.44, 0.3, 0.16, ctrl, (0.92, -0.72, 0.08), (0, 0, 0.3), raio=0.03)
    return dict(azim=-7, elev=5, lente=120, margem=0.05, luz=0.3)


# ---------------------------------------------------------------- andar 5: guirlandas

FRENTE_G = dict(azim=-7, elev=4, sombra=False, margem=0.05)


def bagas(rnd, R, n=16, mat=None):
    for _ in range(n):
        a = rnd.uniform(0, math.tau)
        P.frutinhas(rnd, P.no_anel(R, a, rnd.uniform(0.84, 1.18), -0.22 * R), 4, 0.05 * max(R, 0.7), 0.075 * max(R, 0.7), mat)


def cones(R, n, me, seed=2, esc=0.3):
    rnd = random.Random(seed)
    for i in range(n):
        a = i / n * math.tau + rnd.uniform(-0.2, 0.2)
        P.pinha(me, tuple(P.no_anel(R, a, rnd.uniform(0.86, 1.12), -0.3 * R)), esc, (rnd.uniform(1.1, 2.0), rnd.uniform(-0.5, 0.5), rnd.uniform(0, 6)))


@produto
def guirlanda_tradicional():
    rnd = P.guirlanda(1.0, 11, 760)
    bagas(rnd, 1.0, 16)
    cones(1.0, 7, P.pinha_malha(P.mat_pinha()), 3, 0.24)
    for i in range(5):
        a = i * 1.26 + 0.4
        P.canela(tuple(P.no_anel(1.0, a, 1.0, -0.36)), (1.5, 0.1, a), 0.42, 0.038)
    E.laco(fita_vermelha(), 0.38, 0.62, 0.72, (0, -0.38, -1.02), (0.05, 0, 0))
    return FRENTE_G


@produto
def guirlanda_led():
    rnd = P.guirlanda(1.0, 12, 720)
    P.pontos_luz(fio_na_guirlanda(1.0, 84), 0.03, P.CALIDO, 12.0, "bola")
    E.laco(fita_ouro(), 0.28, 0.46, 0.5, (0, -0.38, -1.02))
    return dict(azim=-7, elev=4, sombra=False, margem=0.05, luz=0.42)


@produto
def guirlanda_mini():
    def corpo():
        rnd = P.guirlanda(1.0, 14, 600, 0.52)
        me = P.pinha_malha(E.pbr("pinha-ouro", C.ouro, 1.0, 0.3))
        cones(1.0, 8, me, 4, 0.24)
        la = E.pbr("laranja", (0.86, 0.3, 0.02), 0, 0.3, 0.6)
        ver = E.pbr("cereja", (0.5, 0.01, 0.03), 0, 0.14, 1.0)
        for i in range(10):
            a = i * 0.77 + 0.3
            E.esfera(0.09, tuple(P.no_anel(1.0, a, 1.1 if i % 2 else 0.9, -0.3)), ver if i % 3 else la, seg=20, aneis=14)
    em((0, 0, 0.3), corpo, rot=(math.pi / 2, 0, 0))
    vel = E.pbr("vela", C.marfim, 0, 0.4, Subsurface_Weight=0.6)
    E.torno([(0, 0), (0.25, 0), (0.25, 1.12), (0.22, 1.16), (0.12, 1.14), (0, 1.14)], vel, seg=64)
    E.tubo([(0, 0, 1.12), (0.01, 0, 1.24)], 0.01, E.pbr("pavio", (0.02, 0.02, 0.02), 0, 0.8), suavizar=1, lados=6)
    E.torno([(0, 1.2), (0.05, 1.27), (0.045, 1.36), (0.02, 1.46), (0, 1.54)], E.luz_mat("chama", (1, 0.56, 0.18), 18), seg=24)
    return dict(azim=-8, elev=26, margem=0.05)


@produto
def guirlanda_rustica():
    rnd = random.Random(21)
    gal = E.pbr("galho", (0.17, 0.09, 0.04), 0, 0.72)
    gal2 = E.pbr("galho2", (0.3, 0.17, 0.08), 0, 0.72)
    for i in range(240):
        a0 = rnd.uniform(0, math.tau)
        v = rnd.uniform(0.5, 1.0)
        pts = []
        rr = rnd.uniform(0.74, 1.3)
        y = rnd.uniform(-0.28, 0.24)
        for k in range(5):
            a = a0 + k * v * 0.28
            pts.append((rr * math.cos(a) + rnd.uniform(-0.03, 0.03), y + rnd.uniform(-0.05, 0.05), rr * math.sin(a) + rnd.uniform(-0.03, 0.03)))
            rr += rnd.uniform(-0.07, 0.07)
        E.tubo(pts, 0.012, gal if i % 3 else gal2, suavizar=4, lados=5, raios=lambda t: 0.016 * (1 - t * 0.8))
    cones(1.0, 7, P.pinha_malha(P.mat_pinha()), 7, 0.3)
    juta = E.tecido("juta", (0.34, 0.22, 0.1), 0.85, 0.6, 0.2)
    E.laco(juta, 0.34, 0.56, 0.62, (0, -0.42, -1.02))
    corda = E.pbr("corda", (0.42, 0.3, 0.16), 0, 0.8)
    E.tubo([(-0.1, -0.1, 1.25), (0, -0.1, 1.75), (0.1, -0.1, 1.25)], 0.018, corda, lados=8)
    return FRENTE_G


@produto
def guirlanda_rgb():
    P.guirlanda(1.0, 15, 720)
    P.pontos_luz(fio_na_guirlanda(1.0, 96), 0.034, [hsv(i / 16) for i in range(16)], 9.0, "bola")
    return dict(azim=-7, elev=4, sombra=False, margem=0.05, luz=0.38)


@produto
def guirlanda_premium():
    rnd = P.guirlanda(1.0, 16, 980, 0.66, 0.36, neve=0.6)
    tampa = E.pbr("tampa", C.ouro, 1.0, 0.26)
    mats = [ouro(), E.glitter("ouro-g", (0.9, 0.6, 0.2)), E.pbr("bola-v", C.vermelho_vivo, 0.0, 0.14, 1.0)]
    for i in range(18):
        a = i * 2.39996
        E.bola(0.075 + 0.05 * ((i * 0.37) % 1), tuple(P.no_anel(1.0, a, 0.78 + 0.46 * ((i * 0.7549) % 1), -0.42)), mats[i % 3], tampa, argola=False)
    E.laco(E.tecido("veludo-v", C.vermelho, 0.46, 0.2, 1.0), 0.46, 0.72, 0.86, (0, -0.5, 1.02), (0.05, 0, 0))
    return FRENTE_G


@produto
def kit_entrada():
    rnd = P.guirlanda(0.9, 17, 700, 0.56)
    bagas(rnd, 0.9, 12)
    E.laco(E.tecido("veludo-v", C.vermelho, 0.46, 0.2, 1.0), 0.36, 0.56, 0.5, (0, -0.42, 0.92))
    fio = fita_ouro()
    E.tubo([(0, -0.12, 0.8), (0, -0.14, 0.22)], 0.012, fio, suavizar=1, lados=8)
    P.sino(0.5, loc=(0, -0.14, -0.3))
    mad = E.imagem_mat("placa", "placa-feliz-natal.png", 0.5, (1 / 1.6, 1, 1 / 0.625), plano="xz")
    E.bloco(1.64, 0.05, 0.66, E.madeira("moldura", (0.26, 0.13, 0.05), (0.1, 0.05, 0.02), 6, 0.5, 0.2), (0, -0.02, -1.92), raio=0.016)
    E.bloco(1.6, 0.012, 0.625, mad, (0, -0.052, -1.92))
    corda = E.pbr("corda", (0.42, 0.3, 0.16), 0, 0.8)
    for x in (-0.6, 0.6):
        E.tubo([(x, -0.02, -1.6), (x * 0.82, -0.08, -1.1)], 0.012, corda, suavizar=1, lados=6)
    return dict(azim=-5, elev=3, sombra=False, margem=0.05)


@produto
def kit_luminosas():
    def uma(R, seed):
        def f():
            P.guirlanda(R, seed, int(620 * R), 0.56, 0.3)
            P.pontos_luz(fio_na_guirlanda(R, int(84 * R) + 12), 0.03, P.CALIDO, 12.0, "bola")
        return f
    em((-1.0, 0.2, 1.1), uma(1.0, 18))
    em((1.22, 0, 0.72), uma(0.68, 19))
    em((0.18, -0.6, 0.2), uma(0.42, 20), rot=(math.pi / 2 - 0.1, 0, 0))
    return dict(azim=-5, elev=8, margem=0.05, luz=0.42)


def fio_na_guirlanda(R, n, voltas=11):
    """Fio de luz enrolado na coroa, visível em toda a volta."""
    pts = []
    for i in range(n):
        a = i / n * math.tau
        r = 1 + 0.25 * math.sin(a * voltas)
        pts.append(P.no_anel(R, a, r, -R * (0.24 + 0.3 * math.cos((r - 1) * 2.4))))
    return pts


# ---------------------------------------------------------------- andar 6: presépios

def tinta(cor, r=0.5):
    return E.pbr("tinta", cor, 0, r)


def mat_madeira_clara():
    return E.madeira("cedro", (0.5, 0.29, 0.14), (0.24, 0.12, 0.05), 5, 0.42, 0.25)


def mat_madeira_escura():
    return E.madeira("nogueira", (0.26, 0.13, 0.055), (0.08, 0.035, 0.015), 5, 0.42, 0.25)


def sagrada_familia(manto_m, veste_m, manto_j, veste_j, cab, mad=None, luz=False, barba=None):
    P.figura(1.5, manto_m, veste_m, cab, veu=True, loc=(-0.74, -0.2, 0), giro=-0.6)
    P.figura(1.72, manto_j, veste_j, cab, cajado=True, loc=(0.74, -0.1, 0), giro=0.5, barba=barba or tinta((0.09, 0.05, 0.03)))
    P.manjedoura(1.3, mad, loc=(0, -0.4, 0), luz=luz)


def reis(cores, cab, veste, x0=1.7, passo=0.62, alt=1.46, presente=None):
    presente = presente or ouro()
    for i, cor in enumerate(cores):
        P.figura(alt - i * 0.06, cor, veste, cab, coroa=True, presente=presente, loc=(x0 + i * passo, -0.56 + i * 0.32, 0), giro=0.72)


def luz_quente(forca=60, pos=(0, 0.2, 1.3)):
    l = bpy.data.lights.new("dentro", "POINT")
    l.energy = forca
    l.color = (1, 0.62, 0.3)
    l.shadow_soft_size = 0.5
    o = bpy.data.objects.new("dentro", l)
    o.location = pos
    bpy.context.scene.collection.objects.link(o)
    return o


@produto
def presepio_tradicional():
    a, b = mat_madeira_clara(), mat_madeira_escura()
    E.bloco(5.9, 2.9, 0.1, b, (0, 0, 0.05), raio=0.02)
    em((0, 0, 0.1), lambda: (
        em((0, 0.7, 0), lambda: P.estabulo(3.0, 1.9, 1.0)),
        P.figura(1.5, b, a, a, veu=True, loc=(-0.74, -0.2, 0), giro=-0.6),
        P.figura(1.72, a, b, a, cajado=True, loc=(0.74, -0.1, 0), giro=0.5, barba=b),
        P.manjedoura(1.3, b, a, loc=(0, -0.4, 0)),
        P.boi(0.82, (0.26, 0.13, 0.055), (-0.72, 0.62, 0), -0.1),
        P.boi(0.72, (0.14, 0.08, 0.04), (0.74, 0.62, 0), 3.1, burro=True),
        reis((b, a, b), a, a, 1.62, 0.44),
        P.figura(1.44, a, b, a, cajado=True, loc=(-2.1, -0.3, 0), giro=-0.4),
        P.ovelha(0.8, (-1.6, -0.9, 0), -0.4, a),
        P.ovelha(0.66, (-2.45, -1.0, 0), 0.4, a),
    ))
    E.estrela(0.3, 0.1, (0, 0.2, 3.1), mat=estrela_madeira())
    return dict(azim=-5, elev=12, margem=0.05)


@produto
def presepio_led():
    cab = E.pbr("rosto", (0.6, 0.36, 0.22), 0, 0.5)
    azul = tinta((0.03, 0.09, 0.36))
    mar = tinta(C.marfim)
    verm = tinta((0.32, 0.03, 0.02))
    ocre = tinta((0.46, 0.26, 0.08))
    E.torno([(0, 0), (2.5, 0), (2.5, 0.08), (2.44, 0.12), (0, 0.12)], mat_madeira_escura(), seg=96, esc=(1.08, 0.6, 1))
    em((0, 0, 0.12), lambda: (
        em((0, 0.7, 0), lambda: P.estabulo(3.0, 1.9, 1.0)),
        sagrada_familia(azul, mar, ocre, verm, cab, luz=True),
        P.boi(0.78, (0.26, 0.13, 0.055), (-0.8, 0.62, 0), -0.1),
        P.boi(0.68, (0.16, 0.1, 0.06), (0.78, 0.62, 0), 3.1, burro=True),
        P.ovelha(0.8, (-1.6, -0.5, 0), -0.4),
        P.ovelha(0.66, (1.62, -0.5, 0), 3.4),
    ))
    P.pontos_luz([Vector((-1.46 + i * 2.92 / 9, 0.32, 1.98)) for i in range(10)], 0.05, P.CALIDO, 12.0, "bola")
    E.estrela(0.42, 0.13, (0, 0.2, 3.0), mat=E.luz_mat("estrela-luz", (1.0, 0.68, 0.26), 2.4))
    luz_quente(70, (0, 0.2, 1.4))
    return dict(azim=-5, elev=9, margem=0.05, luz=0.42)


@produto
def presepio_ceramica():
    esm = E.pbr("esmalte", (0.86, 0.85, 0.82), 0.0, 0.1, 1.0)
    azul = E.pbr("esmalte-a", (0.06, 0.16, 0.44), 0.0, 0.1, 1.0)
    au = ouro()
    pr = E.pbr("prata", C.prata, 1.0, 0.16)
    arco = []
    n = 26
    for i in range(n + 1):
        a = math.pi * i / n
        arco.append((1.9 * math.cos(a), 1.2 + 1.9 * math.sin(a)))
    pts = [(2.1, 0), (2.1, 1.2)] + [(x * 1.1, z * 1.03) for x, z in arco[1:-1]] + [(-2.1, 1.2), (-2.1, 0), (-1.72, 0)] + [(x * 0.9, z) for x, z in reversed(arco[1:-1])] + [(1.72, 0)]
    E.agrupar([chapa(pts, 0.28, esm, raio=0.02)], (0, 0.9, 0), (math.pi / 2, 0, 0))
    E.tubo([(1.98 * math.cos(math.pi * t / 26), 0.62, 1.2 + 2.04 * math.sin(math.pi * t / 26)) for t in range(27)], 0.02, au, suavizar=3, lados=8)
    E.torno([(0, 0), (2.6, 0), (2.6, 0.12), (2.5, 0.16), (0, 0.16)], esm, seg=96, esc=(1.1, 0.56, 1))
    em((0, 0, 0.16), lambda: (
        P.figura(1.5, azul, au, esm, veu=True, loc=(-0.72, -0.1, 0), giro=-0.5),
        P.figura(1.7, esm, au, esm, loc=(0.72, 0.02, 0), giro=0.45),
        P.manjedoura(1.1, E.pbr("g", C.ouro, 1.0, 0.3), E.pbr("p", C.prata, 1.0, 0.26), loc=(0, -0.36, 0), menino=esm),
    ))
    E.estrela(0.3, 0.1, (0, 0.76, 3.54), mat=au)
    for s in (-1, 1):
        P.figura(1.0, E.pbr("esm-a2", (0.86, 0.85, 0.82), 0, 0.1, 1.0), pr, esm, coroa=True, loc=(s * 1.5, -0.3, 0.16), giro=-s * 0.5)
    return dict(azim=-6, elev=9, lente=110, margem=0.05)


@produto
def presepio_minimalista():
    br = aco()
    E.bloco(4.8, 1.7, 0.08, br, (0, 0, 0.04), raio=0.012)
    pts = [(2.15 * math.cos(math.pi * t / 44), 2.15 * math.sin(math.pi * t / 44)) for t in range(45)] + [(2.02 * math.cos(math.pi * (44 - t) / 44), 2.02 * math.sin(math.pi * (44 - t) / 44)) for t in range(45)]
    E.agrupar([chapa(pts, 0.08, br, raio=0.006)], (0, 0.52, 0.08), (math.pi / 2, 0, 0))
    E.estrela(0.34, 0.05, (0, 0.46, 2.58), mat=E.pbr("estrela-aco", C.prata, 1.0, 0.2))
    forma = [(0, 0), (0.32, 0), (0.24, 0.5), (0.13, 0.98), (0.11, 1.08), (0.17, 1.22), (0.18, 1.34), (0.12, 1.47), (0, 1.53)]
    E.torno([(r, z) for r, z in forma], br, seg=72, loc=(-0.62, 0, 0.08), rot=(0, 0.1, 0))
    E.torno([(r * 1.1, z * 1.14) for r, z in forma], br, seg=72, loc=(0.64, 0, 0.08), rot=(0, -0.08, 0))
    E.esfera(0.2, (0, -0.06, 0.3), br, seg=36, aneis=24, esc=(1.6, 0.8, 0.54))
    E.torno([(0.0, 0.0), (0.32, 0.0), (0.42, 0.12), (0.38, 0.13), (0.28, 0.05), (0, 0.05)], br, seg=48, loc=(0, -0.06, 0.08), esc=(1.34, 0.8, 1))
    return dict(azim=-6, elev=9, lente=110, margem=0.05)


def palmeira(alt, loc):
    mad = E.madeira("palma", (0.3, 0.17, 0.08), (0.12, 0.06, 0.03), 12, 0.7, 0)
    fol = E.pbr("folha", (0.03, 0.16, 0.05), 0, 0.42)
    it = [E.torno([(0.06, 0), (0.035, alt)], mad, seg=10)]
    for i in range(9):
        a = i / 9 * math.tau
        c = (math.cos(a), math.sin(a))
        it.append(E.fita([(0, 0, alt), (c[0] * 0.28, c[1] * 0.28, alt + 0.14), (c[0] * 0.58, c[1] * 0.58, alt + 0.02), (c[0] * 0.76, c[1] * 0.76, alt - 0.26)], lambda t: 0.16 * math.sin(min(1, t * 1.2 + 0.1) * math.pi) ** 0.7, fol, 0.006, eixo=(-c[1], c[0], 0.0)))
    return E.agrupar(it, loc)


def poco(loc, esc=1.0):
    ped = E.pbr("pedra", (0.42, 0.36, 0.3), 0, 0.84)
    mad = mat_madeira_escura()
    return E.agrupar([E.torno([(0, 0), (0.26, 0), (0.26, 0.26), (0.2, 0.28), (0.2, 0.18), (0, 0.18)], ped, seg=36), E.bloco(0.04, 0.04, 0.6, mad, (-0.24, 0, 0.3)), E.bloco(0.04, 0.04, 0.6, mad, (0.24, 0, 0.3)), E.bloco(0.62, 0.3, 0.05, mad, (0, 0, 0.62), (0.3, 0, 0))], loc, (0, 0, 0), esc)


def colina(R=3.3, h=1.5, loc=(0, 0.3, 0), esc=(1.0, 0.66, 1)):
    """Morro em terraços onde a vila de Belém sobe."""
    are = E.pbr("areia", (0.62, 0.44, 0.24), 0, 0.92)
    n = are.node_tree
    tc = n.nodes.new("ShaderNodeTexCoord")
    rd = n.nodes.new("ShaderNodeTexNoise")
    rd.inputs["Scale"].default_value = 18
    rd.inputs["Detail"].default_value = 6
    rl = n.nodes.new("ShaderNodeBump")
    rl.inputs["Strength"].default_value = 0.4
    n.links.new(tc.outputs["Object"], rd.inputs["Vector"])
    n.links.new(rd.outputs[0], rl.inputs["Height"])
    n.links.new(rl.outputs[0], n.nodes["Principled BSDF"].inputs["Normal"])
    perfil = [(0, 0), (R, 0), (R * 0.98, 0.1), (R * 0.72, h * 0.28), (R * 0.68, h * 0.34), (R * 0.46, h * 0.62), (R * 0.42, h * 0.68), (R * 0.2, h * 0.96), (0, h)]
    return E.torno(perfil, are, seg=128, loc=loc, esc=esc)


def vila():
    teto = E.pbr("cupula", (0.5, 0.28, 0.14), 0, 0.7)
    casas = [
        (-2.56, -0.55, 0.08, 0.86, 0.7, 0.78, None), (2.56, -0.55, 0.08, 0.86, 0.7, 0.72, teto),
        (-1.72, 0.0, 0.46, 0.84, 0.64, 0.74, teto), (1.72, 0.0, 0.46, 0.84, 0.64, 0.7, None),
        (-0.86, 0.5, 0.92, 0.8, 0.6, 0.66, None), (0.9, 0.5, 0.92, 0.8, 0.6, 0.72, teto),
        (0.0, 0.92, 1.42, 0.84, 0.6, 0.66, teto),
    ]
    for i, (x, y, z, l, p, a, t) in enumerate(casas):
        P.casinha(l, p, a, telhado=t, loc=(x, y, z), giro=0.05 * (i % 3 - 1))


def cena_belem(cab, azul, mar, ocre):
    colina()
    vila()
    em((0, -1.02, 0.1), lambda: P.estabulo(1.7, 1.06, 0.66))
    em((0, -1.1, 0.1), lambda: (P.figura(0.62, azul, mar, cab, veu=True, loc=(-0.34, -0.1, 0), giro=-0.5), P.figura(0.72, ocre, mar, cab, loc=(0.36, -0.06, 0), giro=0.5), P.manjedoura(0.5, loc=(0, -0.22, 0))))
    palmeira(1.5, (-3.2, -1.0, 0.0))
    palmeira(1.3, (3.2, -1.0, 0.0))
    E.estrela(0.34, 0.1, (0, 0.8, 3.34), mat=E.luz_mat("estrela-luz", (1.0, 0.68, 0.26), 2.4))


@produto
def vila_led():
    azul = tinta((0.03, 0.09, 0.36))
    cab = E.pbr("rosto", (0.6, 0.36, 0.22), 0, 0.5)
    mar = tinta(C.marfim)
    ocre = tinta((0.46, 0.26, 0.08))
    cena_belem(cab, azul, mar, ocre)
    poco((-1.46, -1.1, 0.04), 0.9)
    P.ovelha(0.42, (1.3, -1.3, 0.04), -0.4)
    luz_quente(30, (0, -1.0, 0.7))
    return dict(azim=-4, elev=12, margem=0.05, luz=0.5)


@produto
def presepio_barro():
    bar = E.barro()
    bar2 = E.barro("barro-c", (0.62, 0.34, 0.16))
    azul = E.barro("pig-azul", (0.05, 0.2, 0.42), 0.7)
    verm = E.barro("pig-verm", (0.5, 0.06, 0.04), 0.7)
    ama = E.barro("pig-ama", (0.76, 0.46, 0.08), 0.7)
    ver = E.barro("pig-ver", (0.08, 0.3, 0.14), 0.7)
    bra = E.barro("pig-bra", (0.82, 0.74, 0.6), 0.7)
    E.torno([(0, 0), (3.2, 0), (3.1, 0.14), (0, 0.16)], bar, seg=96, esc=(0.92, 0.56, 1))
    em((0, 0.52, 0.15), lambda: P.estabulo(2.6, 1.7, 0.8, bar, ama))
    em((0, 0, 0.15), lambda: (
        P.figura(1.5, azul, bra, bar2, veu=True, loc=(-0.74, -0.2, 0), giro=-0.6),
        P.figura(1.7, verm, ama, bar2, loc=(0.74, -0.1, 0), giro=0.5, barba=bar),
        P.manjedoura(1.3, bar, ama, loc=(0, -0.42, 0)),
        P.boi(0.7, (0.5, 0.2, 0.09), (-0.82, 0.44, 0), -0.1),
        P.ovelha(0.66, (-1.72, -0.6, 0), -0.4, bra),
        P.figura(1.34, ver, ama, bar2, loc=(1.56, -0.46, 0), giro=0.62, coroa=True, presente=ama),
        P.figura(1.24, verm, bra, bar2, loc=(2.06, -0.1, 0), giro=0.62, coroa=True, presente=azul),
    ))
    cac = E.barro("cacto", (0.1, 0.32, 0.16), 0.7)
    for x, y, h in ((-2.2, 0.35, 1.7), (2.42, 0.46, 1.3)):
        E.torno([(0.14, 0.12), (0.13, h), (0.1, h + 0.1), (0, h + 0.14)], cac, seg=16, loc=(x, y, 0))
        for s in (-1, 1):
            E.tubo([(x, y, h * 0.5), (x + s * 0.3, y, h * 0.52), (x + s * 0.34, y, h * 0.8)], 0.075, cac, lados=12)
    return dict(azim=-5, elev=11, margem=0.05)


def musgo_mat():
    musgo = E.pbr("musgo", (0.08, 0.2, 0.05), 0, 0.92)
    n = musgo.node_tree
    tc = n.nodes.new("ShaderNodeTexCoord")
    rd = n.nodes.new("ShaderNodeTexNoise")
    rd.inputs["Scale"].default_value = 24
    rd.inputs["Detail"].default_value = 8
    rl = n.nodes.new("ShaderNodeBump")
    rl.inputs["Strength"].default_value = 0.9
    n.links.new(tc.outputs["Object"], rd.inputs["Vector"])
    n.links.new(rd.outputs[0], rl.inputs["Height"])
    n.links.new(rl.outputs[0], n.nodes["Principled BSDF"].inputs["Normal"])
    return musgo


@produto
def kit_familia_sagrada():
    cab = E.pbr("rosto", (0.6, 0.36, 0.22), 0, 0.5)
    azul = tinta((0.03, 0.09, 0.36))
    mar = tinta(C.marfim)
    verm = tinta((0.32, 0.03, 0.02))
    ocre = tinta((0.46, 0.26, 0.08))
    E.torno([(0, 0), (3.2, 0), (3.0, 0.12), (1.6, 0.2), (0, 0.22)], musgo_mat(), seg=96, esc=(0.98, 0.62, 1))
    em((0, 0.7, 0.18), lambda: P.estabulo(2.8, 1.8, 1.0))
    em((0, 0, 0.2), lambda: (
        sagrada_familia(azul, mar, ocre, verm, cab, luz=True),
        P.boi(0.72, (0.26, 0.13, 0.055), (-0.82, 0.58, 0), -0.1),
        P.boi(0.64, (0.16, 0.1, 0.06), (0.82, 0.58, 0), 3.1, burro=True),
        reis((tinta((0.32, 0.03, 0.02)), tinta((0.04, 0.2, 0.1)), tinta((0.2, 0.04, 0.26))), cab, mar, 1.42, 0.38, 1.36),
        P.figura(1.3, ocre, mar, cab, cajado=True, loc=(-1.9, -0.36, 0), giro=-0.4),
        P.ovelha(0.66, (-1.46, -0.86, 0), -0.4),
    ))
    E.estrela(0.36, 0.12, (0, 0.2, 3.1), mat=E.luz_mat("estrela-luz", (1.0, 0.68, 0.26), 2.4))
    luz_quente(46, (0, 0.2, 1.3))
    return dict(azim=-5, elev=10, margem=0.05, luz=0.8)


def camelo(esc, loc, giro):
    mat = E.pbr("camelo", (0.56, 0.38, 0.18), 0, 0.6)
    it = [E.esfera(0.32, (0, 0, 0.72), mat, seg=28, aneis=20, esc=(1.5, 0.75, 0.8)), E.esfera(0.2, (0, 0, 1.04), mat, seg=20, aneis=14)]
    it.append(E.tubo([(0.42, 0, 0.78), (0.72, 0, 0.92), (0.78, 0, 1.28), (1.0, 0, 1.32)], 0.08, mat, lados=12))
    for x in (-0.3, 0.3):
        for y in (-0.14, 0.14):
            it.append(E.torno([(0.05, 0), (0.038, 0.6), (0.06, 0.74)], mat, seg=10, loc=(x, y, 0)))
    return E.agrupar(it, loc, (0, 0, giro), esc)


@produto
def kit_belem():
    azul = tinta((0.03, 0.09, 0.36))
    cab = E.pbr("rosto", (0.6, 0.36, 0.22), 0, 0.5)
    mar = tinta(C.marfim)
    ocre = tinta((0.46, 0.26, 0.08))
    verm = tinta((0.32, 0.03, 0.02))
    E.torno([(0, 0), (4.1, 0), (4.0, 0.06), (0, 0.08)], E.pbr("areia2", (0.56, 0.38, 0.2), 0, 0.92), seg=96, esc=(1.0, 0.72, 1))
    em((0, 0, 0.06), lambda: cena_belem(cab, azul, mar, ocre))
    poco((-1.56, -1.16, 0.08), 0.8)
    for i, c in enumerate((verm, tinta((0.04, 0.2, 0.1)), tinta((0.2, 0.04, 0.26)))):
        P.figura(0.72, c, mar, cab, coroa=True, presente=ouro(), loc=(1.2 + i * 0.44, -1.86 + i * 0.12, 0.06), giro=-0.9)
    camelo(0.62, (3.05, -1.75, 0.06), 2.8)
    camelo(0.56, (-2.72, -1.5, 0.06), 0.3)
    for x, y in ((-1.3, -2.0), (-0.8, -2.2), (-1.8, -1.9)):
        P.ovelha(0.34, (x, y, 0.08), 0.5)
    P.figura(0.64, ocre, mar, cab, cajado=True, loc=(-0.3, -2.1, 0.08), giro=-0.3)
    luz_quente(30, (0, -1.0, 0.8))
    return dict(azim=-4, elev=16, margem=0.05, luz=0.6)


# Reis magos e cena do andar 6, com quadros próprios para a caminhada até a manjedoura
def rei(cor, veste):
    cab = E.pbr("rosto", (0.6, 0.36, 0.22), 0, 0.5)
    P.figura(1.6, tinta(cor), tinta(veste), cab, coroa=True, presente=ouro(), giro=1.15, barba=tinta((0.2, 0.12, 0.08)))
    return dict(azim=0, elev=4, lente=110, margem=0.05)


@produto
def rei_1():
    return rei((0.32, 0.03, 0.02), C.ouro)


@produto
def rei_2():
    return rei((0.04, 0.2, 0.1), C.marfim)


@produto
def rei_3():
    return rei((0.2, 0.04, 0.26), C.ouro_claro)


@produto
def cena_manjedoura():
    cab = E.pbr("rosto", (0.6, 0.36, 0.22), 0, 0.5)
    azul = tinta((0.03, 0.09, 0.36))
    mar = tinta(C.marfim)
    verm = tinta((0.32, 0.03, 0.02))
    ocre = tinta((0.46, 0.26, 0.08))
    em((0, 0.7, 0), lambda: P.estabulo(3.0, 1.9, 1.0))
    sagrada_familia(azul, mar, ocre, verm, cab, luz=True)
    P.boi(0.78, (0.26, 0.13, 0.055), (-0.8, 0.62, 0), -0.1)
    P.boi(0.68, (0.16, 0.1, 0.06), (0.78, 0.62, 0), 3.1, burro=True)
    P.ovelha(0.8, (-1.64, -0.5, 0), -0.4)
    P.pontos_luz([Vector((-1.46 + i * 2.92 / 9, 0.32, 1.86)) for i in range(10)], 0.05, P.CALIDO, 12.0, "bola")
    luz_quente(80, (0, 0.2, 1.3))
    return dict(azim=-5, elev=6, margem=0.04, luz=0.4)


# ---------------------------------------------------------------- páginas Sobre e Contato

def argola(raio, fio, loc, mat):
    """Argola de metal para pendurar enfeites que não são bolas."""
    v, f = [], []
    for i in range(36):
        a = 2 * math.pi * i / 36
        for j in range(10):
            b = 2 * math.pi * j / 10
            cr = raio + fio * math.cos(b)
            v.append((cr * math.cos(a), fio * math.sin(b), cr * math.sin(a)))
    for i in range(36):
        for j in range(10):
            f.append((i * 10 + j, i * 10 + (j + 1) % 10, ((i + 1) % 36) * 10 + (j + 1) % 10, ((i + 1) % 36) * 10 + j))
    return E.obj(E.malha("argola", v, f, mat), loc)


PENDURADO = dict(azim=0, elev=6, sombra=False, margem=0.04)


@produto
def enfeite_listrado():
    mat = E.listras("listrado", C.vermelho_vivo, C.marfim, faixas=21.0, metal=0.3, rugosidade_a=0.1, rugosidade_b=0.26, onda=0.75)
    E.bola(0.5, (0, 0, 0.5), mat)
    return PENDURADO


@produto
def enfeite_dourado():
    E.bola(0.5, (0, 0, 0.5), E.glitter("ouro-glitter", C.ouro, escala=360, forca=0.3, rugosidade=0.3))
    E.laco(fita_vermelha(), 0.15, 0.24, 0.24, (0, -0.03, 1.13), (math.pi / 2 - 0.12, 0, 0))
    return PENDURADO


@produto
def enfeite_estrela():
    ouro = E.pbr("estrela-ouro", C.ouro_claro, 1.0, 0.24)
    E.estrela(0.5, 0.17, (0, 0, 0.5), (0, 0, 0), ouro)
    argola(0.045, 0.011, (0, 0, 1.04), E.pbr("tampa", C.ouro, 1.0, 0.26))
    return PENDURADO


@produto
def enfeite_verde():
    E.bola(0.5, (0, 0, 0.5), E.pbr("verde-brilho", (0.016, 0.17, 0.075), 0.55, 0.1, 1.0))
    return PENDURADO


@produto
def enfeite_estrelado():
    mat = E.imagem_mat("estrelas", "estrelas-bola.png", 0.2, 1.0, 0.3, 1.0, deslocar=(0.5, 0.5, 0.5), projecao="SPHERE")
    E.bola(0.5, (0, 0, 0.5), mat)
    return PENDURADO


# ---------------------------------------------------------------- a lojinha de bairro onde a história começou

MARCA = os.path.join(AQUI, "..", "..", "redesign", "js")


def caminho_svg(d, passos=8):
    """Atributo d de SVG em contornos de pontos (x, y), com as curvas achatadas."""
    tk = re.findall(r"[MmLlHhVvQqCcSsZz]|-?(?:\d+\.?\d*|\.\d+)", d)
    i, cmd = 0, "M"
    x = y = x0 = y0 = 0.0
    ctrl = None
    contornos, atual = [], []

    def num():
        nonlocal i
        i += 1
        return float(tk[i - 1])

    while i < len(tk):
        if tk[i].isalpha():
            cmd = tk[i]
            i += 1
            if cmd in "Zz":
                if atual:
                    contornos.append(atual)
                atual, ctrl = [], None
                x, y = x0, y0
                continue
        rel = cmd.islower()
        bx, by = (x, y) if rel else (0.0, 0.0)
        k = cmd.upper()
        if k == "M":
            if atual:
                contornos.append(atual)
            x = x0 = num() + bx
            y = y0 = num() + by
            atual, ctrl = [(x, y)], None
            cmd = "l" if rel else "L"
        elif k == "L":
            x, y = num() + bx, num() + by
            atual.append((x, y))
            ctrl = None
        elif k == "H":
            x = num() + bx
            atual.append((x, y))
            ctrl = None
        elif k == "V":
            y = num() + by
            atual.append((x, y))
            ctrl = None
        elif k == "Q":
            cx, cy, nx, ny = num() + bx, num() + by, num() + bx, num() + by
            for j in range(1, passos + 1):
                t = j / passos
                u = 1 - t
                atual.append((u * u * x + 2 * u * t * cx + t * t * nx, u * u * y + 2 * u * t * cy + t * t * ny))
            x, y, ctrl = nx, ny, None
        elif k in "CS":
            if k == "C":
                c1x, c1y = num() + bx, num() + by
            else:
                c1x, c1y = (2 * x - ctrl[0], 2 * y - ctrl[1]) if ctrl else (x, y)
            c2x, c2y, nx, ny = num() + bx, num() + by, num() + bx, num() + by
            for j in range(1, passos + 1):
                t = j / passos
                u = 1 - t
                atual.append((u ** 3 * x + 3 * u * u * t * c1x + 3 * u * t * t * c2x + t ** 3 * nx,
                              u ** 3 * y + 3 * u * u * t * c1y + 3 * u * t * t * c2y + t ** 3 * ny))
            x, y, ctrl = nx, ny, (c2x, c2y)
        else:
            raise ValueError("comando SVG sem suporte: " + cmd)
    if atual:
        contornos.append(atual)
    limpos = []
    for c in contornos:
        p = [c[0]] + [q for a, q in zip(c, c[1:]) if math.dist(a, q) > 1e-6]
        if len(p) > 2 and math.dist(p[0], p[-1]) < 1e-6:
            p.pop()
        if len(p) >= 3:
            limpos += [q for q in desembaracar(p) if len(q) >= 3 and abs(_area(q)) > 1e-3]
    return limpos


def _cruza(p1, p2, p3, p4):
    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if abs(d) < 1e-12:
        return None
    t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    if 1e-9 < t < 1 - 1e-9 and 1e-9 < u < 1 - 1e-9:
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
    return None


def desembaracar(c):
    """Fontes variáveis trazem contornos que se cruzam; o Blender só preenche laços simples."""
    n = len(c)
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            x = _cruza(c[i], c[(i + 1) % n], c[j], c[(j + 1) % n])
            if x:
                return desembaracar(c[:i + 1] + [x] + c[j + 1:]) + desembaracar([x] + c[i + 1:j + 1])
    return [c]


def _area(p):
    return 0.5 * sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1]))


def _centro(p):
    a = _area(p)
    cx = sum((q[0] + r[0]) * (q[0] * r[1] - r[0] * q[1]) for q, r in zip(p, p[1:] + p[:1])) / (6 * a)
    cy = sum((q[1] + r[1]) * (q[0] * r[1] - r[0] * q[1]) for q, r in zip(p, p[1:] + p[:1])) / (6 * a)
    return cx, cy


def _dentro(pt, poli):
    x, y = pt
    dentro = False
    for (x1, y1), (x2, y2) in zip(poli, poli[1:] + poli[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            dentro = not dentro
    return dentro


def preenchidos(contornos):
    """Regra nonzero do SVG: contornos no sentido contrário viram furos de quem os contém."""
    if not contornos:
        return []
    sinal = math.copysign(1, _area(max(contornos, key=lambda c: abs(_area(c)))))
    fora = [[c] for c in contornos if math.copysign(1, _area(c)) == sinal]
    for c in contornos:
        if math.copysign(1, _area(c)) != sinal:
            dono = next((g for g in fora if _dentro(_centro(c), g[0])), None)
            (dono or max(fora, key=lambda g: abs(_area(g[0])))).append(c)
    return fora


def curva_plana(nome, contornos, mat, esc, extrude, loc, chanfro=0.0):
    """Contornos 2D viram uma peça recortada de frente para a câmera (plano xz)."""
    cu = bpy.data.curves.new(nome, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = extrude
    cu.bevel_depth = chanfro
    cu.bevel_resolution = 2
    for pts in contornos:
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for ponto, (x, y) in zip(sp.points, pts):
            ponto.co = (x * esc, -y * esc, 0.0, 1.0)
        sp.use_cyclic_u = True
    cu.materials.append(mat)
    o = bpy.data.objects.new(nome, cu)
    o.location = loc
    o.rotation_euler = (math.pi / 2, 0, 0)
    bpy.context.scene.collection.objects.link(o)
    return o


def letreiro_dados():
    s = open(os.path.join(MARCA, "dados", "letreiro.js"), encoding="utf-8").read()
    i = s.index("Departal.letreiro =") + len("Departal.letreiro =")
    return json.JSONDecoder().raw_decode(s[i:].lstrip())[0]


def gorro_svg():
    s = open(os.path.join(MARCA, "nucleo.js"), encoding="utf-8").read()
    svg = s[s.index("D.gorro = '") + 11:]
    svg = svg[:svg.index("';")]
    caminhos = re.findall(r'<path d="([^"]+)" fill="(#[0-9a-f]+)"', svg)
    circulos = [(float(a), float(b), float(r), cor) for a, b, r, cor in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="(#[0-9a-f]+)"', svg)]
    return caminhos, circulos


def letreiro_3d(largura, cx, cz, frente):
    """Letreiro luminoso da Departal com o gorro na mesma posição do logotipo do site."""
    dados = letreiro_dados()
    esc = largura / dados["largura"]
    origem = (cx - largura / 2, frente, cz + dados["altura"] * esc / 2)
    neon = E.luz_mat("letreiro", (1.0, 0.02, 0.03), 1.15)
    e = 0.012
    for letra in dados["letras"]:
        for grupo in preenchidos(caminho_svg(letra["d"], 6)):
            curva_plana("letra", grupo, neon, esc, e, (origem[0], frente - e, origem[2]), chanfro=0.0015)
    # o chapéu: mesma conta do CSS (.nav__chapeu: top -69%, largura 16,9%)
    caminhos, circulos = gorro_svg()
    k = 0.169 * dados["largura"] / 132.0
    topo = -0.69 * dados["altura"]
    mats = {"#c8102e": E.pbr("gorro", (0.6, 0.006, 0.026), 0.0, 0.55, Sheen_Weight=0.5),
            "#8e0b22": E.pbr("gorro-dobra", (0.25, 0.004, 0.014), 0.0, 0.6),
            "#f6efe2": E.pbr("pelo", (0.9, 0.86, 0.78), 0.0, 0.9, Sheen_Weight=1.0),
            "#cfc9ba": E.pbr("pelo-sombra", (0.58, 0.55, 0.49), 0.0, 0.9)}
    for n, (d, cor) in enumerate(caminhos):
        contornos = [[(x * k, topo + y * k) for x, y in c] for c in caminho_svg(d, 10)]
        y = frente - 2 * e - 0.006 - n * 0.004
        for grupo in preenchidos(contornos):
            curva_plana("gorro", grupo, mats[cor], esc, 0.005, (origem[0], y, origem[2]))
    for x, yy, r, cor in circulos:
        if cor in mats:
            E.esfera(r * k * esc, (origem[0] + x * k * esc, frente - 2 * e - 0.03, origem[2] - (topo + yy * k) * esc), mats[cor], seg=32, aneis=20)


def toldo(x0, x1, ya, za, yb, zb, cair, mat, lado, listras=20):
    """Toldo listrado inclinado, com sanefa recortada em uma onda por listra."""
    nx, nr = listras * 6, 8
    v, f = [], []
    for j in range(nr + 1):
        t = j / nr
        for i in range(nx + 1):
            v.append((x0 + (x1 - x0) * i / nx, ya + (yb - ya) * t, za + (zb - za) * t + 0.035 * math.sin(math.pi * t)))
    for j in range(nr):
        for i in range(nx):
            a = j * (nx + 1) + i
            f.append((a, a + nx + 1, a + nx + 2, a + 1))
    pano = E.obj(E.malha("toldo", v, f, mat))
    pano.modifiers.new("s", "SOLIDIFY").thickness = 0.012
    v, f = [], []
    nx = listras * 8
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx
        v.append((x, yb, zb + 0.004))
        v.append((x, yb, zb - cair - 0.03 * math.sin(math.pi * (i % 8) / 8)))
    for i in range(nx):
        f.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    san = E.obj(E.malha("sanefa", v, f, mat))
    san.modifiers.new("s", "SOLIDIFY").thickness = 0.01
    for x in (x0, x1):
        E.obj(E.malha("aba", [(x, ya, za), (x, yb, zb), (x, yb, zb - cair)], [(0, 1, 2)], lado, suave=False))


def poste(x, y):
    metal = E.pbr("poste", (0.01, 0.035, 0.022), 0.6, 0.35)
    E.torno([(0.0, 0.0), (0.075, 0.0), (0.075, 0.09), (0.05, 0.13), (0.032, 0.24), (0.026, 2.12), (0.042, 2.14), (0.042, 2.18), (0.0, 2.18)], metal, seg=32, loc=(x, y, 0))
    E.torno([(0.0, 2.18), (0.05, 2.18), (0.095, 2.38), (0.0, 2.38)], E.luz_mat("lanterna", (1.0, 0.68, 0.36), 7.0), seg=32, loc=(x, y, 0))
    E.torno([(0.0, 2.38), (0.125, 2.38), (0.11, 2.41), (0.04, 2.5), (0.015, 2.56), (0.0, 2.58)], metal, seg=32, loc=(x, y, 0))
    E.laco(fita_vermelha(), 0.05, 0.08, 0.1, (x, y - 0.035, 1.72), (math.pi / 2 - 0.1, 0, 0))
    l = luz_quente(30, (x, y, 2.28))
    l.data.shadow_soft_size = 0.05


@produto
def lojinha():
    s = bpy.context.scene
    s.render.resolution_y = int(s.render.resolution_x * 1.12)
    s.world.node_tree.nodes["Background"].inputs[1].default_value = 0.34

    parede = E.pbr("reboco", (0.74, 0.57, 0.41), 0.0, 0.88)
    friso = E.pbr("friso", (0.86, 0.8, 0.7), 0.0, 0.6)
    verde = E.pbr("verde-loja", (0.008, 0.075, 0.042), 0.1, 0.42, 0.4)
    verde_fundo = E.pbr("verde-fundo", (0.004, 0.04, 0.022), 0.1, 0.5)
    pedra = E.pbr("pedra", (0.42, 0.4, 0.37), 0.0, 0.8)
    veludo = E.pbr("veludo", (0.24, 0.008, 0.022), 0.0, 0.7, Sheen_Weight=0.8)
    acesa = E.luz_mat("janela-acesa", (1.0, 0.6, 0.28), 1.4)

    W, D, H = 2.6, 1.4, 3.46
    frente = -D / 2
    corpo = E.bloco(W, D, H, parede, (0, 0, H / 2))

    def furo(w, h, prof, x, z, mat):
        c = E.bloco(w, prof + 0.05, h, mat, (x, frente + (prof - 0.05) / 2, z))
        c["apoio"] = 1
        c.hide_render = True
        m = corpo.modifiers.new("furo", "BOOLEAN")
        m.operation = "DIFFERENCE"
        m.object = c
        m.solver = "EXACT"
        m.material_mode = "TRANSFER"

    vx, vw = -0.46, 1.32
    px, pw = 0.74, 0.56
    furo(vw, 1.12, 0.5, vx, 0.96, veludo)
    furo(pw, 1.48, 0.1, px, 0.88, verde)
    for jx in (-0.6, 0.6):
        furo(0.46, 0.62, 0.08, jx, 2.98, friso)

    # base, frisos, platibanda e frontão com o ano de abertura
    E.bloco(W + 0.04, D + 0.04, 0.14, verde_fundo, (0, 0, 0.07))
    E.bloco(W + 0.12, D + 0.12, 0.1, friso, (0, 0, 2.41), raio=0.01)
    E.bloco(W + 0.08, D + 0.08, 0.05, friso, (0, 0, H - 0.025))
    E.bloco(W + 0.16, D + 0.16, 0.1, friso, (0, 0, H + 0.05), raio=0.01)
    E.bloco(W, D, 0.16, parede, (0, 0, H + 0.18))
    E.bloco(W + 0.06, D + 0.06, 0.04, friso, (0, 0, H + 0.28))
    E.bloco(0.92, 0.12, 0.2, parede, (0, frente + 0.06, H + 0.4))
    E.bloco(0.98, 0.16, 0.04, friso, (0, frente + 0.06, H + 0.52))
    for lado in (-1, 1):
        E.bloco(0.12, 0.03, 2.22, friso, (lado * (W / 2 - 0.06), frente - 0.015, 1.25))
        E.bloco(0.12, 0.03, 0.975, friso, (lado * (W / 2 - 0.06), frente - 0.015, 2.947))
    try:
        fonte = bpy.data.fonts.load(os.path.join(E.TEX, "fraunces.ttf"), check_existing=True)
        cu = bpy.data.curves.new("ano", "FONT")
        cu.body = "2025"
        cu.font = fonte
        cu.size = 0.12
        cu.extrude = 0.006
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.materials.append(verde)
        o = bpy.data.objects.new("ano", cu)
        o.location = (0, frente - 0.006, H + 0.4)
        o.rotation_euler = (math.pi / 2, 0, 0)
        s.collection.objects.link(o)
    except Exception:
        traceback.print_exc()

    # vitrine acesa: pinheirinho, presentes e bolas penduradas
    E.bloco(vw + 0.08, 0.05, 0.05, verde, (vx, frente - 0.02, 1.545))
    for lado in (-1, 1):
        E.bloco(0.05, 0.05, 1.2, verde, (vx + lado * (vw / 2 + 0.015), frente - 0.02, 0.96))
    E.bloco(vw + 0.16, 0.13, 0.045, friso, (vx, frente - 0.04, 0.378))
    E.bloco(vw + 0.04, 0.02, 0.2, verde, (vx, frente - 0.01, 0.26))
    vid = E.bloco(vw, 0.006, 1.12, E.vidro("vitrine-vidro", rugosidade=0.0, ior=1.45), (vx, frente - 0.012, 0.96))
    vid.visible_shadow = False
    E.bloco(vw - 0.02, 0.01, 1.1, E.luz_mat("fundo-vitrine", (1.0, 0.52, 0.24), 0.75), (vx, frente + 0.49, 0.96))
    E.bloco(vw - 0.01, 0.46, 0.05, E.madeira("tablado"), (vx, frente + 0.25, 0.425))

    def arvorezinha():
        P.pinheiro(0.82, 0.2, seed=4, andares=14, ramo=0.64, tronco=False)
        P.pontos_luz(P.pontos_copa(0.82, 0.2, 30, seed=8, recuo=1.0), 0.011, P.CALIDO, 16.0, "bola")
        E.estrela(0.05, 0.018, (0, 0, 0.86), (0, 0, 0), E.luz_mat("estrela-acesa", (1.0, 0.78, 0.4), 4.0))
    em((vx - 0.36, frente + 0.25, 0.45), arvorezinha)
    caixa_presente(0.15, 0.13, 0.11, papel(C.vermelho), fita_ouro(), (vx + 0.06, frente + 0.3, 0.45), 0.35)
    caixa_presente(0.11, 0.11, 0.17, papel(C.verde), fita_vermelha(), (vx + 0.27, frente + 0.33, 0.45), -0.25)
    caixa_presente(0.1, 0.09, 0.07, papel(C.marfim), fita_vermelha(), (vx + 0.13, frente + 0.13, 0.45), 0.7)
    caixa_presente(0.09, 0.09, 0.09, ouro(), fita_vermelha(), (vx - 0.1, frente + 0.12, 0.45), -0.4)
    fio = E.pbr("fio-ouro", C.ouro, 1.0, 0.3)
    bolas = [(0.24, 1.24, E.glitter("bola-ouro", C.ouro, escala=500)), (0.4, 1.1, E.pbr("bola-vermelha", C.vermelho_vivo, 0.3, 0.12, 1.0)), (0.54, 1.29, E.pbr("bola-verde", (0.016, 0.17, 0.075), 0.55, 0.1, 1.0))]
    for dx, z, mat in bolas:
        E.bola(0.045, (vx + dx, frente + 0.3, z), mat, argola=False)
        E.tubo([(vx + dx, frente + 0.3, z + 0.05), (vx + dx, frente + 0.3, 1.52)], 0.0016, fio, suavizar=1, lados=6)

    # porta verde com guirlanda
    E.bloco(pw - 0.02, 0.03, 1.46, verde, (px, frente + 0.085, 0.87))
    E.bloco(0.34, 0.01, 0.5, E.luz_mat("vidro-porta", (1.0, 0.62, 0.3), 1.2), (px, frente + 0.068, 1.22))
    E.bloco(0.34, 0.012, 0.4, verde_fundo, (px, frente + 0.066, 0.5))
    E.esfera(0.022, (px + 0.2, frente + 0.05, 0.86), ouro(), seg=24, aneis=16)
    E.bloco(pw + 0.1, 0.04, 0.05, verde, (px, frente - 0.02, 1.645))
    for lado in (-1, 1):
        E.bloco(0.05, 0.04, 1.5, verde, (px + lado * (pw / 2 + 0.025), frente - 0.02, 0.89))
    E.bloco(pw + 0.12, 0.18, 0.07, pedra, (px, frente - 0.09, 0.035))

    def coroa():
        rnd = P.guirlanda(0.105, seed=5, n=170, ramo=0.72, largura=0.34)
        baga = E.pbr("baga", (0.5, 0.01, 0.02), 0.0, 0.25, 0.8)
        for i in range(9):
            a = i / 9 * math.tau + rnd.uniform(-0.2, 0.2)
            E.esfera(0.009, tuple(P.no_anel(0.105, a, rnd.uniform(0.85, 1.15), -0.03)), baga, seg=12, aneis=8)
        E.laco(fita_vermelha(), 0.04, 0.066, 0.075, (0, -0.04, -0.108), (0.05, 0, 0))
    em((px, frente + 0.02, 1.22), coroa)

    # sobrado: janelas acesas com venezianas abertas
    for jx in (-0.6, 0.6):
        E.bloco(0.46, 0.005, 0.62, acesa, (jx, frente + 0.077, 2.98))
        E.bloco(0.022, 0.02, 0.62, friso, (jx, frente + 0.065, 2.98))
        E.bloco(0.46, 0.02, 0.022, friso, (jx, frente + 0.065, 3.06))
        E.bloco(0.58, 0.1, 0.04, friso, (jx, frente - 0.03, 2.65))
        for lado in (-1, 1):
            sx = jx + lado * 0.355
            E.bloco(0.22, 0.03, 0.64, verde, (sx, frente - 0.015, 2.98), raio=0.004)
            for k in range(9):
                E.bloco(0.18, 0.006, 0.014, verde_fundo, (sx, frente - 0.032, 2.73 + k * 0.0625))

    # toldo, letreiro e cordão de luzes na cornija
    toldo(-1.2083, 1.2083, frente, 1.86, frente - 0.48, 1.62, 0.075,
          E.listras("toldo", C.vermelho_vivo, C.marfim, faixas=26.0, metal=0.0, rugosidade_a=0.62, rugosidade_b=0.66, eixo="x"),
          E.pbr("toldo-aba", C.vermelho_vivo, 0.0, 0.62))
    E.bloco(2.1, 0.04, 0.38, E.pbr("moldura", C.ouro, 1.0, 0.35), (0, frente - 0.02, 2.08), raio=0.006)
    E.bloco(2.04, 0.05, 0.32, E.pbr("placa", (0.006, 0.03, 0.018), 0.2, 0.45), (0, frente - 0.03, 2.08), raio=0.004)
    letreiro_3d(1.8, 0.0, 2.08, frente - 0.055)
    pts = []
    for i in range(61):
        t = i / 60
        pts.append(Vector((-1.36 + 2.72 * t, frente - 0.11, H + 0.04 - 0.1 * math.sin(math.pi * ((t * 3) % 1)))))
    P.cordao(pts, 33, 0.0035, 0.017, P.CALIDO, forca=16.0)

    # calçada, vaso com pinheiro e poste
    E.bloco(3.6, 2.24, 0.08, E.pbr("calcada", (0.33, 0.31, 0.29), 0.0, 0.86), (0.22, -0.4, -0.04), raio=0.01)

    def vaso():
        E.torno([(0.0, 0.0), (0.085, 0.0), (0.11, 0.2), (0.125, 0.22), (0.125, 0.25), (0.0, 0.25)], E.barro("vaso"), seg=40)
        P.pinheiro(0.62, 0.19, seed=9, andares=12, base_z=0.2, ramo=0.6, tronco=False)
        P.pontos_luz(P.pontos_copa(0.62, 0.19, 18, seed=3, base_z=0.2, recuo=1.0), 0.01, P.CALIDO, 14.0, "bola")
    em((1.12, frente - 0.24, 0), vaso)
    poste(1.74, -1.22)
    return dict(azim=-22, elev=7, lente=70, margem=0.04, sombra=True, luz=0.36)


# ---------------------------------------------------------------- camadas com a mesma câmera

CAMADAS = {}


def camadas(fn):
    CAMADAS[fn.__name__.replace("_", "-")] = fn
    return fn


def coletar(fn):
    antes = set(bpy.context.scene.objects)
    fn()
    return [o for o in bpy.context.scene.objects if o not in antes]


@camadas
def arvore_montagem():
    """Andar 1: a árvore é montada na ordem da dica da loja."""
    alt, R = 3.3, 1.3
    pe = E.pbr("pe", (0.03, 0.03, 0.035), 0.8, 0.4)
    g = {}
    g["arvore"] = coletar(lambda: (P.pinheiro(alt, R, seed=1, base_z=0.14), E.torno([(0.6, 0.0), (0.6, 0.03), (0.2, 0.08), (0.11, 0.2), (0.1, 0.34), (0.0, 0.34)], pe, seg=48)))
    g["luzes"] = coletar(lambda: P.pontos_luz(P.pontos_copa(alt, R, 340, seed=4, base_z=0.14, recuo=1.0), 0.02, P.CALIDO, 12.0, "bola"))
    g["grandes"] = coletar(lambda: bolas_na_arvore(P.pontos_copa(alt, R, 15, seed=2, base_z=0.14, recuo=1.08, fim=0.8), 0.14, paleta_bolas()))
    def pequenos():
        bolas_na_arvore(P.pontos_copa(alt, R, 22, seed=11, base_z=0.14, recuo=1.08, fim=0.9), 0.075, [ouro(), E.pbr("prata", C.prata, 1.0, 0.16), E.glitter("rubi", (0.72, 0.03, 0.05))])
        au = estrela_madeira()
        for p in P.pontos_copa(alt, R, 12, seed=13, base_z=0.14, recuo=1.1, fim=0.86):
            d = Vector((p.x, p.y, 0)).normalized()
            E.estrela(0.085, 0.03, tuple(p), (0, 0, math.atan2(d.y, d.x) + math.pi / 2), au)
    g["pequenos"] = coletar(pequenos)
    g["estrela"] = coletar(lambda: E.estrela(0.3, 0.1, (0, 0, alt + 0.42), mat=E.luz_mat("estrela-luz", (1.0, 0.68, 0.26), 2.4)))
    quadros = {
        "arvore-0": (["arvore"], []),
        "arvore-1": (["luzes"], ["arvore"]),
        "arvore-2": (["grandes"], ["arvore"]),
        "arvore-3": (["pequenos"], ["arvore"]),
        "arvore-4": (["estrela"], ["arvore"]),
    }
    return g, quadros, dict(azim=-10, elev=5, lente=120, margem=0.05)


@camadas
def guirlanda_montagem():
    """Andar 5: base, laços e extras do personalizador."""
    g = {}
    g["base"] = coletar(lambda: (bagas(P.guirlanda(1.0, 11, 760), 1.0, 16), cones(1.0, 6, P.pinha_malha(P.mat_pinha()), 3, 0.24)))
    def luzes():
        P.pontos_luz(fio_na_guirlanda(1.0, 84), 0.03, P.CALIDO, 12.0, "bola")
    g["luzes"] = coletar(luzes)
    pos = ((0, -0.42, -1.02), (0.05, 0, 0))
    g["vermelho"] = coletar(lambda: E.laco(fita_vermelha(), 0.38, 0.62, 0.72, *pos))
    g["dourado"] = coletar(lambda: E.laco(fita_ouro(), 0.38, 0.62, 0.72, *pos))
    g["xadrez"] = coletar(lambda: E.laco(E.imagem_mat("laco-x", "xadrez-vermelho.png", 0.6, 3.0, plano="xz", brilho=0.5), 0.38, 0.62, 0.72, *pos))
    g["juta"] = coletar(lambda: E.laco(E.tecido("juta", (0.34, 0.22, 0.1), 0.85, 0.6, 0.2), 0.38, 0.62, 0.72, *pos))
    def extras():
        tampa = E.pbr("tampa", C.ouro, 1.0, 0.26)
        mats = [ouro(), E.glitter("ouro-g", (0.9, 0.6, 0.2))]
        for i in range(14):
            a = i * 2.39996 + 0.5
            E.bola(0.07 + 0.04 * ((i * 0.37) % 1), tuple(P.no_anel(1.0, a, 0.8 + 0.42 * ((i * 0.7549) % 1), -0.52)), mats[i % 2], tampa, argola=False)
    g["extras"] = coletar(extras)
    def placa():
        mad = E.madeira("placa", (0.5, 0.3, 0.15), (0.3, 0.16, 0.07), 3, 0.5, 0.2)
        E.bloco(1.08, 0.05, 0.44, mad, (0, -0.1, 0.0), raio=0.03)
        fita = E.pbr("cordao", C.ouro, 0.8, 0.4)
        for x in (-0.36, 0.36):
            E.tubo([(x, -0.1, 0.22), (x * 0.5, -0.12, 0.7), (0, -0.12, 0.92)], 0.012, fita, lados=6)
    g["placa"] = coletar(placa)
    so = lambda n: ([n], ["base"])
    quadros = {"g-base": (["base"], []), "g-luzes": so("luzes"), "g-laco-vermelho": so("vermelho"), "g-laco-dourado": so("dourado"), "g-laco-xadrez": so("xadrez"), "g-laco-juta": so("juta"), "g-extras": so("extras"), "g-placa": so("placa")}
    return g, quadros, dict(azim=-5, elev=3, sombra=False, margem=0.05)


def render_camadas(nome, saida, res, amostras):
    E.cena(res, amostras)
    grupos, quadros, opcoes = CAMADAS[nome]()
    E.estudio(**opcoes)
    chao = [o for o in bpy.context.scene.objects if o.get("apoio")]
    for arquivo, (mostrar, recortar) in quadros.items():
        for g, objs in grupos.items():
            for o in objs:
                o.hide_render = g not in mostrar and g not in recortar
                o.is_holdout = g in recortar
        for o in chao:
            o.hide_render = bool(recortar)
        E.render(os.path.join(saida, arquivo + ".png"))
        print(f"FEITO {arquivo}", flush=True)


# ---------------------------------------------------------------- execução

def principal():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    op = {"--so": "", "--res": "800", "--amostras": "56", "--saida": os.path.join(AQUI, "saida"), "--pular": "0", "--grupo": "tudo"}
    for i in range(0, len(args), 2):
        op[args[i]] = args[i + 1]
    pedidos = [n for n in op["--so"].split(",") if n] or {"tudo": list(PRODUTOS) + list(CAMADAS), "produtos": list(PRODUTOS), "camadas": list(CAMADAS)}[op["--grupo"]]
    os.makedirs(op["--saida"], exist_ok=True)
    feitos = 0
    for nome in pedidos:
        t0 = time.time()
        try:
            if nome in CAMADAS:
                render_camadas(nome, op["--saida"], int(op["--res"]), int(op["--amostras"]))
            else:
                destino = os.path.join(op["--saida"], nome + ".png")
                if op["--pular"] == "1" and os.path.exists(destino):
                    continue
                E.cena(int(op["--res"]), int(op["--amostras"]))
                fim = PRODUTOS[nome]()
                E.estudio(**(fim or {}))
                E.render(destino)
            feitos += 1
            print(f"FEITO {nome} {time.time() - t0:.1f}s", flush=True)
        except Exception:
            print(f"FALHOU {nome}", flush=True)
            traceback.print_exc()
    print(f"FIM {feitos}/{len(pedidos)}", flush=True)


if __name__ == "__main__":
    principal()
