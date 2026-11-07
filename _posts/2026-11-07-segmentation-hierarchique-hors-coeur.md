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
authors:
  - name: Josselin Lefèvre
    url: "https://lefevrej.github.io/"
    affiliations:
      name: "Thermo Fisher Scientific et LIGM, Université Gustave Eiffel"
toc:
  - name: "Premier volet : le calcul exact hors-cœur"
    id: calcul-hors-coeur
  - name: "Que peut traiter une station de travail"
    id: station-de-travail
  - name: "Des représentations plus compactes"
    id: representations-compactes
  - name: "Deuxième volet : accélérer les interactions"
    id: segmentation-interactive
  - name: "Un partenariat industriel et scientifique"
    id: partenariat
  - name: "Les suites envisagées"
    id: perspectives
images:
  compare: true
---

<p class="thesis-languages" aria-label="Langue de lecture"><strong>Français</strong> · <a href="{{ '/blog/2026/scalable-hierarchical-segmentation/' | relative_url }}" lang="en" hreflang="en">Read in English</a></p>

Les progrès de la microscopie électronique produisent des images 3D de plusieurs milliards de voxels. Pour les analyser, il faut **délimiter les régions d’intérêt** : c’est la segmentation. Deux obstacles apparaissent alors : les besoins en mémoire vive et les temps de calcul qui dégradent l’expérience utilisateur.

Ma thèse CIFRE, *Algorithmes scalables pour la segmentation hiérarchique d’images et de données*, menée à **ESIEE Paris, entre le LIGM et Thermo Fisher Scientific**, explore **deux sujets distincts** : le **calcul exact hors-cœur**, pour maîtriser les besoins en mémoire, et la **segmentation interactive incrémentale**, pour accélérer les corrections de l’utilisateur. Un démonstrateur dans Amira<sup>™</sup> prépare leur valorisation industrielle.<d-cite key="lefevre2026thesis"></d-cite>

