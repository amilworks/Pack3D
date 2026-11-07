# The project website

The project website, <https://amilworks.github.io/Pack3D/>, tells the paper's story in one page, with
interactive figures. It is a static site: the files in [website/](../website/) are served as they
are, with no build step. The [Deploy website](../.github/workflows/pages.yml) workflow publishes them
with GitHub Pages.

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
| `app.js` | The page's script, with the plotted data built in. |
| `figure1.svg` | Figure 1 of the paper. |
| `d3.min.js` | d3 7.8.5, for the charts. Its license is in `d3-LICENSE.txt`. |
| `fonts/` | Inter and DM Mono, with their licenses. |
| `social.png`, `favicon.svg`, `favicon-32.png`, `apple-touch-icon.png` | The link-preview card and the icons. [tools/social_card.html](../tools/social_card.html) draws the card and says how to remake it. |
| `robots.txt`, `sitemap.xml` | For search engines. |

Every number on the page was traced to the camera-ready paper when the site was built. If you edit a
number, check it against the paper.

The page's look comes from one small design system: its tokens sit at the top of the styles in
`index.html`, and [The website's design system](design-system.md) explains them and the components
built from them. Build new parts of the page from those.

## Search engines

`index.html` and `sitemap.xml` name the site's address, `https://amilworks.github.io/Pack3D/`, in
absolute URLs: the canonical link, `og:url`, the preview-image URLs and Google Scholar's abstract URL.
If the site moves, for example to a custom domain, update those URLs too.

Crawlers read `robots.txt` only at the root of a domain, so on a project address like this one, submit
`sitemap.xml` in [Google Search Console](https://search.google.com/search-console) instead. Links
from the arXiv listing, the lab's site and this repository also help the page get found.
