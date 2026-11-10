---
layout: distill
title: "Segmenter de grandes images avec moins de ressources"
description: "Calcul exact hors-cœur et segmentation interactive incrémentale : deux apports d’une thèse CIFRE menée entre le LIGM et Thermo Fisher Scientific."
date: 2026-11-07
lang: fr
translation_lang: en
translation_url: /blog/2026/scalable-hierarchical-segmentation/
stylesheet: /assets/css/thesis-segmentation.css
tags: segmentation research out-of-core
categories: research
thumbnail: assets/img/posts/scalable-segmentation/superpixels-original.jpg
related_posts: false
bibliography: scalable-hierarchical-segmentation.bib
thesis_reference_keys:
  - lefevre2026thesis
  - lefevre2022
  - lefevre2025
  - lefevre2024
  - lebon2023
  - lebon2025
thesis_works_heading: "Travaux directement issus de la thèse"
external_references_heading: "Références externes"
authors:
  - name: Josselin Lefèvre
    url: "https://lefevrej.github.io/"
    affiliations:
      name: "Thermo Fisher Scientific et LIGM, Université Gustave Eiffel"
toc:
  - name: "Une image, plusieurs échelles"
    id: hierarchie-de-segmentation
  - name: "Premier volet : le calcul exact hors-cœur"
    id: calcul-hors-coeur
  - name: "Quelle taille d’image peut-on traiter ?"
    id: station-de-travail
  - name: "Des représentations plus compactes"
    id: representations-compactes
  - name: "Deuxième volet : accélérer la segmentation interactive"
    id: segmentation-interactive
  - name: "Un partenariat industriel et scientifique"
    id: partenariat
  - name: "Les suites envisagées"
    id: perspectives
images:
  compare: true
---

<p class="thesis-languages" aria-label="Langue de lecture"><strong>Français</strong> · <a href="{{ '/blog/2026/scalable-hierarchical-segmentation/' | relative_url }}" lang="en" hreflang="en">Read in English</a></p>

Les objets d’intérêt d’une image peuvent apparaître à **plusieurs échelles** : une cellule et ses organites, un animal et les parties de son corps. La **segmentation** consiste à délimiter ces régions. Un unique niveau de découpage ne suffit donc pas toujours à représenter les structures utiles à l’analyse.

Ma thèse CIFRE, *Algorithmes scalables pour la segmentation hiérarchique d’images et de données*, menée à **ESIEE Paris, entre le LIGM et Thermo Fisher Scientific**, cherche à rendre la **segmentation hiérarchique** utilisable sur de grandes images, malgré ses besoins en mémoire et en temps de calcul.<d-cite key="lefevre2026thesis"></d-cite>