## Premier volet : le calcul exact hors-cœur
{: #calcul-hors-coeur }

Une image de 3,35 Go peut nécessiter plusieurs centaines de gigaoctets pour construire les structures utiles à sa segmentation. Le volume FIB-SEM étudié dans la thèse contient **2048 × 1536 × 1065 voxels**, soit environ **3,35 milliards de voxels en 8 bits**. L’algorithme classique en cœur ne pouvait pas traiter ce volume complet sur la station de 256 Go utilisée pour l’étude.<d-cite key="lucchi2012"></d-cite>

Le principe de l'algoritmique **hors-cœur** est de conserver les données sur disque et de ne charger en mémoire que les blocs nécessaires à l’étape courante afin de limiter l’usage de la mémoire vive.

<figure class="l-page thesis-figure thesis-diagram">
  <img class="diagram-light" src="{{ '/assets/img/posts/scalable-segmentation/out-of-core-fr.svg' | relative_url }}" width="1600" height="578" alt="Calcul hors-cœur : chargement de blocs depuis le disque, traitement dans une mémoire vive limitée, puis enregistrement des résultats." data-zoomable>
  <img class="diagram-dark" src="{{ '/assets/img/posts/scalable-segmentation/out-of-core-fr-dark.svg' | relative_url }}" width="1600" height="578" alt="Calcul hors-cœur : chargement de blocs depuis le disque, traitement dans une mémoire vive limitée, puis enregistrement des résultats." data-zoomable>
  <figcaption>Le principe du hors-cœur : seuls les blocs utiles sont présents en mémoire vive. Schéma adapté des slides de soutenance.</figcaption>
</figure>

Le défi scientifique est de préserver les **relations d’inclusion entre les régions**, même lorsqu’une région couvre plusieurs blocs. Traiter chaque bloc indépendamment peut créer des frontières artificielles :

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

**La validité est établie mathématiquement : le calcul par blocs retrouve exactement la hiérarchie du calcul global, selon les mêmes conventions de construction.** Le schéma causal borne aussi la taille des structures intermédiaires par rapport aux éléments voisins de la distribution.

{% details Les fondements mathématiques %}
Le chapitre 4 et ses preuves en annexe comprennent **5 définitions et 9 résultats mathématiques** : 3 propriétés, 5 lemmes et 1 corollaire. Ils formalisent les opérations, les relations entre représentations et les bornes sur les structures intermédiaires.

Pour une hiérarchie globale $$H$$ et un bloc $$S_i$$, l’élément recherché est

$$
H_i = \operatorname{select}(S_i,H).
$$

L’objectif est de construire ces éléments sans devoir stocker préalablement toute la hiérarchie $$H$$ en mémoire. L’exactitude concerne ce calcul ; la pertinence d’une segmentation pour une application reste une question distincte.
{% enddetails %}

Ce cadre s’étend au calcul de caractéristiques régionales comme l'aire, le volume, la hauteur, les minima ainsi qu'à la segmentation par **ligne de partage des eaux**, notamment hiérarchique.<d-cite key="lefevre2024"></d-cite>

<figure class="l-page thesis-figure thesis-diagram">
  <img class="diagram-light" src="{{ '/assets/img/posts/scalable-segmentation/analysis-overview-fr.svg' | relative_url }}" width="1600" height="938" loading="lazy" alt="Une image de microscopie par blocs est représentée par une distribution de hiérarchies. Le calcul des attributs permet notamment le filtrage connexe et la ligne de partage des eaux." data-zoomable>
  <img class="diagram-dark" src="{{ '/assets/img/posts/scalable-segmentation/analysis-overview-fr-dark.svg' | relative_url }}" width="1600" height="938" loading="lazy" alt="Une image de microscopie par blocs est représentée par une distribution de hiérarchies. Le calcul des attributs permet notamment le filtrage connexe et la ligne de partage des eaux." data-zoomable>
  <figcaption>De l’image découpée en blocs à l’analyse hiérarchique : construction de la distribution, calcul d’attributs et opérations de segmentation.</figcaption>
</figure>

## Que peut traiter une station de travail
{: #station-de-travail }

Pour le volet mémoire, considérons une station de **32 Go**, dont **16 Go réservés au système et aux autres applications** : il reste **16 Go pour le calcul**. Les modèles issus des expériences donnent un ordre de grandeur d’environ **98 millions de voxels en cœur**, contre **5,3 milliards avec une représentation hors-cœur compacte**. La construction de cette représentation compacte est détaillée dans la [section suivante](#representations-compactes).

Ces capacités sont **estimées** pour des images 8 bits non compressées. Elles supposent que les coefficients observés restent comparables : le facteur d’environ **55** n’est pas une capacité mesurée sur cette station.

<figure class="l-page thesis-figure">
  <img src="{{ '/assets/img/posts/scalable-segmentation/incore-memory.svg' | relative_url }}" loading="lazy" alt="Pic mémoire en cœur et hors-cœur causal selon la taille de l’image. Le calcul en cœur atteint environ 239 Go pour une image de 1,47 Go." data-zoomable>
  <figcaption>Mémoire mesurée en cœur et hors-cœur causal pour différentes largeurs de blocs, figure 4.11(a). La courbe en cœur sert à l’estimation ; le volume complet n’a pas été mesuré en cœur.</figcaption>
</figure>

<section class="thesis-memory" aria-labelledby="memory-model-title" data-thesis-memory data-locale="fr">
  <h3 id="memory-model-title">Explorer le budget mémoire</h3>
  <p>Modifiez le budget mémoire pour comparer les deux modèles. Les Go sont décimaux ; les images sont considérées en 8 bits non compressés.</p>
  <div class="memory-inputs">
    <label for="memory-total">Mémoire vive installée en Go
      <input id="memory-total" type="number" min="1" max="4096" step="1" value="32" inputmode="decimal">
    </label>
    <label for="memory-reserved">Mémoire réservée au système et aux applications en Go
      <input id="memory-reserved" type="number" min="0" max="4096" step="1" value="16" inputmode="decimal">
    </label>
  </div>
  <div aria-live="polite" aria-atomic="true">
    <p class="memory-error" data-memory-error hidden></p>
    <p>Budget disponible pour le calcul : <strong><output data-memory-budget>16 Go</output></strong>.</p>
    <div class="thesis-table">
      <table>
        <thead><tr><th scope="col">Modèle</th><th scope="col">Taille estimée de l’image</th><th scope="col">Nombre de voxels en 8 bits</th></tr></thead>
        <tbody>
          <tr><th scope="row">En cœur</th><td><output data-memory-incore>98 Mo</output></td><td><output data-memory-incore-voxels>98 millions</output></td></tr>
          <tr><th scope="row">Hors-cœur optimisé</th><td><output data-memory-qfz>5,3 Go</output></td><td><output data-memory-qfz-voxels>5,3 milliards</output></td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <p><small>Estimations sans marge supplémentaire. L’optimisation et ses paramètres sont présentés dans la <a href="#representations-compactes">section suivante</a>. Le coefficient dépend de ces choix, du contenu de l’image et du découpage ; il ne constitue pas une capacité garantie.</small></p>
  <noscript><p>Les valeurs par défaut correspondent à 32 Go installés et 16 Go réservés. Activez JavaScript pour modifier ces hypothèses.</p></noscript>
</section>

{% details Les calculs et leurs hypothèses %}
Pour une image de taille $$S$$ et un pic mémoire $$M$$, en Go, l’ajustement des six points de la figure 4.11(a) donne

$$
M_{\mathrm{en\ cœur}}\approx162{,}94S+0{,}062.
$$

La configuration optimisée atteint un minimum proche de trois fois la taille de l’image. Avec 16 Go disponibles :

$$
S_{\mathrm{en\ cœur}}\approx\frac{16-0{,}062}{162{,}94}\approx0{,}098\text{ Go},
\qquad S_{\mathrm{hors\ cœur}}\approx\frac{16}{3}\approx5{,}3\text{ Go}.
$$

Pour le volume complet de 3,35 Go, prolonger la tendance en cœur donne environ **550 Go**, à comparer aux **10 Go mesurés** pour la configuration optimisée : environ **98 % de réduction estimée**. Cette comparaison entre les implémentations des chapitres 4 et 6 est distincte du gain mesuré de 84 % entre configurations hors-cœur, [présenté plus loin](#representations-compactes).

L’ajustement a été reconstitué à partir des points de la figure, sans les journaux de mesure bruts. Le coefficient hors-cœur dépend du contenu de l’image, du découpage et des choix de représentation détaillés dans la [section suivante](#representations-compactes). Il ne définit pas une limite universelle de la méthode.
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

## Deuxième volet : accélérer les interactions
{: #segmentation-interactive }

Ce second volet porte sur la **réactivité**, lorsque l’image et les structures de calcul tiennent en mémoire. En segmentation interactive, l’utilisateur désigne les objets d’intérêt et le fond à l’aide de **marqueurs**, observe le résultat, puis ajoute ou efface des marqueurs pour afininer les contours.

**Cette démarche est incrémentale par nature** : d’une étape à l’autre, l’image reste la même et les indications de l’utilisateur évoluent progressivement. Pourtant, les implémentations courantesde la ligne de partage des eaux traitent chaque correction comme un nouveau problème : elles relancent le calcul de la segmentation sur toute l’image, même pour une modification locale. Ces recalculs successifs imposent une attente répétée à l’utilisateur.

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
