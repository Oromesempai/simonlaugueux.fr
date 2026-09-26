# Site vitrine Simon Laugueux — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construire le site vitrine one-page statique de Simon Laugueux (dégustations de vins & spiritueux, Cahors / Lot), publiable tel quel sur GitHub Pages.

**Architecture:** Un seul `index.html` sémantique, une feuille `assets/css/style.css` (palette en variables CSS), un petit `assets/js/main.js` optionnel (menu burger + apparition au scroll), des SVG maison dans `assets/img/`. Aucun build, aucune dépendance : les vérifications sont des tests Python stdlib (`tests/test_site.py`) qui analysent le HTML/CSS/assets, plus un test Node natif du JS (`tests/main.test.mjs`).

**Tech Stack:** HTML5, CSS3, JavaScript ES5 (sans module), Python 3.12 stdlib (`unittest`, `html.parser`) pour les tests et la génération de l'image Open Graph, Node 20 (`node:test`, `node:vm`) pour tester le JS, `npx html-validate` ponctuel (non installé dans le projet).

**Spec:** `docs/superpowers/specs/2026-09-26-site-vitrine-design.md`

## Global Constraints

- Langue du site : français, `lang="fr"`.
- E-mail : `simonlaugueux@proton.me` — Téléphone affiché : `07 81 63 15 78` — lien : `tel:+33781631578`.
- Réservation uniquement par liens directs `tel:` / `mailto:` ; aucun formulaire, aucun service tiers.
- Palette (seules couleurs hex autorisées, uniquement dans `:root`) : `--parchemin #F6EFE3`, `--camel #C19A6B`, `--ocre #CC7722`, `--ocre-fonce #8F4E0F`, `--chene #2A1D14`, `--malbec #5A1F2B`.
- Tout couple texte/fond utilisé ≥ 4.5:1 (WCAG AA).
- Polices : Cormorant Garamond (600/700) pour les titres, Lato (400/700) pour le texte, via Google Fonts ; replis `Georgia, serif` / `system-ui, sans-serif`.
- Mention obligatoire en pied de page, texte exact : `L'abus d'alcool est dangereux pour la santé, à consommer avec modération.`
- Aucune dépendance, aucun `package.json`, aucun build. Chemins d'assets **relatifs** (pas de `/` initial).
- Site entièrement lisible et navigable sans JavaScript.
- Animations désactivées sous `prefers-reduced-motion: reduce`.
- Cibles tactiles ≥ 44 px ; barre de contact fixe en bas sur mobile (< 768 px).
- Domaine : `simonlaugueux.fr` (fichier `CNAME`).
- Éléments vides HTML écrits sans `/>` (style attendu par html-validate).
- **Commits : l'utilisateur exige son accord avant tout commit.** Chaque étape « Commit » consiste à demander l'accord, puis à commiter seulement après un oui explicite.

## Review Focus

1. **Accents et retours à la ligne dans les `mailto:`** — un objet « Demande de dégustation » ou un corps multi-lignes non encodé casse le lien sur certains clients mail ; tout `href` mailto doit être percent-encodé, sans `&amp;` résiduel après décodage HTML (test `test_mailto_encodes_et_avec_objet`, Task 2).
2. **JavaScript désactivé ou en échec** — le menu et toutes les sections doivent rester visibles ; aucun masquage (`display: none` / `opacity: 0`) de contenu hors d'un sélecteur `.js …` (test `test_contenu_visible_sans_js`, Task 3 ; tests Node de repli sans `IntersectionObserver`, Task 4).
3. **Barre de contact mobile qui recouvre le pied de page** — la mention loi Évin doit rester lisible en bas de page : `padding-bottom` sur `body` en mobile, barre masquée en desktop (test `test_barre_mobile_ne_masque_pas_le_pied`, Task 3).
4. **Date affichée incohérente avec son `datetime`** — en éditant les dates à la main, on se trompe de jour de semaine ; le jour affiché doit correspondre à la date ISO (test `test_dates_coherentes`, Task 2).
5. **Assets introuvables une fois sur GitHub Pages** — un chemin absolu `/assets/…` ou un fichier manquant donne une page sans style ni icônes ; toute référence locale HTML et CSS doit être relative et exister (tests `test_references_html_relatives_et_existantes` et `test_references_css_existantes`, Task 5).

---

## Structure des fichiers

| Fichier | Responsabilité | Tâche |
|---|---|---|
| `tests/test_site.py` | Vérifications statiques HTML/CSS/assets (stdlib) | 1 → 5 (ajouts) |
| `index.html` | Contenu et structure de la page | 1 (squelette), 2 (contenu) |
| `CNAME`, `.nojekyll` | Configuration GitHub Pages | 1 |
| `assets/css/style.css` | Palette, typographie, mise en page, responsive, animations | 3 |
| `assets/img/*.svg` | Icônes, texture bois, ornement, favicon | 5 |
| `tools/og_image.py`, `assets/img/og-image.png` | Image de partage Open Graph | 5 |
| `assets/js/main.js` | Menu burger + apparition au scroll | 4 |
| `tests/main.test.mjs` | Test du comportement JS avec un faux DOM | 4 |
| `README.md`, `.htmlvalidate.json` | Maintenance, contenu à valider, DNS ; config validateur | 6 |

Lancer les tests Python : `python3 -m unittest discover -s tests -v` (depuis la racine du dépôt).

---

### Task 1: Harnais de test + squelette HTML (head, SEO, navigation, pied de page)

**Files:**
- Create: `tests/test_site.py`
- Create: `index.html`
- Create: `CNAME`
- Create: `.nojekyll`

**Interfaces:**
- Consumes: rien.
- Produces:
  - `tests/test_site.py` : constantes `ROOT: Path`, `PHONE_HREF = "tel:+33781631578"`, `EMAIL = "simonlaugueux@proton.me"`, `SECTIONS = ["accueil", "univers", "formules", "dates", "contact"]` ; classe `Element` avec `.tag: str`, `.attrs: dict[str, str]`, `.text() -> str` (texte des descendants, espaces normalisés), `.iter()` (descendants), `.find_all(tag=None, cls=None, **attrs) -> list[Element]`, `.find(...) -> Element | None` ; fonction `load_page() -> Element` (racine du document `index.html`). Pour un attribut avec tiret : `find("nav", **{"aria-label": "…"})`.
  - `index.html` : `<main id="contenu">` contenant 5 `<section>` d'ids `SECTIONS`, chacune avec `aria-labelledby="titre-<id>"` ; `<ul class="nav-liste" id="menu">` ; `<button class="nav-toggle" aria-controls="menu" aria-expanded="false">` ; `<footer class="pied">`. Les tâches suivantes remplacent le contenu de `<main>` et s'appuient sur ces noms.

- [ ] **Step 1: Écrire les tests qui échouent**

Créer `tests/test_site.py` :

