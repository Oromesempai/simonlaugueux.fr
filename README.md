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
| `assets/fonts/` | Polices Cormorant Garamond et Lato, hébergées sur le site (aucun appel à Google Fonts) |
| `tools/og_image.py` | Régénère l'image de partage `og-image.png` |
| `tests/` | Vérifications automatiques |
| `CNAME` | Nom de domaine pour GitHub Pages |
| `.nojekyll` | Demande à GitHub Pages de servir les fichiers tels quels |
| `.htmlvalidate.json` | Configuration du validateur HTML |

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
- Le texte doit être exactement « Jour N mois AAAA » (par ex. « Samedi 5 décembre 2026 ») : les tests comparent jour, numéro, mois et année avec `datetime`.
- S'il n'y a plus aucune date, supprimer toute la liste `<ul class="dates-liste"> … </ul>` : la phrase « Aucune date ne vous convient ? Organisons la vôtre. » reste affichée.

### Modifier une formule ou un tarif

Section `id="formules"` : chaque formule est un bloc `<article class="formule">`. Le prix est dans `<p class="prix">` et doit contenir « à partir de ».

### Changer le téléphone ou l'e-mail

Rechercher/remplacer dans `index.html` :
- `+33781631578` (liens `tel:` et données `telephone`) et le numéro affiché, écrit avec des espaces insécables `07&nbsp;81&nbsp;63&nbsp;15&nbsp;78` (dans le texte d'un lien `tel:`, tous les espaces doivent être des `&nbsp;` : le validateur HTML l'exige) ;
- `simonlaugueux@proton.me` (liens `mailto:`, texte affiché et données `email`).

Dans les liens `mailto:`, l'objet et le texte pré-rempli sont **encodés** (`%20` pour un espace, `%C3%A9` pour « é », `%0A` pour un retour à la ligne). Pour encoder un nouveau texte :

```bash
python3 -c "from urllib.parse import quote; print(quote('Votre texte ici'))"
```

Entre `subject=…` et `body=…`, le séparateur s'écrit `&amp;` dans le HTML.

### Couleurs

Les six couleurs sont définies une seule fois en haut de `assets/css/style.css` (`:root`). Tout couple texte/fond doit garder un contraste d'au moins 4,5:1. Les tests vérifient les couples listés dans `PAIRES` (`tests/test_site.py`) : si vous utilisez une nouvelle combinaison texte/fond dans le CSS, ajoutez-la à cette liste.

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
