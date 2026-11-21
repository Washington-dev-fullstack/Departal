# Peças maiores usadas por vários produtos: árvores, guirlandas, luzes, roupas e figuras do presépio.
import math
import random

import bpy
import numpy as np
from mathutils import Matrix, Vector

import estudio as E
from estudio import Cores as C


# ---------------------------------------------------------------- pinheiros

def ramos_pinho(rnd, neve=0.0, agulha=0.15, base=(0.018, 0.085, 0.045), ponta=(0.08, 0.26, 0.13)):
    mat = E.pinho_mat(base=base, ponta=ponta, neve=neve)
    return [E.ramo_malha(f"ramo{i}", mat, rnd, agulha=agulha) for i in range(3)]


def pinheiro(alt=3.0, raio=1.2, seed=1, andares=17, neve=0.0, ramo=0.46, base_z=0.0, tronco=True):
    """Pinheiro cheio. Devolve o grupo e uma lista de pontos na copa para pendurar enfeites e luzes."""
    rnd = random.Random(seed)
    malhas = ramos_pinho(rnd, neve)
    mad = E.madeira("tronco", (0.2, 0.1, 0.05), (0.06, 0.03, 0.015), 6, 0.8, 0)
    pontos = []
    if tronco:
        E.torno([(0.075 * alt / 3, base_z), (0.05 * alt / 3, base_z + alt * 0.9), (0.004, base_z + alt * 0.99)], mad, seg=16)
    n_total = 0
    sprig = []
    for k in range(andares):
        t = k / (andares - 1)
        z = base_z + 0.13 * alt + (alt * 0.97 - 0.13 * alt) * t ** 0.94
        R = raio * (1 - t) ** 0.86 + 0.05
        n = int(5 + 10 * (1 - t))
        for i in range(n):
            a = i / n * math.tau + rnd.uniform(-0.28, 0.28) + k * 1.13
            L = R * rnd.uniform(0.84, 1.08)
            ca, sa = math.cos(a), math.sin(a)
            m = int(2 + L * 8 * (1.5 / max(raio, 0.5)) * 0.7) + 2
            cai = rnd.uniform(0.12, 0.3) * (1 - t * 0.6)
            for j in range(m):
                u = (j + 0.5) / m
                zz = z + (-cai * math.sin(u * math.pi * 0.72) + 0.16 * u ** 3) * alt / 3
                lat = rnd.uniform(-0.14, 0.14) * alt / 3
                p = Vector((L * u * ca - lat * sa, L * u * sa + lat * ca, zz))
                d = Vector((ca + rnd.uniform(-0.55, 0.55), sa + rnd.uniform(-0.55, 0.55), rnd.uniform(-0.14, 0.42)))
                s = ramo * rnd.uniform(0.82, 1.12) * (0.6 + 0.4 * (1 - t)) * alt / 3
                sprig.append((p, d, s))
            pontos.append((Vector((L * 0.92 * ca, L * 0.92 * sa, z + (-cai * 0.6 + 0.1) * alt / 3)), a, t))
    E.espalhar_ramos(rnd, malhas, len(sprig), lambda i: sprig[i])
    return pontos


def pontos_copa(alt, raio, n, seed=5, base_z=0.0, recuo=0.86, inicio=0.09, fim=0.95):
    """Pontos sobre o cone da árvore para bolas e luzes, distribuídos por área."""
    rnd = random.Random(seed)
    saida = []
    for i in range(n):
        # mais pontos embaixo, onde o cone é mais largo
        t = 1 - math.sqrt(rnd.uniform((1 - fim) ** 2, (1 - inicio) ** 2))
        z = base_z + alt * (0.1 + 0.88 * t)
        R = (raio * (1 - t) ** 0.88 + 0.03) * recuo * rnd.uniform(0.84, 1.12)
        a = rnd.uniform(0, math.tau)
        saida.append(Vector((R * math.cos(a), R * math.sin(a), z)))
    return saida


# ---------------------------------------------------------------- luzes