```python
"""Vérifications statiques du site (bibliothèque standard uniquement).

Lancer depuis la racine du dépôt : python3 -m unittest discover -s tests -v
"""
import json
import re
import struct
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
PHONE_HREF = "tel:+33781631578"
EMAIL = "simonlaugueux@proton.me"
SECTIONS = ["accueil", "univers", "formules", "dates", "contact"]
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `python3 -m unittest discover -s tests -v`
Expected: ERROR sur chaque test avec `FileNotFoundError: … index.html`.

- [ ] **Step 3: Écrire le squelette**

Créer `CNAME` (une seule ligne) :

```
simonlaugueux.fr
```

Créer `.nojekyll` vide : `touch .nojekyll`

Créer `index.html` :

```html
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Simon Laugueux · Dégustations de vins &amp; spiritueux à Cahors</title>
  <meta name="description" content="Dégustations commentées de vins de Cahors et de spiritueux élevés en fût de chêne, pour particuliers, entreprises, CE, événements privés et touristes dans le Lot.">
  <link rel="canonical" href="https://simonlaugueux.fr/">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:url" content="https://simonlaugueux.fr/">
  <meta property="og:title" content="Simon Laugueux · Dégustations de vins &amp; spiritueux">
  <meta property="og:description" content="Vins de Cahors et spiritueux élevés en fût de chêne : dégustations commentées dans le Lot.">
  <meta property="og:image" content="https://simonlaugueux.fr/assets/img/og-image.png">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&amp;family=Lato:wght@400;700&amp;display=swap">
  <link rel="stylesheet" href="assets/css/style.css">
  <script src="assets/js/main.js" defer></script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "Simon Laugueux – Dégustations de vins & spiritueux",
    "description": "Dégustations commentées de vins de Cahors et de spiritueux élevés en fût de chêne, dans le Lot.",
    "url": "https://simonlaugueux.fr/",
    "image": "https://simonlaugueux.fr/assets/img/og-image.png",
    "telephone": "+33781631578",
    "email": "simonlaugueux@proton.me",
    "areaServed": [
      { "@type": "City", "name": "Cahors" },
      { "@type": "AdministrativeArea", "name": "Lot" }
    ]
  }
  </script>
</head>
<body>
  <a class="lien-evitement" href="#contenu">Aller au contenu</a>

  <header class="entete">
    <nav class="nav conteneur" aria-label="Navigation principale">
      <a class="logo" href="#accueil">Simon Laugueux</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="menu">
        <span class="nav-toggle-barres" aria-hidden="true"></span>
        <span class="visually-hidden">Menu</span>
      </button>
      <ul class="nav-liste" id="menu">
        <li><a href="#univers">L'univers</a></li>
        <li><a href="#formules">Formules</a></li>
        <li><a href="#dates">Dates</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main id="contenu">
    <section id="accueil" class="hero" aria-labelledby="titre-accueil">
      <h1 id="titre-accueil">Simon Laugueux</h1>
    </section>
    <section id="univers" class="section" aria-labelledby="titre-univers">
      <h2 id="titre-univers">L'univers</h2>
    </section>
    <section id="formules" class="section" aria-labelledby="titre-formules">
      <h2 id="titre-formules">Les formules</h2>
    </section>
    <section id="dates" class="section" aria-labelledby="titre-dates">
      <h2 id="titre-dates">Prochaines dates</h2>
    </section>
    <section id="contact" class="section" aria-labelledby="titre-contact">
      <h2 id="titre-contact">Réserver une dégustation</h2>
    </section>
  </main>

  <footer class="pied">
    <div class="conteneur">
      <p class="evin">L'abus d'alcool est dangereux pour la santé, à consommer avec modération.</p>
      <p>© 2026 Simon Laugueux · Dégustations de vins &amp; spiritueux · Cahors, Lot</p>
    </div>
  </footer>
</body>
</html>
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `python3 -m unittest discover -s tests -v`
Expected: 13 tests, `OK`.

