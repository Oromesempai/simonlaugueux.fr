"""Vérifications statiques du site (bibliothèque standard uniquement).

Lancer depuis la racine du dépôt : python3 -m unittest discover -s tests -v
"""
import json
import re
import struct
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
PHONE_HREF = "tel:+33781631578"
EMAIL = "simonlaugueux@proton.me"
SECTIONS = ["accueil", "univers", "contact"]  # « formules » est masquée (commentée)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "source", "track", "wbr"}


class Element:
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.content = []  # str ou Element, dans l'ordre du document

    def text(self):
        raw = "".join(c if isinstance(c, str) else c.text() for c in self.content)
        return " ".join(raw.split())

    def iter(self):
        for child in self.content:
            if isinstance(child, Element):
                yield child
                yield from child.iter()

    def find_all(self, tag=None, cls=None, **attrs):
        found = []
        for el in self.iter():
            if tag and el.tag != tag:
                continue
            if cls and cls not in el.attrs.get("class", "").split():
                continue
            if any(el.attrs.get(k) != v for k, v in attrs.items()):
                continue
            found.append(el)
        return found

    def find(self, tag=None, cls=None, **attrs):
        found = self.find_all(tag, cls, **attrs)
        return found[0] if found else None


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element("#document", {})
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        el = Element(tag, {k: ("" if v is None else v) for k, v in attrs}, self.stack[-1])
        self.stack[-1].content.append(el)
        if tag not in VOID:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].content.append(data)


def load_page():
    builder = TreeBuilder()
    builder.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    return builder.root


class TestHead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = load_page()

    def meta(self, **attrs):
        el = self.page.find("meta", **attrs)
        self.assertIsNotNone(el, f"meta {attrs} manquante")
        return el.attrs.get("content", "")

    def test_langue_francaise(self):
        self.assertEqual(self.page.find("html").attrs.get("lang"), "fr")

    def test_charset_et_viewport(self):
        self.assertIsNotNone(self.page.find("meta", charset="utf-8"))
        self.assertIn("width=device-width", self.meta(name="viewport"))

    def test_titre_cible_cahors(self):
        title = self.page.find("title").text()
        self.assertIn("Simon Laugueux", title)
        self.assertIn("Cahors", title)
        self.assertLessEqual(len(title), 70)

    def test_meta_description(self):
        desc = self.meta(name="description")
        for mot in ("Dégustations", "Cahors", "spiritueux", "Lot"):
            self.assertIn(mot, desc)

    def test_open_graph(self):
        for prop in ("og:title", "og:description", "og:image", "og:url"):
            self.assertTrue(self.meta(property=prop), prop)
        self.assertTrue(self.meta(property="og:image").startswith("https://simonlaugueux.fr/"))

    def test_json_ld_local_business(self):
        scripts = self.page.find_all("script", type="application/ld+json")
        self.assertEqual(len(scripts), 1)
        data = json.loads(scripts[0].text())
        self.assertEqual(data["@type"], "LocalBusiness")
        self.assertEqual(data["telephone"], "+33781631578")
        self.assertEqual(data["email"], EMAIL)
        self.assertEqual({z["name"] for z in data["areaServed"]}, {"Cahors", "Lot"})


class TestStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = load_page()

    def test_lien_evitement_en_premier(self):
        premier_lien = self.page.find("body").find("a")
        self.assertEqual(premier_lien.attrs.get("href"), "#contenu")
        self.assertIsNotNone(self.page.find("main", id="contenu"))

    def test_sections_dans_l_ordre(self):
        ids = [s.attrs.get("id") for s in self.page.find("main").find_all("section")]
        self.assertEqual(ids, SECTIONS)

    def test_chaque_section_a_un_titre(self):
        for section in self.page.find("main").find_all("section"):
            titre_id = section.attrs.get("aria-labelledby")
            self.assertTrue(titre_id, section.attrs.get("id"))
            titre = section.find(id=titre_id)
            self.assertIsNotNone(titre, titre_id)
            self.assertIn(titre.tag, ("h1", "h2"))

    def test_un_seul_h1(self):
        self.assertEqual(len(self.page.find_all("h1")), 1)

    def test_navigation_vers_chaque_section(self):
        nav = self.page.find("nav", **{"aria-label": "Navigation principale"})
        hrefs = {a.attrs.get("href") for a in nav.find_all("a")}
        for sid in SECTIONS:
            self.assertIn(f"#{sid}", hrefs)

    def test_mention_loi_evin(self):
        self.assertIn(
            "L'abus d'alcool est dangereux pour la santé, à consommer avec modération.",
            self.page.find("footer").text(),
        )

    def test_fichiers_github_pages(self):
        self.assertEqual((ROOT / "CNAME").read_text().strip(), "simonlaugueux.fr")
        self.assertTrue((ROOT / ".nojekyll").is_file())


