"""Build interactive hierarchy examples from Ultrametric Pascal-Part JPEG/UCM pairs.

Requires Python 3.9+, numpy and Pillow. Run with --help for selection options.
The associated contour map is required; this tool does not infer one from a photo.
"""
import argparse
import json
from pathlib import Path
import zipfile
from io import BytesIO

import numpy as np
from PIL import Image


def partition(ucm, threshold):
    """Connected components of pixel centres, joined across edges <= threshold.

    The (2H+1, 2W+1) Khalimsky grid stores pixel centres at odd coordinates.
    Even/odd and odd/even samples are the intervening edge weights; vertices
    and the outside frame do not constitute image pixels.
    """
    height, width = (np.array(ucm.shape) - 1) // 2
    labels = np.full((height, width), -1, dtype=np.int32)
    count = 0
    for y in range(height):
        for x in range(width):
            if labels[y, x] != -1:
                continue
            labels[y, x] = count
            queue = [(y, x)]
            index = 0
            while index < len(queue):
                yy, xx = queue[index]
                index += 1
                for dy, dx in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                    ny, nx = yy + dy, xx + dx
                    if (0 <= ny < height and 0 <= nx < width
                            and labels[ny, nx] == -1
                            and ucm[2 * yy + 1 + dy, 2 * xx + 1 + dx] <= threshold):
                        labels[ny, nx] = count
                        queue.append((ny, nx))
            count += 1
    return labels

class DatasetSource:
    """Read selected members without extracting the archive."""
    image_dir = 'pascal_parts/JPEGImages'
    ucm_dir = 'pascal_parts/ucms'

    def __init__(self, path):
        self.path = Path(path)
        self.zip = None if self.path.is_dir() else zipfile.ZipFile(self.path)
        if self.zip is None and (self.path / 'JPEGImages').is_dir() and (self.path / 'ucms').is_dir():
            self.image_dir, self.ucm_dir = 'JPEGImages', 'ucms'

    def close(self):
        if self.zip is not None:
            self.zip.close()

    def read(self, name):
        try:
            if self.zip:
                return self.zip.read(name)
            candidate = self.path / name
            if name == 'retained_ids.txt' and not candidate.is_file() and self.image_dir == 'JPEGImages':
                candidate = self.path.parent / name
            return candidate.read_bytes()
        except (KeyError, FileNotFoundError) as error:
            raise ValueError(f'Missing input: {name}') from error

    def available_ids(self):
        if self.zip:
            members = set(self.zip.namelist())
        else:
            members = {p.relative_to(self.path).as_posix()
                       for folder in (self.image_dir, self.ucm_dir)
                       for p in (self.path / folder).glob('*') if p.is_file()}
        prefix = self.image_dir + '/'
        return sorted(name[len(prefix):-4] for name in members
                      if name.startswith(prefix) and name.endswith('.jpg')
                      and f'{self.ucm_dir}/{name[len(prefix):-4]}.png' in members)


def read_ids(text):
    import re
    ids = [value for line in text.splitlines()
           for value in line.split('#', 1)[0].split()]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError('Select at least one image ID, without duplicates.')
    if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', value) for value in ids):
        raise ValueError('IDs may contain letters, digits, underscores and hyphens, not paths.')
    return ids


