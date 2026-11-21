# Junta renders PNG numa folha de contato sobre o fundo escuro do site, para revisão.
# Uso: python folha.py <pasta> <saida.png> [colunas] [tamanho] [nome1,nome2]
import glob
import os
import sys

from PIL import Image, ImageDraw

pasta, saida = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
tam = int(sys.argv[4]) if len(sys.argv) > 4 else 300
filtro = sys.argv[5].split(",") if len(sys.argv) > 5 else None
arqs = sorted(glob.glob(os.path.join(pasta, "*.png")))
if filtro:
    arqs = [a for a in arqs if os.path.splitext(os.path.basename(a))[0] in filtro]
linhas = (len(arqs) + cols - 1) // cols
folha = Image.new("RGB", (cols * tam, linhas * tam), (8, 24, 18))
d = ImageDraw.Draw(folha)
for i, a in enumerate(arqs):
    x, y = (i % cols) * tam, (i // cols) * tam
    if (i % cols + i // cols) % 2:
        d.rectangle((x, y, x + tam, y + tam), fill=(17, 49, 38))
    im = Image.open(a).convert("RGBA")
    im.thumbnail((tam, tam), Image.LANCZOS)
    folha.paste(im, (x + (tam - im.width) // 2, y + (tam - im.height) // 2), im)
    d.text((x + 6, y + 4), os.path.splitext(os.path.basename(a))[0], fill=(230, 220, 200))
folha.save(saida)
print("folha", folha.size, len(arqs))