## Une image, plusieurs échelles
{: #hierarchie-de-segmentation }

Une **hiérarchie de segmentation** rassemble plusieurs partitions de la même image, de la plus fine à la plus grossière. De petites régions se regroupent progressivement pour en former de plus grandes. Ces partitions sont **imbriquées** : deux régions de la hiérarchie sont disjointes, ou l’une est incluse dans l’autre.

On peut ainsi rechercher un objet entier à une échelle et l’une de ses parties à une autre. **La hiérarchie permet de choisir les régions au niveau de détail adapté à l’objet recherché**, sans fixer une seule échelle pour toute l’analyse. La figure ci-dessous relie les partitions de l’image à leur représentation par un arbre.

{% include thesis-hierarchy.html lang=page.lang %}

Construire et exploiter cette représentation a toutefois un coût : il faut stocker et manipuler les relations entre régions, en plus des pixels. Sur les volumes 3D de plusieurs milliards de voxels produits en microscopie électronique, la **mémoire vive** devient un obstacle. Lorsqu’un utilisateur affine une segmentation, c’est aussi le **temps de réponse** qui compte. Les deux volets de la thèse répondent à ces contraintes : calculer les hiérarchies avec moins de mémoire, puis accélérer les corrections interactives.

## Premier volet : le calcul exact hors-cœur
{: #calcul-hors-coeur }

Une méthode **en cœur** conserve l’image et ses structures de calcul en mémoire vive. Ces structures peuvent être bien plus volumineuses que les pixels : une image de 3,35 Go peut nécessiter plusieurs centaines de gigaoctets pour construire sa hiérarchie. Le volume FIB-SEM étudié dans la thèse contient **2048 × 1536 × 1065 voxels**, soit environ **3,35 milliards de voxels en 8 bits**. L’algorithme classique en cœur ne pouvait pas traiter ce volume complet sur la station de 256 Go utilisée pour l’étude.<d-cite key="lucchi2012"></d-cite>

Le principe de l'algoritmique **hors-cœur** est de conserver les données sur disque et de ne charger en mémoire que les blocs nécessaires à l’étape courante afin de limiter l’usage de la mémoire vive.

<figure class="l-page thesis-figure thesis-diagram">
  <img class="diagram-light" src="{{ '/assets/img/posts/scalable-segmentation/out-of-core-fr.svg' | relative_url }}" width="1600" height="578" alt="Calcul hors-cœur : chargement de blocs depuis le disque, traitement dans une mémoire vive limitée, puis enregistrement des résultats." data-zoomable>
  <img class="diagram-dark" src="{{ '/assets/img/posts/scalable-segmentation/out-of-core-fr-dark.svg' | relative_url }}" width="1600" height="578" alt="Calcul hors-cœur : chargement de blocs depuis le disque, traitement dans une mémoire vive limitée, puis enregistrement des résultats." data-zoomable>
  <figcaption>Le principe du hors-cœur : seuls les blocs utiles sont présents en mémoire vive. Schéma adapté des slides de soutenance.</figcaption>
</figure>

Ce découpage doit toutefois respecter les dépendances du calcul : certaines opérations ne peuvent pas être appliquées à des blocs indépendants.

{% include thesis-processing-callouts.html kind='local-global' lang=page.lang %}

Le défi scientifique est de préserver les **relations d’inclusion entre les régions**, même lorsqu’une région couvre plusieurs blocs. Traiter chaque bloc indépendamment de manière naïve peut créer des frontières artificielles :

<div class="l-body thesis-figure thesis-pair">
  <figure>
    <img src="{{ '/assets/img/posts/scalable-segmentation/blockwise-expected.jpg' | relative_url }}" width="512" height="512" loading="lazy" alt="Segmentation attendue, avec des frontières cohérentes sur l’ensemble de l’image." data-zoomable>
    <figcaption>Résultat global cohérent</figcaption>
  </figure>
  <figure>
    <img src="{{ '/assets/img/posts/scalable-segmentation/blockwise-independent.jpg' | relative_url }}" width="512" height="512" loading="lazy" alt="Segmentation par blocs indépendants, avec des frontières artificielles." data-zoomable>
    <figcaption>Blocs traités indépendamment</figcaption>
  </figure>
</div>

Notre **cadre algébrique** construit une distribution de la hiérarchie binaire de partitions : chaque bloc dispose d’un arbre local, cohérent avec la représentation globale. Trois opérations organisent le calcul : **select** extrait l’information utile, **join** combine les informations de blocs voisins et **insert** corrige et complète les hiérarchies locales.<d-cite key="lefevre2022,lefevre2025"></d-cite>

**La validité est établie mathématiquement : le calcul par blocs retrouve exactement la hiérarchie du calcul global.** Nous proposons un schéma de calcul qui borne la taille des structures intermédiaires par rapport aux éléments voisins de la distribution.

{% details Les fondements mathématiques %}
Le chapitre 4 et ses preuves en annexe comprennent **5 définitions et 9 résultats mathématiques** : 3 propriétés, 5 lemmes et 1 corollaire. Ils formalisent les opérations, les relations entre représentations et les bornes sur les structures intermédiaires.

Pour une hiérarchie globale $$H$$ et un bloc $$S_i$$, l’élément recherché est

$$
H_i = \operatorname{select}(S_i,H).
$$

L’objectif est de construire ces éléments sans devoir stocker préalablement toute la hiérarchie $$H$$ en mémoire. L’exactitude concerne ce calcul ; la pertinence d’une segmentation pour une application reste une question distincte.
{% enddetails %}

Ce cadre s’étend au calcul de caractéristiques régionales comme l'aire, le volume, la hauteur, les minima ainsi qu'à la segmentation par **ligne de partage des eaux**, notamment hiérarchique.<d-cite key="lefevre2024"></d-cite>

{% include thesis-processing-callouts.html kind='watershed' lang=page.lang %}

<figure class="l-page thesis-figure thesis-diagram">
  <img class="diagram-light" src="{{ '/assets/img/posts/scalable-segmentation/analysis-overview-fr.svg' | relative_url }}" width="1600" height="938" loading="lazy" alt="Une image de microscopie par blocs est représentée par une distribution de hiérarchies. Le calcul des attributs permet notamment le filtrage connexe et la ligne de partage des eaux." data-zoomable>
  <img class="diagram-dark" src="{{ '/assets/img/posts/scalable-segmentation/analysis-overview-fr-dark.svg' | relative_url }}" width="1600" height="938" loading="lazy" alt="Une image de microscopie par blocs est représentée par une distribution de hiérarchies. Le calcul des attributs permet notamment le filtrage connexe et la ligne de partage des eaux." data-zoomable>
  <figcaption>De l’image découpée en blocs à l’analyse hiérarchique : construction de la distribution, calcul d’attributs et opérations de segmentation.</figcaption>
</figure>

## Quelle taille d’image peut-on traiter ?
{: #station-de-travail }

La taille du fichier ne suffit pas à savoir si une image peut être traitée : il faut aussi tenir compte de la mémoire nécessaire à la hiérarchie et au calcul. En inversant les modèles issus des expériences, on obtient une **taille maximale d’image estimée pour un budget mémoire donné**.

<p class="thesis-capacity-takeaway"><strong>Avec 32 Go de mémoire vive pour le calcul, une méthode en cœur ne peut traiter qu’une image d’environ 196 Mo au maximum.</strong> Avec la méthode hors-cœur optimisée, ce même budget permet de traiter des images allant jusqu’à <strong>10,7 Go</strong>, soit environ <strong>55 fois plus grandes</strong> (pour des images 8 bits non compressées).</p>

Autrement dit, la méthode hors-cœur fait passer une image de l’ordre de quelques centaines de mégaoctets à une image de plus de dix gigaoctets sur la même station de travail. Le principe de cette représentation compacte est détaillé dans la [section suivante](#representations-compactes).

<figure class="l-page thesis-figure">
  <img src="{{ '/assets/img/posts/scalable-segmentation/incore-memory.svg' | relative_url }}" loading="lazy" alt="Pic mémoire en cœur et hors-cœur causal selon la taille de l’image. Le calcul en cœur atteint environ 239 Go pour une image de 1,47 Go." data-zoomable>
  <figcaption>Mémoire mesurée en cœur et hors-cœur causal pour différentes largeurs de blocs, figure 4.11(a). La courbe en cœur sert à l’estimation ; le volume complet n’a pas été mesuré en cœur.</figcaption>
</figure>

<section class="thesis-memory" aria-labelledby="memory-model-title" data-thesis-memory data-locale="fr">
  <h3 id="memory-model-title">Estimer la taille maximale d’image</h3>
  <p>Choisissez la mémoire disponible pour le calcul. Le tableau estime la taille maximale d’une image 8 bits non compressée selon les deux modèles.</p>
  <div class="memory-slider">
    <label for="memory-total">Mémoire vive pour le calcul : <strong><output data-memory-budget>32 Go</output></strong></label>
    <input id="memory-total" type="range" min="32" max="256" step="4" value="32" aria-valuetext="32 Go">
    <div class="memory-range-ends" aria-hidden="true"><span>32 Go</span><span>256 Go</span></div>
  </div>
  <div class="thesis-table" aria-live="polite" aria-atomic="true">
    <table>
      <thead><tr><th scope="col">Méthode</th><th scope="col">Taille maximale estimée de l’image</th><th scope="col">Nombre de voxels en 8 bits</th></tr></thead>
      <tbody>
        <tr><th scope="row">En cœur — au plus</th><td><output data-memory-incore>196 Mo</output></td><td><output data-memory-incore-voxels>196 millions</output></td></tr>
        <tr><th scope="row">Hors-cœur optimisé — jusqu’à</th><td><output data-memory-qfz>10,7 Go</output></td><td><output data-memory-qfz-voxels>10,7 milliards</output></td></tr>
      </tbody>
    </table>
  </div>
  <p><small>Estimations sans marge supplémentaire. La représentation optimisée et ses paramètres sont présentés dans la <a href="#representations-compactes">section suivante</a>. Les résultats dépendent des données, du découpage et de l’implémentation ; ils ne constituent pas une capacité garantie.</small></p>
  <noscript><p>Les valeurs affichées correspondent à un budget de 32 Go. Activez JavaScript pour explorer les autres budgets.</p></noscript>
</section>

{% details Les calculs et leurs hypothèses %}
Pour une image de taille $$S$$ et un pic mémoire $$M$$, en Go, l’ajustement des six points de la figure 4.11(a) donne

$$
M_{\mathrm{en\ cœur}}\approx162{,}94S+0{,}062.
$$

La configuration hors-cœur optimisée atteint un minimum proche de trois fois la taille de l’image. Pour un budget mémoire $$B$$, les tailles maximales estimées sont donc

$$
S_{\max,\mathrm{en\ cœur}}\approx\frac{B-0{,}062}{162{,}94},
\qquad S_{\max,\mathrm{hors\ cœur}}\approx\frac{B}{3}.
$$

Pour $$B=32$$ Go, cela donne environ $$0{,}196$$ Go en cœur et $$10{,}7$$ Go hors-cœur.

Pour le volume complet de 3,35 Go, prolonger la tendance en cœur donne environ **550 Go**, à comparer aux **10 Go mesurés** pour la configuration optimisée : environ **98 % de réduction estimée**. Cette comparaison entre les implémentations des chapitres 4 et 6 est distincte du gain mesuré de 84 % entre configurations hors-cœur, [présenté plus loin](#representations-compactes).

L’ajustement a été reconstitué à partir des points de la figure, sans les journaux de mesure bruts. Le coefficient hors-cœur dépend du contenu de l’image, du découpage et des choix de représentation détaillés dans la [section suivante](#representations-compactes). Il ne définit pas une limite universelle de la méthode. Les Go sont décimaux : pour une image 8 bits non compressée, 1 Go correspond à un milliard de voxels.
{% enddetails %}

## Des représentations plus compactes
{: #representations-compactes }

Pour réduire davantage les ressources nécessaires, nous regroupons les pixels en **superpixels**, définis par des zones quasi-plates. Le paramètre $$\alpha$$ règle la granularité de cette représentation.

<figure class="l-body thesis-figure">
  <img-comparison-slider class="thesis-comparison" tabindex="0" aria-label="Comparer l’image de microscopie et sa représentation par zones quasi-plates à alpha 111">
    <img slot="first" src="{{ '/assets/img/posts/scalable-segmentation/superpixels-original.jpg' | relative_url }}" width="500" height="500" loading="lazy" alt="Image de microscopie originale">
    <img slot="second" src="{{ '/assets/img/posts/scalable-segmentation/superpixels-111.jpg' | relative_url }}" width="500" height="500" loading="lazy" alt="Représentation par zones quasi-plates à alpha 111">
  </img-comparison-slider>
  <figcaption>Déplacez le curseur pour comparer l’image originale et sa représentation à α = 111. Chaque zone est affichée avec son intensité moyenne ; il ne s’agit pas de la segmentation finale.</figcaption>
</figure>

Pour la ligne de partage des eaux à partir de marqueurs, le calcul sur cette représentation conserve le résultat au niveau des pixels **lorsque les marqueurs occupent des zones quasi-plates distinctes**. Cette condition préserve l’information nécessaire pour les séparer.

<figure class="l-page thesis-figure">
  <img src="{{ '/assets/img/posts/scalable-segmentation/qfz-memory.svg' | relative_url }}" loading="lazy" alt="Pic mémoire selon le nombre de blocs : configuration Classic au niveau pixel et zones quasi-plates à alpha 66, 72, 82 et 111. Le minimum à alpha 111 est proche de 10 Go." data-zoomable>
  <figcaption>Pic de mémoire vive pour le volume de 3,35 milliards de voxels, figure 6.4(a) du manuscrit. L’axe « Number of Slices » indique ici le nombre de blocs de calcul.</figcaption>
</figure>

Les expériences de construction de la distribution, menées avec l’implémentation interne sur une station de 256 Go, donnent les résultats suivants :<d-cite key="lefevre2026thesis"></d-cite>

<div class="thesis-table" role="region" aria-label="Résultats mesurés du calcul hors-cœur" tabindex="0" markdown="1">

| Ressource | Résultat pour α = 111 |
| :--- | :--- |
| **Mémoire vive** | Pic minimal réduit d’environ **84 %** : environ 10 Go contre 62 Go. |
| **Stockage temporaire** | Environ **40 Go contre 299 Go**, soit 87 % de réduction. |
| **Temps de construction** | Environ **40 min contre 100 min**, soit 60 % de réduction. |

</div>

Les deux configurations sont hors-cœur : la comparaison porte sur le niveau pixel et le niveau superpixel, avec des stratégies de partitionnement différentes. Les 84 % comparent les minima obtenus en faisant varier le nombre de blocs ; le stockage et le temps sont comparés à 80 blocs.

## Deuxième volet : accélérer la segmentation interactive
{: #segmentation-interactive }

Le premier volet permet de traiter de grandes images malgré la mémoire limitée. Un autre obstacle apparaît pendant l’utilisation : **attendre le résultat après chaque correction**. Ce second volet exploite la hiérarchie pour accélérer la **segmentation interactive par ligne de partage des eaux**, lorsque l’image et les structures de calcul tiennent en mémoire.

En segmentation interactive, l’utilisateur désigne les objets d’intérêt et le fond à l’aide de **marqueurs**, observe le résultat, puis ajoute ou efface des marqueurs pour affiner les contours.

**Cette démarche est incrémentale par nature** : d’une étape à l’autre, l’image reste la même et les indications de l’utilisateur évoluent progressivement. Pourtant, les implémentations non incrémentales de la ligne de partage des eaux traitent chaque correction comme un nouveau problème : elles relancent le calcul de la segmentation sur toute l’image, même pour une modification locale. Ces recalculs successifs imposent une attente répétée à l’utilisateur.

Notre méthode **incrémentale** conserve l’état du calcul entre deux interactions. Elle réutilise les résultats précédents et actualise uniquement les régions affectées par l’ajout ou le retrait d’un marqueur. Le coût de la mise à jour est proportionnel au nombre de pixels concernés : une correction locale peut donc être prise en compte rapidement, ce qui facilite l’affinage progressif de la segmentation.<d-cite key="lebon2023,lebon2025"></d-cite>

<div class="l-body thesis-figure thesis-stack">
  <figure>
    <svg viewBox="0 0 1024 768" width="1024" height="768" role="img" aria-labelledby="interactive-first-title">
      <title id="interactive-first-title">Premiers marqueurs pour la segmentation interactive d’une plante.</title>
      <image href="{{ '/assets/img/posts/scalable-segmentation/interactive-first.jpg' | relative_url }}" width="768" height="1024" transform="translate(1024 0) rotate(90)"></image>
    </svg>
    <figcaption>Premiers marqueurs</figcaption>
  </figure>
  <figure>
    <svg viewBox="0 0 1024 768" width="1024" height="768" role="img" aria-labelledby="interactive-refined-title">
      <title id="interactive-refined-title">Segmentation de la même plante après affinage des marqueurs.</title>
      <image href="{{ '/assets/img/posts/scalable-segmentation/interactive-refined.jpg' | relative_url }}" width="768" height="1024" transform="translate(1024 0) rotate(90)"></image>
    </svg>
    <figcaption>Segmentation affinée</figcaption>
  </figure>
</div>

{% include video.html path="/assets/video/incremental_watershed.mp4" class="thesis-video" controls=true width="1024" title="Démonstration de la ligne de partage des eaux incrémentale" caption="Démonstration de la segmentation interactive incrémentale : le résultat est mis à jour au fil de l’ajout et du retrait des marqueurs." %}

Une stratégie parallèle accélère les mises à jour importantes. Sur les cinq volumes 3D du benchmark, le temps moyen atteint **0,34 seconde par interaction**, contre **9,26 secondes pour ITK**, soit une accélération d’environ **27 fois**, hors initialisation.<d-cite key="lebon2025"></d-cite>

## Un partenariat industriel et scientifique
{: #partenariat }

La collaboration a permis de **remplir conjointement les objectifs industriels et scientifiques**. Les besoins opérationnels de Thermo Fisher Scientific ont nourri les questions de recherche ; le LIGM a apporté son expertise en morphologie mathématique et en algorithmique des graphes. Les solutions développées associent garanties mathématiques, performances mesurées et développement logiciel.

Les travaux ont donné lieu à **deux articles de revue et trois publications en conférences internationales**, tout en préparant leur transfert vers les outils de l’entreprise. Le démonstrateur Amira<sup>™</sup> a notamment été présenté à **VivaTech en 2025**. Le [code C++ de la segmentation interactive incrémentale](https://github.com/lebonq/incremental_watershed) accompagne la publication correspondante.<d-cite key="lebon2025"></d-cite>

**Les personnes ayant contribué aux travaux.** Jean Cousty et Benjamin Perret, au LIGM/ESIEE Paris, et Harold Phelippeau, chez Thermo Fisher Scientific, ont assuré l’encadrement de la thèse. La segmentation interactive a été développée avec Quentin Lebon. Matheus Sano a également participé aux travaux dans le cadre de son stage. Je remercie aussi Nicolas Constanty, Franck Fauverte et Daniel Lichau pour leur contribution au démonstrateur Amira<sup>™</sup>.

## Les suites envisagées
{: #perspectives }

La poursuite des travaux vise à :

- réduire la duplication des régions en construisant les hiérarchies **par plages d’échelles successives**, pour faciliter le traitement à pleine résolution ;
- rapprocher le **hors-cœur et la segmentation interactive incrémentale** ;
- enrichir le calcul des caractéristiques géométriques des régions ;
- étudier les architectures **parallèles, distribuées et GPU**, ainsi que les complémentarités avec l’apprentissage profond.

Ces perspectives scientifiques accompagnent la consolidation du démonstrateur et l’évaluation de son intégration dans les logiciels **Amira<sup>™</sup>/Avizo<sup>™</sup>**, sur des données et des usages plus variés.

<script defer src="{{ '/assets/js/thesis-memory.js' | relative_url }}"></script>
