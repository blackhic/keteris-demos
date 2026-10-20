#!/usr/bin/env python3
"""Fabrique une maquette Keteris à partir d'un gabarit + un fichier JSON.
Usage (depuis la racine du dépôt keteris-demos) :
  python3 _gabarits/fabriquer.py <slug> <donnees.json>
Crée <slug>/index.html et <slug>/apercu.png (1200x750), vérifie bureau + mobile, sans erreur console.
"""
import json, re, sys, pathlib, asyncio

ROOT = pathlib.Path(__file__).resolve().parent.parent
REQUIS = ["entreprise", "ville", "couleur", "segment", "titre", "kpis", "vue", "agent", "a_valider", "benefices"]


def construire(slug, data_path):
    data = json.loads(pathlib.Path(data_path).read_text(encoding="utf-8"))
    manque = [k for k in REQUIS if not data.get(k)]
    if manque:
        sys.exit(f"Champs manquants : {manque}")
    if data["vue"] == "table" and not data.get("table"):
        sys.exit("vue=table exige le champ table")
    if data["vue"] == "pipeline" and not data.get("colonnes"):
        sys.exit("vue=pipeline exige le champ colonnes")
    if data["vue"] == "dashboard" and not data.get("graph"):
        sys.exit("vue=dashboard exige le champ graph")
    html = (ROOT / "_gabarits" / "app.html").read_text(encoding="utf-8")
    bloc = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = re.sub(r'(<script id="data" type="application/json">).*?(</script>)',
                  lambda m: m.group(1) + "\n" + bloc + "\n" + m.group(2), html, count=1, flags=re.S)
    out = ROOT / slug
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    return out


async def verifier(out):
    from playwright.async_api import async_playwright
    url = (out / "index.html").as_uri()
    erreurs = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h, shot in ((1200, 750, True), (390, 844, False)):
            pg = await b.new_page(viewport={"width": w, "height": h})
            pg.on("console", lambda m: m.type == "error" and erreurs.append(m.text))
            pg.on("pageerror", lambda e: erreurs.append(str(e)))
            await pg.goto(url, wait_until="networkidle")
            sw = await pg.evaluate("document.documentElement.scrollWidth")
            if sw > w + 1:
                erreurs.append(f"défilement horizontal à {w}px ({sw}px)")
            if shot:
                await pg.screenshot(path=str(out / "apercu.png"))
            await pg.close()
        await b.close()
    erreurs = [e for e in erreurs if "fonts.g" not in e and "Failed to load resource" not in e]
    if erreurs:
        sys.exit("ERREURS : " + " | ".join(erreurs))
    print(f"OK {out.name} : index.html + apercu.png")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    asyncio.run(verifier(construire(sys.argv[1], sys.argv[2])))
