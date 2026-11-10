# Hierarchical segmentation introduction

The five photographs and their contour maps come from the user-supplied
`pascal_part_export.zip` (Ultrametric Pascal-Part export, based on Pascal VOC / Pascal-Part). All and only the
image IDs in `retained_ids.txt` are included. Original JPEG bytes are preserved.
No semantic part names, model predictions, or extra scales have been added.

The UCMs have values 0, 127 and 255 on a (2H+1, 2W+1) Khalimsky grid.
At each threshold, adjacent image pixels are joined when the intervening edge
has a value less than or equal to that threshold. This yields three nested
partitions, including the whole image. Equal regions across scales share one
tree node: artificial unary nodes are omitted. The inclusion tree may have
more than two children per node; it is not a binary refinement of these data.

`*-labels.png` stores finest-region IDs as exact 8-bit grayscale values;
do not resize, quantize, colour-convert or lossily recompress these files.
The JSON contains region areas, parent/child links and the three cuts.
The browser reconstructs the masks for each cut from this single label map.

Rebuild from the original archive, with Python, numpy and Pillow:

    python scripts/build_hierarchy_demo.py /path/to/pascal_part_export.zip

The exporter verifies dimensions, region nesting, area conservation, complete
pixel coverage, and reconstruction of every threshold partition for all five
samples. The full 10,103-image archive is not copied into the website.

Dataset reference: Raphael Lapertot, Giovanni Chierchia and Benjamin Perret,
*Supervised Learning of Hierarchical Image Segmentation*, CIARP 2023,
LNCS 14469, pp. 201–213, Springer (2024; first online 27 November 2023).
https://doi.org/10.1007/978-3-031-49018-7_15

For an extracted dataset and editable image selections, see scripts/pascal-part/README.md. The complete toolkit is available at assets/downloads/pascal-part-toolkit.zip.
