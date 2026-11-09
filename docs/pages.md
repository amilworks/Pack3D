# The project website

The project website, <https://amilworks.github.io/Pack3D/>, tells the paper's story in one page, with
interactive figures. It is a static site: the files in [website/](../website/) are served as they
are, and nothing is built when it deploys. The [Deploy website](../.github/workflows/pages.yml)
workflow publishes them with GitHub Pages. One file, `d3.min.js`, is built ahead of time with
[tools/d3](../tools/d3/) and kept in `website/` (see [Rebuild d3](#rebuild-d3)).

## Turn on GitHub Pages (once)

1. On GitHub, open the repository's **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.

After that, every push to `main` that changes `website/` deploys the site. To deploy by hand, open the
**Actions** tab, choose **Deploy website**, and select **Run workflow**.

If you pushed before turning Pages on, the first deployment failed at its **Configure Pages** step.
Turn Pages on, then run **Deploy website** by hand once.

## What the workflow does

1. Runs [tools/check_pages_artifact.py](../tools/check_pages_artifact.py) on `website/`. The check
   stops the deployment if the folder has no `index.html`, if it holds linked files, or if it holds
   private artifacts such as `.env` files, keys or checkpoints. It never deploys the repository root.
2. Uploads `website/` as the Pages artifact.
3. Deploys the artifact to the `github-pages` environment.

The first job can only read the repository and the Pages settings. Only the deploy job can write to
Pages and request the identity token that Pages requires. Every action is pinned to a commit hash,
and the checkout does not keep credentials. The workflow deploys only from the default branch.

## What is in `website/`

| File | What it is |
| :--- | :--- |
| `index.html` | The page, with its styles inline, and the search, Google Scholar and link-preview tags. |
| `404.html` | The page GitHub Pages shows for a missing address. It stands alone, with its own styles and absolute links, since Pages serves it at any depth. |
| `app.js` | The page's script, with the plotted data built in. |
| `d3.min.js` | A partial build of d3 7.8.5: the modules the charts draw with, made by [tools/d3](../tools/d3/). Their licenses are in `d3-LICENSE.txt`. |
| `figure1-1000.webp`, `figure1-1500.webp`, `figure1-2300.webp` | Figure 1 of the paper as pictures at three widths. The browser picks the one that suits the screen, for the tour's overview and its minimap. |
| `figure1.min.svg` | Figure 1 as a vector, which the tour loads when the reader stops on the figure or zooms into it. |
| `figure1.svg` | Figure 1 at full detail, which the page used before the copies above. The page no longer loads it; it stays so that existing links to it keep working. |
| `fonts/` | Inter, upright and italic, and DM Mono in its regular weight, with their licenses. The page preloads the upright Inter; the italic loads once the page is up. |
| `social.png`, `favicon.svg`, `favicon-32.png`, `apple-touch-icon.png` | The link-preview card and the icons. [tools/social_card.html](../tools/social_card.html) draws the card and says how to remake it. |
| `robots.txt`, `sitemap.xml` | For search engines. |

Every number on the page was traced to the camera-ready paper when the site was built. If you edit a
number, check it against the paper.

The page's look comes from one small design system: its tokens sit at the top of the styles in
`index.html`, and [The website's design system](design-system.md) explains them and the components
built from them. Build new parts of the page from those.

## Rebuild d3

`website/d3.min.js` carries only the d3 modules the charts use, at the versions d3 7.8.5 shipped with.
To rebuild it, run `tools/d3/build.sh` with Node.js and npm installed. The script runs
`npm ci --ignore-scripts`, which installs the versions pinned in `package.json` and
`package-lock.json` without running their install scripts, and then `node build.mjs`. That bundles
`entry.mjs` with esbuild 0.24.2, writes `website/d3.min.js` and `website/d3-LICENSE.txt`, and fails if
`app.js` uses a d3 function the bundle lacks. To use a function from another d3 module, export that
module from `entry.mjs`, add it to `package.json`, and run the script again. Commit both files it
writes.

## Search engines

`index.html`, `404.html` and `sitemap.xml` name the site's address, `https://amilworks.github.io/Pack3D/`,
in absolute URLs: in `index.html` the canonical link, `og:url`, the preview-image URLs, the structured
data and Google Scholar's abstract URL, and in `404.html` its icons, its font and its links back to the
site. If the site moves, for example to a custom domain, update those URLs too.

Crawlers read `robots.txt` only at the root of a domain, so on a project address like this one, submit
`sitemap.xml` in [Google Search Console](https://search.google.com/search-console) instead. Links
from the arXiv listing, the lab's site and this repository also help the page get found.