- [ ] **Step 5: Commit (après accord de l'utilisateur)**

```bash
git add tests/test_site.py index.html CNAME .nojekyll
git commit -m "feat: squelette HTML, SEO local et harnais de test"
```

---

### Task 2: Contenu des sections, liens de réservation et barre de contact mobile

**Files:**
- Modify: `index.html` — remplacer tout le bloc `<main id="contenu"> … </main>` ; insérer la barre de contact entre `</main>` et `<footer class="pied">`
- Test: `tests/test_site.py` — ajouter à la fin (avant le bloc `if __name__ == "__main__":`)

**Interfaces:**
- Consumes: `load_page()`, `Element.find/find_all/text`, `PHONE_HREF`, `EMAIL` (Task 1).
- Produces (classes/ids utilisés par le CSS de la Task 3, le JS de la Task 4 et les assets de la Task 5) :
  - Sections : `section.hero` (#accueil) ; `section.section.reveal` (#univers, #dates) ; `section.section.section-camel.reveal` (#formules) ; `section.section.section-contact.reveal` (#contact).
  - Blocs : `.conteneur`, `.hero-contenu`, `.hero-surtitre`, `.hero-sous-titre`, `.hero-accroche`, `.actions`, `.bouton` + `.bouton-principal` / `.bouton-secondaire` / `.bouton-clair`, `.separateur`, `.intro`, `.atouts` > `li.atout`, `.formules` > `article.formule` (`.formule-infos`, `p.prix`), `aside.encart-touristes` (`.lien`), `ul.dates-liste` > `li.date` (`time`, `.date-lieu`, `.date-theme`), `p.dates-repli`, `.contact-actions` > `a.contact-carte` (`.contact-label`, `.contact-valeur`), `p.zone`, `nav.barre-contact`.
  - Images référencées (créées en Task 5) : `assets/img/grappe.svg`, `assets/img/barrique.svg`, `assets/img/verre.svg`, `assets/img/carafe.svg`.

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter dans `tests/test_site.py`, avant `if __name__ == "__main__":` :

```python
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


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
        self.assertGreaterEqual(len(mails), 6)
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
        self.assertIn("Cahors, le Lot et alentours", contact)

    def test_trois_formules_completes(self):
        formules = self.page.find("section", id="formules").find_all("article", cls="formule")
        titres = [f.find("h3").text() for f in formules]
        self.assertEqual(titres, ["Particuliers & amis", "Entreprises & CE", "Événements privés"])
        for f in formules:
            self.assertIn("à partir de", f.find("p", cls="prix").text())
            self.assertEqual(len(self.liens("mailto:", f)), 1)

    def test_encart_touristes(self):
        encart = self.page.find("aside", cls="encart-touristes")
        self.assertIsNotNone(encart)
        self.assertIn("De passage dans le Lot", encart.text())
        self.assertEqual(len(self.liens(PHONE_HREF, encart)), 1)

    def test_dates_coherentes(self):
        items = self.page.find("ul", cls="dates-liste").find_all("li", cls="date")
        self.assertGreaterEqual(len(items), 1)
        for li in items:
            t = li.find("time")
            jour = date.fromisoformat(t.attrs["datetime"])
            self.assertTrue(t.text().lower().startswith(JOURS[jour.weekday()]), t.text())
            self.assertIn(str(jour.day), t.text().split())
            self.assertTrue(li.find(cls="date-lieu").text())
            self.assertTrue(li.find(cls="date-theme").text())

    def test_repli_si_aucune_date(self):
        repli = self.page.find("p", cls="dates-repli")
        self.assertIn("Organisons la vôtre", repli.text())
        self.assertTrue(repli.find("a").attrs["href"].startswith("mailto:"))

    def test_barre_contact_mobile(self):
        barre = self.page.find("nav", cls="barre-contact")
        self.assertEqual(barre.attrs.get("aria-label"), "Contact rapide")
        hrefs = [a.attrs.get("href", "") for a in barre.find_all("a")]
        self.assertEqual(len(hrefs), 2)
        self.assertEqual(hrefs[0], PHONE_HREF)
        self.assertTrue(hrefs[1].startswith("mailto:"))

    def test_tarifs_signales_indicatifs(self):
        self.assertIn("Tarifs indicatifs", self.page.find("section", id="formules").text())
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `python3 -m unittest discover -s tests -v`
Expected: les 11 tests `TestContenu` en FAIL/ERROR (par ex. `AssertionError: 0 not greater than or equal to 4`, `AttributeError: 'NoneType' object has no attribute 'find_all'`) ; les 13 tests de la Task 1 restent OK.

- [ ] **Step 3: Écrire le contenu**

Dans `index.html`, remplacer tout le bloc `<main id="contenu"> … </main>` par le bloc ci-dessous, suivi de la barre de contact (qui se retrouve donc entre `</main>` et `<footer class="pied">`) :

```html
  <main id="contenu">
    <section id="accueil" class="hero" aria-labelledby="titre-accueil">
      <div class="conteneur hero-contenu">
        <p class="hero-surtitre">Cahors &amp; le Lot</p>
        <h1 id="titre-accueil">Simon Laugueux</h1>
        <p class="hero-sous-titre">Dégustations de vins &amp; spiritueux</p>
        <p class="hero-accroche">Des vins de Cahors aux eaux-de-vie patiemment élevées en barriques de chêne&nbsp;: je vous fais découvrir ce que le bois, le temps et le terroir racontent dans le verre.</p>
        <div class="actions">
          <a class="bouton bouton-principal" href="tel:+33781631578">Appeler le 07 81 63 15 78</a>
          <a class="bouton bouton-clair" href="mailto:simonlaugueux@proton.me?subject=Demande%20de%20d%C3%A9gustation&amp;body=Bonjour%20Simon%2C%0A%0AJe%20souhaite%20organiser%20une%20d%C3%A9gustation.%0A%0ADate%20souhait%C3%A9e%20%3A%20%0ANombre%20de%20personnes%20%3A%20%0AType%20d%27%C3%A9v%C3%A9nement%20%3A%20%0ALieu%20%3A%20%0A%0AMerci%20%21">Réserver par e-mail</a>
        </div>
      </div>
    </section>

    <section id="univers" class="section reveal" aria-labelledby="titre-univers">
      <div class="conteneur">
        <div class="separateur" aria-hidden="true"></div>
        <h2 id="titre-univers">L'univers</h2>
        <p class="intro">Le Cahors, c'est d'abord le malbec&nbsp;: un vin sombre et profond, que l'on surnomme «&nbsp;le vin noir&nbsp;». Autour de lui, je propose des dégustations commentées de vins du Sud-Ouest et de spiritueux élevés en fût de chêne, pour comprendre comment la barrique façonne les arômes, la texture et la couleur.</p>
        <ul class="atouts">
          <li class="atout">
            <img src="assets/img/grappe.svg" alt="" width="48" height="48">
            <h3>Terroir du Lot</h3>
            <p>Des vins et des producteurs de la région, choisis pour leur caractère.</p>
          </li>
          <li class="atout">
            <img src="assets/img/barrique.svg" alt="" width="48" height="48">
            <h3>Élevage en fût de chêne</h3>
            <p>Ce que le bois apporte&nbsp;: vanille, épices, notes fumées et une texture plus ronde.</p>
          </li>
          <li class="atout">
            <img src="assets/img/verre.svg" alt="" width="48" height="48">
            <h3>Dégustation commentée</h3>
            <p>Un moment convivial et accessible, que l'on soit novice ou amateur éclairé.</p>
          </li>
        </ul>
      </div>
    </section>

    <section id="formules" class="section section-camel reveal" aria-labelledby="titre-formules">
      <div class="conteneur">
        <div class="separateur" aria-hidden="true"></div>
        <h2 id="titre-formules">Les formules</h2>
        <p class="intro">Chaque dégustation s'adapte à votre groupe, à votre lieu et à vos envies. Tarifs indicatifs, devis sur demande.</p>
        <div class="formules">
          <article class="formule">
            <h3>Particuliers &amp; amis</h3>
            <p>Une soirée de dégustation chez vous ou sur place, entre amis ou en famille.</p>
            <ul class="formule-infos">
              <li>Durée&nbsp;: environ 2&nbsp;h</li>
              <li>À partir de 6 personnes</li>
            </ul>
            <p class="prix">à partir de 35&nbsp;€ / pers.</p>
            <a class="bouton bouton-secondaire" href="mailto:simonlaugueux@proton.me?subject=D%C3%A9gustation%20entre%20amis">Demander une date</a>
          </article>
          <article class="formule">
            <h3>Entreprises &amp; CE</h3>
            <p>Séminaires, afterworks, team-building ou offre CE&nbsp;: une dégustation pour fédérer vos équipes.</p>
            <ul class="formule-infos">
              <li>Durée&nbsp;: 1&nbsp;h&nbsp;30 à 2&nbsp;h</li>
              <li>De 10 à 50 personnes</li>
            </ul>
            <p class="prix">à partir de 30&nbsp;€ / pers.</p>
            <a class="bouton bouton-secondaire" href="mailto:simonlaugueux@proton.me?subject=D%C3%A9gustation%20entreprise%20/%20CE">Demander un devis</a>
          </article>
          <article class="formule">
            <h3>Événements privés</h3>
            <p>Mariages, anniversaires, fêtes de famille&nbsp;: une animation dégustation pour marquer le moment.</p>
            <ul class="formule-infos">
              <li>Durée&nbsp;: sur mesure</li>
              <li>Devis personnalisé</li>
            </ul>
            <p class="prix">à partir de 300&nbsp;€ la prestation</p>
            <a class="bouton bouton-secondaire" href="mailto:simonlaugueux@proton.me?subject=D%C3%A9gustation%20%C3%A9v%C3%A9nement%20priv%C3%A9">Parlons de votre événement</a>
          </article>
        </div>
        <aside class="encart-touristes" aria-labelledby="titre-touristes">
          <img src="assets/img/carafe.svg" alt="" width="48" height="48">
          <div>
            <h3 id="titre-touristes">De passage dans le Lot&nbsp;?</h3>
            <p>Vacanciers et curieux&nbsp;: je propose aussi des dégustations découverte en petit groupe. Appelez-moi pour connaître les prochaines disponibilités.</p>
            <a class="bouton bouton-principal" href="tel:+33781631578">Appeler</a>
            <a class="lien" href="mailto:simonlaugueux@proton.me?subject=D%C3%A9gustation%20d%C3%A9couverte%20%28de%20passage%20dans%20le%20Lot%29">ou écrire un e-mail</a>
          </div>
        </aside>
      </div>
    </section>

    <section id="dates" class="section reveal" aria-labelledby="titre-dates">
      <div class="conteneur">
        <div class="separateur" aria-hidden="true"></div>
        <h2 id="titre-dates">Prochaines dates</h2>
        <ul class="dates-liste">
          <li class="date">
            <time datetime="2026-10-17">Samedi 17 octobre 2026</time>
            <span class="date-lieu">Cahors</span>
            <span class="date-theme">Le malbec dans tous ses états</span>
          </li>
          <li class="date">
            <time datetime="2026-11-14">Samedi 14 novembre 2026</time>
            <span class="date-lieu">Luzech</span>
            <span class="date-theme">Spiritueux et fûts de chêne</span>
          </li>
          <li class="date">
            <time datetime="2026-12-05">Samedi 5 décembre 2026</time>
            <span class="date-lieu">Cahors</span>
            <span class="date-theme">Accords vins &amp; fêtes de fin d'année</span>
          </li>
        </ul>
        <p class="dates-repli">Aucune date ne vous convient&nbsp;? <a href="mailto:simonlaugueux@proton.me?subject=Demande%20de%20d%C3%A9gustation">Organisons la vôtre.</a></p>
      </div>
    </section>

    <section id="contact" class="section section-contact reveal" aria-labelledby="titre-contact">
      <div class="conteneur">
        <h2 id="titre-contact">Réserver une dégustation</h2>
        <p class="intro">Un appel ou un e-mail suffit&nbsp;: dites-moi la date, le nombre de personnes et le type d'événement, je vous réponds rapidement.</p>
        <div class="contact-actions">
          <a class="contact-carte" href="tel:+33781631578">
            <span class="contact-label">Téléphone</span>
            <span class="contact-valeur">07 81 63 15 78</span>
          </a>
          <a class="contact-carte" href="mailto:simonlaugueux@proton.me?subject=Demande%20de%20d%C3%A9gustation&amp;body=Bonjour%20Simon%2C%0A%0AJe%20souhaite%20organiser%20une%20d%C3%A9gustation.%0A%0ADate%20souhait%C3%A9e%20%3A%20%0ANombre%20de%20personnes%20%3A%20%0AType%20d%27%C3%A9v%C3%A9nement%20%3A%20%0ALieu%20%3A%20%0A%0AMerci%20%21">
            <span class="contact-label">E-mail</span>
            <span class="contact-valeur">simonlaugueux@proton.me</span>
          </a>
        </div>
        <p class="zone">Zone d'intervention&nbsp;: Cahors, le Lot et alentours.</p>
      </div>
    </section>
  </main>

  <nav class="barre-contact" aria-label="Contact rapide">
    <a href="tel:+33781631578">Appeler</a>
    <a href="mailto:simonlaugueux@proton.me?subject=Demande%20de%20d%C3%A9gustation&amp;body=Bonjour%20Simon%2C%0A%0AJe%20souhaite%20organiser%20une%20d%C3%A9gustation.%0A%0ADate%20souhait%C3%A9e%20%3A%20%0ANombre%20de%20personnes%20%3A%20%0AType%20d%27%C3%A9v%C3%A9nement%20%3A%20%0ALieu%20%3A%20%0A%0AMerci%20%21">E-mail</a>
  </nav>
```

Note : `&nbsp;` est décodé en U+00A0 par le parseur ; `text()` le traite comme un espace (`str.split()`), les assertions de texte restent donc valides. Les valeurs de `href` ne contiennent jamais de `&nbsp;`.

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `python3 -m unittest discover -s tests -v`
Expected: 24 tests, `OK`.

- [ ] **Step 5: Commit (après accord de l'utilisateur)**

```bash
git add index.html tests/test_site.py
git commit -m "feat: contenu des sections, liens de réservation et barre mobile"
```

---

### Task 3: Feuille de style (palette, typographie, mise en page, responsive, animations)

**Files:**
- Create: `assets/css/style.css`
- Test: `tests/test_site.py` — ajouter avant `if __name__ == "__main__":`

**Interfaces:**
- Consumes: les classes HTML listées dans « Produces » de la Task 2 ; `load_page()` (Task 1).
- Produces :
  - Classe `js` posée sur `<html>` par le JS (Task 4) : tout masquage de contenu est scopé `.js …`.
  - Classes d'état attendues du JS : `.nav-liste.ouvert` (menu ouvert en mobile), `.reveal.visible` (section apparue).
  - `url("../img/bois.svg")` et `url("../img/douelles.svg")` référencés (créés en Task 5).
  - Helpers de test `css_rules(css) -> list[(selecteur, corps)]`, `media_blocks(css, condition) -> str`, `contraste(hex1, hex2) -> float`.

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter dans `tests/test_site.py`, avant `if __name__ == "__main__":` :

```python
CSS = ROOT / "assets" / "css" / "style.css"
PALETTE = {
    "parchemin": "#F6EFE3", "camel": "#C19A6B", "ocre": "#CC7722",
    "ocre-fonce": "#8F4E0F", "chene": "#2A1D14", "malbec": "#5A1F2B",
}
# (texte, fond) réellement utilisés dans style.css — à tenir à jour si on en ajoute
PAIRES = [
    ("chene", "parchemin"), ("chene", "camel"), ("chene", "ocre"),
    ("parchemin", "chene"), ("parchemin", "ocre-fonce"), ("parchemin", "malbec"),
    ("malbec", "parchemin"), ("malbec", "camel"),
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

    def test_polices(self):
        fonts = [l.attrs["href"] for l in self.page.find_all("link", rel="stylesheet")
                 if "fonts.googleapis.com" in l.attrs["href"]]
        self.assertEqual(len(fonts), 1)
        self.assertIn("Cormorant+Garamond", fonts[0])
        self.assertIn("Lato", fonts[0])
        self.assertIn('"Cormorant Garamond", Georgia, serif', self.css)
        self.assertIn('"Lato", system-ui, sans-serif', self.css)
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `python3 -m unittest discover -s tests -v`
Expected: `TestStyles` en ERROR (`FileNotFoundError: … assets/css/style.css`) ; les 24 tests précédents restent OK.

- [ ] **Step 3: Écrire la feuille de style**

Créer `assets/css/style.css` :

```css
/* Simon Laugueux — dégustations de vins & spiritueux */

:root {
  --parchemin: #F6EFE3;
  --camel: #C19A6B;
  --ocre: #CC7722;
  --ocre-fonce: #8F4E0F;
  --chene: #2A1D14;
  --malbec: #5A1F2B;

  --police-titre: "Cormorant Garamond", Georgia, serif;
  --police-texte: "Lato", system-ui, sans-serif;
  --rayon: 10px;
  --ombre: 0 6px 20px rgba(42, 29, 20, 0.12);
  --filet: rgba(42, 29, 20, 0.2);
  --largeur: 1100px;
  --hauteur-barre: 64px;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  scroll-padding-top: 72px;
}

body {
  margin: 0;
  background: var(--parchemin);
  color: var(--chene);
  font-family: var(--police-texte);
  font-size: 1.0625rem;
  line-height: 1.65;
}

img {
  display: block;
  max-width: 100%;
  height: auto;
}

h1,
h2,
h3 {
  margin: 0 0 0.5em;
  font-family: var(--police-titre);
  font-weight: 700;
  line-height: 1.15;
}

h1 { font-size: clamp(2.75rem, 8vw, 5rem); }
h2 { font-size: clamp(2rem, 5vw, 3rem); }
h3 { font-size: 1.5rem; }

p { margin: 0 0 1rem; }

a { color: var(--malbec); }
a:hover { color: var(--chene); }

:focus-visible {
  outline: 3px solid var(--malbec);
  outline-offset: 3px;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}

.lien-evitement {
  position: absolute;
  top: -100px;
  left: 1rem;
  z-index: 100;
  padding: 0.75rem 1rem;
  border-radius: var(--rayon);
  background: var(--chene);
  color: var(--parchemin);
}

.lien-evitement:focus { top: 1rem; }

.conteneur {
  width: 100%;
  max-width: var(--largeur);
  margin: 0 auto;
  padding: 0 1rem;
}

/* En-tête et navigation */

.entete {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--parchemin);
  border-bottom: 1px solid var(--filet);
}

.nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0 1rem;
  min-height: 64px;
}

.logo {
  font-family: var(--police-titre);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--chene);
  text-decoration: none;
}

.nav-liste {
  display: flex;
  flex-wrap: wrap;
  gap: 0 1.25rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.nav-liste a {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  color: var(--chene);
  font-weight: 700;
  text-decoration: none;
}

.nav-liste a:hover {
  color: var(--malbec);
  text-decoration: underline;
  text-underline-offset: 4px;
}

.nav-toggle { display: none; }

/* Boutons */

.bouton {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  font-weight: 700;
  text-decoration: none;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.bouton-principal { background: var(--chene); color: var(--parchemin); }
.bouton-principal:hover { background: var(--malbec); color: var(--parchemin); }
.bouton-secondaire { background: var(--ocre-fonce); color: var(--parchemin); }
.bouton-secondaire:hover { background: var(--chene); color: var(--parchemin); }
.bouton-clair { background: var(--parchemin); color: var(--chene); }
.bouton-clair:hover { background: var(--chene); color: var(--parchemin); }

/* Hero */

.hero {
  padding: clamp(4rem, 12vw, 8rem) 0;
  background:
    url("../img/bois.svg") center / cover no-repeat,
    linear-gradient(135deg, var(--camel) 0%, var(--ocre) 100%);
}

.hero-surtitre {
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.hero-sous-titre {
  font-family: var(--police-titre);
  font-size: clamp(1.5rem, 4vw, 2.25rem);
  font-weight: 600;
}

.hero-accroche {
  max-width: 40rem;
  margin-bottom: 2rem;
  font-size: 1.125rem;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

/* Sections */

.section { padding: clamp(3.5rem, 8vw, 6rem) 0; }
.section-camel { background: var(--camel); }

.intro {
  max-width: 46rem;
  margin-bottom: 2.5rem;
  font-size: 1.125rem;
}

.separateur {
  width: 200px;
  height: 32px;
  margin-bottom: 1rem;
  background: url("../img/douelles.svg") left center / 200px 32px no-repeat;
}

/* L'univers */

.atouts,
.formules {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1.5rem;
}

.atouts {
  margin: 0;
  padding: 0;
  list-style: none;
}

.atout {
  padding-top: 1.5rem;
  border-top: 3px solid var(--ocre);
}

.atout img { margin-bottom: 1rem; }

/* Formules */

.formule {
  display: flex;
  flex-direction: column;
  padding: 1.75rem;
  border-radius: var(--rayon);
  background: var(--parchemin);
  box-shadow: var(--ombre);
}

.formule-infos {
  margin: 0 0 1rem;
  padding: 0;
  list-style: none;
}

.formule-infos li::before {
  content: "— ";
  color: var(--ocre-fonce);
}

.prix {
  margin-top: auto;
  font-family: var(--police-titre);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--malbec);
}

.formule .bouton { align-self: flex-start; }

.encart-touristes {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1.5rem;
  margin-top: 2rem;
  padding: 1.75rem;
  border: 2px dashed var(--chene);
  border-radius: var(--rayon);
}

.encart-touristes > div { flex: 1 1 18rem; }

.encart-touristes .lien {
  display: inline-block;
  margin-left: 1rem;
  padding: 0.75rem 0;
  color: var(--chene);
  font-weight: 700;
}

/* Prochaines dates */

.dates-liste {
  margin: 0 0 2rem;
  padding: 0;
  list-style: none;
  border-top: 1px solid var(--filet);
}

.date {
  display: grid;
  gap: 0.25rem 1.5rem;
  padding: 1.25rem 0;
  border-bottom: 1px solid var(--filet);
}

.date time {
  font-weight: 700;
  color: var(--malbec);
}

.date-theme {
  font-family: var(--police-titre);
  font-size: 1.375rem;
  font-weight: 600;
}

/* Contact */

.section-contact {
  background: var(--chene);
  color: var(--parchemin);
}

.section-contact :focus-visible { outline-color: var(--camel); }

.contact-actions {
  display: grid;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.contact-carte {
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  border-radius: var(--rayon);
  background: var(--ocre-fonce);
  color: var(--parchemin);
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.contact-carte:hover {
  background: var(--malbec);
  color: var(--parchemin);
}

.contact-label {
  font-size: 0.8125rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.contact-valeur {
  font-family: var(--police-titre);
  font-size: clamp(1.5rem, 5vw, 2.25rem);
  font-weight: 700;
  overflow-wrap: anywhere;
}

/* Pied de page */

.pied {
  padding: 2rem 0;
  border-top: 1px solid rgba(246, 239, 227, 0.15);
  background: var(--chene);
  color: var(--parchemin);
  font-size: 0.9375rem;
}

.evin { font-weight: 700; }

/* Barre de contact mobile */

.barre-contact {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 60;
  display: grid;
  grid-template-columns: 1fr 1fr;
  height: var(--hauteur-barre);
  background: var(--chene);
  box-shadow: 0 -4px 16px rgba(42, 29, 20, 0.2);
}

.barre-contact a {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--parchemin);
  font-weight: 700;
  text-decoration: none;
}

.barre-contact a + a { background: var(--ocre-fonce); }

/* Apparition au scroll (uniquement si le JS a posé la classe .js) */

.js .reveal {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.js .reveal.visible {
  opacity: 1;
  transform: none;
}

/* Responsive */

@media (max-width: 767px) {
  body { padding-bottom: var(--hauteur-barre); }

  .js .nav-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--chene);
    cursor: pointer;
  }

  .nav-toggle-barres,
  .nav-toggle-barres::before,
  .nav-toggle-barres::after {
    display: block;
    position: relative;
    width: 24px;
    height: 2px;
    background: currentColor;
  }

  .nav-toggle-barres::before,
  .nav-toggle-barres::after {
    content: "";
    position: absolute;
    left: 0;
  }

  .nav-toggle-barres::before { top: -7px; }
  .nav-toggle-barres::after { top: 7px; }

  .js .nav-liste {
    display: none;
    flex-direction: column;
    width: 100%;
    padding-bottom: 0.75rem;
  }

  .js .nav-liste.ouvert { display: flex; }
}

@media (min-width: 768px) {
  .barre-contact { display: none; }

  .contact-actions { grid-template-columns: 1fr 1fr; }

  .date {
    grid-template-columns: 15rem 9rem 1fr;
    align-items: baseline;
  }
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }

  .js .reveal {
    opacity: 1;
    transform: none;
    transition: none;
  }

  .bouton,
  .contact-carte { transition: none; }
}
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `python3 -m unittest discover -s tests -v`
Expected: 35 tests, `OK`.

- [ ] **Step 5: Commit (après accord de l'utilisateur)**

```bash
git add assets/css/style.css tests/test_site.py
git commit -m "feat: feuille de style ocre et camel, responsive et accessible"
```

---

### Task 4: JavaScript — menu burger et apparition au scroll

**Files:**
- Create: `assets/js/main.js`
- Create: `tests/main.test.mjs`
- Test: `tests/test_site.py` — ajouter avant `if __name__ == "__main__":`

**Interfaces:**
- Consumes: `button.nav-toggle[aria-controls="menu"]`, `#menu`, `.reveal` (Tasks 1–2) ; classes CSS `.js`, `.nav-liste.ouvert`, `.reveal.visible` (Task 3).
- Produces: script autonome (IIFE, pas de module, pas d'export) qui : ajoute `js` à `document.documentElement.classList` ; bascule `aria-expanded` et la classe `ouvert` au clic sur le bouton ; referme le menu au clic sur un lien du menu ; ajoute `visible` aux `.reveal` à l'entrée dans le viewport, ou immédiatement si `prefers-reduced-motion: reduce` ou si `window.IntersectionObserver` est absent. N'utilise que `document.documentElement`, `document.querySelector`, `document.getElementById`, `document.querySelectorAll`, `window.matchMedia`, `window.IntersectionObserver` (le test Node fournit exactement ces API).

- [ ] **Step 1: Écrire les tests qui échouent**

Créer `tests/main.test.mjs` :

```js
// Test du comportement de assets/js/main.js avec un faux DOM minimal.
// Lancer : node --test tests/main.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const code = readFileSync(new URL("../assets/js/main.js", import.meta.url), "utf8");

class FakeClassList {
  constructor() { this.noms = new Set(); }
  add(n) { this.noms.add(n); }
  remove(n) { this.noms.delete(n); }
  contains(n) { return this.noms.has(n); }
  toggle(n, force) {
    const actif = force === undefined ? !this.noms.has(n) : force;
    if (actif) this.noms.add(n); else this.noms.delete(n);
    return actif;
  }
}

class FakeElement {
  constructor(tag, parent = null) {
    this.tagName = tag.toUpperCase();
    this.parent = parent;
    this.classList = new FakeClassList();
    this.attrs = {};
    this.listeners = {};
  }
  getAttribute(n) { return n in this.attrs ? this.attrs[n] : null; }
  setAttribute(n, v) { this.attrs[n] = String(v); }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  dispatch(type, target = this) { (this.listeners[type] || []).forEach((fn) => fn({ target })); }
  closest(sel) {
    for (let el = this; el; el = el.parent) {
      if (el.tagName === sel.toUpperCase()) return el;
    }
    return null;
  }
}

function charger({ mouvementReduit = false, observer = true } = {}) {
  const racine = new FakeElement("html");
  const bouton = new FakeElement("button");
  bouton.setAttribute("aria-expanded", "false");
  const menu = new FakeElement("ul");
  const lien = new FakeElement("a", new FakeElement("li", menu));
  const reveals = [new FakeElement("section"), new FakeElement("section")];
  const observes = [];
  let rappel = null;

  const document = {
    documentElement: racine,
    querySelector: (s) => (s === ".nav-toggle" ? bouton : null),
    getElementById: (id) => (id === "menu" ? menu : null),
    querySelectorAll: (s) => (s === ".reveal" ? reveals : []),
  };
  const window = { matchMedia: () => ({ matches: mouvementReduit }) };
  if (observer) {
    window.IntersectionObserver = class {
      constructor(cb) { rappel = cb; }
      observe(el) { observes.push(el); }
      unobserve(el) { observes.splice(observes.indexOf(el), 1); }
    };
  }
  vm.runInNewContext(code, { document, window });
  return { racine, bouton, menu, lien, reveals, observes, declencher: (entries) => rappel(entries) };
}

test("pose la classe js sur <html>", () => {
  assert.ok(charger().racine.classList.contains("js"));
});

test("le bouton ouvre puis referme le menu", () => {
  const { bouton, menu } = charger();
  bouton.dispatch("click");
  assert.equal(bouton.getAttribute("aria-expanded"), "true");
  assert.ok(menu.classList.contains("ouvert"));
  bouton.dispatch("click");
  assert.equal(bouton.getAttribute("aria-expanded"), "false");
  assert.ok(!menu.classList.contains("ouvert"));
});

test("cliquer un lien du menu referme le menu", () => {
  const { bouton, menu, lien } = charger();
  bouton.dispatch("click");
  menu.dispatch("click", lien);
  assert.equal(bouton.getAttribute("aria-expanded"), "false");
  assert.ok(!menu.classList.contains("ouvert"));
});

test("cliquer dans le menu hors d'un lien ne le referme pas", () => {
  const { bouton, menu } = charger();
  bouton.dispatch("click");
  menu.dispatch("click", menu);
  assert.equal(bouton.getAttribute("aria-expanded"), "true");
});

test("les sections apparaissent à l'entrée dans le viewport", () => {
  const { reveals, observes, declencher } = charger();
  assert.equal(observes.length, 2);
  assert.ok(!reveals[0].classList.contains("visible"));
  declencher([
    { isIntersecting: true, target: reveals[0] },
    { isIntersecting: false, target: reveals[1] },
  ]);
  assert.ok(reveals[0].classList.contains("visible"));
  assert.ok(!reveals[1].classList.contains("visible"));
  assert.deepEqual(observes, [reveals[1]]);
});

test("mouvement réduit : tout est visible d'emblée, rien n'est observé", () => {
  const { reveals, observes } = charger({ mouvementReduit: true });
  assert.ok(reveals.every((el) => el.classList.contains("visible")));
  assert.equal(observes.length, 0);
});

test("sans IntersectionObserver : tout est visible d'emblée", () => {
  const { reveals } = charger({ observer: false });
  assert.ok(reveals.every((el) => el.classList.contains("visible")));
});
```

Ajouter dans `tests/test_site.py`, avant `if __name__ == "__main__":` :

```python
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
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `node --test tests/main.test.mjs`
Expected: échec au chargement, `ENOENT: no such file or directory, open '…/assets/js/main.js'`.

Run: `python3 -m unittest discover -s tests -v`
Expected: `test_script_charge_en_defer` en FAIL (`False is not true`) ; les autres OK.

- [ ] **Step 3: Écrire le script**

Créer `assets/js/main.js` :

```js
// Menu mobile et apparition des sections au scroll.
// Le site reste entièrement utilisable sans ce script.
(function () {
  document.documentElement.classList.add("js");

  var bouton = document.querySelector(".nav-toggle");
  var menu = document.getElementById("menu");

  function basculerMenu(ouvert) {
    bouton.setAttribute("aria-expanded", String(ouvert));
    menu.classList.toggle("ouvert", ouvert);
  }

  if (bouton && menu) {
    bouton.addEventListener("click", function () {
      basculerMenu(bouton.getAttribute("aria-expanded") !== "true");
    });
    menu.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("a")) {
        basculerMenu(false);
      }
    });
  }

  var sections = document.querySelectorAll(".reveal");
  var mouvementReduit = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (mouvementReduit || !window.IntersectionObserver) {
    sections.forEach(function (el) { el.classList.add("visible"); });
    return;
  }

  var observateur = new window.IntersectionObserver(function (entrees) {
    entrees.forEach(function (entree) {
      if (entree.isIntersecting) {
        entree.target.classList.add("visible");
        observateur.unobserve(entree.target);
      }
    });
  }, { rootMargin: "0px 0px -10% 0px" });

  sections.forEach(function (el) { observateur.observe(el); });
})();
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `node --test tests/main.test.mjs`
Expected: `# pass 7`, `# fail 0`.

Run: `python3 -m unittest discover -s tests -v`
Expected: 38 tests, `OK`.

- [ ] **Step 5: Commit (après accord de l'utilisateur)**

```bash
git add assets/js/main.js tests/main.test.mjs tests/test_site.py
git commit -m "feat: menu mobile et apparition des sections au scroll"
```

---

### Task 5: Illustrations SVG, favicon et image Open Graph

**Files:**
- Create: `assets/img/barrique.svg`, `assets/img/verre.svg`, `assets/img/grappe.svg`, `assets/img/carafe.svg`
- Create: `assets/img/bois.svg`, `assets/img/douelles.svg`, `assets/img/favicon.svg`
- Create: `tools/og_image.py`
- Create (généré) : `assets/img/og-image.png`
- Test: `tests/test_site.py` — ajouter avant `if __name__ == "__main__":`

**Interfaces:**
- Consumes: `assets/js/main.js` (Task 4, référencé par le HTML) ; références d'images de la Task 1 (`favicon.svg`, `og-image.png`), de la Task 2 (4 icônes), de la Task 3 (`../img/bois.svg`, `../img/douelles.svg`) ; `CSS`, `lire_css()`, `load_page()`.
- Produces: tous les fichiers ci-dessus ; commande `python3 tools/og_image.py` qui (ré)écrit `assets/img/og-image.png` en 1200×630.

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter dans `tests/test_site.py`, avant `if __name__ == "__main__":` :

```python
IMG = ROOT / "assets" / "img"
SVG_ATTENDUS = {"barrique", "verre", "grappe", "carafe", "bois", "douelles", "favicon"}


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
        self.assertEqual(len(urls), 2)
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
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `python3 -m unittest discover -s tests -v`
Expected: `TestAssets` en FAIL/ERROR (`introuvable : assets/img/favicon.svg`, `FileNotFoundError: … og-image.png`, ensemble SVG vide) ; les 38 tests précédents restent OK.

- [ ] **Step 3: Créer les SVG**

`assets/img/barrique.svg` :

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="#2A1D14" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 6h20c3 5 4.5 11 4.5 18S37 37 34 42H14c-3-5-4.5-11-4.5-18S11 11 14 6z" fill="#C19A6B"/>
  <path d="M11 14h26M9.8 24h28.4M11 34h26" stroke="#8F4E0F" stroke-width="2.5"/>
  <path d="M20 6.5c-1.5 5-2.2 11-2.2 17.5s.7 12.5 2.2 17.5M28 6.5c1.5 5 2.2 11 2.2 17.5S29.5 36.5 28 41.5" stroke-width="1.2" opacity=".6"/>
</svg>
```

`assets/img/verre.svg` :

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="#2A1D14" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M15.6 14h16.8c-.3 4.5-1.4 7.4-3.3 9.2-1.4 1.3-3.2 1.8-5.1 1.8s-3.7-.5-5.1-1.8c-1.9-1.8-3-4.7-3.3-9.2z" fill="#5A1F2B" stroke="none"/>
  <path d="M15 5h18c1 9 .5 15-3 18.5-1.8 1.8-4 2.5-6 2.5s-4.2-.7-6-2.5C14.5 20 14 14 15 5z"/>
  <path d="M24 26v14M16 43h16"/>
</svg>
```

`assets/img/grappe.svg` :

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="#2A1D14" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M24 9V3M24 6c3-3 7-3 10-1"/>
  <g fill="#5A1F2B" stroke="none">
    <circle cx="15" cy="14" r="4.5"/>
    <circle cx="24" cy="14" r="4.5"/>
    <circle cx="33" cy="14" r="4.5"/>
    <circle cx="19.5" cy="22" r="4.5"/>
    <circle cx="28.5" cy="22" r="4.5"/>
    <circle cx="24" cy="30" r="4.5"/>
    <circle cx="24" cy="38.5" r="4"/>
  </g>
</svg>
```

`assets/img/carafe.svg` :

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="#2A1D14" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M11.5 30h25c-.5 6-5 10.5-12.5 10.5S12 36 11.5 30z" fill="#5A1F2B" stroke="none"/>
  <path d="M20 5h8v9c6 3 10 9 10 16 0 7-5 13-14 13S10 37 10 30c0-7 4-13 10-16z"/>
  <path d="M18.5 5h11"/>
</svg>
```

`assets/img/bois.svg` (veinage de bois très discret, posé sur le dégradé du hero) :

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" preserveAspectRatio="none" fill="none" stroke="#2A1D14" stroke-opacity="0.08" stroke-width="2">
  <path d="M0 30 C150 10 300 55 450 35 S700 20 800 40"/>
  <path d="M0 75 C160 55 320 100 480 80 S710 60 800 85"/>
  <path d="M0 120 C140 105 290 150 440 125 S690 110 800 130"/>
  <path d="M0 165 C170 150 330 195 500 170 S720 150 800 175"/>
  <path d="M0 210 C150 195 300 240 470 212 S700 195 800 220"/>
  <path d="M0 255 C160 240 320 285 480 258 S720 240 800 265"/>
  <path d="M0 300 C140 285 300 330 450 302 S690 285 800 310"/>
  <path d="M0 345 C170 330 330 375 500 348 S720 330 800 355"/>
  <path d="M0 390 C150 375 310 415 470 392 S710 375 800 398"/>
  <ellipse cx="590" cy="190" rx="46" ry="13"/>
  <ellipse cx="590" cy="190" rx="26" ry="7"/>
</svg>
```

`assets/img/douelles.svg` (ornement au-dessus des titres, raccordable horizontalement) :

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 32" width="200" height="32" fill="none" stroke-width="1.5" stroke-linecap="round">
  <path d="M0 14 Q50 4 100 14 T200 14" stroke="#8F4E0F"/>
  <path d="M0 22 Q50 12 100 22 T200 22" stroke="#2A1D14" stroke-opacity="0.5"/>
</svg>
```

`assets/img/favicon.svg` :

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <circle cx="16" cy="16" r="16" fill="#CC7722"/>
  <path d="M10 6h12c2 3.3 3 6.6 3 10s-1 6.7-3 10H10c-2-3.3-3-6.6-3-10s1-6.7 3-10z" fill="#C19A6B" stroke="#2A1D14" stroke-width="1.5"/>
  <path d="M8 11.5h16M7.2 16h17.6M8 20.5h16" stroke="#2A1D14" stroke-width="1.5"/>
</svg>
```

- [ ] **Step 4: Créer le générateur d'image Open Graph et générer l'image**

Créer `tools/og_image.py` :

```python
"""Génère assets/img/og-image.png (1200x630) : dégradé camel → ocre veiné de bois.

Bibliothèque standard uniquement. Usage : python3 tools/og_image.py
"""
import math
import struct
import zlib
from pathlib import Path

W, H = 1200, 630
CAMEL = (0xC1, 0x9A, 0x6B)
OCRE = (0xCC, 0x77, 0x22)
CHENE = (0x2A, 0x1D, 0x14)
OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "og-image.png"


def melange(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def pixel(x, y):
    couleur = melange(CAMEL, OCRE, (x / W + y / H) / 2)
    veine = math.sin(y / 9 + 3 * math.sin(x / 140) + 1.5 * math.sin(x / 37 + y / 80))
    if veine > 0.93:
        couleur = melange(couleur, CHENE, 0.12)
    return bytes(round(c) for c in couleur)


def chunk(kind, data):
    crc = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def main():
    lignes = (b"\x00" + b"".join(pixel(x, y) for x in range(W)) for y in range(H))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"".join(lignes), 9))
        + chunk(b"IEND", b"")
    )
    OUT.write_bytes(png)
    print(f"{OUT} ({len(png)} octets)")


if __name__ == "__main__":
    main()
```

Run: `python3 tools/og_image.py`
Expected: une ligne `…/assets/img/og-image.png (N octets)` (quelques secondes).

- [ ] **Step 5: Lancer les tests pour vérifier qu'ils passent**

Run: `python3 -m unittest discover -s tests -v`
Expected: 44 tests, `OK`.

- [ ] **Step 6: Commit (après accord de l'utilisateur)**

```bash
git add assets/img tools/og_image.py tests/test_site.py
git commit -m "feat: illustrations SVG, favicon et image Open Graph"
```

---

### Task 6: README, validation HTML et vérification visuelle

**Files:**
- Create: `README.md`
- Create: `.htmlvalidate.json`
- Modify (seulement si le validateur signale une erreur) : `index.html`

**Interfaces:**
- Consumes: tout le site (Tasks 1–5), commandes de test des Tasks 1 et 5, `tools/og_image.py`.
- Produces: documentation de maintenance et de mise en ligne.

- [ ] **Step 1: Lancer le validateur HTML (doit échouer faute de config)**

Créer `.htmlvalidate.json` :

```json
{
  "extends": ["html-validate:recommended"]
}
```

Run: `npx --yes html-validate index.html`
Expected: soit aucune sortie (code 0), soit une liste d'erreurs `ligne:colonne  error  message  règle`. Pour chaque erreur, corriger `index.html` en suivant le message de la règle (ne pas désactiver de règle), puis relancer jusqu'à ce que la commande ne produise plus d'erreur. Après chaque correction, relancer `python3 -m unittest discover -s tests -v` : il doit rester `OK`.

- [ ] **Step 2: Écrire le README**

Créer `README.md` :

````markdown
# simonlaugueux.fr

Site vitrine de **Simon Laugueux** — dégustations de vins & spiritueux à Cahors et dans le Lot.
Site statique d'une seule page, publié avec GitHub Pages. Aucun outil à installer pour le modifier : un éditeur de texte suffit.

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | Tout le contenu de la page |
| `assets/css/style.css` | Couleurs, polices, mise en page |
| `assets/js/main.js` | Menu mobile et animations (facultatif) |
| `assets/img/` | Icônes, texture bois, favicon, image de partage |
| `tools/og_image.py` | Régénère l'image de partage `og-image.png` |
| `tests/` | Vérifications automatiques |
| `CNAME` | Nom de domaine pour GitHub Pages |

## Modifier le contenu

### Ajouter ou retirer une date

Dans `index.html`, section `id="dates"`, copier un bloc :

```html
<li class="date">
  <time datetime="2026-10-17">Samedi 17 octobre 2026</time>
  <span class="date-lieu">Cahors</span>
  <span class="date-theme">Le malbec dans tous ses états</span>
</li>
```

- `datetime` : la date au format `AAAA-MM-JJ`.
- Le texte doit commencer par le **bon jour de la semaine** (les tests le vérifient).
- Pensez à **supprimer les dates passées**.
- S'il n'y a plus aucune date, supprimer tous les `<li>` : la phrase « Aucune date ne vous convient ? Organisons la vôtre. » reste affichée.

### Modifier une formule ou un tarif

Section `id="formules"` : chaque formule est un bloc `<article class="formule">`. Le prix est dans `<p class="prix">` et doit contenir « à partir de ».

### Changer le téléphone ou l'e-mail

Rechercher/remplacer dans `index.html` :
- `+33781631578` (liens `tel:` et données `telephone`) et `07 81 63 15 78` (texte affiché) ;
- `simonlaugueux@proton.me` (liens `mailto:`, texte affiché et données `email`).

Dans les liens `mailto:`, l'objet et le texte pré-rempli sont **encodés** (`%20` pour un espace, `%C3%A9` pour « é », `%0A` pour un retour à la ligne). Pour encoder un nouveau texte :

```bash
python3 -c "from urllib.parse import quote; print(quote('Votre texte ici'))"
```

Entre `subject=…` et `body=…`, le séparateur s'écrit `&amp;` dans le HTML.

### Couleurs

Les six couleurs sont définies une seule fois en haut de `assets/css/style.css` (`:root`). Tout couple texte/fond doit garder un contraste d'au moins 4,5:1 (vérifié par les tests).

## Vérifier avant de publier

```bash
python3 -m unittest discover -s tests -v   # structure, contenu, styles, images
node --test tests/main.test.mjs            # comportement du menu et des animations
npx --yes html-validate index.html         # validité HTML
python3 -m http.server 8000                # aperçu sur http://localhost:8000
```

Image de partage (après modification des couleurs) : `python3 tools/og_image.py`.

## Contenu à valider par Simon

Les éléments suivants sont **provisoires** :

- Textes de présentation (accroche, « L'univers », descriptions des formules).
- Formules, durées, tailles de groupe et tarifs « à partir de » (35 €/pers., 30 €/pers., 300 € la prestation).
- Les trois dates d'exemple (17 octobre, 14 novembre, 5 décembre 2026) et leurs lieux.
- Absence de photos : les illustrations SVG pourront être remplacées par de vraies photos.
- Pas de lien WhatsApp pour l'instant.

## Mise en ligne (GitHub Pages)

1. Pousser le dépôt sur GitHub.
2. *Settings → Pages* : « Deploy from a branch », branche `main`, dossier `/ (root)`.
3. *Custom domain* : `simonlaugueux.fr` (déjà renseigné par le fichier `CNAME`).
4. Chez le registrar du domaine, créer les enregistrements DNS :

   | Type | Nom | Valeur |
   |---|---|---|
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |
   | AAAA | `@` | `2606:50c0:8000::153` |
   | AAAA | `@` | `2606:50c0:8001::153` |
   | AAAA | `@` | `2606:50c0:8002::153` |
   | AAAA | `@` | `2606:50c0:8003::153` |
   | CNAME | `www` | `<utilisateur-github>.github.io` |

5. Une fois le DNS propagé, cocher *Enforce HTTPS*.
````

- [ ] **Step 3: Lancer toute la suite de vérifications**

Run: `python3 -m unittest discover -s tests -v && node --test tests/main.test.mjs && npx --yes html-validate index.html`
Expected: 44 tests Python `OK`, `# pass 7` / `# fail 0` côté Node, aucune erreur html-validate.

- [ ] **Step 4: Vérification visuelle**

Run: `python3 -m http.server 8000` puis ouvrir `http://localhost:8000` dans un navigateur, outils de développement en mode responsive, aux largeurs **375 px**, **768 px** et **1280 px**. Vérifier et noter le résultat de chaque point :

- Pas de défilement horizontal à 375 px ; l'adresse e-mail de la carte contact ne déborde pas.
- À 375 px : bouton burger visible, menu fermé par défaut, s'ouvre/se referme, se referme après clic sur un lien ; barre « Appeler / E-mail » fixée en bas ; la mention loi Évin reste entièrement visible en fin de page.
- À 768 px et 1280 px : barre du bas absente, menu horizontal, formules en grille.
- Le hero affiche le dégradé camel → ocre avec le veinage discret ; les icônes et les ornements s'affichent.
- La navigation au clavier (Tab) montre un focus visible partout ; le premier Tab fait apparaître « Aller au contenu ».
- JavaScript désactivé (DevTools → *Disable JavaScript*, puis recharger) : toutes les sections visibles, liens du menu visibles, pas de bouton burger.
- Émulation `prefers-reduced-motion: reduce` (DevTools → *Rendering*) : les sections s'affichent sans animation.
- Cliquer « Réserver par e-mail » : le client mail s'ouvre avec l'objet « Demande de dégustation » et le corps pré-rempli, accents corrects.

Corriger tout problème constaté (dans `style.css` ou `index.html`), relancer la suite de l'étape 3, puis refaire le point concerné.

- [ ] **Step 5: Commit (après accord de l'utilisateur)**

```bash
git add README.md .htmlvalidate.json index.html
git commit -m "docs: README de maintenance et mise en ligne GitHub Pages"
```
