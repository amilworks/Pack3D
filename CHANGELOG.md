# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Every change below is to the project website.

### Added

- A Pause motion button on the opening, the title figure and the repack window. One press pauses every
  figure that moves on its own, the end included, and the site remembers the choice on the device.
  Turning the opening's sculpture or the repack cells by hand also pauses motion, so the view you chose
  stays put. With motion paused, the closing line and the word PACK3D appear whole.
- Keyboard control of the figures. The arrow keys turn the opening's sculpture and the repack cells and
  move the rotary grid's *q* and *k*. Tab to the title, and the usual slider keys read its letters one
  at a time with their coordinate and memory position. A rotary token can also be moved by clicking or
  tapping it and then a cell, pointing at or tapping a slot in the memory row under the title reads the
  letter stored in it, and in the two-indices lab Home and End move the query to the ends of its row.
- "Show the numbers" tables under the second-domain, intervention, probe, per-seed and per-structure
  charts, as under the result chart, each with a caption and row headers for screen readers.
- A "Skip to the paper" link, shown on the first press of Tab.
- A page for a missing address, in the site's design, with a way back to the paper that stays on the
  first screen of a phone held sideways, even with Safari's toolbars showing, and wraps with very large
  text.

### Changed

- The site tells its story in three full-screen figures. It opens on one glowing path through 512
  tokens that morphs from one storage order to the next. The paper's first screen threads the letters
  of the title to their places in memory. In the result chapter, the same repack runs on a cell under
  both models, with one spark for each changed prediction at the paper's rates; it replaces the two flat
  squares that showed those counts.
- Buttons, option trays, figure sheets, stats, cards and callouts follow one design system, written up
  in [docs/design-system.md](docs/design-system.md). A tray of options is one control: one Tab stop
  whose arrow keys, Home and End move the choice, announced as a radio group. The chosen option is
  ringed as well as raised, a mouse's press darkens a control as a finger's does, and a button whose
  label changes keeps its width.
- The top bar is a breadcrumb, the wordmark and the chapter being read, named in full where there is
  room, which opens the contents on hover, a click, a tap or the keyboard; the contents list "Take it
  home" with the other chapters. The bar takes the stage's dark colors over the opening, the repack
  window and the end, and on phones the browser's own bar matches it. On a phone held sideways the bar
  is shorter, as iOS's own is.
- The link-preview card shows the closing word, PACK3D built from cubes on the dark stage, under the
  paper's title. [tools/social_card.html](tools/social_card.html) draws it.
- The type follows one scale of sizes and weights: small labels share one size, captions, notes and
  card text one set of sizes, and bold words the weight of the rest of the emphasis. Titles of sheets,
  cards, stats, callouts and the Figure 1 steps share one line height and letter spacing, so a title
  that wraps reads as one, and the small monospaced labels (counts, chapter numbers, the rotary grid's
  positions) share one letter spacing. DM Mono is set in its regular weight only, so the page loads one
  font file fewer.
- Variables such as *q*, *k* and *z*, and the statistics symbols *p* and *t*, are set in italic, as in
  the paper, in the text, the figure labels, the buttons, the tour, the dial captions and the tips. They
  stay upright in the monospaced readouts.
- Lines break with more care. Headlines and short labels balance their lines, paragraphs avoid
  one-word last lines, and dimensions such as 3 × 3 × 3, the name U-Net, *p* values, coordinates such
  as *c* = (*z*, *y*, *x*) and changes such as 0.8247 → 0.8248 no longer break across two lines.
  Captions and notes under wide figures keep a comfortable line length.
- Every figure's title is a heading, and the outline runs from the title to chapters, sections and
  figures without skipping a level, the colophon's headings included.
- Spacing follows one scale: rows of buttons and trays are spaced alike, the chapter, repack-window and
  closing headings sit the same distance under their labels, and captions, tables and cards are spaced
  the same way throughout. The side margin grows with the screen, from 16px on phones to 32px on wide
  screens. With the sheets' new heads and number tables, and on a phone the footer's taller link rows,
  the page is a little longer: 21,610px against 21,253px on a desktop, and 28,568px against 28,180px on
  an iPhone.
