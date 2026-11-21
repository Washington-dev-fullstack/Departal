# Estúdio 3D da Departal: cena, luz, materiais e peças básicas.
# Tudo aqui é usado por produtos.py. Roda dentro do Python do Blender.
import math
import os
import random

import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(AQUI, "tex")


# ---------------------------------------------------------------- cena

def cena(res=900, amostras=72, altura=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = amostras
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.025
    s.cycles.use_denoising = True
    s.cycles.denoiser = "OPENIMAGEDENOISE"
    s.cycles.max_bounces = 7
    s.cycles.diffuse_bounces = 3
    s.cycles.glossy_bounces = 4
    s.cycles.transmission_bounces = 8
    s.cycles.transparent_max_bounces = 8
    s.cycles.caustics_reflective = False
    s.cycles.caustics_refractive = False
    s.cycles.sample_clamp_indirect = 8
    s.render.resolution_x = res
    s.render.resolution_y = altura or res
    s.render.film_transparent = True
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"
    s.view_settings.view_transform = "Khronos PBR Neutral"
    s.view_settings.look = "None"
    s.view_settings.exposure = 0.0
    _ambiente(s)
    return s


def _ambiente(s):
    """Mapa de reflexos pintado à mão: softboxes quentes e pontos de luz da vitrine."""
    w, h = 1024, 512
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    lon, lat = np.meshgrid(lon, lat)
    img = np.zeros((h, w, 3), dtype=np.float32)
    ceu = np.clip((lat + 12) / 60, 0, 1)[..., None]
    img += np.array([0.42, 0.3, 0.2], np.float32) * (1 - ceu) + np.array([0.6, 0.62, 0.54], np.float32) * ceu

    def caixa(cx, cy, lx, ly, cor, forca, suave=7.0):
        dx = np.abs(((lon - cx + 180) % 360) - 180)
        dy = np.abs(lat - cy)
        fx = np.clip((lx - dx) / suave, 0, 1)
        fy = np.clip((ly - dy) / suave, 0, 1)
        m = (fx * fx * (3 - 2 * fx)) * (fy * fy * (3 - 2 * fy))
        img[..., 0] += m * cor[0] * forca
        img[..., 1] += m * cor[1] * forca
        img[..., 2] += m * cor[2] * forca

    caixa(-52, 34, 36, 24, (1.0, 0.82, 0.6), 9.0)
    caixa(0, 84, 180, 26, (1.0, 0.9, 0.76), 2.6, 16)
    caixa(70, 22, 15, 34, (1.0, 0.56, 0.3), 5.2)
    caixa(158, 26, 30, 16, (0.46, 0.92, 0.72), 3.2)
    caixa(-140, 12, 12, 26, (1.0, 0.2, 0.16), 2.6)
    caixa(10, -46, 60, 8, (1.0, 0.7, 0.42), 1.1, 12)
    rnd = random.Random(25)
    for _ in range(70):
        c = rnd.choice([(1, 0.72, 0.36), (1, 0.82, 0.55), (1, 0.32, 0.22), (0.6, 1, 0.8)])
        caixa(rnd.uniform(-180, 180), rnd.uniform(-20, 60), 1.8, 1.8, c, rnd.uniform(6, 20), 2.0)

    im = bpy.data.images.new("reflexos", w, h, float_buffer=True)
    rgba = np.dstack([img[::-1], np.ones((h, w, 1), np.float32)]).ravel()
    im.pixels.foreach_set(rgba)
    im.colorspace_settings.name = "Linear Rec.709"
    mundo = bpy.data.worlds.new("mundo")
    s.world = mundo
    mundo.use_nodes = True
    nt = mundo.node_tree
    tx = nt.nodes.new("ShaderNodeTexEnvironment")
    tx.image = im
    nt.links.new(tx.outputs[0], nt.nodes["Background"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = 1.15


def _colecao():
    return bpy.context.scene.collection


def objetos_produto():
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.get("apoio")]


def limites():
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    bpy.context.view_layer.update()
    for o in objetos_produto():
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, p))
            hi = Vector(map(max, hi, p))
    return lo, hi


