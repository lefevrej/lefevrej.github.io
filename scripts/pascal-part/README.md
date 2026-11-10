# Pascal-Part hierarchy toolkit

Rebuild the blog's interactive images and region trees, or add your own selection
from **Ultrametric Pascal-Part**. The same exporter works in the website repository
and in the downloadable toolkit. No changes to the viewer JavaScript are needed
when you change the selected images.

## What each file does

| File | Purpose |
| --- | --- |
| `scripts/build_hierarchy_demo.py` | Read JPEG/UCM pairs, reconstruct three nested partitions, build the inclusion tree, validate it, and export browser assets. |
| `scripts/pascal-part/retained_ids.txt` | Editable image selection, one ID per line, in display order. |
| `scripts/pascal-part/names.json` | Optional French and English display names, keyed by image ID. Unknown IDs display their ID. |
| `assets/js/thesis-hierarchy.js` | Draw the image overlay and SVG tree; link scale, image and node selections. |
| `assets/css/thesis-hierarchy.css` | Responsive, theme-aware figure styling. |
| `_includes/thesis-hierarchy.html` | Bilingual Jekyll markup used by the blog. |
| `scripts/pascal-part/preview.html` | Standalone viewer, without Jekyll. |
| `scripts/pascal-part/test_exporter.py` | Data and command-line regression tests. |
| `scripts/package_pascal_part_toolkit.py` | Rebuild the downloadable ZIP from these source files. |

The coloured image overlays and tree are drawn in the browser. There are no
hand-edited tree images or extra TikZ-generation steps for these examples.

## 1. Install the Python dependencies

From the website repository, or the root of the extracted toolkit:

```bash
python3 -m venv .venv-pascal-part
source .venv-pascal-part/bin/activate
python -m pip install -r scripts/pascal-part/requirements.txt
```

In Windows PowerShell, use `python` in place of `python3` and activate with
`.\.venv-pascal-part\Scripts\Activate.ps1`.
The exporter requires Python 3.9 or newer, NumPy and Pillow. It has been tested
with NumPy 2.3.5 and Pillow 13.0.0.

## 2. Choose images from your extracted dataset

Point to the extracted export, or directly to its `pascal_parts/` directory:

```bash
DATASET="/path/to/extracted-dataset/pascal_parts"
```

List the IDs which have both a photograph and a contour map:

```bash
python scripts/build_hierarchy_demo.py "$DATASET" --list
```

Add the IDs you want to `scripts/pascal-part/retained_ids.txt`. Keep the existing
five lines if you want to retain those examples. Blank lines and `#` comments
are allowed; duplicate IDs are rejected.

Optionally add names to `scripts/pascal-part/names.json`:

```json
{
  "2010_004483": {"fr": "Oiseau", "en": "Bird"}
}
```

Names are display labels only. They do not supply semantic names for individual
tree regions or change the segmentation.

## 3. Rebuild the website assets

```bash
python scripts/build_hierarchy_demo.py "$DATASET" \
  --ids-file scripts/pascal-part/retained_ids.txt \
  --names scripts/pascal-part/names.json \
  --default 2010_005565
```

`--default` must be in your selection. Omit it to preserve the currently exported
default if it is still selected, or use the first selected ID otherwise.
If neither `--ids` nor `--ids-file` is supplied, the exporter reads
`retained_ids.txt` from the dataset ZIP/folder itself. When passing `pascal_parts/`
directly, it also looks for that file in its parent export directory.

For a separate experiment, without changing the blog's current selection:

```bash
python scripts/build_hierarchy_demo.py "$DATASET" \
  --ids 2010_005492 2010_004483 \
  --default 2010_005492 \
  --output /tmp/pascal-part-example
```

The default output is `assets/data/thesis-hierarchy/`, with:

- the original JPEG bytes for each selected image;
- `ID-labels.png`, an exact 8-bit map of the finest-region IDs;
- `hierarchies.json`, containing areas, parent/child links and the three cuts.

The manifest is replaced with the chosen selection; it is not an append command.
All samples are validated before output changes, and the manifest is replaced
last. Previously exported files which are no longer referenced are left intact.
Do not resize or lossily compress the label PNGs: their pixel values are IDs.

## 4. Preview the result

For the standalone viewer, after exporting to the default output:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Open [the standalone preview](http://localhost:8000/scripts/pascal-part/preview.html).
Serve the **repository/toolkit root**, not just the `scripts` directory.
Use HTTP: opening the HTML with `file://` prevents its JSON from loading in most
browsers. The standalone page uses the same viewer script and styles as the blog.

In the website repository, the existing two posts automatically use the new
manifest. Preview them with:

```bash
bundle exec jekyll serve --host 0.0.0.0 --port 4000
```

Regenerate the download after changing the toolkit source:

```bash
python scripts/package_pascal_part_toolkit.py
```

This writes `assets/downloads/pascal-part-toolkit.zip`. It contains the toolset,
not the full dataset; point the exporter at your own copy of the archive.

## Input format and scope

An extracted dataset directory must have this structure:

```text
dataset/
  retained_ids.txt                 # optional when --ids/--ids-file is supplied
  pascal_parts/
    JPEGImages/ID.jpg
    ucms/ID.png
```

Both `dataset/` and `dataset/pascal_parts/` work as the source. A directory with
`JPEGImages/` and `ucms/` directly inside it also works, regardless of its name.
You may also place additional compatible JPEG/UCM pairs in this structure. The tool **does not
predict a hierarchy from an unannotated photograph**: you must supply its UCM.

The original ZIP is also accepted as the source, without extraction, for example
`/mnt/c/Users/josselin.lefevre/Downloads/pascal_part_export.zip` in WSL.

This viewer is designed for the three Pascal-Part thresholds **0, 127 and 255**.
The UCM must be 8-bit grayscale on a **(2H+1) × (2W+1) Khalimsky grid**, with
zero-valued pixel centres at odd coordinates. Adjacent image pixels join when
their intervening edge value is less than or equal to the threshold. The outer
frame and grid vertices are not treated as image pixels.

A map may omit a level (for example, contain only 0 and 255). In that case two
displayed scales can have the same partition. Equal regions share one node;
no artificial unary nodes are added. The tree can have more than two children
per node. At most **255 finest regions per image** are supported by the current
8-bit label format. Arbitrary continuous-valued hierarchies require a different
export/viewer configuration; they are not silently quantized by this tool.

Dimensions, value ranges, nesting, area conservation, full coverage and exact
reconstruction of all three threshold partitions are checked. Run the tests with:

```bash
python -m unittest discover -s scripts/pascal-part -p 'test_*.py'
```

## Dataset credit

**Ultrametric Pascal-Part**: Raphael Lapertot, Giovanni Chierchia and Benjamin
Perret, *Supervised Learning of Hierarchical Image Segmentation*, CIARP 2023,
LNCS 14469, pp. 201–213, Springer (2024; first online November 2023).
[Publication](https://doi.org/10.1007/978-3-031-49018-7_15).
The toolset does not change the source dataset's terms or the photographs'
attribution requirements.