- The figures answer a click at once. A new storage order, the result chart's replay and the repack
  window's button are a quarter to two fifths of the way there a tenth of a second after the click, and
  the repack window's counts start as soon as its cells settle. Every hover, press and state change,
  links included, shares one quick ease-out, and jumps from the contents and the footer are instant.
- The keyboard's focus ring is a deeper teal on the light page and the stage's own mint on the stage,
  and the opening's sculpture shows the same ring as every other control. In a tray it hugs the focused
  option, and in the contents the focused row shows a clear ring.
- The controls use the same words for the same thing: the lab's orders read Raster, Morton, Blocks and
  Repacked, like every other tray, and buttons name what they do ("Repack the rows", "Replay the
  repack", "Swap tokens 1 and 2").
- The opening fits the first screen on short laptops (down to 1366 × 768 with the browser's bars), on
  tablets, tall portrait ones included, and on most phones, Safari's toolbars included, where the title
  keeps to three lines and the sculpture takes the room the first screen leaves; on the smallest, such
  as an iPhone SE with Safari's toolbars showing, the caption runs just below the first screen. On a
  phone held sideways it is a compact version of the laptop's, the title, caption and orders on the left
  and the whole sculpture on the right, even with Safari's toolbars showing. On wide high-resolution
  screens the sculpture is drawn sharp and keeps to the page's grid.
- The title figure takes the chapters' column below 981px, with its readouts and orders right under
  the letters, and its memory row's letters are never smaller than 12px. On a phone held sideways the
  letters, memory row, readouts, orders and note fit one screen, unless Safari's toolbars are showing,
  and on short laptop windows the buttons beside the figure stay in view.
- The two-indices lab shows eight slices to a row once it is 880px wide, for a mouse. On phones each
  option keeps to one line, the four orders share a row from 361px wide, and the readouts form an even
  grid. On a phone held sideways its slices fit the screen under the top bar, unless Safari's toolbars
  are showing. The local window is shown by its own tokens, outlined, with the rest faded.
- The rotary dials keep up with a dragged token, and their hands turn around the dial with the shaded
  arc between them. The query's hand, a deeper orange, ends in a dot, and the key's in a ring. The two
  logit meters are the same length, and with large text the dials stack instead of overlapping.
- Figure 1 has a title and a step count, and each part is named after the figure's own panel ("Panel
  5.1"). Previous and Next sit right under the figure and stay put between steps, and the step's text is
  a size smaller than its title. The minimap's parts have clearer outlines and the page's own tip, and
  on phones the minimap appears once a part is open.
- The chart marks are deeper in the light theme, 3:1 or more against the sheet, and the legend dots
  match them. The U-Net is drawn as a ring, the cost chart draws Window dashed and PACK3D heaviest, and
  probe bars are drawn as meters with a tick at chance. Hovering a mark outlines it, as a tap does, and
  every mean point of the result chart shows the mean, never a single seed. A tip stays open while the
  mouse moves onto it, and closes with Escape or as the page scrolls. On a phone held sideways the
  result and latency charts, the rotary grid and the pooling figure fit the screen under the top bar
  with the control that changes each, even with Safari's toolbars showing, and the Predictions changed
  chart fits on its own while they are hidden.
- The paired sheets in chapters 7 and 8 end level with matching heads, and the result, named-switch,
  cost and contract sheets have proper titles and meta lines.
- The repack window fits under the top bar on laptops and desktops, so its button is always on screen,
  and it keeps one height through its whole run. It fits one screen on an upright phone, a short one or
  one with Safari's toolbars included, and on a phone held sideways its words and counts sit beside the
  cells, clear of the notch, with its title on one line even with Safari's toolbars showing.
- The closing word rebuilds in about a second when you pick another storage order; the first build and
  "Build it again" still take about three. It colors memory order with the opening's lavender ramp, it
  shares one screen with its memory and its order buttons, and a click or a tap picks a cube, from which
  the keyboard walks on as on any slider (Page Up and Page Down step ten).
- The footer's lists, Read and Chapters, look and behave alike: plain links that turn mint on hover,
  with taller rows for a finger. The footer keeps two columns up to 1199px.
- The site loads less and does less while you scroll. d3 is a partial build of half the size, made by a
  new script in [tools/d3](tools/d3/), and the italic font loads after the first screen. Figure 1's
  large drawing loads only once you stop on it, the repack window's cells are made in the background as
  you come near, and a figure stops drawing once it is paused, settled or off the screen. The styles the
  browser reads before the first screen are inline, 86 KB (21 KB compressed), with their comments kept
  short. Measured on one machine, emulating an iPhone on slow 4G, the first screen painted in a median
  of 496 ms, against 488 ms before the redesign.

### Fixed

- On iPhone, the repack window in the result chapter draws its two cells instead of saying "This
  figure needs WebGL". Mobile Safari refused WebGL to the figure's canvas once the page had been open a
  few seconds. The figure now draws on a canvas it makes when it is built, asks again when it is
  refused, draws its cells with Canvas 2D where WebGL cannot run, and recovers by itself when the
  browser takes its WebGL context away.
- On iPhone, the top bar no longer stays dark over the light page, or light over the dark stage, after
  a jump or a scroll made by a script, and its words no longer fade as it switches between the two.
- Figure labels no longer set variables in capitals, where the variable *z* read as *Z*.
- The site works with touch on phones and tablets. The rotary grid's tokens can be dragged with a
  finger and are easy to grab however small the grid is drawn, and with a token picked, a tap right
  beside a token moves the picked one there. Every chart opens its tip on a tap (the nearest mark within
  reach, outlined while its tip is up), a tap on the token field names the token, the closing word can
  be tapped or scrubbed, and hover styles no longer stick after a tap. Buttons, tray options, the
  wordmark and "Show the numbers" answer taps just above and below them too, every row of a tray that
  wraps keeps a full target, and so does a Pause motion button under a tray or a button, and the
  contents' rows and the footer's links are finger-sized.
- Nothing moves under the reader as the page loads: the opening, the lab and every chart hold their
  final size before the scripts run, the opening's caption no longer shifts when the web font arrives,
  and the charts no longer redraw when a phone's toolbar shows or hides, but do redraw at the right
  width after Safari's Page Zoom.
- Scrolling, tapping or pinching over the opening or the repack cells no longer stops the orders from
  cycling or turns the cells, and pinch-zoom works over them and the closing word. A right-click on the
  opening no longer starts a drag that can get stuck, and a chart's tip no longer sticks when the mouse
  crosses the chart quickly.
- Picking a storage order while the title's letters or the lab's memory ribbon are still moving carries
  on from where they are instead of jumping. Clicking a title letter with a mouse keeps it picked, and
  the note under the title's tray keeps room for two lines.
- Screen readers hear what the reader changes, and only that. The title's packed reading is spoken
  once, spelled out, when you pick an order; the lab's moves, the repack window's states with both
  counts, the rotary grid's logits, the pooling readouts, the contract's verdict and the cost chart's
  token count are announced, but not the repack window's first run by itself or the tour's text as the
  page loads. The 3D views are announced as such, each "Show the numbers" names its chart, equations are
  read in words and can be copied and found as text, the outside links say they open in a new tab, and
  Tab meets the opening's and the title figure's parts in the order they appear. Each tray is named for
  its figure and each wide equation for its place, so no two controls or regions share a name.
- A control that takes keyboard focus is never hidden under the top bar, and tabbing through the bar
  no longer scrolls the page. After a choice in the contents, focus moves to the chapter's heading, and
  the closed menu's rows leave the Tab order at once. The contents no longer nudge the page as you move
  through them, and open at their top with your chapter in view. A figure that cycles on its own stops
  once you move into it with the keyboard, so an option or a button never changes under your focus, and
  closing a part of Figure 1 from its map on a phone leaves focus on Next.
- A jump lands a chapter right under the bar, with no half-cut line from the one before. A link to a
  place in the page, such as #test, leaves a reader who has started scrolling where they are, and "Back
  to the top" goes all the way to the top.
- Chapter names are no longer cut off in the breadcrumb: on small phones and with large text the
  wordmark shows only its cube, and two long names have short forms for where they would not fit. The
  names are measured to a fraction of a pixel, so Safari no longer cuts one by half a pixel, and they
  refit after Safari's Page Zoom and with large text; at very large sizes the Paper link moves into the
  contents. On wide screens the bar's content lines up with the page's column.
- With large text, a reader's own text spacing or on very narrow screens, button labels wrap, formulas,
  file names and long words fit their column, the numbers tables wrap their headers, the title figure's
  big title stays in its sheet, and the page never scrolls sideways. Long formulas, wide tables, the
  pseudocode and the BibTeX fade at the edge where more of them lies, and can be scrolled from the
  keyboard.
- Double- or triple-clicking a button, an option or a choice card no longer selects its label, and a
  long press on a figure no longer selects the words beside it or offers to save Figure 1.
- In contrast themes, buttons and options have visible edges, the chosen option is highlighted, the
  "Show the numbers" arrow shows whether it is open, the Figure 1 map keeps its outlines and focus ring,
  series dots and meters stay visible, and the dash before each chapter label is drawn.
- Printed from either theme, the page comes out in dark ink on white, with no black blocks, even from
  the end with background graphics on. The charts and the lab print at full size, and Figure 1 prints
  whole at any step of the tour. Buttons, moving figures and the words that point at them ("drag",
  "click", "Step 1 of 11", "Back to the top") are left out, the dash before each chapter label prints,
  the repack window prints as its one-sentence summary on the text column, and the footer's paper and
  code links print their addresses. Pages no longer strand a chapter label at their foot, split the two
  readings or the footer's lists, or leave a nearly blank page before the rotary dials, and code and
  BibTeX copied from a PDF printed on a phone are no longer doubled.
- Without JavaScript, the page drops the controls that would do nothing, the empty figure frames, the
  parts the script draws (the lab, the pooling figure's readouts) and the contract's checkboxes, and no
  sentence points at a figure or a control that is not there. The opening takes only the room its words
  need, Figure 1's frame fits the picture, the repack window states its result in a sentence, and the
  note above the opening is accurate and sits on the stage.
- If the browser refuses a canvas, the lab still works, the end shows its closing line and credits
  instead of an empty figure, and the words around the repack window no longer describe cells that are
  not drawn.
- On phones, chart text stays at 12 to 13px down to 320px wide, the rotary grid's memory positions are
  readable, and the intervention chart's zero line no longer cuts through its labels. The seeds in the
  second-domain chart no longer overlap into crescents, the chance mark in the probes chart no longer
  blocks a bar's tip, and the result chart stops at 420px tall on tablets.
- The contract callout lists missing items as "a, b, c and d", its dot stays on the first line of a
  wrapped title, and its choice cards darken when pressed.
- The opening and the repack window no longer blink while the browser window is resized, and a
  double-click on Figure 1 no longer zooms in and straight back out.
- Text selected on the dark stage is light on deep teal, and Copy BibTeX answers every press with a
  note that clears after a few seconds.
- With reduced motion, "Replay the repack" is hidden, as "Build it again" is.

## [0.1.0] - 2026-11-06

First public release, accompanying the NeurIPS 2026 paper
[Geometry Matters in Packed 3D Attention](https://arxiv.org/abs/2610.38694).

### Added

- The `pack3d` package: explicit 3D geometry (`build_layout`, `TokenLayout.repack`), axial RoPE,
  learned two-stage compression, a differentiable reference implementation, and the
  `PACK3DAttention` layer.
- An optional streamed Triton backend with an explicit backward pass (`backend="triton"`).
- CPU examples for a forward and backward pass, packing equivariance, and the repack test.
- The paper's 45 recipes for Allen-15, MSD Heart and MSD Spleen, with offline training and
  checkpoint evaluation through the paper backend.
- Frozen per-seed and camera-ready results, with checksums and a dataset-free aggregator.
- Safety checks in the reproduction scripts: tensor-only checkpoint loading, restricted archive
  extraction, refusal to overwrite outputs, and strict JSON for evaluation metrics.
- The project website under `website/`, deployed with GitHub Pages.
- The MIT license, citation metadata, contribution guide, issue and pull request templates,
  continuous integration, and Dependabot updates for the pinned GitHub Actions.

### Notes

- The new API does not use the state-dict names of the paper's historical layer. To load the
  paper's checkpoints, use the paper backend in `reproduce/`.
- Scientific corrections made after review are listed in
  [docs/corrections.md](docs/corrections.md).

[0.1.0]: https://github.com/amilworks/Pack3D/releases/tag/v0.1.0
