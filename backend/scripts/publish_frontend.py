"""Copy a completed Vite build into the committed FastAPI static directory."""
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'frontend/dist'
target=(ROOT/'backend/app/static').resolve()
assert target.is_relative_to(ROOT.resolve()) and target.name=='static'
if not (source/'index.html').is_file():
    raise SystemExit('Run npm run build --prefix frontend first.')
assets=target/'assets'
if assets.exists():
    assert assets.resolve().is_relative_to(target)
    # Only generated asset files are removed. Preserve unrelated support files.
    for file in assets.iterdir():
        if file.is_file() and file.resolve().is_relative_to(target):
            file.unlink()
shutil.copytree(source,target,dirs_exist_ok=True)
print('Published frontend build to backend/app/static.')