def estudio(azim=-16, elev=11, lente=95, margem=0.1, sombra=True, parede=False, luz=1.0, topo=False):
    """Enquadra o produto automaticamente e monta luz proporcional ao tamanho dele."""
    s = bpy.context.scene
    lo, hi = limites()
    centro = (lo + hi) * 0.5
    raio = (hi - lo).length * 0.5

    if topo:
        elev = 74
    a, e = math.radians(azim), math.radians(elev)
    direcao = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))

    cam = bpy.data.cameras.new("cam")
    cam.lens = lente
    cam.sensor_width = 36
    cam.sensor_fit = "HORIZONTAL"
    co = bpy.data.objects.new("cam", cam)
    _colecao().objects.link(co)
    s.camera = co

    # distância e centro exatos para o produto caber no quadro com a margem pedida
    giro = direcao.to_track_quat("Z", "Y")
    dir_x, dir_y = giro @ Vector((1, 0, 0)), giro @ Vector((0, 1, 0))
    res_x, res_y = s.render.resolution_x, s.render.resolution_y
    tan_x = 18.0 / lente
    tan_y = tan_x * res_y / res_x
    cantos = []
    for o in objetos_produto():
        cantos += [o.matrix_world @ Vector(c) for c in o.bound_box]
    alvo = centro.copy()
    dist = raio * 6
    for _ in range(5):
        dist = 0.0
        for c in cantos:
            r = c - alvo
            x, y, z = abs(r.dot(dir_x)), abs(r.dot(dir_y)), r.dot(direcao)
            dist = max(dist, z + x / (tan_x * (1 - margem)), z + y / (tan_y * (1 - margem)))
        xs = [(c - alvo).dot(dir_x) / (dist - (c - alvo).dot(direcao)) for c in cantos]
        ys = [(c - alvo).dot(dir_y) / (dist - (c - alvo).dot(direcao)) for c in cantos]
        alvo += dir_x * ((min(xs) + max(xs)) * 0.5 * dist) + dir_y * ((min(ys) + max(ys)) * 0.5 * dist)
    co.location = alvo + direcao * dist
    co.rotation_euler = giro.to_euler()
    bpy.context.view_layer.update()

    if sombra:
        chao = bpy.data.meshes.new("chao")
        tam = raio * 14
        chao.from_pydata([(-tam, -tam, 0), (tam, -tam, 0), (tam, tam, 0), (-tam, tam, 0)], [], [(0, 1, 2, 3)])
        ob = bpy.data.objects.new("chao", chao)
        ob.location = (centro.x, centro.y, lo.z)
        ob.is_shadow_catcher = True
        ob.visible_glossy = False
        ob.visible_transmission = False
        ob.visible_diffuse = False
        ob["apoio"] = 1
        _colecao().objects.link(ob)
    if parede:
        mp = bpy.data.meshes.new("parede")
        tam = raio * 14
        mp.from_pydata([(-tam, 0, -tam), (tam, 0, -tam), (tam, 0, tam), (-tam, 0, tam)], [], [(0, 1, 2, 3)])
        ob = bpy.data.objects.new("parede", mp)
        ob.location = (centro.x, hi.y + 0.02 * raio, centro.z)
        ob.is_shadow_catcher = True
        ob.visible_glossy = False
        ob.visible_transmission = False
        ob.visible_diffuse = False
        ob["apoio"] = 1
        _colecao().objects.link(ob)

    def lampada(pos, tam, forca, cor):
        l = bpy.data.lights.new("luz", "AREA")
        l.size = tam * raio
        l.energy = forca * 5.5 * raio * raio * luz
        l.color = cor
        o = bpy.data.objects.new("luz", l)
        o.location = centro + Vector(pos) * raio
        o.rotation_euler = (centro - o.location).to_track_quat("-Z", "Y").to_euler()
        _colecao().objects.link(o)

    # luz principal quente, recorte verde-água atrás e um toque vermelho de lado
    lampada((-2.4, -3.0, 3.2), 3.2, 46, (1.0, 0.86, 0.68))
    lampada((3.0, 1.8, 2.6), 2.0, 40, (0.62, 1.0, 0.82))
    lampada((3.2, -1.8, 0.4), 1.6, 18, (1.0, 0.42, 0.26))


def render(caminho):
    s = bpy.context.scene
    s.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- materiais

def _novo(nome):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    return m, m.node_tree, m.node_tree.nodes["Principled BSDF"]


def pbr(nome, cor, metal=0.0, rugosidade=0.4, verniz=0.0, **extra):
    m, _, b = _novo(nome)
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rugosidade
    b.inputs["Coat Weight"].default_value = verniz
    b.inputs["Coat Roughness"].default_value = 0.06
    for chave, valor in extra.items():
        b.inputs[chave.replace("_", " ")].default_value = valor
    return m


def luz_mat(nome, cor, forca=8.0):
    m, _, b = _novo(nome)
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Emission Color"].default_value = (*cor, 1)
    b.inputs["Emission Strength"].default_value = forca
    return m


def lampada_mat(nome, cor, forca=9.0):
    """Bulbo de vidro aceso: núcleo brilhante com borda de vidro."""
    m, nt, b = _novo(nome)
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Roughness"].default_value = 0.15
    b.inputs["Coat Weight"].default_value = 1.0
    fres = nt.nodes.new("ShaderNodeFresnel")
    fres.inputs["IOR"].default_value = 1.2
    calc = nt.nodes.new("ShaderNodeMath")
    calc.operation = "SUBTRACT"
    calc.inputs[0].default_value = 1.0
    nt.links.new(fres.outputs[0], calc.inputs[1])
    mult = nt.nodes.new("ShaderNodeMath")
    mult.operation = "MULTIPLY"
    mult.inputs[1].default_value = forca
    nt.links.new(calc.outputs[0], mult.inputs[0])
    b.inputs["Emission Color"].default_value = (*cor, 1)
    nt.links.new(mult.outputs[0], b.inputs["Emission Strength"])
    return m


def vidro(nome="vidro", cor=(1, 1, 1), rugosidade=0.02, ior=1.5):
    m, _, b = _novo(nome)
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Roughness"].default_value = rugosidade
    b.inputs["IOR"].default_value = ior
    b.inputs["Transmission Weight"].default_value = 1.0
    return m


