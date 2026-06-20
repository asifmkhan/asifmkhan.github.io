# siffykhan.github.io

Personal academic website of **Prof. Mohammad Asif Khan** — Professor & Associate Dean,
University of Doha for Science & Technology.

Live site: https://siffykhan.github.io

## Structure

| File | Purpose |
|---|---|
| `index.html` | The entire site — single self-contained file (HTML + CSS + JS). |
| `scholar_data.json` | Metrics and per-year data the page reads at load. Source of truth for the numbers. |
| `scripts/update_scholar.py` | Refreshes `scholar_data.json` from Google Scholar. |
| `.github/workflows/update-scholar.yml` | Weekly GitHub Action that runs the script and commits any change. |

## How the numbers stay current

The page fetches `scholar_data.json` on load and fills in the citation count,
h-index, i10, and the two charts. A scheduled GitHub Action (Mondays 06:00 UTC)
runs `update_scholar.py`, which pulls fresh figures from Google Scholar and commits
them back. You can also trigger it manually from the repo's **Actions** tab →
*Update Scholar metrics* → *Run workflow*.

Google Scholar has no public API and sometimes blocks automated requests. When that
happens the script makes no change and the site keeps showing the last good values —
nothing breaks.

Fields **not** on Scholar — funding, patents, graduates, the "90+" publications
headline, and the publications-per-year chart — are maintained by hand in
`scholar_data.json`.

## Editing content

Prose, sections, and links live directly in `index.html`. To update text, edit it
there and commit. To change a headline number permanently, edit `scholar_data.json`.

### To add ORCID / LinkedIn / X links
Add another `<a class="chip" ...>` in the `.mh-links` block of `index.html` (and,
if you like, a matching button in the `#connect` section).

## Local preview

Because the page fetches a JSON file, open it through a local server (not `file://`):

```bash
cd <repo>
python3 -m http.server 8000
# then visit http://localhost:8000
```

Opened directly via `file://`, the page still renders using built-in fallback values.