def page_depuis(html):
    builder = TreeBuilder()
    builder.feed(html)
    return builder.root
def mailto_parts(href):
    parsed = urlparse(href)
    return parsed.path, {k: v[0] for k, v in parse_qs(parsed.query).items()}


class TestContenu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = load_page()

    def liens(self, prefixe, racine=None):
        racine = racine or self.page
        return [a for a in racine.find_all("a") if a.attrs.get("href", "").startswith(prefixe)]

    def test_tous_les_liens_tel_sont_corrects(self):
        tels = self.liens("tel:")
        self.assertGreaterEqual(len(tels), 4)
        for a in tels:
            self.assertEqual(a.attrs["href"], PHONE_HREF)

    def test_mailto_encodes_et_avec_objet(self):
        mails = self.liens("mailto:")
        self.assertGreaterEqual(len(mails), 4)
        for a in mails:
            href = a.attrs["href"]
            self.assertIsNone(re.search(r"\s", href), f"espace ou retour non encodé : {href}")
            self.assertNotIn("&amp;", href)
            self.assertIsNone(re.search(r"[^\x00-\x7f]", href), f"caractère non encodé : {href}")
            adresse, params = mailto_parts(href)
            self.assertEqual(adresse, EMAIL)
            self.assertTrue(params.get("subject"), href)

    def test_mailto_contact_pre_rempli(self):
        mail = self.liens("mailto:", self.page.find("section", id="contact"))[0]
        _, params = mailto_parts(mail.attrs["href"])
        self.assertEqual(params["subject"], "Demande de dégustation")
        for champ in ("Date souhaitée", "Nombre de personnes", "Type d'événement", "Lieu"):
            self.assertIn(champ, params["body"])

    def test_hero_propose_appel_et_email(self):
        hero = self.page.find("section", id="accueil")
        self.assertEqual(len(self.liens(PHONE_HREF, hero)), 1)
        self.assertEqual(len(self.liens("mailto:", hero)), 1)

    def test_coordonnees_affichees_en_clair(self):
        contact = self.page.find("section", id="contact").text()
        self.assertIn("07 81 63 15 78", contact)
        self.assertIn(EMAIL, contact)
        self.assertIsNone(self.page.find("p", cls="zone"), "zone de déplacement pas encore décidée")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertRegex(html, r'<!--[^>]*<p class="zone">Je me déplace à Cahors, dans le Lot et ses alentours\.</p>\s*-->')

    def formules_commentees(self):
        """Page reconstruite à partir de la section formules laissée en commentaire."""
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bloc = re.search(r"<!-- =+ DÉBUT SECTION FORMULES MASQUÉE.*?-->\s*<!--(.*?)-->\s*<!-- =+ FIN SECTION FORMULES MASQUÉE", html, re.S)
        self.assertIsNotNone(bloc, "section formules commentée introuvable")
        return page_depuis(bloc.group(1))

    def test_formules_masquees(self):
        self.assertIsNone(self.page.find("section", id="formules"))
        self.assertIsNone(self.page.find("aside", cls="encart-touristes"))
        hrefs = {a.attrs.get("href") for a in self.page.find_all("a")}
        self.assertNotIn("#formules", hrefs)
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertRegex(html, r'<!--\s*<li><a href="#formules">Formules</a></li>\s*-->')

    def test_commentaires_html_bien_formes(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for m in re.finditer(r"<!--(.*?)-->", html, re.S):
            self.assertNotIn("--", m.group(1), f"« -- » dans un commentaire : {m.group(1)[:60]}")
            self.assertNotIn("<!--", m.group(1))
        self.assertNotIn("SECTION FORMULES", self.page.find("body").text())

    def test_formules_commentees_restent_pretes(self):
        section = self.formules_commentees().find("section", id="formules")
        self.assertIsNotNone(section)
        formules = section.find_all("article", cls="formule")
        titres = [f.find("h3").text() for f in formules]
        self.assertEqual(titres, ["Particuliers & amis", "Entreprises & CE", "Événements privés"])
        for f in formules:
            prix = f.find("p", cls="prix").text()
            self.assertIn("à partir de XX €", prix)
            self.assertNotRegex(prix, r"\d", "tarif chiffré alors qu'il n'est pas décidé")
            self.assertEqual(len(self.liens("mailto:", f)), 1)
        self.assertIn("Tarifs communiqués prochainement", section.text())
        encart = section.find("aside", cls="encart-touristes")
        self.assertIn("De passage dans le Lot", encart.text())
        self.assertEqual(len(self.liens(PHONE_HREF, encart)), 1)

    def test_section_dates_supprimee(self):
        self.assertIsNone(self.page.find(id="dates"))
        self.assertNotIn("#dates", {a.attrs.get("href") for a in self.page.find_all("a")})
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("dates-liste", html)
        self.assertNotIn("Prochaines dates", html)

    def test_barre_contact_mobile(self):
        barre = self.page.find("nav", cls="barre-contact")
        self.assertEqual(barre.attrs.get("aria-label"), "Contact rapide")
        hrefs = [a.attrs.get("href", "") for a in barre.find_all("a")]
        self.assertEqual(len(hrefs), 2)
        self.assertEqual(hrefs[0], PHONE_HREF)
        self.assertTrue(hrefs[1].startswith("mailto:"))

    def test_annonce_en_haut_de_page(self):
        main = self.page.find("main")
        premier = next(c for c in main.content if isinstance(c, Element))
        self.assertEqual((premier.tag, premier.attrs.get("class")), ("aside", "annonce"))
        self.assertEqual(premier.attrs.get("aria-label"), "Annonce")
        texte = premier.text()
        for extrait in ("Bonjour à tous, le site sera prêt courant octobre.",
                        "carte des vins", "réserver une dégustation", "À bientôt."):
            self.assertIn(extrait, texte)
        self.assertIn(EMAIL, texte)
        self.assertEqual(len(self.liens("mailto:", premier)), 1)
        self.assertEqual(len(self.liens(PHONE_HREF, premier)), 1)

    def test_barriere_de_chantier_au_dessus_de_l_annonce(self):
        annonce = self.page.find("aside", cls="annonce")
        premier = next(el for el in annonce.iter() if el.tag in ("img", "p"))
        self.assertEqual(premier.tag, "img", "la barrière doit précéder le texte")
        self.assertEqual(premier.attrs.get("src"), "assets/img/barriere.svg")
        self.assertEqual(premier.attrs.get("alt"), "")

CSS = ROOT / "assets" / "css" / "style.css"
PALETTE = {
    "parchemin": "#F6EFE3", "camel": "#C19A6B", "ocre": "#CC7722",
    "ocre-fonce": "#8F4E0F", "chene": "#2A1D14", "malbec": "#5A1F2B",
}
# (texte, fond) réellement utilisés dans style.css — à tenir à jour si on en ajoute
PAIRES = [
    ("chene", "parchemin"), ("chene", "camel"), ("chene", "ocre"),
    ("parchemin", "chene"), ("parchemin", "ocre-fonce"), ("parchemin", "malbec"),
    ("malbec", "parchemin"), ("malbec", "camel"), ("camel", "chene"),
]


def luminance(hex_color):
    canaux = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canaux]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def lire_css():
    return re.sub(r"/\*.*?\*/", "", CSS.read_text(encoding="utf-8"), flags=re.S)