def glitter(nome, cor, escala=420.0, forca=0.34, rugosidade=0.32):
    m, nt, b = _novo(nome)
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = rugosidade
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = 0.04
    co = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = escala
    nt.links.new(co.outputs["Object"], vor.inputs["Vector"])
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = (0.5, 0.5, 0.5)
    nt.links.new(vor.outputs["Color"], sub.inputs[0])
    esc = nt.nodes.new("ShaderNodeVectorMath")
    esc.operation = "SCALE"
    esc.inputs["Scale"].default_value = forca * 2
    nt.links.new(sub.outputs[0], esc.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    soma = nt.nodes.new("ShaderNodeVectorMath")
    soma.operation = "ADD"
    nt.links.new(geo.outputs["Normal"], soma.inputs[0])
    nt.links.new(esc.outputs[0], soma.inputs[1])
    norm = nt.nodes.new("ShaderNodeVectorMath")
    norm.operation = "NORMALIZE"
    nt.links.new(soma.outputs[0], norm.inputs[0])
    nt.links.new(norm.outputs[0], b.inputs["Normal"])
    return m


def listras(nome, cor_a, cor_b, faixas=8.0, metal=1.0, rugosidade_a=0.16, rugosidade_b=0.42, eixo="z", onda=0.0):
    """Listras de bola de Natal: uma faixa polida e outra acetinada."""
    m, nt, b = _novo(nome)
    b.inputs["Metallic"].default_value = metal
    co = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(co.outputs["Object"], sep.inputs[0])
    arc = nt.nodes.new("ShaderNodeMath")
    arc.operation = "SINE"
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = faixas
    if onda:
        som = nt.nodes.new("ShaderNodeMath")
        som.operation = "ADD"
        giro = nt.nodes.new("ShaderNodeMath")
        giro.operation = "MULTIPLY"
        giro.inputs[1].default_value = onda
        nt.links.new(sep.outputs["X"], giro.inputs[0])
        nt.links.new(sep.outputs[eixo.upper()], som.inputs[0])
        nt.links.new(giro.outputs[0], som.inputs[1])
        nt.links.new(som.outputs[0], mul.inputs[0])
    else:
        nt.links.new(sep.outputs[eixo.upper()], mul.inputs[0])
    nt.links.new(mul.outputs[0], arc.inputs[0])
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].position = 0.46
    rampa.color_ramp.elements[1].position = 0.54
    arc2 = nt.nodes.new("ShaderNodeMapRange")
    arc2.inputs["From Min"].default_value = -1
    arc2.inputs["From Max"].default_value = 1
    nt.links.new(arc.outputs[0], arc2.inputs["Value"])
    nt.links.new(arc2.outputs[0], rampa.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*cor_a, 1)
    mix.inputs["B"].default_value = (*cor_b, 1)
    nt.links.new(rampa.outputs[0], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    rg = nt.nodes.new("ShaderNodeMapRange")
    rg.inputs["To Min"].default_value = rugosidade_a
    rg.inputs["To Max"].default_value = rugosidade_b
    nt.links.new(rampa.outputs[0], rg.inputs["Value"])
    nt.links.new(rg.outputs[0], b.inputs["Roughness"])
    return m


def imagem_mat(nome, arquivo, rugosidade=0.7, escala=1.0, metal=0.0, verniz=0.0, relevo=0.0, deslocar=(0.5, 0.5, 0), projecao="FLAT", plano="xy", brilho=0.0):
    """Imagem de tools/blender/tex presa às coordenadas do objeto: as peças são remalhadas e não têm UV."""
    m, nt, b = _novo(nome)
    b.inputs["Roughness"].default_value = rugosidade
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = verniz
    b.inputs["Sheen Weight"].default_value = brilho
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(TEX, arquivo), check_existing=True)
    tx.extension = "REPEAT"
    tx.projection = projecao
    co = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = escala if hasattr(escala, "__len__") else (escala, escala, escala)
    mp.inputs["Location"].default_value = deslocar
    if plano == "xz":
        mp.inputs["Rotation"].default_value = (-math.pi / 2, 0, 0)
    nt.links.new(co.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs[0], tx.inputs["Vector"])
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if relevo:
        ruido = nt.nodes.new("ShaderNodeTexNoise")
        ruido.inputs["Scale"].default_value = 700
        rel = nt.nodes.new("ShaderNodeBump")
        rel.inputs["Strength"].default_value = relevo
        nt.links.new(co.outputs["Object"], ruido.inputs["Vector"])
        nt.links.new(ruido.outputs[0], rel.inputs["Height"])
        nt.links.new(rel.outputs[0], b.inputs["Normal"])
    return m


def tecido(nome, cor, rugosidade=0.62, relevo=0.25, brilho=0.7):
    m, nt, b = _novo(nome)
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Roughness"].default_value = rugosidade
    b.inputs["Sheen Weight"].default_value = brilho
    b.inputs["Sheen Roughness"].default_value = 0.4
    co = nt.nodes.new("ShaderNodeTexCoord")
    ruido = nt.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value = 420
    ruido.inputs["Detail"].default_value = 4
    rel = nt.nodes.new("ShaderNodeBump")
    rel.inputs["Strength"].default_value = relevo
    nt.links.new(co.outputs["Object"], ruido.inputs["Vector"])
    nt.links.new(ruido.outputs[0], rel.inputs["Height"])
    nt.links.new(rel.outputs[0], b.inputs["Normal"])
    return m


