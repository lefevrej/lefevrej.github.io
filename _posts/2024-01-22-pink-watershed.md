---
layout: distill
title: "Getting to grips with the watershed"
date: 2024-01-22
description: Learn how to performs basic watershed segmentation with Pink
tags: classes
categories: classes

thumbnail: assets/img/uo.png

authors:
  - name: Jean Cousty
    url: "https://perso.esiee.fr/~coustyj/"
    affiliations:
      name: ESIEE Paris
  - name: Josselin Lefèvre
    url: "lefevrej.github.io"
    affiliations:
      name: ESIEE Paris, Thermo Fisher Scientific

toc:
    - name: Problem 1 Uranium oxide
    - name: Problem 2 Segmentation of red blood cells
    - name: How To Watershed with PINK

images:
    compare: true
    slider: true
---

## Problem 1 Uranium oxide

<div class="row">
    <div class="col-sm mt-md-0">
        {% include figure.liquid path="assets/img/uo.png" class="img-fluid rounded z-depth-1"
        zoomable=true %}
    </div>
    <div class="col-sm mt-md-0">
        {% include figure.liquid path="assets/img/uo.png" class="img-fluid rounded z-depth-1"
        zoomable=true %}
    </div>
</div>

1. Segment all the cells of the attached uranium oxide image.
2. Remove the cells that touch the frame of the image.
3. Give some statistics about the cells (number, average size, etc.).

### Tools

| :-----------: | :------------: |
| - [pgm2GA](https://perso.esiee.fr/~coupriem/Pink/doc/html/pgm2GA_8c.html) | - [GAwatershed](https://perso.esiee.fr/~coupriem/Pink/doc/html/GAwatershed_8c.html) |
| - [GA2khalimsky](https://perso.esiee.fr/~coupriem/Pink/doc/html/GA2khalimsky_8c.html) | - [frame](https://perso.esiee.fr/~coupriem/Pink/doc/html/frame_8c.html) |
| - [nbcomp](https://perso.esiee.fr/~coupriem/Pink/doc/html/nbcomp_8c.html) | - [area](https://perso.esiee.fr/~coupriem/Pink/doc/html/area_8c.html) |

> **Hint**: you can use the [How to Watershed with PINK](#how-to-watershed-with-pink) section below to find some useful pink commands :wink:

## Problem 2 Segmentation of red blood cells

<style>
  .slider-example-focus {
    width: 50% !important;
  }

  .slider-example-focus:focus {
    outline: none;
  }

  .center-content {
    display: flex;
    justify-content: center;
  }
</style>

<div class="center-content">
    <img-comparison-slider class="slider-example-focus">
    {% include figure.liquid path="assets/img/bloodcells.png" class="img-fluid rounded z-depth-1 custom-image-size" slot="first" %}
    {% include figure.liquid path="assets/img/bloodcells_ws.png" class="img-fluid rounded z-depth-1 custom-image-size" slot="second" %}
    </img-comparison-slider>
</div>

1. Segment all the red blood cells in the attached bloodCells image.
2. Remove the ones that touch the edge of the image.
3. Separate the cells that are touching each other.
4. Give some statistics about the globules (number, average size).

> **Hint**: step 3 is tricky. It needs the notion of a [**distance map**](#distance-map) of a binary object.

## How to Watershed with PINK

### Key instructions

```shell
# To transform an image into a weighted edge graph:
pgm2GA im.pgm 0 relief.ga
```

> ##### TIP
>
> The second argument (here 0) indicates how we proceed to **weight**
> the edges (maximum / minimum or intensity difference between pixels at the ends of each edge).
>
> *Is the choice of one weighting function more relevant than another?
> In which cases?
> What difference could it make to the output?*
{: .block-tip }

```shell
# To calculate a Watershed Line of a weighted edge graph
GAwatershed relief.ga watershed.ga

# To visualize the result, we switch to the Khalimsky grid
GA2khalimsky watershed.ga 0 watershed.pgm
```

> ##### TIP
>
> To superimpose a segmentation (in the form of a binary image) on a grayscale image,
> we can use [`surimp`](https://perso.esiee.fr/~coupriem/Pink/doc/html/surimp_8c.html) **be careful the two images must be the same size**.
{: .block-tip }

To resize an image to the desired size we can use zoom or make the image `img.pgm` undergo a transition to a weighted graph and then to the Khalimsky grid.

```shell
pgm2GA img.pgm 0 img.ga
GA2khalimsky img.ga 0  imgRightSize.pgm
```

### Distance map

Basically, the distance map to a subset $$X$$ of the space $$E$$ is the image $$D_X$$ on $$E$$ defined, for every pixel $$x$$ in $$E$$ by
$$ D_X(x) = \min \{ \, d(x,y) \, | \, y \in X \, \} $$ where $$d(x,y)$$ denotes the (Euclidean) distance between $$x$$ and $$y$$.

The the distance map to $$X$$ is an image where the value of each pixel $$x$$ is the distance from this point to the closest point which belongs to the set $$X$$.

To obtain the distance map of an object in Pink you can use the command [`dist`](https://perso.esiee.fr/~coupriem/Pink/doc/html/dist_8c.html) for example with the command:

```shell
dist X.pgm 1 distMapToX.pgm
```

If needed you can convert the resulting image to a byte image (i.e., an image with values between 0 and 255) with the command:

```shell
long2byte distMapToX.pgm  1 distMapToX_Byte.pgm
```

> ##### WARNING
>
> If you calculate the map distance on an image that is too large,
> then the byte conversion will not work. The distances will be too large,
> resulting in an [integer overflow](https://www.wikiwand.com/en/Integer_overflow).
{: .block-warning }

### Threshold an image, interactively

Remind of the fantastic interactive [`seuil.tcl`](https://perso.esiee.fr/~coupriem/Pink/doc/html/seuil_8tcl.html).

### Filter an image...

* with an area closing: [`areaclosing`](https://perso.esiee.fr/~coupriem/Pink/doc/html/areaclosing_8c.html)
* with a dynamic closing (depth): [`heightminima`](https://perso.esiee.fr/~coupriem/Pink/doc/html/heightminima_8c.html)
* with a volume closing: [`volmaxima`](https://perso.esiee.fr/~coupriem/Pink/doc/html/volmaxima_8c.html) and [`inverse`](https://perso.esiee.fr/~coupriem/Pink/doc/html/inverse_8c.html)

### Compute statistics 

* To count the number of white pixels in a binary image: [`area`](https://perso.esiee.fr/~coupriem/Pink/doc/html/area_8c.html)
* To count the number of connected components in a binary image: [`nbcomp`](https://perso.esiee.fr/~coupriem/Pink/doc/html/nbcomp_8c.html)

### To obtain a black image with a white border

Try [`frame`](https://perso.esiee.fr/~coupriem/Pink/doc/html/frame_8c.html).