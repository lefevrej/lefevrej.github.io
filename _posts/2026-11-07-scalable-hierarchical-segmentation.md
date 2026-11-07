---
layout: distill
title: "Segmenting large images with less memory"
description: "Exact out-of-core computation and incremental interaction, from a CIFRE PhD at LIGM and Thermo Fisher Scientific."
date: 2026-11-07
lang: en
translation_lang: fr
translation_url: /blog/2026/segmentation-hierarchique-hors-coeur/
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
      name: "Thermo Fisher Scientific and LIGM, Université Gustave Eiffel"
toc:
  - name: "First contribution: exact out-of-core computation"
    id: exact-out-of-core-computation
  - name: "What fits on a workstation"
    id: workstation-capacity
  - name: "More compact representations"
    id: compact-representations
  - name: "Second contribution: faster interactive corrections"
    id: interactive-segmentation
  - name: "An industrial and scientific partnership"
    id: partnership
  - name: "Next steps"
    id: perspectives
images:
  compare: true
---

<p class="thesis-languages" aria-label="Reading language"><strong>English</strong> · <a href="{{ '/blog/2026/segmentation-hierarchique-hors-coeur/' | relative_url }}" lang="fr" hreflang="fr">Lire en français</a></p>

Electron microscopy produces 3D images containing billions of voxels. Analysing them requires **segmentation**: identifying and delineating regions of interest. Two obstacles follow: the memory needed for the computation and the delays that interrupt interactive work.

My CIFRE PhD, *Scalable Algorithms for Hierarchical Image and Data Segmentation*, carried out at **ESIEE Paris between LIGM and Thermo Fisher Scientific**, explores **two distinct problems**: **exact out-of-core computation** to control memory use, and **incremental interactive segmentation** to accelerate user corrections. An Amira<sup>™</sup> demonstrator provides a route towards industrial transfer.<d-cite key="lefevre2026thesis"></d-cite>

