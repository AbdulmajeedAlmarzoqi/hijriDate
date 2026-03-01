"""Build script to package the Hijri Date NVDA add-on."""
import os
import re
import zipfile

def get_version(addon_dir):
    """Read version from manifest.ini."""
    manifest_path = os.path.join(addon_dir, 'manifest.ini')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'version\s*=\s*"?([^"\s]+)"?', line)
            if match:
                return match.group(1)
    return '0.0.0'

def build_addon():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    addon_dir = os.path.join(base_dir, 'hijriDate')
    version = get_version(addon_dir)
    output_file = os.path.join(base_dir, f'hijriDate-{version}.nvda-addon')

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(addon_dir):
            for f in files:
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, addon_dir)
                # Skip __pycache__ and .pyc files
                if '__pycache__' in filepath or f.endswith('.pyc'):
                    continue
                zf.write(filepath, arcname)
                print(f'  Added: {arcname}')

    print(f'\nAdd-on packaged successfully: {output_file}')

if __name__ == '__main__':
    build_addon()
