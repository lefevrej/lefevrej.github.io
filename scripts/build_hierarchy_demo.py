"""Export the retained Pascal Parts images and their region-inclusion trees.

Usage: python scripts/build_hierarchy_demo.py /path/to/pascal_part_export.zip
Requires numpy and Pillow. Only retained_ids.txt and its image/UCM pairs are read.
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


def export(archive, output):
    output.mkdir(parents=True, exist_ok=True)
    names = {
        '2010_005715': {'fr': 'Avion', 'en': 'Aeroplane'},
        '2010_005604': {'fr': 'Chien', 'en': 'Dog'},
        '2010_005565': {'fr': 'Trains', 'en': 'Trains'},
        '2010_005492': {'fr': 'Chat', 'en': 'Cat'},
        '2010_004483': {'fr': 'Oiseau', 'en': 'Bird'},
    }
    samples = []
    with zipfile.ZipFile(archive) as z:
        ids = z.read('retained_ids.txt').decode('utf-8-sig').split()
        if not ids or len(set(ids)) != len(ids):
            raise ValueError('Missing or duplicate retained IDs')
        for image_id in ids:
            if not all(c.isdigit() or c == '_' for c in image_id):
                raise ValueError('Invalid image ID')
            photo = z.read(f'pascal_parts/JPEGImages/{image_id}.jpg')
            image = Image.open(BytesIO(photo))
            ucm = np.asarray(Image.open(BytesIO(z.read(f'pascal_parts/ucms/{image_id}.png'))))
            if ucm.shape != (2 * image.height + 1, 2 * image.width + 1):
                raise ValueError(f'UCM/image size mismatch: {image_id}')
            levels = np.unique(ucm).tolist()
            if levels != [0, 127, 255]:
                raise ValueError(f'Unexpected levels for this three-level example: {levels}')
            fine, coarse, whole = [partition(ucm, t) for t in levels]
            assert whole.max() == 0
            leaf_count = int(fine.max()) + 1
            assert leaf_count < 256
            nodes = []
            for i in range(leaf_count):
                positions = np.flatnonzero(fine == i)
                nodes.append(dict(id=i + 1, level=0, children=[],
                                  area=len(positions), anchor=int(positions[len(positions) // 2])))
            middle = []
            for group in range(int(coarse.max()) + 1):
                leaves = (np.unique(fine[coarse == group]) + 1).tolist()
                for leaf in leaves:
                    # Every fine region belongs wholly to a single coarse one.
                    assert np.all(coarse[fine == leaf - 1] == group)
                if len(leaves) == 1:
                    middle.append(leaves[0])  # No artificial unary nodes.
                    continue
                biggest = max(leaves, key=lambda v: nodes[v - 1]['area'])
                node = dict(id=len(nodes) + 1, level=1, children=leaves,
                            area=sum(nodes[v - 1]['area'] for v in leaves),
                            anchor=nodes[biggest - 1]['anchor'])
                nodes.append(node)
                middle.append(node['id'])
            root_id = len(nodes) + 1
            biggest = max(middle, key=lambda v: nodes[v - 1]['area'])
            nodes.append(dict(id=root_id, level=2, children=middle,
                              area=image.width * image.height,
                              anchor=nodes[biggest - 1]['anchor']))
            for node in nodes:
                for child in node['children']:
                    nodes[child - 1]['parent'] = node['id']
                if node['children']:
                    assert node['area'] == sum(nodes[c - 1]['area'] for c in node['children'])
            nodes[-1]['parent'] = None
            cuts = [list(range(1, leaf_count + 1)), middle, [root_id]]
            # Verify every cut covers every pixel exactly once and reconstructs
            # the corresponding original threshold partition (up to label names).
            for cut, expected in zip(cuts, [fine, coarse, whole]):
                leaf_to_node = {}
                def descend(node_id, owner):
                    node = nodes[node_id - 1]
                    if not node['children']:
                        assert node_id not in leaf_to_node
                        leaf_to_node[node_id] = owner
                    for child in node['children']:
                        descend(child, owner)
                for node_id in cut:
                    descend(node_id, node_id)
                assert len(leaf_to_node) == leaf_count
                predicted = np.array([leaf_to_node[i + 1] for i in range(leaf_count)])[fine]
                assert len(np.unique(predicted)) == len(np.unique(expected))
                assert all(len(np.unique(predicted[expected == i])) == 1 for i in np.unique(expected))
            (output / f'{image_id}.jpg').write_bytes(photo)
            Image.fromarray((fine + 1).astype(np.uint8)).save(output / f'{image_id}-labels.png', optimize=True)
            samples.append(dict(id=image_id, names=names.get(image_id, dict(fr=image_id, en=image_id)),
                                width=image.width, height=image.height, image=f'{image_id}.jpg',
                                labels=f'{image_id}-labels.png', nodes=nodes, cuts=cuts, root=root_id))
            print(image_id, [len(cut) for cut in cuts], 'regions; validated')
    manifest = dict(version=1, default='2010_004483', thresholds=[0, 127, 255], samples=samples)
    (output / 'hierarchies.json').write_bytes(json.dumps(manifest, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/data/thesis-hierarchy')
    args = parser.parse_args()
    export(args.archive, args.output)
