# Recorta os enfeites pendurados rente à argola (o fio do site encosta no topo da imagem) e salva em WebP.
# Uso: python pendurados.py <pasta_png> <pasta_webp> nome1,nome2
import os
import sys

from PIL import Image

entrada, destino, nomes = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
os.makedirs(destino, exist_ok=True)
for nome in nomes:
    im = Image.open(os.path.join(entrada, nome + ".png")).convert("RGBA")
    x0, y0, x1, y1 = im.getbbox()
    folga = round((x1 - x0) * 0.03)
    im = im.crop((max(0, x0 - folga), y0, min(im.width, x1 + folga), min(im.height, y1 + folga)))
    largura = 360
    im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
    saida = os.path.join(destino, nome + ".webp")
    im.save(saida, "WEBP", quality=86, alpha_quality=90, method=6)
    print(nome, im.size, os.path.getsize(saida) // 1024, "KB")
