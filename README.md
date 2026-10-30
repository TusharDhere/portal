# Azure Portal SOP Knowledge Base

A static documentation site built from your 13-part Azure Fundamentals notes plus 62 Azure Portal SOPs,
a troubleshooting knowledge base, interview mode, quick reference and production readiness checklist.
The output is one self-contained file: `dist/index.html`. No server or database is needed.

## Run locally
```
pip install -r requirements.txt
python build.py --local        # writes dist/index.html (adds the Mermaid diagram loader)
```
Open `dist/index.html` in a browser. The first load needs internet for Google Fonts and the Mermaid script
(pinned to mermaid@11.4.0 from jsDelivr). Without internet the page still works but diagrams show as text.
Use `python build.py` (without `--local`) for a copy to publish on a host that renders Mermaid itself.

## Run with Docker
```
docker compose up --build -d     # builds the image and starts the site
```
Open http://localhost:8080 (health check: http://localhost:8080/healthz). Stop with `docker compose down`.

Without Compose:
```
docker build -t azure-portal-sop-kb .
docker run -d --name azure-portal-sop-kb -p 8080:8080 azure-portal-sop-kb
```
The image is Python-based. It builds `dist/index.html` during the image build and starts `python app.py`, which serves it
(gzip-compressed) on `$PORT` (default 8080). Edit content, then rebuild with `docker compose up --build -d`.

**Deploying to a container host or PaaS:** the start command is `python app.py` (also in `Procfile`), the working directory is
`/app`, and the app listens on the `PORT` environment variable. Set the host's exposed port to the same value (8080 by default).
If a host reports "can't open file '/app/app.py'", it is running a different image or folder: make sure this project's root
(the folder containing `app.py`) is what gets deployed.

**nginx alternative:** `docker compose -f docker-compose.nginx.yml up --build -d` serves the static site with nginx
(`Dockerfile.nginx`, `nginx.conf`) on port 8080. Do not use it on hosts that force a `python` start command.

The browser still needs internet for Google Fonts, React and Mermaid, which load from CDNs.

## Project layout
| Path | What it holds |
|---|---|
| `source/` | Your original 13 study-guide HTML files. Content is extracted from here, nothing is deleted. |
| `template.html` | Page shell: CSS, layout, search, navigation, copy buttons, checklists, interview filters. |
| `app.py` | Small web server for the built site (`python app.py`, reads `$PORT`). |
| `build.py` | Extracts the 13 parts, builds the catalog, quick reference and views, writes `dist/index.html`. |
| `content/sops_core.py` | SOP page layout (`sop_html`), first 8 SOPs, comparison tables, production readiness. |
| `content/sops_identity_networking.py` | The `S()` helper and 18 Identity and Networking SOPs. |
| `content/sops_storage_compute_monitoring_dr_security_cost.py` | 27 further SOPs. |
| `content/sops_custom.py` | **Your own SOPs and catalog rows go here.** |
| `content/sop_sections.py` | Recommended configuration, related services, area best practices, callouts (Note, Warning, Cost) and field tables, by SOP id. |
| `content/sop_enrichment.py` | Prerequisites, diagrams, field tables, security and production notes by SOP id. |
| `content/troubleshooting.py` | Troubleshooting guides by service area. |
| `content/interview.py` | Added Advanced, Production, Why and Intermediate questions. |
| `content/screenshots.py` + `shots/shots.json` | Embedded Microsoft Learn screenshots. |
| `tools/add_screenshot.py` | Helper to add a screenshot to an SOP. |

## Add a new SOP
1. Open `content/sops_custom.py` and add an `S(...)` entry to `CUSTOM` (the file has the argument order).
   Use `|` to separate steps, validations and rollback items, and `symptom => fix` for troubleshooting rows.
2. Add a catalog row to `CAT`: `Service name|Category|concept part number|sop id`.
3. Optional extras for your SOP id: `content/sop_enrichment.py` dictionaries `P` (prerequisites), `A` (diagram as `A>B>C`),
   `SC` (security), `PR` (production), `F` (field table); and `content/sop_sections.py` dictionaries `REC` (recommended
   configuration), `REL` (related SOP ids), `COST` and `WARN` (callouts).
4. Run `python build.py --local` and open `dist/index.html`.

## Other additions
- **Troubleshooting guide:** add a `T('Area','Title','causes|..','portal checks|..','resolution|..','optional command')` line in `content/troubleshooting.py`.
- **Interview question:** add to `XQ` (Advanced, Production, Why) or `IQ` (Intermediate) in `content/interview.py`.
- **Quick reference table:** add to `CMP` in `content/sops_core.py`.
- **Screenshot:** `python tools/add_screenshot.py <sop-id> <image-url-or-file> "<alt>" <learn-url> "<title>"`.
- **Study notes:** edit the files in `source/`; the build re-extracts them.

## Sources and licensing
- Concepts, notes, Q&A and diagrams: your supplied ZIP.
- Procedures and Learn links: written from general Azure knowledge, each linking to its Microsoft Learn page
  (`https://learn.microsoft.com/en-us/azure/` and `/en-us/entra/`). **They have not been verified against the live docs.**
  Portal menus change; confirm against the linked page before relying on a step.
- Screenshots: Microsoft's public docs repositories on GitHub (licensed CC BY 4.0, (c) Microsoft), credited in each SOP.

## Design (v2 purple poster)
This package is the **v2 purple** design (poster-style hero with 3D discs, condensed headlines, glass panels; SOP pages are a hero band with numbered spec-sheet sections and a step timeline). The earlier look is saved as `azure-portal-sop-kb-v1-classic.zip`; to revert, deploy that package.

## Design details
- Theme tokens (light and dark), layout and animations are in the `<style>` block of `template.html`. The theme toggle remembers the choice in `localStorage` (`azth`).
- The footer ("Designed by Tushar Dhere") is the `<footer id="ft">` element in `template.html`.
- The home page is a small React component (`mountHome` in `template.html`). React 18.3.1 and ReactDOM load from cdnjs; if they fail to load, the plain static home content is shown instead.
- The sidebar is a drawer opened by the menu button. Nav items are capsules with a hover fill (see the `#nav a` rules at the end of the `<style>` block).
- Progress tracks the 13 Azure Fundamentals parts and the last reading position in `localStorage` (`azprog`); the top bar shows the percentage and a Continue button.
- Each SOP is its own page (`#sop-<id>`, section `v-sop-<id>`) with an index at `#sops`; previous/next follows the domain order set in `content/navigation.py`.
- Diagrams: `build.py` (marked `MERMAID-FIX`) prepends a theme/spacing directive to every diagram and turns literal `\n` in labels into line breaks; the CSS near the end of `template.html` keeps diagram colours readable in dark mode. Diagrams scroll sideways inside their card on phones.
- Motion respects `prefers-reduced-motion`. Domain colours are set in the `COL` map and the `data-dom` / `data-cat` CSS rules.

## Verification
SOP labels were cross-checked against the Microsoft docs source on GitHub (66 of 76 SOPs; 79% of labels matched directly, rest reviewed by hand). Ten SOPs could not be checked automatically. See the Verification section on the home page.

## Known gaps
27 SOPs have no embedded screenshot (they link to the Learn article instead). Portal screenshots exist for 35 of 76 SOPs; the rest link to Microsoft Learn. Procedures remain from general Azure knowledge
plus the label cross-check described above; confirm against the linked Learn page.