def make_hierarchy(ucm):
    """Three Pascal-Part cuts; equal regions share one node across levels."""
    partitions = [partition(ucm, value) for value in (0, 127, 255)]
    fine = partitions[0]
    count = int(fine.max()) + 1
    if count > 255:
        raise ValueError(f'{count} fine regions: the viewer supports at most 255 per image.')
    nodes = []
    for i in range(count):
        positions = np.flatnonzero(fine == i)
        nodes.append(dict(id=i + 1, level=0, children=[], parent=None,
                          area=len(positions), anchor=int(positions[len(positions) // 2])))
    owners = fine + 1
    cuts = [list(range(1, count + 1))]
    for level, labels in enumerate(partitions[1:], 1):
        cut, next_owners = [], np.empty_like(owners)
        for group in range(int(labels.max()) + 1):
            members = set(np.unique(owners[labels == group]).tolist())
            children = [child for child in cuts[-1] if child in members]
            for child in children:
                if not np.all(labels[owners == child] == group):
                    raise ValueError('The threshold partitions are not nested.')
            if len(children) == 1:
                owner = children[0]
            else:
                biggest = max(children, key=lambda child: nodes[child - 1]['area'])
                owner = len(nodes) + 1
                nodes.append(dict(id=owner, level=level, children=children, parent=None,
                                  area=sum(nodes[child - 1]['area'] for child in children),
                                  anchor=nodes[biggest - 1]['anchor']))
                for child in children:
                    if nodes[child - 1]['parent'] is not None:
                        raise ValueError('A region has multiple parents.')
                    nodes[child - 1]['parent'] = owner
            cut.append(owner)
            next_owners[labels == group] = owner
        cuts.append(cut)
        owners = next_owners
    if len(cuts[-1]) != 1:
        raise ValueError('The last partition must cover the whole image as one region.')

    def leaves(node_id):
        n = nodes[node_id - 1]
        return [node_id] if not n['children'] else [leaf for c in n['children'] for leaf in leaves(c)]

    # Verify each cut against all pixels of its threshold partition.
    for cut, expected in zip(cuts, partitions):
        mapping = np.zeros(count + 1, dtype=np.int32)
        for node_id in cut:
            for leaf in leaves(node_id):
                if mapping[leaf]:
                    raise ValueError('Overlapping regions in a cut.')
                mapping[leaf] = node_id
        if not np.all(mapping[1:]):
            raise ValueError('A cut does not cover the whole image.')
        actual = mapping[fine + 1]
        if len(np.unique(actual)) != len(np.unique(expected)) or any(
                len(np.unique(actual[expected == i])) != 1 for i in np.unique(expected)):
            raise ValueError('A tree cut does not reproduce its UCM partition.')
    for n in nodes:
        if n['children'] and n['area'] != sum(nodes[c - 1]['area'] for c in n['children']):
            raise ValueError('Region area is not conserved.')
    return nodes, cuts, cuts[-1][0], (fine + 1).astype(np.uint8)


def export(archive, output, ids=None, names=None, default=None):
    output = Path(output)
    source = DatasetSource(archive)
    try:
        ids = read_ids(source.read('retained_ids.txt').decode('utf-8-sig')) if ids is None else read_ids('\n'.join(ids))
        if default is not None and default not in ids:
            raise ValueError('--default must be one of the selected IDs.')
        names = {} if names is None else names
        if not isinstance(names, dict):
            raise ValueError('The names JSON must be an object keyed by image ID.')
        samples, files = [], {}
        for image_id in ids:
            photo = source.read(f'{source.image_dir}/{image_id}.jpg')
            with Image.open(BytesIO(photo)) as image:
                width, height = image.size
                if image.format != 'JPEG':
                    raise ValueError(f'{image_id}: the photograph must be a JPEG.')
                image.load()
            with Image.open(BytesIO(source.read(f'{source.ucm_dir}/{image_id}.png'))) as image:
                ucm = np.asarray(image).copy()
            if ucm.shape != (2 * height + 1, 2 * width + 1) or ucm.dtype != np.uint8:
                raise ValueError(f'{image_id}: expected an 8-bit grayscale UCM of size {2 * width + 1} x {2 * height + 1}.')
            if not set(np.unique(ucm)).issubset({0, 127, 255}) or np.any(ucm[1::2, 1::2]):
                raise ValueError(f'{image_id}: expected Pascal-Part values 0/127/255 and zero-valued pixel centres.')
            nodes, cuts, root, label_map = make_hierarchy(ucm)
            entry = names.get(image_id, {})
            if not isinstance(entry, dict):
                raise ValueError(f'{image_id}: names must contain optional "fr" and "en" strings.')
            display_names = {lang: entry.get(lang, image_id) for lang in ('fr', 'en')}
            if any(not isinstance(v, str) or not v.strip() for v in display_names.values()):
                raise ValueError(f'{image_id}: display names must be non-empty strings.')
            sample = dict(id=image_id, names=display_names, width=width, height=height,
                          image=f'{image_id}.jpg', labels=f'{image_id}-labels.png',
                          nodes=nodes, cuts=cuts, root=root)
            samples.append(sample)
            files[sample['image']] = photo
            buffer = BytesIO()
            Image.fromarray(label_map).save(buffer, format='PNG', optimize=True)
            files[sample['labels']] = buffer.getvalue()
            print(image_id, [len(cut) for cut in cuts], 'regions; validated')
    finally:
        source.close()
    # Keep the current default when it remains selected; otherwise use the first ID.
    if default is None:
        try:
            existing = json.loads((output / 'hierarchies.json').read_bytes()).get('default')
        except (FileNotFoundError, ValueError, AttributeError):
            existing = None
        default = existing if existing in ids else ids[0]
    manifest = dict(version=1, default=default, thresholds=[0, 127, 255], samples=samples)
    # Validate every selected sample before changing output files. Commit the
    # manifest last; old unreferenced assets are deliberately left untouched.
    import os
    import tempfile
    output.mkdir(parents=True, exist_ok=True)
    files['hierarchies.json'] = json.dumps(manifest, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    for name, data in files.items():
        fd, temporary = tempfile.mkstemp(dir=output, prefix='.pascal-part-')
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
            Path(temporary).replace(output / name)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Extracted dataset root, its pascal_parts/ folder, or a dataset ZIP.')
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--ids', nargs='+', help='Image IDs to export, in display order.')
    selection.add_argument('--ids-file', type=Path, help='ID list (one per line; # comments allowed).')
    parser.add_argument('--names', type=Path, help='JSON display names: {"ID": {"fr": "…", "en": "…"}}.')
    parser.add_argument('--default', help='Initially selected ID; must belong to the selection.')
    parser.add_argument('--list', action='store_true', help='List IDs with both a JPEG and UCM; do not export.')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/data/thesis-hierarchy')
    args = parser.parse_args()
    try:
        if args.list:
            source = DatasetSource(args.source)
            try:
                print('\n'.join(source.available_ids()))
            finally:
                source.close()
            return
        ids = read_ids(args.ids_file.read_text(encoding='utf-8-sig')) if args.ids_file else args.ids
        names_path = args.names or Path(__file__).parent / 'pascal-part/names.json'
        if args.names or names_path.exists():
            names = json.loads(names_path.read_text(encoding='utf-8-sig'))
        else:
            names = {}
        manifest = export(args.source, args.output, ids, names, args.default)
        print(f'Wrote {len(manifest["samples"])} images to {args.output / "hierarchies.json"}')
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(2, f'Error: {error}\n')


if __name__ == '__main__':
    main()