def pontos_luz(pontos, raio, cores, forca=9.0, formato="gota"):
    """Muitos LEDs instanciados. `cores` é uma lista de tuplas RGB, usada em ciclo."""
    mats = [E.lampada_mat(f"led{i}", c, forca * 0.17) for i, c in enumerate(cores)]
    bulbos = []
    for m in mats:
        if formato == "gota":
            me = E.torno([(0, -1.0), (0.42, -0.9), (0.62, -0.45), (0.46, 0.32), (0.16, 0.92), (0, 1.1)], m, seg=14).data
        else:
            me = E.esfera(1, (0, 0, 0), m, seg=14, aneis=10).data
        bulbos.append(me)
    for o in [o for o in bpy.context.scene.objects if o.data in bulbos]:
        bpy.data.objects.remove(o)
    rnd = random.Random(9)
    for i, p in enumerate(pontos):
        o = bpy.data.objects.new("led", bulbos[i % len(bulbos)])
        o.location = p
        o.rotation_euler = (rnd.uniform(-1.2, 1.2), rnd.uniform(-1.2, 1.2), 0)
        o.scale = (raio, raio, raio)
        bpy.context.scene.collection.objects.link(o)


def cordao(caminho, n, raio_fio, raio_luz, cores, mat_fio=None, forca=9.0, formato="gota", suavizar=10):
    """Fio com lâmpadas ao longo de um caminho."""
    mat_fio = mat_fio or E.pbr("fio", (0.01, 0.05, 0.03), 0.0, 0.4)
    E.tubo(caminho, raio_fio, mat_fio, suavizar=suavizar, lados=6)
    c = E._catmull(caminho, 12)
    dist = [0.0]
    for a, b in zip(c, c[1:]):
        dist.append(dist[-1] + (b - a).length)
    pts = []
    for i in range(n):
        alvo = dist[-1] * (i + 0.5) / n
        k = next(j for j, d in enumerate(dist) if d >= alvo)
        pts.append(c[k])
    pontos_luz(pts, raio_luz, cores, forca, formato)


QUENTE = [(1.0, 0.56, 0.18)]
CALIDO = [(1.0, 0.6, 0.2), (1.0, 0.48, 0.12)]
COLORIDO = [(1.0, 0.09, 0.1), (0.08, 0.9, 0.26), (0.1, 0.3, 1.0), (1.0, 0.72, 0.1)]


# ---------------------------------------------------------------- pelúcia e fios soltos