def css_rules(css):
    return [(sel.strip(), corps) for sel, corps in re.findall(r"([^{}]+)\{([^{}]*)\}", css)]


def media_blocks(css, condition):
    blocs = []
    for m in re.finditer(r"@media([^{]*)\{", css):
        if condition not in m.group(1):
            continue
        profondeur, i = 1, m.end()
        while profondeur:
            profondeur += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
        blocs.append(css[m.end():i - 1])
    return "\n".join(blocs)


class TestStyles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = lire_css()
        racine = re.search(r":root\s*\{([^}]*)\}", cls.css).group(1)
        cls.couleurs = {k: v.upper() for k, v in re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})", racine)}
        cls.page = load_page()

    def test_feuille_liee(self):
        self.assertIsNotNone(self.page.find("link", rel="stylesheet", href="assets/css/style.css"))

    def test_palette(self):
        self.assertEqual(self.couleurs, PALETTE)

    def test_pas_de_couleur_en_dur_hors_root(self):
        hors_root = re.sub(r":root\s*\{[^}]*\}", "", self.css)
        self.assertEqual(re.findall(r"#[0-9A-Fa-f]{3,8}\b", hors_root), [])

    def test_contrastes_wcag_aa(self):
        for texte, fond in PAIRES:
            ratio = contraste(PALETTE[texte], PALETTE[fond])
            self.assertGreaterEqual(ratio, 4.5, f"{texte} sur {fond} : {ratio:.2f}")

    def test_contenu_visible_sans_js(self):
        for sel, corps in css_rules(self.css):
            if not re.search(r"display:\s*none|opacity:\s*0\s*;", corps):
                continue
            for s in (x.strip() for x in sel.split(",")):
                if s in (".nav-toggle", ".barre-contact"):
                    continue
                self.assertTrue(s.startswith(".js "), f"« {s} » masque du contenu même sans JS")

    def test_menu_mobile_active_par_js(self):
        mobile = media_blocks(self.css, "max-width: 767px")
        self.assertRegex(self.css, r"(^|\})\s*\.nav-toggle\s*\{[^}]*display:\s*none")
        self.assertRegex(mobile, r"\.js \.nav-toggle\s*\{[^}]*display:\s*inline-flex")
        self.assertRegex(mobile, r"\.js \.nav-liste\s*\{[^}]*display:\s*none")
        self.assertRegex(mobile, r"\.js \.nav-liste\.ouvert\s*\{[^}]*display:\s*flex")

    def test_barre_mobile_ne_masque_pas_le_pied(self):
        mobile = media_blocks(self.css, "max-width: 767px")
        self.assertRegex(mobile, r"body\s*\{[^}]*padding-bottom:\s*var\(--hauteur-barre\)")
        desktop = media_blocks(self.css, "min-width: 768px")
        self.assertRegex(desktop, r"\.barre-contact\s*\{[^}]*display:\s*none")

    def test_mouvement_reduit(self):
        reduit = media_blocks(self.css, "prefers-reduced-motion: reduce")
        self.assertRegex(reduit, r"\.js \.reveal\s*\{[^}]*opacity:\s*1")
        self.assertIn("scroll-behavior: auto", reduit)

    def test_focus_visible(self):
        self.assertRegex(self.css, r":focus-visible\s*\{[^}]*outline:")

    def test_cibles_tactiles(self):
        self.assertRegex(self.css, r"\.bouton\s*\{[^}]*min-height:\s*48px")
        self.assertRegex(self.css, r"\.nav-liste a\s*\{[^}]*min-height:\s*44px")

    def test_polices_hebergees_localement(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("fonts.googleapis.com", html)
        self.assertNotIn("fonts.gstatic.com", html)
        faces = re.findall(r"@font-face\s*\{([^}]*)\}", self.css)
        familles = {re.search(r'font-family:\s*"([^"]+)"', f).group(1) for f in faces}
        self.assertEqual(familles, {"Cormorant Garamond", "Lato"})
        for f in faces:
            self.assertRegex(f, r'url\("\.\./fonts/[\w.-]+\.woff2"\)\s*format\("woff2"\)')
            self.assertIn("font-display: swap", f)
        self.assertIn('"Cormorant Garamond", Georgia, serif', self.css)
        self.assertIn('"Lato", system-ui, sans-serif', self.css)

    def test_impression_affiche_tout(self):
        impression = media_blocks(self.css, "print")
        self.assertRegex(impression, r"\.js \.reveal\s*\{[^}]*opacity:\s*1")
        self.assertRegex(impression, r"\.js \.reveal\s*\{[^}]*transition:\s*none")
        self.assertRegex(impression, r"\.barre-contact\s*\{[^}]*display:\s*none")

    def test_annonce_en_gros_caracteres(self):
        regle = re.search(r"(^|\})\s*\.annonce\s*\{([^}]*)\}", self.css).group(2)
        taille = float(re.search(r"font-size:\s*clamp\(([\d.]+)rem", regle).group(1))
        self.assertGreaterEqual(taille, 1.25, "annonce : au moins 20 px même sur mobile")

    def test_focus_visible_sur_l_annonce(self):
        self.assertRegex(self.css, r"\.annonce :focus-visible\s*\{[^}]*outline-color:\s*var\(--camel\)")

    def test_focus_visible_sur_la_barre_mobile(self):
        self.assertRegex(self.css, r"\.barre-contact :focus-visible\s*\{[^}]*outline-color:\s*var\(--camel\)")

    def test_texte_du_hero_lisible_sur_la_texture(self):
        svg = (ROOT / "assets" / "img" / "bois.svg").read_text()
        opacite = float(re.search(r'stroke-opacity="([\d.]+)"', svg).group(1))
        ocre = [int(PALETTE["ocre"][i:i + 2], 16) for i in (1, 3, 5)]
        chene = [int(PALETTE["chene"][i:i + 2], 16) for i in (1, 3, 5)]
        fond = "#" + "".join(f"{round(o + (c - o) * opacite):02X}" for o, c in zip(ocre, chene))
        self.assertGreaterEqual(contraste(PALETTE["chene"], fond), 4.5, fond)

class TestScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = load_page()

    def test_script_charge_en_defer(self):
        script = self.page.find("script", src="assets/js/main.js")
        self.assertIsNotNone(script)
        self.assertIn("defer", script.attrs)
        self.assertTrue((ROOT / "assets" / "js" / "main.js").is_file())

    def test_bouton_menu_accessible(self):
        bouton = self.page.find("button", cls="nav-toggle")
        self.assertEqual(bouton.attrs.get("type"), "button")
        self.assertEqual(bouton.attrs.get("aria-expanded"), "false")
        self.assertEqual(bouton.attrs.get("aria-controls"), "menu")
        menu = self.page.find(id="menu")
        self.assertIsNotNone(menu)
        self.assertNotIn("hidden", menu.attrs)

    def test_sections_animees_sauf_hero(self):
        for section in self.page.find("main").find_all("section"):
            classes = section.attrs.get("class", "").split()
            attendu = section.attrs["id"] != "accueil"
            self.assertEqual("reveal" in classes, attendu, section.attrs["id"])

IMG = ROOT / "assets" / "img"
SVG_ATTENDUS = {"barrique", "verre", "grappe", "carafe", "bois", "douelles", "favicon", "barriere"}


def refs_locales(page):
    refs = []
    for el in page.iter():
        for attr in ("src", "href"):
            valeur = el.attrs.get(attr)
            if valeur and not re.match(r"(https?:|#|tel:|mailto:|data:)", valeur):
                refs.append(valeur)
    return refs


class TestAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = load_page()
        cls.css = lire_css()

    def test_references_html_relatives_et_existantes(self):
        refs = refs_locales(self.page)
        self.assertGreaterEqual(len(refs), 6)
        for ref in refs:
            self.assertFalse(ref.startswith("/"), f"chemin absolu : {ref}")
            self.assertTrue((ROOT / ref).is_file(), f"introuvable : {ref}")

    def test_references_css_existantes(self):
        urls = re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", self.css)
        self.assertEqual(len(urls), 5)
        for u in urls:
            self.assertFalse(u.startswith("/"), f"chemin absolu : {u}")
            self.assertTrue((CSS.parent / u).resolve().is_file(), f"introuvable : {u}")

    def test_svg_valides(self):
        self.assertLessEqual(SVG_ATTENDUS, {p.stem for p in IMG.glob("*.svg")})
        for svg in sorted(IMG.glob("*.svg")):
            racine = ET.parse(svg).getroot()
            self.assertEqual(racine.tag, "{http://www.w3.org/2000/svg}svg", svg.name)
            self.assertIn("viewBox", racine.attrib, svg.name)

    def test_svg_utilisent_la_palette(self):
        autorisees = set(PALETTE.values())
        for svg in sorted(IMG.glob("*.svg")):
            couleurs = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", svg.read_text())}
            self.assertLessEqual(couleurs, autorisees, svg.name)

    def test_icones_decoratives(self):
        imgs = self.page.find_all("img")
        self.assertEqual(len(imgs), 4)
        for img in imgs:
            self.assertEqual(img.attrs.get("alt"), "", img.attrs.get("src"))
            self.assertTrue(img.attrs.get("width") and img.attrs.get("height"))

    def test_image_open_graph(self):
        og = self.page.find("meta", property="og:image").attrs["content"]
        data = (ROOT / og.removeprefix("https://simonlaugueux.fr/")).read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", data[16:24]), (1200, 630))

if __name__ == "__main__":
    unittest.main()
