#!/usr/bin/env python3
"""Export the reviewed shared design for an independent project site."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from build_site import ROOT, VERSION

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True, help='New or empty destination')
parser.add_argument('--source-only', action='store_true', help='Omit the example page and its library social image')
args = parser.parse_args()
if subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=ROOT, text=True).strip():
    raise SystemExit('Commit/review the source first; theme exports must identify an exact clean commit.')
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
output = args.output.resolve()
if output.exists() and any(output.iterdir()):
    raise SystemExit('Use a new or empty destination; existing work is never replaced.')
output.mkdir(parents=True, exist_ok=True)
(output/'assets').mkdir()
for name in ('site.css','site.js','tokens.css','logo.png','logo-original.png','favicon.png'):
    shutil.copy2(ROOT/'assets'/name, output/'assets'/name)
shutil.copy2(ROOT/'favicon.ico',output/'favicon.ico')
shutil.copytree(ROOT/'assets/fonts',output/'assets/fonts')
shutil.copytree(ROOT/'assets/icons',output/'assets/icons')
(output/'assets/upstream').mkdir()
for name in ('opencode.svg','immich.svg','opencloud.svg','OPENCODE-LICENSE.txt','IMMICH-LICENSE.txt','OPENCLOUD-DOCS-LICENSE.txt'):
    shutil.copy2(ROOT/'assets/upstream'/name,output/'assets/upstream'/name)
shutil.copytree(ROOT/'site/templates',output/'templates')
shutil.copytree(ROOT/'site/data',output/'data')
(output/'shared').mkdir()
shutil.copy2(ROOT/'scripts/shared_navigation.py',output/'shared/navigation.py')
(output/'notices').mkdir()
for name in ('ASSETS.md','upstream-sources.json'):
    shutil.copy2(ROOT/'docs/development'/name,output/'notices'/name)
shutil.copy2(ROOT/'site/shared-theme.md',output/'README.md')
shutil.copy2(ROOT/'LICENSE',output/'LICENSE')
if not args.source_only:
    shutil.copy2(ROOT/'assets/social.jpg',output/'assets/social.jpg')
    html=(ROOT/'examples/volparossa-application/index.html').read_text()
    html=html.replace('../../assets/','assets/').replace('https://volparossa.org/examples/volparossa-application/','https://volparossa.org/volparossa-example/')
    (output/'index.html').write_text(html)
    (output/'.nojekyll').touch()
files={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob('*')) if p.is_file()}
(output/'theme-version.json').write_text(json.dumps({'version':VERSION,'source_repository':'https://github.com/VOLPAROSSA/volparossa.github.io','source_commit':commit,'source_only':args.source_only,'files':files},indent=2)+'\n')
print(f'Exported design {VERSION} from {commit} to {output}.')
if not args.source_only:
    print('Replace the noindex example and its canonical before publication.')
