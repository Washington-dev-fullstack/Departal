import json, re, sys
raiz = sys.argv[1]
t = open(raiz + r"\js\dados\letreiro.js", encoding="utf8").read()
t = t[t.index("Departal.letreiro"):]
dados = json.loads(t[t.index("{"):t.rindex("}") + 1])
d, e = dados["letras"][0], dados["letras"][1]
x0, x1, alt = d["x0"], e["x1"], dados["altura"]
gorro = """<g transform="translate(-34 -24) rotate(-10 66 48) scale(.62)"><path d="M13 62C16 34 36 9 67 7c23-1 39 15 44 37 2 7 3 13 3 18h-11c-1-14-9-25-20-27 7 9 10 19 8 31-23 9-53 8-78-4Z" fill="#c8102e"/><path d="M6 58c29 14 62 15 88 2 5-2 8 1 8 6l-1 9c-1 5-4 7-8 8-30 7-60 5-87-7-5-2-6-6-5-11l1-4c0-3 2-4 4-3Z" fill="#f6efe2"/><circle cx="111" cy="73" r="12" fill="#f6efe2"/></g>"""
esc = 150 / (x1 - x0)
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="44" fill="#07130e"/><g transform="translate(25 72) scale({esc:.5f}) translate({-x0} 0)" fill="#e8283f"><path d="{d["d"]}"/><path d="{e["d"]}"/></g><g transform="translate(36 42)">{gorro}</g></svg>'
open(raiz + r"\images\marca\favicon.svg", "w", encoding="utf8").write(svg)
print(len(svg), alt, x0, x1)