def superficie(obj, n, seed=2):
    """Sorteia pontos e normais sobre a malha, proporcional à área."""
    bpy.context.view_layer.update()
    me = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    me.calc_loop_triangles()
    tri = np.zeros(len(me.loop_triangles) * 3, dtype=np.int32)
    me.loop_triangles.foreach_get("vertices", tri)
    tri = tri.reshape(-1, 3)
    co = np.zeros(len(me.vertices) * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    a, b, c = co[tri[:, 0]], co[tri[:, 1]], co[tri[:, 2]]
    nor = np.cross(b - a, c - a)
    area = np.linalg.norm(nor, axis=1)
    nor = nor / np.maximum(area, 1e-9)[:, None]
    r = np.random.default_rng(seed)
    esc = r.choice(len(tri), size=n, p=area / area.sum())
    u, v = r.random(n), r.random(n)
    fora = u + v > 1
    u[fora], v[fora] = 1 - u[fora], 1 - v[fora]
    p = a[esc] + (b[esc] - a[esc]) * u[:, None] + (c[esc] - a[esc]) * v[:, None]
    m = np.array(obj.matrix_world, dtype=np.float32)
    p = p @ m[:3, :3].T + m[:3, 3]
    nn = nor[esc] @ m[:3, :3].T
    nn /= np.maximum(np.linalg.norm(nn, axis=1), 1e-9)[:, None]
    return p, nn


def fios_malha(p, direcao, comp, largura, mat, curva=None, seed=3, nome="fios", cor=None):
    """Malha de fios finos de três lados, em duas seções para poderem curvar."""
    n = len(p)
    r = np.random.default_rng(seed)
    d = direcao / np.maximum(np.linalg.norm(direcao, axis=1), 1e-9)[:, None]
    u = np.cross(d, r.normal(size=(n, 3)))
    u /= np.maximum(np.linalg.norm(u, axis=1), 1e-9)[:, None]
    w = np.cross(d, u)
    L = comp * r.uniform(0.7, 1.15, n)[:, None]
    meio = p + d * L * 0.55
    fim = p + d * L
    if curva is not None:
        fim = fim + curva * L
        meio = meio + curva * L * 0.3
    verts = np.zeros((n * 7, 3), dtype=np.float32)
    for k, a in enumerate((0.0, 2.094, 4.188)):
        off = (u * math.cos(a) + w * math.sin(a)) * largura
        verts[k::7] = p + off
        verts[3 + k::7] = meio + off * 0.62
    verts[6::7] = fim
    b = np.arange(n, dtype=np.int32) * 7
    q = np.stack([b, b + 1, b + 4, b + 3, b + 1, b + 2, b + 5, b + 4, b + 2, b, b + 3, b + 5], 1).reshape(-1, 4)
    t = np.stack([b + 3, b + 4, b + 6, b + 4, b + 5, b + 6, b + 5, b + 3, b + 6], 1).reshape(-1, 3)
    me = bpy.data.meshes.new(nome)
    me.vertices.add(len(verts))
    me.vertices.foreach_set("co", verts.ravel())
    me.polygons.add(len(q) + len(t))
    me.loops.add(len(q) * 4 + len(t) * 3)
    me.polygons.foreach_set("loop_start", np.concatenate([np.arange(len(q), dtype=np.int32) * 4, len(q) * 4 + np.arange(len(t), dtype=np.int32) * 3]))
    me.loops.foreach_set("vertex_index", np.concatenate([q.ravel(), t.ravel()]))
    me.update(calc_edges=True)
    me.shade_smooth()
    me.materials.append(mat)
    if cor is not None:
        at = me.color_attributes.new("cor", "FLOAT_COLOR", "POINT")
        dados = np.concatenate([np.repeat(cor, 7, axis=0), np.ones((n * 7, 1), np.float32)], 1)
        at.data.foreach_set("color", dados.ravel().astype(np.float32))
    return E.obj(me)


def pelo_mat(nome, metal=0.0, rugosidade=0.55):
    """Fios coloridos por atributo: cada fio tem seu próprio tom."""
    m, nt, b = E._novo(nome)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rugosidade
    at = nt.nodes.new("ShaderNodeVertexColor")
    at.layer_name = "cor"
    nt.links.new(at.outputs["Color"], b.inputs["Base Color"])
    return m


def tons(n, cor, var=0.3, seed=1):
    r = np.random.default_rng(seed)
    return np.array(cor, np.float32)[None, :] * r.uniform(1 - var, 1 + var, (n, 1)).astype(np.float32)

def pelagem(alvo, n, comp, largura, mat, cor=None, pente=(0, 0, -0.8), ruido=0.45, seed=4):
    p, nor = superficie(alvo, n, seed)
    r = np.random.default_rng(seed + 1)
    d = nor + np.array(pente, dtype=np.float32) * 0.35 + r.normal(size=nor.shape) * ruido
    curva = np.array(pente, dtype=np.float32)[None, :] * 0.4
    return fios_malha(p, d, comp, largura, mat, curva=curva, seed=seed, cor=tons(n, cor) if cor else None)

def juntar_remalhar(objs, voxel=0.025, suavizar=14, mat=None):
    """Une volumes sobrepostos numa pele só, como massa de modelar."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    m = o.modifiers.new("r", "REMESH")
    m.mode = "VOXEL"
    m.voxel_size = voxel
    s = o.modifiers.new("s", "SMOOTH")
    s.factor = 0.7
    s.iterations = suavizar
    bpy.ops.object.modifier_apply(modifier="r")
    bpy.ops.object.modifier_apply(modifier="s")
    o.data.shade_smooth()
    if mat:
        o.data.materials.clear()
        o.data.materials.append(mat)
    o.select_set(False)
    return o


# ---------------------------------------------------------------- guirlandas

def guirlanda(R=1.0, seed=11, n=None, ramo=0.6, largura=0.3, neve=0.0, agulha=0.15, base=(0.018, 0.085, 0.045), ponta=(0.08, 0.26, 0.13), plano="vertical"):
    """Anel de ramos que correm no mesmo sentido, como uma guirlanda montada à mão."""
    rnd = random.Random(seed)
    malhas = ramos_pinho(rnd, neve, agulha, base, ponta)
    n = n or int(640 * R ** 0.9)

    def pos(i):
        a = i * 0.0812 * math.tau + rnd.uniform(-0.12, 0.12)
        rad = R + rnd.gauss(0, largura * 0.5) * R
        fundo = rnd.uniform(-0.3, 0.2) * R * largura * 2
        radial = Vector((math.cos(a), 0, math.sin(a)))
        tang = Vector((-math.sin(a), 0, math.cos(a)))
        p = radial * rad + Vector((0, fundo, 0))
        d = tang * 1.0 + radial * rnd.uniform(-0.55, 0.55) + Vector((0, rnd.uniform(-0.6, 0.18), 0))
        return p, d, ramo * R * rnd.uniform(0.78, 1.15) if R < 1 else ramo * rnd.uniform(0.78, 1.15)

    E.espalhar_ramos(rnd, malhas, n, pos)
    aro = E.torno([(R * (1 + 0.2 * math.cos(t / 16 * math.tau)), 0.18 * R * math.sin(t / 16 * math.tau)) for t in range(17)], E.pbr("aro", (0.02, 0.03, 0.02), 0, 0.8), seg=64, rot=(math.pi / 2, 0, 0))
    return rnd


def no_anel(R, a, r=1.0, fundo=-0.2):
    return Vector((math.cos(a) * R * r, fundo, math.sin(a) * R * r))


def frutinhas(rnd, centro, n=4, raio=0.045, espalhar=0.06, mat=None):
    mat = mat or E.pbr("fruta", C.vermelho_vivo, 0.0, 0.18, 1.0)
    for _ in range(n):
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized() * espalhar
        E.esfera(raio * rnd.uniform(0.8, 1.1), tuple(Vector(centro) + d), mat, seg=18, aneis=12)


def pinha_malha(mat, n=110, alt=1.3, rx=0.36):
    """Pinha com escamas em espiral. Malha única para instanciar."""
    bv, bf = [], []
    linhas, colunas = 6, 5
    for i in range(n):
        t = (i + 1) / n
        z = alt * t ** 1.08
        rho = rx * math.sin(math.pi * (t * 0.9 + 0.08)) ** 0.75
        ang = i * 2.39996
        tam = (1 - t * 0.66) * 0.27
        incl = math.radians(70 - 44 * t)
        ca, sa = math.cos(ang), math.sin(ang)
        base = len(bv)
        for a in range(linhas):
            u = a / (linhas - 1)
            for b in range(colunas):
                v = b / (colunas - 1) - 0.5
                larg = tam * 0.68 * (1 - 0.7 * u ** 2.2) * (0.72 + 0.28 * math.sin(math.pi * min(1, u + 0.25)))
                saida = tam * u
                al = saida * math.tan(incl) * 0.4 + 0.08 * tam * math.sin(u * 3.1) - 0.17 * tam * abs(v * 2) ** 2
                x0 = rho * 0.72 + saida
                y0 = larg * v
                bv.append((x0 * ca - y0 * sa, x0 * sa + y0 * ca, z + al))
        for a in range(linhas - 1):
            for b in range(colunas - 1):
                q = base + a * colunas + b
                bf.append((q, q + 1, q + colunas + 1, q + colunas))
    return E.malha("pinha", bv, bf, mat)


def mat_pinha():
    return E.madeira("escama", (0.34, 0.16, 0.06), (0.08, 0.03, 0.012), 2.2, 0.55, 0.0)


def pinha(me, loc, esc=0.4, rot=(0, 0, 0)):
    o = E.obj(me, loc, rot, esc)
    s = o.modifiers.new("s", "SOLIDIFY")
    s.thickness = 0.02
    return o


def canela(loc, rot, comp=0.5, r=0.04):
    mat = E.madeira("canela", (0.34, 0.14, 0.05), (0.14, 0.05, 0.02), 14, 0.72, 0)
    return E.torno([(r, -comp / 2), (r, comp / 2)], mat, seg=18, loc=loc, rot=rot)


def sino(alt=1.0, mat=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    mat = mat or E.pbr("sino", C.ouro, 1.0, 0.22)
    perfil = [(0.0, 1.0), (0.14, 0.98), (0.2, 0.86), (0.23, 0.6), (0.3, 0.34), (0.44, 0.1), (0.54, 0.0), (0.52, -0.02), (0.42, 0.06), (0.26, 0.3), (0.0, 0.3)]
    o = E.torno([(r * alt, z * alt) for r, z in perfil], mat, seg=64)
    b = E.esfera(0.09 * alt, (0, 0, -0.04 * alt), mat, seg=20, aneis=14)
    a = E.tubo([(0, 0, 1.0 * alt), (0.08 * alt, 0, 1.08 * alt), (0, 0, 1.16 * alt), (-0.08 * alt, 0, 1.08 * alt)], 0.018 * alt, mat, fechado=True)
    return E.agrupar([o, b, a], loc, rot)


# ---------------------------------------------------------------- roupas

def espelho(meia):
    """Fecha um contorno a partir da metade direita, do centro superior ao centro inferior."""
    return meia + [(-x, y) for x, y in reversed(meia) if abs(x) > 1e-4]


CAMISETA = espelho([(0.0, 0.9), (0.1, 0.92), (0.19, 1.02), (0.25, 1.03), (0.46, 0.96), (0.56, 0.9), (0.82, 0.58), (0.7, 0.44), (0.47, 0.64), (0.44, 0.5), (0.43, 0.0), (0.42, -0.34), (0.2, -0.36), (0.0, -0.36)])
MANGA_LONGA = espelho([(0.0, 0.9), (0.1, 0.92), (0.19, 1.02), (0.25, 1.03), (0.46, 0.96), (0.58, 0.88), (0.74, 0.4), (0.86, -0.22), (0.88, -0.3), (0.72, -0.34), (0.7, -0.27), (0.58, 0.22), (0.47, 0.54), (0.45, 0.4), (0.44, 0.0), (0.44, -0.28), (0.42, -0.33), (0.2, -0.34), (0.0, -0.34)])
CALCA = espelho([(0.0, 0.5), (0.2, 0.5), (0.43, 0.5), (0.46, 0.3), (0.5, 0.0), (0.53, -0.6), (0.56, -1.2), (0.54, -1.26), (0.12, -1.26), (0.09, -1.2), (0.05, -0.4), (0.02, -0.12), (0.0, -0.08)])
VESTIDO = espelho([(0.0, 0.92), (0.1, 0.94), (0.17, 1.03), (0.23, 1.04), (0.4, 0.97), (0.47, 0.92), (0.62, 0.7), (0.5, 0.6), (0.37, 0.72), (0.31, 0.5), (0.26, 0.28), (0.33, 0.16), (0.56, -0.46), (0.72, -1.0), (0.4, -1.06), (0.0, -1.08)])
SHORT = None


def camisa(mat, escala=1.0, loc=(0, 0, 0), rot=(0, 0, 0), seed=3, dobras=0.018, espessura=0.05, gola=None, manga=True):
    """Blusa estendida no plano XZ, com gola e punhos opcionais."""
    contorno = MANGA_LONGA if manga else CAMISETA
    voxel = 0.011
    partes = [E.peca_2d(contorno, mat, espessura, voxel, dobras, seed=seed, bojo=0.42)]
    if gola:
        partes.append(E.tubo([(-0.19, -0.02, 1.02), (-0.1, -0.045, 0.94), (0.0, -0.05, 0.91), (0.1, -0.045, 0.94), (0.19, -0.02, 1.02)], 0.022, gola, lados=12))
    return E.agrupar(partes, loc, rot, escala)


def calca(mat, escala=1.0, loc=(0, 0, 0), rot=(0, 0, 0), seed=5, cos=None):
    partes = [E.peca_2d(CALCA, mat, 0.05, 0.011, 0.018, seed=seed)]
    if cos:
        partes.append(E.tubo([(-0.43, -0.052, 0.44), (0, -0.07, 0.44), (0.43, -0.052, 0.44)], 0.04, cos, lados=10, suavizar=6))
    return E.agrupar(partes, loc, rot, escala)


def meia(mat, punho=None, escala=1.0, loc=(0, 0, 0), rot=(0, 0, 0), seed=7):
    """Meia estendida de perfil."""
    forma = [(-0.2, 0.9), (0.2, 0.9), (0.21, 0.1), (0.3, -0.12), (0.62, -0.28), (0.72, -0.42), (0.62, -0.56), (0.1, -0.56), (-0.14, -0.46), (-0.22, -0.2), (-0.2, 0.1)]
    p = [E.peca_2d(forma, mat, 0.05, 0.012, 0.01, seed=seed, bojo=0.3)]
    if punho:
        p.append(E.peca_2d([(-0.24, 0.98), (-0.12, 1.0), (0.12, 1.0), (0.24, 0.98), (0.25, 0.84), (0.24, 0.7), (0.12, 0.68), (-0.12, 0.68), (-0.24, 0.7), (-0.25, 0.84)], punho, 0.075, 0.012, 0.0, loc=(0, -0.05, 0), bojo=0.34))
    return E.agrupar(p, loc, rot, escala)


def cabide(escala=1.0, loc=(0, 0, 0)):
    mad = E.madeira("cabide", (0.5, 0.28, 0.13), (0.24, 0.11, 0.05), 5, 0.4, 0.4)
    metal = E.pbr("gancho", C.ouro, 1.0, 0.24)
    a = E.tubo([(-0.56, 0, 0.9), (-0.3, 0, 1.0), (0, 0, 1.06), (0.3, 0, 1.0), (0.56, 0, 0.9)], 0.028, mad, lados=14)
    g = E.tubo([(0, 0, 1.06), (0, 0, 1.18), (0.03, 0, 1.26), (0.09, 0, 1.31), (0.04, 0, 1.38), (-0.04, 0, 1.33)], 0.009, metal, lados=10)
    return E.agrupar([a, g], loc, (0, 0, 0), escala)


def botoes(n, x, z0, z1, raio=0.024, y=-0.09, mat=None):
    mat = mat or E.pbr("botao", C.ouro, 1.0, 0.3)
    for i in range(n):
        z = z0 + (z1 - z0) * i / max(1, n - 1)
        E.torno([(0, y - 0.01), (raio * 0.8, y - 0.008), (raio, y - 0.004), (raio, y + 0.004), (0, y + 0.004)], mat, seg=24, loc=(x, 0, z))


# ---------------------------------------------------------------- presépio

def figura(alt, manto, veste=None, cabeca=None, veu=False, coroa=False, cajado=False, presente=None, loc=(0, 0, 0), giro=0.0, seg=64, barba=None):
    """Figura torneada de presépio: corpo, braços em prece, cabeça levemente inclinada."""
    cabeca = cabeca or E.pbr("rosto", (0.6, 0.36, 0.22), 0, 0.5)
    corpo = [(0.31, 0.0), (0.3, 0.02), (0.25, 0.22), (0.2, 0.42), (0.175, 0.56), (0.17, 0.64), (0.135, 0.72), (0.07, 0.76), (0.0, 0.77)]
    p = [E.torno([(r * alt, z * alt) for r, z in corpo], manto, seg=seg)]
    cx, cz = -0.018 * alt, 0.875 * alt
    p.append(E.esfera(0.11 * alt, (0, cx, cz), cabeca, seg=36, aneis=24, esc=(1, 1, 1.1)))
    braco = lambda s: E.tubo([(s * 0.155 * alt, -0.02 * alt, 0.67 * alt), (s * 0.2 * alt, -0.12 * alt, 0.52 * alt), (s * 0.05 * alt, -0.22 * alt, 0.5 * alt)], 0.05 * alt, manto, lados=14, raios=lambda t: (0.055 - 0.018 * t) * alt)
    p += [braco(-1), braco(1)]
    if presente:
        p.append(E.bloco(0.13 * alt, 0.11 * alt, 0.11 * alt, presente, (0, -0.27 * alt, 0.53 * alt), raio=0.008 * alt))
    else:
        p.append(E.esfera(0.042 * alt, (0, -0.235 * alt, 0.515 * alt), cabeca, seg=16, aneis=12, esc=(1, 0.8, 1.2)))
    if veste:
        cinto = [(0.205 * alt + 0.02 * alt * math.cos(i / 8 * math.tau), 0.41 * alt + 0.02 * alt * math.sin(i / 8 * math.tau)) for i in range(9)]
        p.append(E.torno(cinto, veste, seg=48))
        barra = [(0.312 * alt, 0.0), (0.316 * alt, 0.02 * alt), (0.3 * alt, 0.075 * alt), (0.292 * alt, 0.075 * alt)]
        p.append(E.torno(barra, veste, seg=seg))
    if veu:
        v = [(0.0, 1.005), (0.06, 0.995), (0.115, 0.95), (0.14, 0.86), (0.15, 0.76), (0.165, 0.68), (0.14, 0.68), (0.12, 0.8), (0.1, 0.92), (0.0, 0.97)]
        p.append(E.torno([(r * alt, z * alt) for r, z in v], manto, seg=36, loc=(0, 0.018 * alt, 0)))
    if barba:
        p.append(E.esfera(0.07 * alt, (0, cx - 0.06 * alt, cz - 0.09 * alt), barba, seg=20, aneis=14, esc=(0.95, 0.7, 1.15)))
    if coroa:
        ouro = E.pbr("coroa", C.ouro, 1.0, 0.22)
        anel = [(0.086, 0.965), (0.1, 0.99), (0.094, 1.03), (0.082, 1.03), (0.08, 0.985), (0.086, 0.965)]
        p.append(E.torno([(r * alt, z * alt) for r, z in anel], ouro, seg=32))
        for i in range(6):
            a = i / 6 * math.tau
            p.append(E.esfera(0.017 * alt, (math.cos(a) * 0.092 * alt, math.sin(a) * 0.092 * alt, 1.045 * alt), ouro, seg=12, aneis=8))
    if cajado:
        mad = E.madeira("cajado", (0.3, 0.15, 0.06), (0.1, 0.05, 0.02), 9, 0.6, 0)
        x = 0.27 * alt
        p.append(E.tubo([(x, -0.08 * alt, 0.0), (x, -0.08 * alt, 0.95 * alt), (x + 0.03 * alt, -0.08 * alt, 1.08 * alt), (x + 0.11 * alt, -0.08 * alt, 1.09 * alt), (x + 0.13 * alt, -0.08 * alt, 1.01 * alt)], 0.014 * alt, mad, lados=8))
    return E.agrupar(p, loc, (0, 0, giro))

def manjedoura(esc=1.0, mad=None, palha=None, loc=(0, 0, 0), menino=None, luz=False):
    mad = mad or E.madeira("mad", (0.32, 0.16, 0.07), (0.1, 0.05, 0.02), 7, 0.6, 0)
    palha = palha or E.pbr("palha", (0.62, 0.42, 0.14), 0, 0.7)
    p = []
    for lado in (-1, 1):
        p.append(E.bloco(0.5, 0.04, 0.03, mad, (0, lado * 0.17, 0.26), raio=0.006))
        for x in (-0.22, 0.22):
            p.append(E.bloco(0.03, 0.03, 0.34, mad, (x, lado * 0.09, 0.14), (lado * 0.5, 0, 0), raio=0.005))
    p.append(E.esfera(0.22, (0, 0, 0.28), palha, seg=24, aneis=14, esc=(1.2, 0.72, 0.26)))
    faixa = menino or E.pbr("faixa", C.marfim, 0, 0.6)
    p.append(E.esfera(0.09, (0, 0, 0.36), faixa, seg=24, aneis=16, esc=(1.7, 0.84, 0.72)))
    p.append(E.esfera(0.052, (0.17, 0, 0.385), E.pbr("rosto2", (0.6, 0.36, 0.22), 0, 0.5), seg=20, aneis=14))
    if luz:
        p.append(E.esfera(0.13, (0, 0, 0.4), E.luz_mat("halo", (1, 0.76, 0.42), 1.6), seg=20, aneis=14, esc=(1.8, 1, 0.4)))
    return E.agrupar(p, loc, (0, 0, 0), esc)


def estabulo(l=2.4, a=1.6, p=1.0, mad=None, palha=None, loc=(0, 0, 0)):
    """Estábulo de troncos com telhado de palha."""
    mad = mad or E.madeira("viga", (0.3, 0.15, 0.06), (0.09, 0.04, 0.02), 6, 0.62, 0)
    palha = palha or E.palha_mat("telhado")
    pecas = []
    for x in (-l / 2, l / 2):
        for y in (-p / 2, p / 2):
            pecas.append(E.torno([(0.05, 0), (0.044, a if y < 0 else a * 1.16)], mad, seg=12, loc=(x, y, 0)))
    for y, z in ((-p / 2, a), (p / 2, a * 1.16)):
        pecas.append(E.bloco(l + 0.32, 0.09, 0.09, mad, (0, y, z), raio=0.012))
    # tábuas do fundo
    rnd = random.Random(4)
    for i in range(int(l / 0.2)):
        x = -l / 2 + (i + 0.5) * 0.2
        h = a * 1.12 * rnd.uniform(0.97, 1.0)
        pecas.append(E.bloco(0.18, 0.03, h, mad, (x, p / 2, h / 2), (0, rnd.uniform(-0.012, 0.012), 0), raio=0.006))
    # telhado inclinado em fiadas de palha
    inclin = math.atan2(a * 0.16, p)
    for k in range(9):
        y = -p / 2 - 0.2 + k * (p + 0.4) / 8
        z = a + 0.1 + (y + p / 2) * math.tan(inclin)
        pecas.append(E.bloco(l + 0.54 + 0.05 * (k % 2), (p + 0.5) / 6.4, 0.12, palha, (0.02 * (k % 3), y, z - 0.03 * (k % 2)), (inclin + 0.14, 0, 0), raio=0.05))
    return E.agrupar(pecas, loc)


def boi(esc=1.0, cor=(0.34, 0.2, 0.1), loc=(0, 0, 0), giro=0.0, burro=False):
    """Animal de presépio em volumes simples."""
    mat = E.pbr("animal", cor, 0, 0.62)
    o = []
    o.append(E.esfera(0.32, (0, 0, 0.42), mat, seg=32, aneis=22, esc=(1.5, 0.82, 0.86)))
    o.append(E.esfera(0.17, (0.52, 0, 0.62), mat, seg=28, aneis=18, esc=(1.12, 0.84, 0.92)))
    o.append(E.esfera(0.09, (0.68, 0, 0.55), mat, seg=18, aneis=12, esc=(1.1, 0.95, 0.8)))
    for x in (-0.3, 0.3):
        for y in (-0.15, 0.15):
            o.append(E.torno([(0.058, 0), (0.05, 0.34), (0.07, 0.42)], mat, seg=12, loc=(x, y, 0)))
    if burro:
        for y in (-0.08, 0.08):
            o.append(E.esfera(0.05, (0.46, y, 0.84), mat, seg=12, aneis=10, esc=(0.6, 0.7, 2.0)))
    else:
        chifre = E.pbr("chifre", C.marfim, 0, 0.4)
        for y in (-1, 1):
            o.append(E.tubo([(0.5, y * 0.1, 0.74), (0.5, y * 0.2, 0.8), (0.52, y * 0.22, 0.9)], 0.02, chifre, lados=8, raios=lambda t: 0.024 * (1 - t * 0.9)))
    return E.agrupar(o, loc, (0, 0, giro), esc)


def ovelha(esc=1.0, loc=(0, 0, 0), giro=0.0, mat=None):
    la = mat or E.pbr("la", (0.82, 0.8, 0.74), 0, 0.85)
    esc_cabeca = E.pbr("cara", (0.09, 0.07, 0.06), 0, 0.6)
    rnd = random.Random(3)
    o = []
    for i in range(22):
        o.append(E.esfera(rnd.uniform(0.11, 0.16), (rnd.uniform(-0.24, 0.24), rnd.uniform(-0.13, 0.13), 0.32 + rnd.uniform(-0.1, 0.1)), la, seg=14, aneis=10))
    o.append(E.esfera(0.095, (0.33, 0, 0.42), esc_cabeca, seg=18, aneis=12, esc=(1.2, 0.86, 0.9)))
    for x in (-0.16, 0.16):
        for y in (-0.08, 0.08):
            o.append(E.torno([(0.03, 0), (0.025, 0.2)], esc_cabeca, seg=8, loc=(x, y, 0)))
    return E.agrupar(o, loc, (0, 0, giro), esc)


def casinha(l=0.7, p=0.6, a=0.6, parede=None, telhado=None, luz=True, loc=(0, 0, 0), giro=0.0, sem_janela=False):
    """Casa baixa de Belém, de teto plano ou abobadado, com janela acesa."""
    parede = parede or E.pbr("adobe", (0.72, 0.56, 0.38), 0, 0.84)
    o = [E.bloco(l, p, a, parede, (0, 0, a / 2), raio=0.02)]
    o.append(E.bloco(l + 0.04, p + 0.04, 0.05, parede, (0, 0, a + 0.02), raio=0.015))
    if telhado:
        o.append(E.esfera(min(l, p) * 0.46, (0, 0, a + 0.03), telhado, seg=32, aneis=18, esc=(1, 1, 0.8)))
    jan = E.luz_mat("janela", (1.0, 0.64, 0.24), 6.0) if luz else E.pbr("porta", (0.08, 0.05, 0.03), 0, 0.7)
    if not sem_janela:
        o.append(E.bloco(0.13, 0.015, 0.2, jan, (-l * 0.2, -p / 2 - 0.004, a * 0.42)))
        o.append(E.bloco(0.1, 0.015, 0.14, jan, (l * 0.2, -p / 2 - 0.004, a * 0.58)))
    return E.agrupar(o, loc, (0, 0, giro))
