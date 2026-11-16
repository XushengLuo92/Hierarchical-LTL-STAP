# Project website

Live site: https://xushengluo92.github.io/Hierarchical-LTL-STAP/

GitHub Pages serves the repository root from `codex/scenario-demo-refresh`. `.nojekyll` keeps it a plain static site. Push changes to that branch to publish.

- `index.html`: layout, introduction, and first-demo fallback.
- `site/demos.js`: selectable demo descriptions and media paths.
- `site/app.js`: accessible demo selection and query-string links (`?demo=2`).
- `site/style.css`: responsive layout.
- `demo/generated/`: existing video and replay assets, shared with the README.

Preview from the repository root with `python3 -m http.server 8000`, then open `http://localhost:8000`. No Node, build step, or external CDN is required. When replacing a video, refresh its poster as well.