## First contribution: exact out-of-core computation
{: #exact-out-of-core-computation }

A 3.35 GB image can require hundreds of gigabytes to construct the structures used for segmentation. The thesis experiments include an 8-bit FIB-SEM volume of **2048 × 1536 × 1065 voxels**, approximately **3.35 billion voxels**. The classical in-core algorithm could not process the complete volume on the 256 GB workstation used in the study.<d-cite key="lucchi2012"></d-cite>

An **out-of-core algorithm** keeps data on disk and loads only the blocks needed for the current computation.

<figure class="l-page thesis-figure thesis-diagram">
  <img class="diagram-light" src="{{ '/assets/img/posts/scalable-segmentation/out-of-core.svg' | relative_url }}" width="1600" height="578" alt="An out-of-core workflow: load a few image blocks from disk into limited main memory, process them with the CPU, and write the result back to disk." data-zoomable>
  <img class="diagram-dark" src="{{ '/assets/img/posts/scalable-segmentation/out-of-core-dark.svg' | relative_url }}" width="1600" height="578" alt="An out-of-core workflow: load a few image blocks from disk into limited main memory, process them with the CPU, and write the result back to disk." data-zoomable>
  <figcaption>The out-of-core principle. Only the working portion of the data is resident in RAM. This diagram is adapted directly from the TikZ figure in my defense slides.</figcaption>
</figure>

The scientific challenge is preserving **region inclusion relationships** across the complete image, including regions that span several blocks. Processing each block independently can introduce artificial boundaries:

<div class="l-body thesis-figure thesis-pair">
  <figure>
    <img src="{{ '/assets/img/posts/scalable-segmentation/blockwise-expected.jpg' | relative_url }}" width="512" height="512" loading="lazy" alt="Expected segmentation with globally consistent boundaries." data-zoomable>
    <figcaption>Globally consistent result</figcaption>
  </figure>
  <figure>
    <img src="{{ '/assets/img/posts/scalable-segmentation/blockwise-independent.jpg' | relative_url }}" width="512" height="512" loading="lazy" alt="Segmentation obtained by processing blocks independently, showing artificial boundaries." data-zoomable>
    <figcaption>Independent block processing</figcaption>
  </figure>
</div>

Our **algebraic framework** constructs a distribution of the binary partition hierarchy: local trees consistent with one global representation. Three operations organize the computation: **select** extracts relevant information, **join** combines information from neighboring blocks, and **insert** completes and corrects local hierarchies.<d-cite key="lefevre2022,lefevre2025"></d-cite>

**Mathematical guarantees establish that blockwise computation recovers the hierarchy of the global calculation, under the same construction conventions.** The causal scheme also bounds auxiliary structures relative to neighboring elements of the distribution.

{% details Mathematical foundations %}
Chapter 4 and its supporting appendix contain **five definitions and nine mathematical results**: three properties, five lemmas, and one corollary. They formalize the operations, relationships between representations, and bounds on intermediate structures.

For a global hierarchy $$H$$ and a block $$S_i$$, the intended local element is

$$
H_i = \operatorname{select}(S_i,H).
$$

The challenge is constructing these elements without first storing the complete hierarchy $$H$$ in RAM. This exactness guarantee concerns the computation; whether a segmentation is suitable for an application is a separate question.
{% enddetails %}

The framework extends to regional attributes—area, volume, height, and minima—and to **watershed segmentation**, including its hierarchical version.<d-cite key="lefevre2024"></d-cite>

<figure class="l-page thesis-figure thesis-diagram">
  <img class="diagram-light" src="{{ '/assets/img/posts/scalable-segmentation/analysis-overview.svg' | relative_url }}" width="1600" height="938" loading="lazy" alt="A tiled microscopy image is represented by a distribution of binary partition hierarchies. Attributes are computed across the distribution and used for operations including connected filtering and watershed segmentation." data-zoomable>
  <img class="diagram-dark" src="{{ '/assets/img/posts/scalable-segmentation/analysis-overview-dark.svg' | relative_url }}" width="1600" height="938" loading="lazy" alt="A tiled microscopy image is represented by a distribution of binary partition hierarchies. Attributes are computed across the distribution and used for operations including connected filtering and watershed segmentation." data-zoomable>
  <figcaption>From a tiled image to hierarchical analysis. The TikZ overview from my defense connects the distributed representation to region attributes and segmentation operations.</figcaption>
</figure>

## What fits on a workstation
{: #workstation-capacity }

For the memory question, consider a **32 GB workstation** with **16 GB reserved for the system and other applications**: this leaves **16 GB for computation**. Models derived from the experiments suggest approximately **98 million voxels in core**, compared with **5.3 billion using a compact out-of-core representation**. The compact representation is explained in the [next section](#compact-representations).

These are **estimates** for uncompressed 8-bit images, assuming comparable memory coefficients. The factor of approximately **55** is not a measured capacity gain on that workstation.

<figure class="l-page thesis-figure">
  <img src="{{ '/assets/img/posts/scalable-segmentation/incore-memory.svg' | relative_url }}" loading="lazy" alt="Measured in-core and causal out-of-core peak RAM as image size increases. The in-core curve reaches approximately 239 GB at an image size of 1.47 GB." data-zoomable>
  <figcaption>The measured in-core curve used for the illustrative fit, alongside causal out-of-core configurations with different block widths. Thesis Figure 4.11(a). No full-volume in-core measurement is shown.</figcaption>
</figure>

<section class="thesis-memory" aria-labelledby="memory-model-title" data-thesis-memory data-locale="en">
  <h3 id="memory-model-title">Explore the memory assumptions</h3>
  <p>Change the RAM budget to compare the two illustrative models. All sizes use decimal GB; image sizes refer to uncompressed 8-bit data.</p>
  <div class="memory-inputs">
    <label for="memory-total">Installed RAM in GB
      <input id="memory-total" type="number" min="1" max="4096" step="1" value="32" inputmode="decimal">
    </label>
    <label for="memory-reserved">RAM reserved for the system and other apps in GB
      <input id="memory-reserved" type="number" min="0" max="4096" step="1" value="16" inputmode="decimal">
    </label>
  </div>
  <div aria-live="polite" aria-atomic="true">
    <p class="memory-error" data-memory-error hidden></p>
    <p>Available working budget: <strong><output data-memory-budget>16 GB</output></strong>.</p>
    <div class="thesis-table">
      <table>
        <thead><tr><th scope="col">Model</th><th scope="col">Estimated image size</th><th scope="col">8-bit voxel count</th></tr></thead>
        <tbody>
          <tr><th scope="row">In core</th><td><output data-memory-incore>98 MB</output></td><td><output data-memory-incore-voxels>98 million</output></td></tr>
          <tr><th scope="row">Optimized out of core</th><td><output data-memory-qfz>5.3 GB</output></td><td><output data-memory-qfz-voxels>5.3 billion</output></td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <p><small>Estimates without an additional safety margin. The optimization and its parameters are explained in the <a href="#compact-representations">next section</a>. The coefficient depends on those choices, image content, and partitioning; it is not a capacity guarantee.</small></p>
  <noscript><p>The default estimates above use 32 GB installed and 16 GB reserved. Enable JavaScript to change these assumptions.</p></noscript>
</section>

{% details Calculations and assumptions %}
With image size $$S$$ and peak RAM $$M$$ in GB, fitting the six points of Figure 4.11(a) gives

$$
M_{\mathrm{in\ core}}\approx162.94S+0.062.
$$

The optimized configuration reaches a minimum close to three times the raw image size. For a 16 GB budget:

$$
S_{\mathrm{in\ core}}\approx\frac{16-0.062}{162.94}\approx0.098\text{ GB},
\qquad S_{\mathrm{out\ of\ core}}\approx\frac{16}{3}\approx5.3\text{ GB}.
$$

Continuing the in-core trend to the complete 3.35 GB volume predicts about **550 GB**, compared with the optimized **measured minimum of 10 GB**: roughly **98% less RAM by estimation**. This comparison between the Chapter 4 and Chapter 6 implementations is distinct from the measured 84% gain between out-of-core configurations, [presented below](#compact-representations).

The fit was reconstructed from plotted points rather than raw measurement logs. The out-of-core coefficient depends on image content, partitioning, and the representation choices explained in the [next section](#compact-representations). It is not a universal capacity limit.
{% enddetails %}

## More compact representations
{: #compact-representations }

To reduce resource use further, we group pixels into **superpixels** defined by quasi-flat zones. A parameter $$\alpha$$ controls the granularity of this representation.

<figure class="l-body thesis-figure">
  <img-comparison-slider class="thesis-comparison" tabindex="0" aria-label="Compare the original microscopy image with its quasi-flat-zone representation at alpha 111">
    <img slot="first" src="{{ '/assets/img/posts/scalable-segmentation/superpixels-original.jpg' | relative_url }}" width="500" height="500" loading="lazy" alt="Original microscopy image">
    <img slot="second" src="{{ '/assets/img/posts/scalable-segmentation/superpixels-111.jpg' | relative_url }}" width="500" height="500" loading="lazy" alt="Quasi-flat-zone representation at alpha 111">
  </img-comparison-slider>
  <figcaption>Move the divider to compare the original image with its representation at α = 111. Each zone is shown using its average intensity. The figure illustrates the change of representation, rather than a final segmentation.</figcaption>
</figure>

For marker-based watershed, the compact representation preserves the corresponding pixel-level result **when markers occupy distinct quasi-flat zones**. This condition retains the information needed to separate them.

<figure class="l-page thesis-figure">
  <img src="{{ '/assets/img/posts/scalable-segmentation/qfz-memory.svg' | relative_url }}" loading="lazy" alt="Measured peak memory versus number of blocks for the pixel-level Classic configuration and quasi-flat-zone configurations with alpha 66, 72, 82, and 111. The alpha 111 curve reaches a minimum of approximately 10 GB." data-zoomable>
  <figcaption>Measured peak memory for the 3.35-billion-voxel volume. Reproduced from thesis Figure 6.4(a). “Number of Slices” denotes the number of processing blocks in this experiment, not the number of acquired image planes.</figcaption>
</figure>

Experiments constructing the hierarchy distribution with the in-house implementation on a 256 GB workstation gave the following results:<d-cite key="lefevre2026thesis"></d-cite>

<div class="thesis-table" role="region" aria-label="Measured out-of-core results" tabindex="0" markdown="1">

| Resource | Result at α = 111 |
| :--- | :--- |
| **RAM** | Approximately **84% lower minimum peak**: about 10 GB versus 62 GB. |
| **Temporary storage** | Approximately **40 GB versus 299 GB**, an 87% reduction. |
| **Construction time** | Approximately **40 min versus 100 min**, a 60% reduction. |

</div>

Both configurations are out-of-core. They use pixel-level and superpixel representations with different partitioning strategies. The 84% compares the minima over a sweep of block counts; storage and time are compared at 80 blocks.

## Second contribution: faster interactive corrections
{: #interactive-segmentation }

This second contribution concerns **responsiveness**, when the image and computation structures fit in RAM. In interactive segmentation, the user identifies objects of interest and the background with **markers**, inspects the result, then adds or erases markers to refine the boundaries.

**The workflow is incremental by nature**: the image remains the same while the user’s instructions evolve step by step. Yet non-incremental watershed implementations treat each correction as a new problem, recomputing the segmentation across the entire image even for a local edit. Repeating this computation makes the user wait after each correction.

Our **incremental** method preserves the computation state between interactions. It reuses results that remain valid and updates only regions affected by adding or removing a marker. The update cost is proportional to the affected pixels, allowing local corrections to be incorporated quickly as the user progressively refines the segmentation.<d-cite key="lebon2023,lebon2025"></d-cite>

<div class="l-body thesis-figure thesis-stack">
  <figure>
    <svg viewBox="0 0 1024 768" width="1024" height="768" role="img" aria-labelledby="interactive-first-title">
      <title id="interactive-first-title">Early interactive plant segmentation, rotated clockwise to show the plant upright.</title>
      <image href="{{ '/assets/img/posts/scalable-segmentation/interactive-first.jpg' | relative_url }}" width="768" height="1024" transform="translate(1024 0) rotate(90)"></image>
    </svg>
    <figcaption>Early markers</figcaption>
  </figure>
  <figure>
    <svg viewBox="0 0 1024 768" width="1024" height="768" role="img" aria-labelledby="interactive-refined-title">
      <title id="interactive-refined-title">Refined interactive segmentation of the same upright plant.</title>
      <image href="{{ '/assets/img/posts/scalable-segmentation/interactive-refined.jpg' | relative_url }}" width="768" height="1024" transform="translate(1024 0) rotate(90)"></image>
    </svg>
    <figcaption>Refined segmentation</figcaption>
  </figure>
</div>

A parallel strategy accelerates larger updates. Across the five 3D benchmark volumes, the mean time was **0.34 seconds per interaction**, compared with **9.26 seconds for ITK**: approximately **27 times faster**, excluding initialization.<d-cite key="lebon2025"></d-cite>

These timings describe the experimental **in-core** implementation with simulated 3D interactions, not the Amira<sup>™</sup> demonstrator. The practical benefit is a shorter wait between a correction and its visible effect.

## An industrial and scientific partnership
{: #partnership }

The collaboration fulfilled **industrial and scientific objectives together**. Thermo Fisher Scientific’s operational needs informed the research questions; LIGM contributed expertise in mathematical morphology and graph algorithms. The resulting methods combine mathematical guarantees, measured performance, and software development.

The work produced **two journal articles and three international conference publications** while preparing transfer into the company’s tools. An Amira<sup>™</sup> demonstrator was presented at **VivaTech in 2025**. The [public C++ implementation of incremental interactive watershed](https://github.com/lebonq/incremental_watershed) accompanies the associated article and maintains a direct connection with the research community.<d-cite key="lebon2025"></d-cite>

**People behind the work.** Jean Cousty and Benjamin Perret at LIGM/ESIEE Paris, and Harold Phelippeau at Thermo Fisher Scientific, supervised the thesis. The interactive segmentation contribution was developed with Quentin Lebon. **My intern Matheus Sano also contributed to the work.** I also thank Nicolas Constanty, Franck Fauverte, and Daniel Lichau for their contributions to the Amira<sup>™</sup> demonstrator.

## Next steps
{: #perspectives }

The next research directions are to:

- reduce repeated region information by constructing hierarchies **across successive ranges of scales**, making full-resolution processing more economical;
- bring **incremental interactive updates into the out-of-core setting**;
- extend the computation of geometric region attributes;
- explore **parallel, distributed, and GPU architectures**, together with connections to deep learning.

These directions support further maturation of the demonstrator and evaluation of its integration into **Amira<sup>™</sup>/Avizo<sup>™</sup>**, across a wider range of data and user workflows.

*Figures adapted from my thesis and defense slides. Out-of-core results: Chapters 4 and 6; interactive segmentation: Chapter 7 and the associated paper. See also the [public thesis record](https://theses.fr/s339025).*

<script defer src="{{ '/assets/js/thesis-memory.js' | relative_url }}"></script>
