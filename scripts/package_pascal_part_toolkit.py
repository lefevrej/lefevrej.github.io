"""Package the Pascal-Part toolset, without dataset images or local environments."""
import argparse
from pathlib import Path
import zipfile


def package(root, output):
    files = [
        'scripts/build_hierarchy_demo.py',
        'scripts/package_pascal_part_toolkit.py',
        'scripts/pascal-part/README.md',
        'scripts/pascal-part/requirements.txt',
        'scripts/pascal-part/retained_ids.txt',
        'scripts/pascal-part/names.json',
        'scripts/pascal-part/preview.html',
        'scripts/pascal-part/test_exporter.py',
        'assets/js/thesis-hierarchy.js',
        'assets/css/thesis-hierarchy.css',
        '_includes/thesis-hierarchy.html',
    ]
    for name in files:
        if not (root / name).is_file():
            raise ValueError(f'Missing toolkit source: {name}')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        prefix = 'pascal-part-toolkit/'
        archive.write(root / 'scripts/pascal-part/README.md', prefix + 'README.md')
        for name in files:
            archive.write(root / name, prefix + name)
    print(f'Packaged {len(files) + 1} files: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    package(root, args.output or root / 'assets/downloads/pascal-part-toolkit.zip')
