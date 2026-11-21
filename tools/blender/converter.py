# Converte os renders em WebP para o site. Produtos com luz recebem brilho real ao redor dos LEDs.
# Uso: python converter.py <pasta_png> <pasta_webp> [nome1,nome2]
import glob
import os
import sys

import numpy as np
from PIL import Image

COM_LUZ = {
    "arvore-180", "kit-decoracao", "fita-led", "rena-led", "pisca-pisca", "cortina-led", "boneco-neve-led", "leds-arvore", "kit-externa",
    "kit-arvore-premium", "guirlanda-led", "guirlanda-mini", "guirlanda-rgb", "kit-luminosas", "presepio-led", "vila-led", "kit-belem",
    "kit-familia-sagrada", "cena-manjedoura", "arvore-1", "arvore-4", "g-luzes",
}


def desfocar(canal, sigma):
    """Desfoque gaussiano em ponto flutuante, sem faixas visíveis."""
    h, w = canal.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (fx * fx + fy * fy))
    return np.fft.irfft2(np.fft.rfft2(canal) * g, s=canal.shape)


def brilho(a):
    rgb, alfa = a[..., :3], a[..., 3:4]
    pre = rgb * alfa
    lum = pre.max(axis=2)
    t = np.clip((lum - 0.66) / 0.3, 0, 1)
    fonte = pre * (t * t * (3 - 2 * t))[..., None]
    halo = np.zeros_like(pre)
    esc = a.shape[1] / 800
    for sigma, peso in ((2.5, 0.9), (7, 0.7), (18, 0.5), (46, 0.34)):
        for c in range(3):
            halo[..., c] += desfocar(fonte[..., c], sigma * esc) * peso
    halo = np.clip(halo, 0, 1)
    soma = 1 - (1 - pre) * (1 - halo)
    novo_alfa = np.maximum(alfa[..., 0], np.clip(halo.max(axis=2) * 1.15, 0, 1))
    saida = np.zeros_like(a)
    saida[..., :3] = soma / np.maximum(novo_alfa, 1e-4)[..., None]
    saida[..., 3] = novo_alfa
    return np.clip(saida, 0, 1)


def sombra_suave(a):
    """A sombra do chão some antes da borda da imagem, sem deixar um quadrado escuro na página."""
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    t = np.clip((r - 0.62) / 0.36, 0, 1)
    queda = 1 - t * t * (3 - 2 * t)
    sombra = (a[..., :3].max(axis=2) < 0.08) & (a[..., 3] < 0.92)
    a = a.copy()
    a[..., 3] = np.where(sombra, a[..., 3] * queda, a[..., 3])
    return a


entrada, destino = sys.argv[1], sys.argv[2]
filtro = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
os.makedirs(destino, exist_ok=True)
total = 0
for arq in sorted(glob.glob(os.path.join(entrada, "*.png"))):
    nome = os.path.splitext(os.path.basename(arq))[0]
    if filtro and nome not in filtro:
        continue
    a = sombra_suave(np.asarray(Image.open(arq).convert("RGBA")).astype(np.float32) / 255)
    if nome in COM_LUZ:
        a = brilho(a)
    im = Image.fromarray((a * 255 + 0.5).astype(np.uint8), "RGBA")
    saida = os.path.join(destino, nome + ".webp")
    im.save(saida, "WEBP", quality=84, alpha_quality=88, method=6)
    total += os.path.getsize(saida)
    print(nome, os.path.getsize(saida) // 1024, "KB")
print("total", total // 1024, "KB")
