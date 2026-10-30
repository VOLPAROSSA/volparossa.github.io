#!/usr/bin/env python3
"""Export the reviewed shared design for a future independent project site."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from build_site import ROOT, VERSION

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True, help='New or empty destination')
args = parser.parse_args()
output = args.output.resolve()
if output.exists() and any(output.iterdir()):
    raise SystemExit('Use a new or empty destination; existing work is never replaced.')
output.mkdir(parents=True, exist_ok=True)
for name in ('site.css','site.js','tokens.css','logo.png','favicon.png','social.jpg'):
    (output/'assets').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'assets'/name, output/'assets'/name)
shutil.copytree(ROOT/'assets/fonts',output/'assets/fonts')
shutil.copytree(ROOT/'assets/icons',output/'assets/icons')
shutil.copytree(ROOT/'site/templates',output/'templates')
shutil.copy2(ROOT/'LICENSE',output/'LICENSE')
html=(ROOT/'examples/volparossa-application/index.html').read_text()
html=html.replace('../../assets/','assets/').replace('https://volparossa.org/examples/volparossa-application/','https://volparossa.org/volparossa-example/')
(output/'index.html').write_text(html)
(output/'.nojekyll').touch()
files={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob('*')) if p.is_file()}
(output/'theme-version.json').write_text(json.dumps({'version':VERSION,'files':files},indent=2)+'\n')
print(f'Exported design {VERSION} to {output}; change the example canonical before publication.')