def cetim(nome, cor):
    m, nt, b = _novo(nome)
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Roughness"].default_value = 0.34
    b.inputs["Anisotropic"].default_value = 0.72
    b.inputs["Sheen Weight"].default_value = 0.35
    b.inputs["Specular IOR Level"].default_value = 0.62
    return m


def madeira(nome="madeira", clara=(0.42, 0.23, 0.1), escura=(0.14, 0.06, 0.025), escala=3.0, rugosidade=0.46, verniz=0.25):
    m, nt, b = _novo(nome)
    b.inputs["Roughness"].default_value = rugosidade
    b.inputs["Coat Weight"].default_value = verniz
    co = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (escala * 0.35, escala * 3.2, escala * 3.2)
    nt.links.new(co.outputs["Object"], mp.inputs["Vector"])
    onda = nt.nodes.new("ShaderNodeTexWave")
    onda.wave_type = "RINGS"
    onda.inputs["Scale"].default_value = 3.6
    onda.inputs["Distortion"].default_value = 4.5
    onda.inputs["Detail"].default_value = 3.0
    onda.inputs["Detail Scale"].default_value = 1.6
    nt.links.new(mp.outputs[0], onda.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*escura, 1)
    mix.inputs["B"].default_value = (*clara, 1)
    nt.links.new(onda.outputs["Fac"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    rel = nt.nodes.new("ShaderNodeBump")
    rel.inputs["Strength"].default_value = 0.15
    nt.links.new(onda.outputs["Fac"], rel.inputs["Height"])
    nt.links.new(rel.outputs[0], b.inputs["Normal"])
    return m


def barro(nome="barro", cor=(0.5, 0.2, 0.09), rugosidade=0.82):
    m, nt, b = _novo(nome)
    b.inputs["Roughness"].default_value = rugosidade
    co = nt.nodes.new("ShaderNodeTexCoord")
    ruido = nt.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value = 26
    ruido.inputs["Detail"].default_value = 7
    nt.links.new(co.outputs["Object"], ruido.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (cor[0] * 0.62, cor[1] * 0.55, cor[2] * 0.5, 1)
    mix.inputs["B"].default_value = (*cor, 1)
    nt.links.new(ruido.outputs[0], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    rel = nt.nodes.new("ShaderNodeBump")
    rel.inputs["Strength"].default_value = 0.5
    nt.links.new(ruido.outputs[0], rel.inputs["Height"])
    nt.links.new(rel.outputs[0], b.inputs["Normal"])
    return m


def palha_mat(nome="palha", cor=(0.5, 0.33, 0.1), escura=(0.16, 0.09, 0.03)):
    """Fibras longas: ruído esticado ao longo do eixo Y do objeto."""
    m, nt, b = _novo(nome)
    b.inputs["Roughness"].default_value = 0.72
    co = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (46, 3.4, 46)
    nt.links.new(co.outputs["Object"], mp.inputs["Vector"])
    ruido = nt.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value = 1.6
    ruido.inputs["Detail"].default_value = 6
    nt.links.new(mp.outputs[0], ruido.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*escura, 1)
    mix.inputs["B"].default_value = (*cor, 1)
    faixa = nt.nodes.new("ShaderNodeMapRange")
    faixa.inputs["From Min"].default_value = 0.36
    faixa.inputs["From Max"].default_value = 0.66
    nt.links.new(ruido.outputs[0], faixa.inputs["Value"])
    nt.links.new(faixa.outputs[0], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    rel = nt.nodes.new("ShaderNodeBump")
    rel.inputs["Strength"].default_value = 0.9
    nt.links.new(ruido.outputs[0], rel.inputs["Height"])
    nt.links.new(rel.outputs[0], b.inputs["Normal"])
    return m


def neve_mat():
    m, nt, b = _novo("neve")
    b.inputs["Base Color"].default_value = (0.92, 0.95, 1.0, 1)
    b.inputs["Roughness"].default_value = 0.5
    b.inputs["Subsurface Weight"].default_value = 0.8
    b.inputs["Subsurface Radius"].default_value = (0.12, 0.14, 0.2)
    b.inputs["Subsurface Scale"].default_value = 0.1
    co = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 260
    nt.links.new(co.outputs["Object"], vor.inputs["Vector"])
    rel = nt.nodes.new("ShaderNodeBump")
    rel.inputs["Strength"].default_value = 0.5
    nt.links.new(vor.outputs["Distance"], rel.inputs["Height"])
    nt.links.new(rel.outputs[0], b.inputs["Normal"])
    return m


def pinho_mat(nome="pinho", base=(0.018, 0.085, 0.045), ponta=(0.08, 0.26, 0.13), neve=0.0):
    """Agulhas: varia o verde entre ramos e clareia nas pontas. Com neve, as pontas ficam brancas."""
    m, nt, b = _novo(nome)
    b.inputs["Roughness"].default_value = 0.42
    b.inputs["Specular IOR Level"].default_value = 0.55
    info = nt.nodes.new("ShaderNodeObjectInfo")
    attr = nt.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "ponta"
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*base, 1)
    mix.inputs["B"].default_value = (*ponta, 1)
    nt.links.new(attr.outputs["Color"], mix.inputs["Factor"])
    var = nt.nodes.new("ShaderNodeHueSaturation")
    faixa = nt.nodes.new("ShaderNodeMapRange")
    faixa.inputs["To Min"].default_value = 0.47
    faixa.inputs["To Max"].default_value = 0.53
    nt.links.new(info.outputs["Random"], faixa.inputs["Value"])
    nt.links.new(faixa.outputs[0], var.inputs["Hue"])
    nt.links.new(mix.outputs["Result"], var.inputs["Color"])
    saida = var.outputs["Color"]
    if neve > 0:
        ruido = nt.nodes.new("ShaderNodeTexNoise")
        ruido.inputs["Scale"].default_value = 3.4
        ruido.inputs["Detail"].default_value = 5
        co = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(co.outputs["Object"], ruido.inputs["Vector"])
        mult = nt.nodes.new("ShaderNodeMath")
        mult.operation = "MULTIPLY"
        nt.links.new(attr.outputs["Color"], mult.inputs[0])
        nt.links.new(ruido.outputs[0], mult.inputs[1])
        rampa = nt.nodes.new("ShaderNodeMapRange")
        rampa.inputs["From Min"].default_value = 0.36 - neve * 0.2
        rampa.inputs["From Max"].default_value = 0.6 - neve * 0.2
        nt.links.new(mult.outputs[0], rampa.inputs["Value"])
        branco = nt.nodes.new("ShaderNodeMix")
        branco.data_type = "RGBA"
        branco.inputs["B"].default_value = (0.9, 0.93, 0.96, 1)
        nt.links.new(rampa.outputs[0], branco.inputs["Factor"])
        nt.links.new(saida, branco.inputs["A"])
        saida = branco.outputs["Result"]
    nt.links.new(saida, b.inputs["Base Color"])
    return m


class Cores:
    """Paleta da loja: mesmos materiais em todos os produtos."""
    vermelho = (0.46, 0.008, 0.02)
    vermelho_vivo = (0.62, 0.012, 0.03)
    vinho = (0.17, 0.006, 0.018)
    verde = (0.012, 0.13, 0.06)
    verde_escuro = (0.006, 0.05, 0.028)
    ouro = (0.86, 0.56, 0.2)
    ouro_claro = (0.95, 0.74, 0.42)
    prata = (0.82, 0.84, 0.86)
    marfim = (0.84, 0.76, 0.62)
    branco = (0.86, 0.85, 0.82)
    preto = (0.012, 0.012, 0.013)
    pele = (0.72, 0.5, 0.36)


# ---------------------------------------------------------------- peças básicas

def malha(nome, verts, faces, mat=None, suave=True, cores=None):
    me = bpy.data.meshes.new(nome)
    me.from_pydata(verts, [], faces)
    me.update()
    if suave:
        me.shade_smooth()
    if mat:
        me.materials.append(mat)
    if cores is not None:
        at = me.color_attributes.new("ponta", "FLOAT_COLOR", "POINT")
        dados = np.ones(len(verts) * 4, dtype=np.float32)
        dados[0::4] = cores
        dados[1::4] = cores
        dados[2::4] = cores
        at.data.foreach_set("color", dados)
    return me


def obj(me, loc=(0, 0, 0), rot=(0, 0, 0), esc=(1, 1, 1), nome=None):
    o = bpy.data.objects.new(nome or me.name, me)
    o.location = loc
    o.rotation_euler = rot
    o.scale = esc if hasattr(esc, "__len__") else (esc, esc, esc)
    _colecao().objects.link(o)
    return o


def esfera(raio, loc=(0, 0, 0), mat=None, seg=64, aneis=44, esc=(1, 1, 1)):
    verts, faces = [], []
    for i in range(aneis + 1):
        t = math.pi * i / aneis
        for j in range(seg):
            f = 2 * math.pi * j / seg
            verts.append((raio * math.sin(t) * math.cos(f), raio * math.sin(t) * math.sin(f), raio * math.cos(t)))
    for i in range(aneis):
        for j in range(seg):
            a = i * seg + j
            b = i * seg + (j + 1) % seg
            c = (i + 1) * seg + (j + 1) % seg
            d = (i + 1) * seg + j
            faces.append((a, d, c, b))
    return obj(malha("esfera", verts, faces, mat), loc, esc=esc)


def torno(perfil, mat=None, seg=96, loc=(0, 0, 0), rot=(0, 0, 0), esc=(1, 1, 1)):
    """Sólido de revolução a partir de pares (raio, altura). As normais sempre apontam para fora."""
    verts, faces = [], []
    n = len(perfil)
    area = sum(perfil[i][0] * perfil[(i + 1) % n][1] - perfil[(i + 1) % n][0] * perfil[i][1] for i in range(n))
    for r, z in perfil:
        for j in range(seg):
            f = 2 * math.pi * j / seg
            verts.append((r * math.cos(f), r * math.sin(f), z))
    for i in range(n - 1):
        for j in range(seg):
            a = i * seg + j
            b = i * seg + (j + 1) % seg
            c = (i + 1) * seg + (j + 1) % seg
            d = (i + 1) * seg + j
            faces.append((a, b, c, d) if area > 0 else (a, d, c, b))
    anel = math.dist(perfil[0], perfil[-1]) < 1e-6
    if perfil[0][0] > 1e-6 and not anel:
        faces.append(tuple(range(seg - 1, -1, -1)) if area > 0 else tuple(range(seg)))
    if perfil[-1][0] > 1e-6 and not anel:
        f = tuple(range((n - 1) * seg, n * seg))
        faces.append(f if area > 0 else f[::-1])
    return obj(malha("torno", verts, faces, mat), loc, rot, esc)

def bloco(lx, ly, lz, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), raio=0.0, segs=3):
    x, y, z = lx / 2, ly / 2, lz / 2
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    f = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    o = obj(malha("bloco", v, f, mat, suave=False), loc, rot)
    if raio:
        b = o.modifiers.new("b", "BEVEL")
        b.width = raio
        b.segments = segs
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(35)
        b.harden_normals = True
        o.data.shade_smooth()
    return o


def _catmull(pts, passos=10):
    p = [Vector(x) for x in pts]
    p = [p[0] * 2 - p[1]] + p + [p[-1] * 2 - p[-2]]
    saida = []
    for i in range(1, len(p) - 2):
        a, b, c, d = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(passos):
            t = k / passos
            saida.append(0.5 * ((2 * b) + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t ** 3))
    saida.append(p[-2])
    return saida


def tubo(pontos, raio, mat=None, suavizar=10, lados=10, fechado=False, raios=None):
    """Fio, galho ou cabo que passa pelos pontos."""
    caminho = _catmull(pontos, suavizar) if suavizar > 1 else [Vector(p) for p in pontos]
    if fechado and suavizar > 1:
        caminho = caminho[:-1]
    n = len(caminho)
    verts, faces = [], []
    ref = Vector((0.31, 0.74, 0.59)).normalized()
    for i, p in enumerate(caminho):
        ant = caminho[i - 1] if (i > 0 or fechado) else p
        seg = caminho[(i + 1) % n] if (i < n - 1 or fechado) else p
        t = (seg - ant).normalized()
        u = t.cross(ref).normalized()
        w = t.cross(u).normalized()
        rr = raios(i / max(1, n - 1)) if raios else raio
        for j in range(lados):
            a = 2 * math.pi * j / lados
            verts.append(tuple(p + (u * math.cos(a) + w * math.sin(a)) * rr))
    ultimo = n if fechado else n - 1
    for i in range(ultimo):
        for j in range(lados):
            a = i * lados + j
            b = i * lados + (j + 1) % lados
            c = ((i + 1) % n) * lados + (j + 1) % lados
            d = ((i + 1) % n) * lados + j
            faces.append((a, b, c, d))
    if not fechado:
        faces.append(tuple(range(lados - 1, -1, -1)))
        faces.append(tuple(range((n - 1) * lados, n * lados)))
    return obj(malha("tubo", verts, faces, mat))


def fita(pontos, largura, mat=None, espessura=0.006, suavizar=10, eixo=(0, 0, 1), secoes=6, bojo=0.08):
    """Tira de tecido. `largura` pode ser um número ou função de t (0 a 1). `eixo` é a direção da largura."""
    caminho = _catmull(pontos, suavizar)
    n = len(caminho)
    verts, faces = [], []
    eixo_v = Vector(eixo).normalized()
    for i, p in enumerate(caminho):
        ant = caminho[max(0, i - 1)]
        seg = caminho[min(n - 1, i + 1)]
        t = (seg - ant).normalized()
        lado = (eixo_v - t * eixo_v.dot(t)).normalized()
        nor = t.cross(lado).normalized()
        tt = i / (n - 1)
        la = largura(tt) if callable(largura) else largura
        for k in range(secoes + 1):
            v = k / secoes - 0.5
            verts.append(tuple(p + lado * (la * v) + nor * (math.cos(v * math.pi) - 0.6) * bojo * la))
    for i in range(n - 1):
        for k in range(secoes):
            a = i * (secoes + 1) + k
            faces.append((a, a + 1, a + secoes + 2, a + secoes + 1))
    o = obj(malha("fita", verts, faces, mat))
    so = o.modifiers.new("s", "SOLIDIFY")
    so.thickness = espessura
    so.offset = 0
    return o


def agrupar(objetos, loc=(0, 0, 0), rot=(0, 0, 0), esc=1.0):
    """Coloca vários objetos sob um único pai, para mover e girar conjuntos."""
    pai = bpy.data.objects.new("grupo", None)
    _colecao().objects.link(pai)
    pai.location = loc
    pai.rotation_euler = rot
    pai.scale = (esc, esc, esc) if not hasattr(esc, "__len__") else esc
    for o in objetos:
        o.parent = pai
    return pai


def ramo_malha(nome, mat, rnd, comp=1.0, agulha=0.15, densidade=46, laterais=3):
    """Raminho de pinheiro com brotos laterais. Devolve uma malha para ser instanciada muitas vezes."""
    verts, faces, cor = [], [], []

    def caule(p0, direcao, comprimento, agulhas, tam):
        d = direcao.normalized()
        lado = d.cross(Vector((0, 0, 1)))
        if lado.length < 0.01:
            lado = Vector((1, 0, 0))
        lado.normalize()
        cima = lado.cross(d).normalized()
        for i in range(agulhas):
            t = (i + rnd.random()) / agulhas
            base = p0 + d * (comprimento * t)
            a = i * 2.39996 + rnd.uniform(-0.3, 0.3)
            radial = lado * math.cos(a) + cima * math.sin(a)
            dirn = (radial * 0.82 + d * 0.92).normalized()
            L = tam * (1 - 0.45 * t) * rnd.uniform(0.82, 1.12)
            curva = (d * 0.2 - radial * 0.1) * L
            ponta = base + dirn * L + curva
            meio = base + dirn * L * 0.55 + curva * 0.3
            s1 = dirn.cross(d)
            if s1.length < 0.01:
                s1 = lado
            s1.normalize()
            s2 = dirn.cross(s1).normalized()
            r = tam * 0.038
            b0 = len(verts)
            for q, c in ((base, 0.0), (meio, 0.55)):
                for k in range(3):
                    ang = k * 2.094 + 0.4
                    verts.append(tuple(q + (s1 * math.cos(ang) + s2 * math.sin(ang)) * r * (1 if c == 0 else 0.72)))
                    cor.append(c)
            verts.append(tuple(ponta))
            cor.append(1.0)
            for k in range(3):
                k2 = (k + 1) % 3
                faces.append((b0 + k, b0 + k2, b0 + 3 + k2, b0 + 3 + k))
                faces.append((b0 + 3 + k, b0 + 3 + k2, b0 + 6))

    eixo = Vector((1, 0, 0))
    caule(Vector((0, 0, 0)), eixo, comp, densidade, agulha)
    for i in range(laterais):
        t = 0.2 + 0.6 * i / max(1, laterais - 1) * 0.8
        for lado in (-1, 1):
            base = eixo * (comp * (t + rnd.uniform(-0.03, 0.03)))
            d = Vector((0.78, lado * 0.62, rnd.uniform(-0.1, 0.1)))
            caule(base, d, comp * (0.56 - t * 0.28), int(densidade * 0.56), agulha * 0.92)
    return malha(nome, verts, faces, mat, suave=True, cores=cor)


def bola(raio, loc, mat, mat_tampa=None, argola=True, rot=(0, 0, 0)):
    """Bola de Natal completa: esfera, tampa canelada e argola."""
    tampa = mat_tampa or pbr("tampa", Cores.ouro, 1.0, 0.26)
    e = esfera(raio, (0, 0, 0), mat)
    r = raio * 0.2
    t = torno([(0, raio * 0.94), (r * 0.98, raio * 0.94), (r, raio * 1.0), (r * 0.96, raio * 1.13), (r * 0.72, raio * 1.17), (0, raio * 1.17)], tampa, seg=40)
    partes = [e, t]
    if argola:
        giro = (math.pi / 2, 0, 0)
        v = []
        f = []
        maior, menor = raio * 0.075, raio * 0.014
        for i in range(36):
            a = 2 * math.pi * i / 36
            for j in range(10):
                b = 2 * math.pi * j / 10
                cr = maior + menor * math.cos(b)
                v.append((cr * math.cos(a), cr * math.sin(a), menor * math.sin(b)))
        for i in range(36):
            for j in range(10):
                a = i * 10 + j
                b = i * 10 + (j + 1) % 10
                c = ((i + 1) % 36) * 10 + (j + 1) % 10
                d = ((i + 1) % 36) * 10 + j
                f.append((a, b, c, d))
        partes.append(obj(malha("argola", v, f, tampa), (0, 0, raio * 1.22), giro))
    return agrupar(partes, loc, rot)


def laco(mat, largura=0.3, volta=0.62, cauda=0.72, loc=(0, 0, 0), rot=(0, 0, 0), esc=1.0):
    """Laço de presente: duas voltas, nó central e duas pontas."""
    partes = []

    def volta_uma(lado, sobe):
        pts = []
        for i in range(17):
            t = i / 16
            x = volta * math.sin(math.pi * t) * lado
            y = 0.22 * volta * math.sin(2 * math.pi * t)
            z = sobe * x * lado + 0.02 * math.sin(math.pi * t)
            pts.append((x, y, z))
        return pts

    def larg(t):
        return largura * (0.26 + 0.74 * math.sin(math.pi * t) ** 0.55)

    partes.append(fita(volta_uma(1, 0.36), larg, mat, suavizar=3))
    partes.append(fita(volta_uma(-1, 0.36), larg, mat, suavizar=3))
    no = esfera(largura * 0.27, (0, -0.012, 0.02), mat, seg=32, aneis=24, esc=(0.92, 0.8, 1.15))
    partes.append(no)
    for lado in (-1, 1):
        pts = [(0, 0.012, 0), (lado * cauda * 0.2, 0.01, -cauda * 0.38), (lado * cauda * 0.44, -0.015, -cauda * 0.72), (lado * cauda * 0.5, 0.02, -cauda)]
        partes.append(fita(pts, lambda t: largura * (0.34 + 0.46 * t), mat, eixo=(lado * 0.85, 0, 0.5)))
    return agrupar(partes, loc, rot, esc)


def estrela(raio=1.0, fundo=0.34, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, pontas=5, interno=0.42):
    """Estrela facetada como as da sua imagem de Natal."""
    v = [(0, -fundo * raio, 0), (0, fundo * raio, 0)]
    for i in range(pontas * 2):
        a = math.pi / 2 + math.pi * i / pontas
        r = raio if i % 2 == 0 else raio * interno
        v.append((r * math.cos(a), 0, r * math.sin(a)))
    f = []
    n = pontas * 2
    for i in range(n):
        a, b = 2 + i, 2 + (i + 1) % n
        f.append((0, b, a))
        f.append((1, a, b))
    return obj(malha("estrela", v, f, mat, suave=False), loc, rot)


def peca_2d(contorno, mat, espessura=0.05, voxel=0.012, dobras=0.02, loc=(0, 0, 0), rot=(0, 0, 0), esc=1.0, seed=3, plano="xz", bojo=0.6):
    """Peça macia a partir de um contorno 2D: roupas, meias e gorros.
    O contorno vira curva, ganha volume, é remalhado e recebe dobras de tecido."""
    cu = bpy.data.curves.new("contorno", "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = espessura * 0.3
    cu.bevel_depth = espessura
    cu.bevel_resolution = 5
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(contorno) - 1)
    for p, c in zip(sp.bezier_points, contorno):
        p.co = (c[0], c[1], 0)
        p.handle_left_type = "AUTO"
        p.handle_right_type = "AUTO"
    sp.use_cyclic_u = True
    cu.resolution_u = 12
    o = bpy.data.objects.new("peca", cu)
    _colecao().objects.link(o)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.view_layer.objects.active
    rm = o.modifiers.new("r", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = voxel
    rm.adaptivity = 0
    sm = o.modifiers.new("s", "SMOOTH")
    sm.factor = 0.8
    sm.iterations = 16
    bpy.ops.object.modifier_apply(modifier="r")
    bpy.ops.object.modifier_apply(modifier="s")
    me = o.data
    if dobras or bojo:
        co = np.empty(len(me.vertices) * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        if bojo:
            # a peça estufa no meio e afina na borda, como tecido com enchimento leve
            pol = np.array(contorno, dtype=np.float32)
            a, b = pol, np.roll(pol, -1, axis=0)
            ab = b - a
            d2 = np.full(len(co), 1e9, dtype=np.float32)
            passo = 2
            for i in range(0, len(a)):
                ap = co[:, :2] - a[i]
                t = np.clip((ap @ ab[i]) / max(float(ab[i] @ ab[i]), 1e-9), 0, 1)
                d = ap - t[:, None] * ab[i]
                d2 = np.minimum(d2, (d * d).sum(1))
            dist = np.sqrt(d2)
            perfil = np.clip(dist / max(dist.max(), 1e-6), 0, 1)
            co[:, 2] *= (1 - bojo) + bojo * 2.6 * np.sqrt(perfil)
            me.vertices.foreach_set("co", co.ravel())
            me.update()
            lisa = o.modifiers.new("l", "SMOOTH")
            lisa.factor = 1.0
            lisa.iterations = 26
            bpy.ops.object.modifier_apply(modifier="l")
            me = o.data
            me.vertices.foreach_get("co", co.ravel())
        r = np.random.default_rng(seed)
        h = np.zeros(len(co), dtype=np.float32)
        for _ in range(11 if dobras else 0):
            ang = r.uniform(-0.5, 0.5) + (math.pi / 2 if r.random() < 0.8 else 0.0)
            fr = r.uniform(3.2, 11.0)
            fase = r.uniform(0, 6.3)
            amp = 1.0 / (fr ** 0.72)
            h += amp * np.sin((co[:, 0] * math.cos(ang) + co[:, 1] * math.sin(ang)) * fr + fase + 1.4 * np.sin(co[:, 1] * 1.7 + fase))
        peso = np.clip(np.abs(co[:, 2]) / max(espessura, 1e-5), 0, 1)
        co[:, 2] += h * dobras * peso * np.sign(co[:, 2] + 1e-6)
        me.vertices.foreach_set("co", co.ravel())
        me.update()
    me.shade_smooth()
    me.materials.append(mat)
    o.select_set(False)
    if plano == "xz":
        o.rotation_euler = (math.pi / 2, 0, 0)
        bpy.context.view_layer.update()
        o.data.transform(o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    o.location = loc
    o.rotation_euler = rot
    o.scale = esc if hasattr(esc, "__len__") else (esc, esc, esc)
    return o


def espalhar_ramos(rnd, malhas, n, posicao):
    """Instancia ramos. `posicao(i)` devolve (ponto, direção, escala)."""
    for i in range(n):
        p, d, s = posicao(i)
        o = bpy.data.objects.new("r", rnd.choice(malhas))
        o.location = p
        rot = Vector((1, 0, 0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        giro = Matrix.Rotation(rnd.uniform(-math.pi, math.pi), 4, "X")
        o.rotation_euler = (rot @ giro).to_euler()
        o.scale = (s, s, s)
        _colecao().objects.link(o)
