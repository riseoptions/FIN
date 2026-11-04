"""Build a portable GitHub source ZIP, excluding identity and nested archives."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parents[1]
out=root/'dist/moving-average-analyzer.zip'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root)
        if p.is_file() and not any(x in {'.git','.openai','__pycache__','.pytest_cache','.venv'} for x in rel.parts) and p.suffix not in {'.zip','.pyc','.tar','.gz'}:
            z.write(p,rel)
print(out)
