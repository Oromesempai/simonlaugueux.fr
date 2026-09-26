# Site vitrine — Simon Laugueux, dégustations de vins & spiritueux

Date : 2026-09-26
Statut : validé en brainstorming, en attente de relecture

## 1. Objectif

Site vitrine statique, hébergé sur GitHub Pages (domaine `simonlaugueux.fr`), présentant l'activité de Simon Laugueux : dégustations de vins et spiritueux dans la région de Cahors (Lot), avec un fil conducteur autour de l'élevage en barriques de chêne.

Le site doit, par ordre d'importance égale :

- **A. Faire réserver** une dégustation (appel ou e-mail).
- **B. Inspirer confiance** : présenter l'univers et la démarche de Simon.
- **C. Donner les infos pratiques** : formules, tarifs indicatifs, prochaines dates, zone d'intervention.

### Publics

- Particuliers (groupes d'amis, à domicile ou sur place)
- Entreprises / CE (séminaires, afterworks)
- Événements privés (mariages, anniversaires)
- Touristes de passage dans le Lot

### Critères de succès

- Un visiteur sur mobile peut appeler ou écrire à Simon en un tap depuis n'importe quel endroit de la page.
- Les trois publics principaux trouvent une formule qui les concerne sans chercher.
- Modifier une date ou un tarif ne nécessite qu'un éditeur de texte (pas de build, pas d'outil).
- Contraste texte conforme WCAG AA (≥ 4.5:1).

## 2. Données confirmées vs hypothèses

**Confirmé par l'utilisateur :**

