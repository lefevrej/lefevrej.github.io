"""Regression checks for input selection and exact three-level region trees."""
import importlib.util
import json
from io import BytesIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import numpy as np
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / 'build_hierarchy_demo.py'
spec = importlib.util.spec_from_file_location('hierarchy_exporter', SCRIPT)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'input'
        for folder in ('JPEGImages', 'ucms'):
            (self.source / 'pascal_parts' / folder).mkdir(parents=True)
        self.add('new_image', [127, 255])
        (self.source / 'retained_ids.txt').write_text('new_image\n', encoding='utf-8')
        self.output = self.root / 'output'

    def tearDown(self):
        self.temp.cleanup()

    def add(self, name, edges):
        Image.new('RGB', (3, 1), 'grey').save(self.source / f'pascal_parts/JPEGImages/{name}.jpg')
        ucm = np.zeros((3, 7), dtype=np.uint8)
        ucm[1, 2], ucm[1, 4] = edges
        Image.fromarray(ucm).save(self.source / f'pascal_parts/ucms/{name}.png')

    def test_known_nested_partitions_and_original_photo(self):
        manifest = exporter.export(self.source, self.output)
        sample = manifest['samples'][0]
        self.assertEqual(manifest['default'], 'new_image')
        self.assertEqual(sample['names'], dict(fr='new_image', en='new_image'))
        self.assertEqual([len(cut) for cut in sample['cuts']], [3, 2, 1])
        self.assertEqual([node['area'] for node in sample['nodes']], [1, 1, 1, 2, 3])
        self.assertEqual(sample['nodes'][3]['children'], [1, 2])
        self.assertEqual(sample['nodes'][4]['children'], [4, 3])
        self.assertEqual(np.asarray(Image.open(self.output / sample['labels'])).tolist(), [[1, 2, 3]])
        self.assertEqual((self.source / 'pascal_parts/JPEGImages/new_image.jpg').read_bytes(),
                         (self.output / sample['image']).read_bytes())

    def test_absent_intermediate_level_and_single_region(self):
        self.add('two_regions', [0, 255])
        self.add('whole', [0, 0])
        manifest = exporter.export(self.source, self.output, ['two_regions', 'whole'], default='whole')
        first, second = manifest['samples']
        self.assertEqual([len(c) for c in first['cuts']], [2, 2, 1])
        self.assertEqual(first['cuts'][0], first['cuts'][1])
        self.assertEqual(len(second['nodes']), 1)
        self.assertEqual(second['cuts'], [[1], [1], [1]])

    def test_extracted_pascal_parts_folder_directly(self):
        direct = self.source / 'pascal_parts'
        manifest = exporter.export(direct, self.output)
        self.assertEqual(manifest['samples'][0]['id'], 'new_image')
        source = exporter.DatasetSource(direct)
        try:
            self.assertEqual(source.available_ids(), ['new_image'])
        finally:
            source.close()

    def test_names_order_and_default(self):
        self.add('another', [0, 255])
        names = {'another': {'en': 'Another example', 'fr': 'Autre exemple'}}
        first = exporter.export(self.source, self.output, ['new_image', 'another'], names, 'another')
        self.assertEqual(first['samples'][1]['names']['fr'], 'Autre exemple')
        second = exporter.export(self.source, self.output, ['another', 'new_image'])
        self.assertEqual(second['default'], 'another')
        third = exporter.export(self.source, self.output, ['new_image'])
        self.assertEqual(third['default'], 'new_image')
        with self.assertRaises(ValueError):
            exporter.export(self.source, self.output, ['new_image'], default='absent')

    def test_zip_and_cli_selection(self):
        archive = self.root / 'dataset.zip'
        with zipfile.ZipFile(archive, 'w') as z:
            for p in self.source.rglob('*'):
                if p.is_file():
                    z.write(p, p.relative_to(self.source).as_posix())
        result = subprocess.run([sys.executable, str(SCRIPT), str(archive), '--list'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'new_image')
        ids = self.root / 'ids.txt'
        ids.write_text('# editable selection\nnew_image\n', encoding='utf-8')
        result = subprocess.run([sys.executable, str(SCRIPT), str(archive), '--ids-file', str(ids),
                                 '--output', str(self.output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.output / 'hierarchies.json').read_bytes())['default'], 'new_image')

    def test_invalid_selection_does_not_change_existing_export(self):
        exporter.export(self.source, self.output)
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        for ids in (['new_image', 'missing'], ['new_image', 'new_image'], ['../escape']):
            with self.assertRaises(ValueError):
                exporter.export(self.source, self.output, ids)
            self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})
        Image.new('L', (2, 2)).save(self.source / 'pascal_parts/ucms/new_image.png')
        with self.assertRaises(ValueError):
            exporter.export(self.source, self.output)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})


if __name__ == '__main__':
    unittest.main()
