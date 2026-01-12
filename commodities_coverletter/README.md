# Commodity cover letter generator (LaTeX)

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python generate.py example_job.yaml

cd output
pdflatex cover_letter_redstone_group.tex
```