- E-mail : `simonlaugueux@proton.me`
- Téléphone : `07 81 63 15 78` (lien `tel:+33781631578`)
- Réservation par liens directs uniquement (pas de formulaire, pas d'outil tiers)
- Couleurs dominantes : ocre et camel
- Approche technique : une page HTML + CSS pur, sans build

**Hypothèses (contenu provisoire à valider par Simon) :**

- Pas de photos disponibles → design graphique avec illustrations SVG ; emplacements prévus pour photos futures.
- Textes de présentation rédigés de façon générique.
- Trois formules avec tarifs « à partir de » marqués comme indicatifs.
- Liste de prochaines dates d'exemple.
- Pas de lien WhatsApp (non confirmé) — ajout trivial ultérieur.

Tout contenu provisoire est signalé dans le README (section « Contenu à valider »).

## 3. Structure de la page (one-page)

Navigation fixe en haut avec ancres ; menu burger sous 768 px.

1. **Hero** (`#accueil`)
   - Titre « Simon Laugueux »
   - Sous-titre « Dégustations de vins & spiritueux · Cahors & le Lot »
   - Accroche courte évoquant les barriques de chêne
   - Deux boutons : **Appeler** (`tel:`) et **Réserver par e-mail** (`mailto:` pré-rempli)
2. **L'univers** (`#univers`)
   - Paragraphe sur la démarche : vins de Cahors, malbec, spiritueux, élevage en fût de chêne
   - Trois points forts avec icône : Terroir du Lot · Élevage en fût de chêne · Dégustation commentée
3. **Les formules** (`#formules`)
   - Carte « Particuliers & amis » — à domicile ou sur place
   - Carte « Entreprises & CE » — séminaires, afterworks, team-building
   - Carte « Événements privés » — mariages, anniversaires
   - Chaque carte : description, durée indicative, tarif « à partir de … € / pers. », bouton e-mail avec objet adapté
   - Encart « Touristes de passage » : dégustations découverte, contact direct
4. **Prochaines dates** (`#dates`)
   - Liste `<ul>` : date, lieu, thème
   - Message permanent : « Aucune date ne vous convient ? Organisons la vôtre. » + lien e-mail
5. **Contact** (`#contact`)
   - Gros boutons téléphone et e-mail, numéro et adresse affichés en clair
   - Zone d'intervention : Cahors, le Lot et alentours
   - `mailto:` pré-rempli : objet « Demande de dégustation », corps modèle (date souhaitée, nombre de personnes, type d'événement, lieu)
6. **Footer**
   - Mention légale obligatoire (loi Évin) : « L'abus d'alcool est dangereux pour la santé, à consommer avec modération. »
   - © année, nom

Sur mobile (< 768 px) : barre de contact collée en bas d'écran (Appeler / E-mail), toujours visible ; un `padding-bottom` sur `body` évite qu'elle masque le footer.

## 4. Style visuel

### Palette (variables CSS sur `:root`)

| Token | Rôle | Hex |
|---|---|---|
| `--parchemin` | fond principal | `#F6EFE3` |
| `--camel` | fonds de sections, cartes | `#C19A6B` |
| `--ocre` | accents, boutons | `#CC7722` |
| `--ocre-fonce` | fond bouton si contraste insuffisant | `#A85F16` (ajustable) |
| `--chene` | texte principal | `#3B2A1E` |
| `--malbec` | touches rares : filets, survols | `#5A1F2B` |

Règle : le texte est toujours `--chene` sur fond clair, ou `--parchemin` sur fond foncé ; chaque couple texte/fond utilisé est vérifié ≥ 4.5:1.

### Typographie (Google Fonts)

- Titres : **Cormorant Garamond** (600/700)
- Texte : **Lato** (400/700)
- Repli : `Georgia, serif` / `system-ui, sans-serif`

### Ambiance

- Hero en dégradé camel → ocre avec texture SVG de veinage de bois en faible opacité
- Séparateurs de sections : fines courbes évoquant douelles/cerclages de barrique (SVG inline)
- Icônes SVG maison : barrique, verre, grappe, carafe (monochromes, `currentColor`)
- Cartes : coins arrondis (8–12 px), ombre douce
- Apparition légère au scroll (IntersectionObserver), désactivée sous `prefers-reduced-motion: reduce` ; le contenu reste visible sans JS

## 5. Technique

### Arborescence

```
index.html
assets/css/style.css
assets/js/main.js        # menu burger + apparition au scroll
assets/img/              # SVG (icônes, texture, séparateurs), favicon, image Open Graph
CNAME                    # simonlaugueux.fr
README.md                # modifier dates/tarifs, contenu à valider, DNS GitHub Pages
docs/superpowers/specs/  # cette spec
```

Pas de dépendance, pas de build, pas de framework. JS optionnel : le site est entièrement lisible et utilisable sans JS (le menu mobile retombe sur une liste de liens visible, ou `<details>` si plus simple).

### Responsive

- Mobile-first ; points de rupture ~768 px et ~1100 px
- Largeur de contenu max ~1100 px
- Cibles tactiles ≥ 44 px

### SEO local

- `<title>` et `<meta name="description">` ciblant « dégustation vin Cahors », « spiritueux », « Lot »
- `lang="fr"`
- Open Graph (titre, description, image)
- JSON-LD schema.org `LocalBusiness` : nom, téléphone, e-mail, `areaServed` (Cahors, Lot), URL

### Accessibilité

- HTML sémantique (`header`, `nav`, `main`, `section` avec titres, `footer`)
- Lien d'évitement « Aller au contenu »
- Focus visible personnalisé
- Icônes décoratives `aria-hidden="true"` ; images informatives avec `alt`
- Bouton burger avec `aria-expanded` / `aria-controls`

### Déploiement

- GitHub Pages depuis la branche `main`, racine du dépôt
- Fichier `CNAME` = `simonlaugueux.fr`
- README : enregistrements DNS à créer chez le registrar (A vers les IP GitHub Pages, `www` en CNAME), activation HTTPS

## 6. Vérification

- Validation HTML (validator.w3.org ou `npx html-validate`, sans ajout de dépendance au projet)
- Vérification des contrastes des couples de couleurs utilisés
- Test visuel local via `python3 -m http.server` à 375 px, 768 px, 1280 px
- Vérification que `tel:` et `mailto:` (avec objet/corps encodés) sont corrects
- Test sans JS : contenu et navigation accessibles

## 7. Hors périmètre

- Formulaire de contact, réservation en ligne, paiement
- Multilingue (anglais possible plus tard pour les touristes)
- Blog, CMS, back-office
- Analytics
