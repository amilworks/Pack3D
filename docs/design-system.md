# The website's design system

The website in [website/](../website/) is built from one small design system. Its tokens sit at the top
of the `<style>` block in `website/index.html`, and every component below is written in those tokens.
The parts every section shares (the spacing classes, the note, the dashed eyebrow, the large tray, and
the one rule each that sets the title role and the data labels) sit in one block, headed "shared
parts", after every component rule, so they win over a component's own rules. This page says what each
token and component is for, and why, so the next figure, section or control can be built from the same
parts.

When something needs a value the system does not have, add a token, to the stylesheet and to this
page, instead of writing a one-off value into a rule. The literal values the system keeps on purpose are
named where they occur: the stage's color on the root element ([The dark stage](#the-dark-stage)), the
spaces [Spacing](#spacing) lists, and the copies of the tokens that `404.html` carries. The reasons live
on this page rather than in the code: the stylesheet is inline and blocks the first paint, so its
comments are section headers and short notes only (see [Performance](#performance)).

## Principles

1. **The page is a sheet of paper lifted off a dark stage.** The reading column and its figures sit on
   the sheet. The stage shows at the opening, through one window in the result chapter, and at the
   end, and it is dark in both themes.
2. **Fills, not outlines.** A group is a wash of ink, a figure sits on a sheet with a soft shadow, a
   chosen option is lifted out of its tray. Nothing gets a border to look like a box. Lines are kept
   for information; the list is under [Lines](#lines).
3. **Color carries meaning.** Teal is PACK3D, the coordinate, the primary action and where you are.
   Coral is packed RoPE and what a sequence-indexed model reads. Lavender is memory: the threads that
   tie the title's letters to memory, and a lavender ramp for memory order in the opening and at the
   end. It is also the third model, separable PE, and the stage's lamp. Orange and green are the query
   and the key. Warm grey is a baseline. Everything else is ink.
4. **A choice is lifted and ringed; the current place is checked.** The chosen option in a tray is
   raised out of it and ringed in ink, and the current chapter in the contents carries a check.
   Nothing is shown as chosen by turning it black or white.
5. **Controls speak in one voice.** Every control is set in Inter 500 at one of two sizes, with one
   tracking; the contents' rows on a phone are the one exception, at 1rem for a finger. Choosing an
   option never changes its weight, so no word shifts when it is pressed. A count that runs up holds
   the width of its final value, and a button whose label changes (the motion switch, Repack the rows
   and the repack window's button) holds the width of its longer label, so nothing beside it moves.
6. **Corners nest.** An inner corner is the outer corner less the padding between them: a tray of 13px
   with 3px of padding holds options of 10px.
7. **Motion answers the reader.** A state change eases out in 0.15 to 0.4 seconds, and a figure's move
   that answers a press eases out too, so it is under way at once. Motion nobody asked for eases in and
   out, one switch, Pause motion, stops it everywhere, the end included, and a figure that cycles by
   itself stops once focus enters it, so no option or button changes under focus. Hover changes only a
   fill, the ink or a mark's outline, never a size or a position; apart from a figure's tips, the one
   thing a hover opens is the contents, and only after the mouse rests. With reduced motion, every
   change is instant.
8. **Precision in type.** Numbers use tabular figures. Labels for data are set in DM Mono, at 400 only.
   Capitals are kept for eyebrows and never set text that holds a variable: an uppercase label would
   turn the variable *z* into *Z*. Variables are italic wherever Inter sets them: in prose, captions,
   controls, figure labels, dial captions and tips, as in the paper. They stay upright in DM Mono
   labels and where text cannot carry markup (an `aria-label`, a canvas). The statistics symbols *p*
   and *t* are italic too, in prose, captions, notes and tips, like the paper (exact *p* = 0.031, a
   paired *t*-test); they stay upright only inside DM Mono labels and in canvas or SVG text.
9. **What belongs together stays on one line.** A dimension keeps its parts together
   (`3&nbsp;×&nbsp;3&nbsp;×&nbsp;3`), the name U-Net and an inline statistic such as *p* = 0.031 sit in
   `.nw`, and a change such as 0.8233 → 0.7445 keeps its arrow between no-break spaces. A test's name
   and its value are two units (`paired <i>t</i>-test`, then `<i>p</i> = 0.0035`), so enlarged text can
   break a line between them but never inside either. What app.js writes keeps its expressions whole
   the same way, with no-break spaces around ×, = and an arrow and after a coordinate's commas: in
   captions, notes, tips, dial captions, the tour's text, the lab's coordinates and memory positions,
   and the closing word's readout.

## Tokens

### Color

| Token | Light | Dark | Use |
| :--- | :--- | :--- | :--- |
| `--bg` | `#F3F5F4` | `#0B0F0E` | The page |
| `--surface` | `#FFFFFF` | `#121816` | Sheets and cards |
| `--surface-2` | `#F8FAF9` | `#161D1B` | A fill inside a sheet: the faces of the rotary dials, the cells of the pooling figure |
| `--ink`, `--ink-2`, `--ink-3` | `#0F1513`, `#444D49`, `#5F6964` | `#E8EEEB`, `#B9C2BE`, `#93A09A` | Text, secondary text, labels and captions |
| `--rule` | `#D5D8D2` | `#2D3633` | The hairline under the bar, a badge's outline, the page's rim, the colophon's dividers, the rule above a mean row; reference lines and dial faces in the figures |
| `--grid` | `#E4EBE8` | `#202927` | Chart grids and table rules |
| `--teal` | `#00B796` | `#19AC8B` | PACK3D's fills: the primary action's wash, a PACK3D callout and its dot, reading progress, link underlines, the checkbox |
| `--mint-ink` | `#00735D` | `#5FE0C3` | Teal text: eyebrows, primary buttons, the current-chapter check, a link on hover; the focus ring |
| `--coral` | `#FF7276` | `#C9474F` | Packed RoPE's fills: its callout and dot, the lab's sequence-neighbor dots, the repack window's state dot |
| `--coral-ink` | `#B5363F` | `#FF8F94` | Coral text: what a sequence-indexed model reads, its count of changed predictions |
| `--orange`, `--green` | `#FFAA4D`, `#8FE07A` | `#FFB15E`, `#7BD866` | The query and the key: their tokens in the lab and in the rotary grid |
| `--lav` | `#997ADB` | `#9479D8` | Separable PE; the dot that labels the title figure's memory row, and the threads that run to it; the edges of the pooling figure's cells |
| `--warm` | `#9E978E` | `#A39C93` | A baseline's faint marks: the members of the summary pooled at the center |
| `--tint-teal`, `--tint-coral` | `#8EDDCB`, `#FFB4B6` | `#1F5F51`, `#6B2F33` | The faint per-seed lines behind a series, the members of a summary; teal is also text selection |
| `--track` | `#EEF1EF` | `#1C2422` | The empty part of a meter or a bar, the cells of the rotary grid |

A mark that carries a value (a chart's dot, line or bar, a dial's hand, a meter's fill) and the legend
dot that keys it take the series' mark color, deep enough for 3:1 against the sheet; in light they
measure 3.7:1 or more on white. In the dark theme `--teal-mark`, `--coral-mark`, `--warm-mark` and
`--orange-mark` are the series colors themselves, and on the stage the teal and coral marks are the
stage's own. The plain series colors stay for fills, tints and callouts, and for the lab's cells,
which are outlined in ink.

| Token | Light | Dark | Use |
| :--- | :--- | :--- | :--- |
| `--teal-mark`, `--coral-mark` | `#00957A`, `#E04F55` | `#19AC8B`, `#C9474F` | PACK3D and packed RoPE as marks, and their dots (`.dot.teal`, `.dot.coral`) |
| `--warm-mark` | `#857E75` | `#A39C93` | A baseline as a mark: the U-Net, dense SDPA, window attention, the ablations |
| `--orange-mark`, `--green-ink` | `#B35F00`, `#2C8F1F` | `#FFB15E`, `#8FE07A` | The query's hand and the key's hand on a dial |

The stage keeps its colors in both themes, and so does memory order in the moments:

| Token | Value | Use |
| :--- | :--- | :--- |
| `--stage-bg` | `#060A09` | The stage |
| `--stage-ink`, `--stage-ink-2`, `--stage-ink-3` | `#EEF3F1`, `#B4BEBA`, `#8C9A95` | Text on the stage |
| `--stage-teal`, `--stage-mint` | `#19AC8B`, `#5FE0C3` | Teal on the stage, and its text, ring and light: the opening's running head, PACK3D's sparks, the closing word's trail |
| `--lamp` | `#8062DC` | The lavender lamp behind a figure on the stage |
| `--stage-halo` | `rgba(6, 10, 9, 0.9)` | The stage's color behind text laid over a figure |
| `--mem-0` to `--mem-4` | `#4B3AB0`, `#7356D6`, `#9A7DE6`, `#C9B6F4`, `#F7F3FE` | Memory order, first position to last, mixed in OKLab between the stops: the opening's path, the closing word's cubes and ribbon |

app.js reads a token with `tok(name)`, from the root element, so a figure takes its colors from the
stylesheet. A figure on the stage reads the `--stage-*` tokens by name, because the stage's own values
of the page's tokens are set on its sections, not on the root; the repack window reads its coral from
its own section. The colors a figure keeps of its own are the ones no token names: the lab's teal ramp
for a token's place in the sample (one for each theme), the opening's near-white head (`#C9FFF1`), the
white that marks a picked cube at the end, the shades the repack cell is built from in its worker, and
the four class colors of the memory strips.

### Fills

Fills are the ink, or teal or coral, mixed at low strength with nothing. Because they are partly
transparent, one fill works on any surface and in either theme.

| Token | Strength | Use |
| :--- | :--- | :--- |
| `--wash-1` | ink 4.5% | A group at rest: stats, readouts, code, choice cards, the title figure's reading box; hover on an option in a tray |
| `--wash-2` | ink 7% | Trays, quiet buttons at rest, hover on a row or a plain button, an option pressed, the ring of a frame |
| `--wash-3` | ink 10% | Hover on a quiet button, the chapter while the contents are open, the focused row in the contents |
| `--wash-4` | ink 14% | Pressed |
| `--teal-1`, `--teal-2`, `--teal-3` | teal 15%, 22%, 28% | A primary button at rest, on hover and pressed; a PACK3D callout; a part of the Figure 1 map on hover, pressed (`--teal-2`) and chosen |
| `--coral-1` | coral 14% | A packed RoPE callout |

### Elevation

| Token | What it raises | Light | Dark |
| :--- | :--- | :--- | :--- |
| `--sheet-shadow` | Sheets and cards | A soft shadow | A faint edge of light and a deep shadow |
| `--lift`, `--lift-shadow` | The chosen option in a tray | White with a hairline shadow | Ink at 13%, no shadow |
| `--pop`, `--pop-rule`, `--pop-shadow` | Menus | White, a 9% edge, a wide shadow | A raised surface, a 9% edge, a deep shadow |
| `--tip-shadow` | Tips | A short dark shadow | The same |
| `--page-rim-top`, `--page-rim-bottom` | The page where it meets the stage: its top edge over the opening, its bottom edge over the end | A 1px `--rule` rim and a long dark shadow | The same; here the rim is the page's edge, since page and stage differ by only 1.03:1 |

### Radius

| Token | Size | Use |
| :--- | :--- | :--- |
| `--r-xs` | 6px | Marks: meters, the memory strips and the memory ribbon, the parts of the Figure 1 map, and the cells and memory slots drawn in the figures (a slot narrower than 30px takes 0.2 of its width) |
| `--r-sm` | 10px | Controls and rows: options in a tray, menu rows, readouts, frames, tips, disclosures, the wordmark; the focus ring of a large block that takes the keyboard |
| `--r-md` | 13px | Groups: trays (10 + 3), stats, code, callouts, choice cards, the title figure's reading box, the closing word's canvas |
| `--r-lg` | 16px | Small sheets: the contents menu (10 + 6), cards that sit on the page |
| `--r-xl` | 20px | Sheets: the benches that hold the figures |
| `--sheet-r` | 22 to 48px | The page itself, where it meets the stage, and the stage window |
| (pill) | 999px | Buttons and badges |
| (chart bar) | 3px | The bars in the charts: the named switch and the interventions |

The lab's token grid is the one exception to rounded cells. Its 512 slice cells and 512 memory cells
are square, because the lab draws all 1,024 again each time the pointer moves onto another token, and
the memory's 512 on every frame of its 1.1-second morph; rounding that many cells costs frame time.

### Type

Inter sets the words (`--font-display`, `--font-body`), and DM Mono sets data labels, data lines and
code (`--font-mono`). The sizes are tokens:

| Token | Size | Use |
| :--- | :--- | :--- |
| `--fs-label` | 0.75rem | Eyebrows, DM Mono data labels, index numbers, badges |
| `--fs-meta` | 0.8rem | The quieter words in a control, figure labels and meta lines, dial captions, hint and readout lines, tips |
| `--fs-code` | 0.82rem | Code |
| `--fs-caption` | 0.84rem | The caption under a sheet, tables, a stat's change, the copy note, the venue line, the colophon's last line, a tip under a finger |
| `--fs-control-sm` | 0.84rem | Options in a tray, small buttons, disclosures |
| `--fs-small` | 0.9rem | A note beside a figure, card text, choice cards, a meter's label, the opening's byline and caption, the Figure 1 tour's step text, the repack window's state, and its model names at 640px and below, the closing word's caption, the colophon |
| `--fs-control` | 0.9rem | Buttons, the breadcrumb, menu rows, options in a large tray |
| `--fs-title` | 1.02rem | Sheet, card, stat, callout and step titles, a readout's or a meter's value, the wordmark, the colophon's paper title |
| `--fs-body` | 1.05rem | The reading column, the abstract; the repack window's title on a phone held sideways under Safari's bars, so it keeps to one line inside their insets |

Display, lede and heading sizes stay as `clamp()` and `min()` values in their own rules. A few sizes
belong to one element each: a display formula (1.12rem), the breadcrumb's slash (1.15rem), the
two-readings lede on a short laptop (1.18rem, and 1.08rem where that laptop is 981 to 1100px wide),
the stage window's title on a short upright phone (1.35rem), the repack window's counts on a phone held
sideways (1.6rem), DM Mono inside a line of Inter (`.mono`, 0.9em), and a subscript in a readout label
(0.9em, never under 12px).

| Role | Set in | Where |
| :--- | :--- | :--- |
| Display | Inter 320 to 380, a size of its own, line height 0.95 to 1.2, tight tracking (-0.022 to -0.034em) | The title (320, line height 1; its size follows a short screen's height, full from about 950px tall, and on a phone it keeps to three lines down to 320px wide), the two-readings title (320, line height 0.95, tracked open at 0.02em), the stage window's title and the closing line (340), the stage window's counts (360), stat values and pull quotes (380) |
| Heading | Inter 480, 1.9 to 3.1rem, line height 1.08, tracking -0.024em | Chapter headings, `h2` |
| Section heading | Inter 600, 1.32rem, line height 1.25, tracking -0.012em | Sections inside a chapter, `h3` |
| Title | Inter 600, `--fs-title`, line height 1.3, tracking -0.012em, set by one rule in the shared parts | Sheet titles, card titles, stat names, callout titles, the tour's step titles, the stage window's model names (at `--fs-small` on a phone; their meta line keeps the 1.3), the colophon's paper title. At 1.3 a title that wraps still reads as one; at the body's 1.62 its lines come apart |
| Body | Inter 400, `--fs-body`, line height 1.62, tracking -0.004em | The reading column |
| Lede | Inter 400, 1.18 to 1.42rem, line height 1.5 | The first paragraph of a chapter; the opening's is 1.02 to 1.14rem at line height 1.52, in ink-2 |
| Small | Inter 400, `--fs-small`, line height 1.5 | A note beside a figure (`.note`, in ink-2), card text, the Figure 1 tour's step text, `.small`; choice cards at line height 1.35, and the lists in the Limits cards at the body's 1.62 |
| Control | Inter 500, `--fs-control`, line height 1.2 (menu rows 1.3), `--ls-control` (-0.006em) | Buttons, the breadcrumb, menu rows, options in a large tray |
| Small control | Inter 500, `--fs-control-sm`, line height 1.2, `--ls-control` | Options in a tray, small buttons, disclosures |
| Phone menu row | Inter 500, 1rem, line height 1.3 | The contents' rows at 560px and below: the one control set larger, for a finger |
| Meta | Inter 500, `--fs-meta`, ink-3 | Figure labels and meta lines, the quieter words in a control |
| Caption | Inter 400, `--fs-caption`, line height 1.5, ink-3 | The caption under a sheet |
| Data label | DM Mono 400, `--fs-label`, tracking 0.01em (one rule in the shared parts), ink-3 | Readout labels, chapter numbers in the contents and the colophon, the stage window's count labels, the end's memory label and its count, and the rotary grid's memory positions (`--fs-label` through `--u`); on a canvas, 12px |
| Data line | DM Mono 400, `--fs-meta` | The hint under the title figure, the closing word's readout, the colophon's address and arXiv id |
| Code | DM Mono 400, `--fs-code`, line height 1.7 | Code blocks; a keyword takes mint-ink |
| Chart text | Inter 13px; 500 for labels, 600 for emphasis; values in tabular figures | Axis values and labels inside the charts |
| Chart note | Inter 12px | Axis titles and notes inside a chart: tokens (log scale), chance, ← U-Net ahead, the structures' names, the pooling figure's legend |
| Eyebrow | Inter 600, `--fs-label`, capitals, tracking 0.12em | Chapter and section labels, in mint-ink; the colophon's headings, in ink-3 |
| Venue line | Inter 600, `--fs-caption`, tracking 0.03em, in its own case (`.eyebrow.keep-case`) | "NeurIPS 2026 · Sydney, Australia" above the title, in mint-ink |

Weights follow the role: display 320 to 380, headings 480, body 400, controls, meta and chart labels
500, and titles, section headings, eyebrows, bold words and chart emphasis 600. Bold (`b`, `strong`) is
600, so Inter is never set at 700. The breadcrumb's slash, at 300, is the one other weight. DM Mono is
set at 400 only, and the page loads only that face of it; a code keyword takes its emphasis from
mint-ink, not from weight. The title figure's two readings (GEOMETRY MATTERS and its packed form) are
DM Mono at `--fs-title`, tracked 0.08em so the letters read as slots, and its memory row draws each
letter in DM Mono at half a slot, never under 12px. In a figure, the rotary grid's *q* and *k* are
marks, not labels: Inter 600 italic, 15 units of the grid's 320-unit square, so about 21.6px at the
grid's full 460px and scaling with the cells. Headlines and short labels balance their lines
(`text-wrap: balance`), and paragraphs, captions and notes avoid one-word last lines
(`text-wrap: pretty`).

### Spacing

| Token | Size | Use |
| :--- | :--- | :--- |
| `--s-1` | 6px | A label to its figure, a table under its summary, the items of a list in a card, a dial to its caption |
| `--s-2` | 10px | The items in a row of controls, on both axes; the second key of a legend in a meta line |
| `--s-3` | 14px | Parts of one group: a side panel's stack, a figure to its controls, its caption or its disclosure, cards in a grid; the eyebrow to the heading at the head of a chapter, the stage window and the end, and the opening's venue line to its title |
| `--s-4` | 22px | A block after a paragraph |
| `--s-5` | 28px | A sheet after prose; a chapter's head to what follows it |
| `--s-6` | 46px | A subsection after a sheet |
| `--s-7` | 64px | A moment: a pull quote, a closing block |

The scale governs the gaps between parts: `gap`, and the margins that separate blocks. Every row of
controls is spaced `--s-2` on both axes (the opening's and the title figure's, the link buttons under
them, a chart's, the lab's, the rotary grid's, the repack window's foot, the tour's, Copy BibTeX's and
the end's). The three heads (a chapter's, the stage window's and the end's) space their eyebrow and
heading `--s-3`, and the opening spaces its venue line and title the same (`--s-2` on a short phone,
`--s-1` on a phone held sideways). A space that falls between two steps takes the nearer one; a tie
goes to the smaller step where a fit depends on it, and otherwise to the step whose role it is, in the
table above. There are no tokens for 4, 8 or 12px.

These stay literal on purpose: padding; nudges under 6px (a tray's 3px, the 2px between its options);
the gaps inside one control or label (an icon, a dot or a chevron to its words, a number to its row's
title, a count to its label, the eyebrow's dash); fluid `clamp()` and `min()` spaces; the row gaps that
keep two 44px bands apart under a finger (12px, and 14px in the lab; see [Components](#components)),
which are the bands' arithmetic, not spacing; the 10px inset of the dividers in the contents, which
lines up with the rows' padding; and two spaces far from any step, the 36px above the stage window and
the colophon's 36px between columns. The scale reaches the page through the shared classes, never
through inline styles; the only inline styles in the page are the vertical alignments MathJax wrote
into its equations.

| Class | Sets | Use |
| :--- | :--- | :--- |
| `.stack` | A grid with a gap of `--s-3`, min-width 0 | A side panel's parts, one under another |
| `.sub` | margin-top `--s-6` | A subsection, or a block that follows a sheet |
| `.moment` | margin-top `--s-7` | A pull quote, the block right after it, the closing pull quote |
| `.mt-1` to `.mt-5` | margin-top `--s-1` to `--s-5` | A pair of sheets right after a lede, and the note under the placement probe's meters (1), the parts of a figure and the line under a pull quote (3), cards or code after prose, and prose after a sheet or code (4), the note after the Limits cards (5); `.mt-2` completes the scale |
| `.mb-1` | margin-bottom `--s-1` | A figure label above its dials |
| `.m-0` | margin 0 | A row of controls inside a stack |

### Layout

| Token | Value | Use |
| :--- | :--- | :--- |
| `--col` | 42rem | The reading column. Its parts may shrink and break a long word, so a formula or a file name wider than the line never widens it. Captions and notes under a wide sheet keep the column too, or 66 of their own characters where that is narrower, and so do the numbers tables |
| `--wide` | 76rem | Wide sheets, the stage window's words and the bar's content |
| `--gutter` | `clamp(16px, 3.2vw - 8px, 32px)` | The side margin, or the safe-area inset where that is larger: 16px up to 750px wide, growing to 32px at 1250px |
| `--bar-h` | 52px; 44px on a phone held sideways | The top bar without its 1px hairline. On a phone held sideways, `(orientation: landscape) and (max-height: 500px)`, it takes iOS's compact height. Every height that must fit under the bar is written with `var(--bar-h)` and 1px for the hairline, except the opening's two tablet heights, which the compact bar never meets: their constants hold the 53px |

A jump lands a section (a chapter, the paper's first sheet, the end) flush under the bar, so no line
of the section before it shows cut by the bar's edge. Any other target, and a control that takes focus,
lands 12px under the bar: the page's scroll padding is the bar, its hairline, the safe area and 12px,
and a section's scroll margin of -12px takes the air back. The bar's own controls never scroll the page
when they take focus: their scroll margin cancels that padding. The contents' rows take a scroll margin
of -12px too, so moving through the menu scrolls only the menu, which leaves 6px of air around a row it
brings into view. A link to a place in the page (`#test`) is landed again once every figure above it
has drawn, and held there for up to 4 seconds while fonts and late layouts settle, because the figures
push it down as they draw; a reader who has moved (a wheel, a touch, a key or a press) is left where
they are, and a reload or a step back is left to the browser.

Most layouts change at a few widths and one shape. At 560px and below a screen is a phone: trays fill
the rows they wrap to, readouts form two columns, and the contents' rows grow and span the bar. A phone
held sideways is landscape and 500px tall or less: the bar takes 44px, and each moment and the Figure 1
tour fit one screen under it, as do the result chart, the rotary grid, the pooling figure and the
latency chart, each with the control that changes it. The Predictions changed chart and the lab's slices
fit under the bar on their own, though the lab's trays and its slices together take more than a screen.
With Safari's toolbars showing (874 by 292) the opening, the repack window, the tour and those four
pairs still fit, but the title figure runs 79px past the screen, and the Predictions changed chart, the
lab's slices, the probes and the per-seed U-Net chart are taller than it. Below 375px the wordmark keeps
its cube and drops its word, and below 360px the dashed eyebrow drops its dash. A component that stacks
at its own width says so in its rule.

The opening fits the first screen of a phone at 375 by 667, or at 390 by 664 (an iPhone with Safari's
toolbars showing); at 375 by 553 and 320 by 568 its sculpture is at its 180px floor and its caption runs
about 50px past the screen. Side by side (from 921px wide on a screen 4:5 or wider, and from 1101px),
its title and spaces shrink with the screen's height, so it fits above the sheet down to a 1366 by 768
laptop's 657px window; at exactly 4:5 both layout queries match, which does no harm. Stacked, the field
is a height, not an aspect ratio, since it is a size container, and at most 80svh, since the sculpture
scales with the field's shorter side and must not fill the screen. On a tablet or a tall portrait screen
the field takes the height the rest of the opening leaves, `min(94vw, max(300px, 100svh - 604px))`, with
638px in place of 604 from 921 to 1100px wide. On a phone the sculpture takes what the first screen
leaves: the screen less the bar, the space above the title, the title's three lines and `--rest`, which
holds the venue line, the spaces, the orders, Pause motion, the caption and 8px to spare. `--rest` is
234px (236 under a finger, whose Pause motion sits 12px under the orders, and 268 below 375px, where the
orders wrap 3 + 2), and 222, 224 and 256px on a short phone, 760px tall or less, where the opening and
the two readings tighten so the sculpture keeps more room and the orders reach the screen that shows the
letters they move. The opening's canvas reaches 14cqmin + 24px past its field, as far as the cube's
corners and glow go, and CSS places it, so it never moves after the first paint.

### Motion

| Token | Value | Use |
| :--- | :--- | :--- |
| `--ease` | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Every transition and animation in the stylesheet, the long ones too |
| `--t-1` | 0.15s | A fill on hover, a link's color, a tip, a finger's press |
| `--t-2` | 0.25s | A change of state: a callout, a chevron, the contents opening, the repack window's state dot |
| `--t-3` | 0.4s | A change of place: the chapter name in the breadcrumb, the bar's hairline between stage and page, a meter's fill, the copy note, the tour's spotlight appearing; and every d3 move that answers the reader |

Between stage and page the bar's fill and its words switch at once, together: the fill never eases,
because Safari leaves a fill that eases under the bar's frost unpainted after a scroll from script, and
the bar's controls ease only their transform, fill and shadow, never their color, so their words switch
with it. The bar's hairline eases over `--t-3`, and the fills of the skip link and the Paper pill over
`--t-1`, like any control's.

A motion that answers the reader eases out. In the stylesheet that is `--ease`. In app.js it is
`easeOut(t) = 1 - (1 - t)^5`, within 0.013 of `--ease` at 10, 20 and 30% of the time, so a figure is
between a quarter and two fifths of the way there 0.1 seconds after the click; a d3 move that answers
the reader lasts `--t-3` on `d3.easePolyOut.exponent(5)`. Motion nobody asked for, a figure playing by
itself, eases in and out. A mark the reader drags follows the pointer with no curve at all. The
contents' visibility switch, 0s after `--t-2`, is the one transition without a curve.

These motions run longer than `--t-3`:

| Motion | Takes | Plays |
| :--- | :--- | :--- |
| The opening's path, from one order to the next | 1.7s | Every 5.2s while the opening is in view and motion is on, and when the reader picks an order |
| The title figure's memory line | 1.3s | Every 4.2s while the figure is in view, motion is on and no letter is picked, and when the reader picks an order |
| The lab's memory ribbon | 1.1s | When the reader picks an order |
| The Figure 1 camera, the picture and its spotlight together | 1.1s, on `--ease` | At each step of the tour |
| The result chart's replay | 1.6s | Once by itself, the first time the chart's top passes 60% of the screen, and on Replay the repack |
| The repack in the repack window, then its sparks and its counts | By itself 1.7s, in and out; pressed 1.0s, and the restore 0.7s, eased out; then sparks 0.9s and counts 1.1s | Once by itself, 0.7s after 45% of the window is in view, and on its button |
| The closing line, a word at a time | 0.9s to fade in and sharpen, 1s to rise, 60ms between words, on `--ease` | Once, as the line comes into view |
| The closing word, built in memory order | 3.2s, or 1.1s after a new order; its trail fades over 0.8s | As the word comes into view (again once the reader has been a screen away), and on Build it again |

One switch stops every motion nobody asked for. The opening, the title figure and the repack window each
carry it as a Pause motion button beside their controls (`.btn.plain.sm` with `data-motion`, which reads
Play motion while paused and holds one width, `min-width: 8.25em`). One press pauses them all, and the
choice is remembered on the device. Paused, the opening neither turns, runs its head nor takes its
orders in turn, the title figure keeps its order, the repack window neither turns, twinkles nor plays
its first repack, and the result chart does not replay by itself. The end has no button of its own but
follows the switch: paused, the closing line and the closing word arrive whole, without their entrance.
A figure still moves in answer to its own controls, so a new order and Build it again still play. Focus
also stops what plays by itself, as the ARIA Authoring Practices ask of a carousel: once focus enters
the opening's or the title figure's tray (or the title itself), that figure stops taking its orders in
turn, and once it enters the repack window, the window never plays its first repack, so no option or
button changes under focus. Play motion starts the title figure's cycle again, never the opening's. With
reduced motion the page starts paused and hides the buttons, and every transition and animation is
instant: each moment shows a still frame, the closing line and the closing word show whole, and Build it
again and Replay the repack are hidden.

## Components

| Component | Class | Made of |
| :--- | :--- | :--- |
| Sheet | `.bench` | `--surface`, `--r-xl`, `--sheet-shadow`, 16 to 28px of padding. A head with a title and a meta line (`.bench-sub`); `.bench-name` stacks them when the head also holds a control. A caption below (`.bench-foot`). Two sheets side by side (`.split.pair`) end level, each caption under its chart and the numbers at the foot; `.split.mid` centers a chart and its numbers on each other. Two sheets stack at 900px and below, and on paper |
| Sheet title | `h3.bench-title`, `h4.bench-title` | A heading set as a title: Inter 600 at `--fs-title`, at the title role's one line height and tracking, so it lends the sheet only its place in the outline. An `h4` where the sheet's section already uses `h3` subsections; the stage window's title is an `h4`, the colophon's headings are `h2`. The outline never skips a level |
| Card on the page | `.claim` | `--surface`, `--r-lg`, `--sheet-shadow`, 18px 20px of padding; an `h3` title at `--fs-title`. A word longer than a card's line breaks rather than widen the card |
| Stat | `.bignum` | `--wash-1`, `--r-md`. The name with its series dot, the value in display weight with tabular figures, the change in ink-3 |
| Readout | `.readout` | `--wash-1`, `--r-sm`. A data label over a tabular value. On a phone the readouts form an even two-column grid, and a label that wraps keeps tight, balanced lines (line height 1.35) and may break anywhere; in the lab the first readout, and the fourth when no fifth shows, take a whole row |
| Callout | `.verdict`, `.verdict.off` | `--teal-1` or `--coral-1`, `--r-md`. The title carries a 10px dot of `--teal` or `--coral`, which sits on its first line when it wraps |
| Note | `.note` | Inter 400 at `--fs-small`, line height 1.5, ink-2: words beside a figure, inside its sheet, kept to `--col` or 66 characters |
| Dashed eyebrow | `.eyebrow.eyebrow-dash` | An eyebrow led by a rule of 22 by 1.5px in its own color, 10px before the words: the chapters, the stage window and the end. Below 360px the rule steps aside, so the longest eyebrow keeps to one line |
| Code | `pre.code` | `--wash-1`, `--r-md`, DM Mono 400 at `--fs-code`. Comments in ink-3, keywords in mint-ink. A block wider than its column fades out over 3em on the side where more of it lies and becomes a named Tab stop; the fade steps aside while it has focus |
| Choice card | `.tag` | `--wash-1`, `--wash-2` on hover, `--wash-4` pressed, `--r-md`, a teal checkbox. Its words cannot be selected; the focus ring goes around the card |
| Button | `.btn` | A pill. Primary: `--teal-1` with mint-ink text. `.ghost`: `--wash-2`. `.plain`: no fill until hover. `.sm`: the small control size. A label cannot be selected, and wraps, balanced and centered, when the pill is wider than its column. A button whose label changes holds the width of its longer label: the motion switch (8.25em), Repack the rows (11.7em, never wider than its place) and the repack window's button (14.6em, never wider than its foot) |
| Tray of options | `.chips` with `.chip`; `.chips.chips-lg` in the opening and at the end | A `--wash-2` tray of `--r-md` with 3px of padding; options of `--r-sm` at the small control size, 7px 12px. The chosen one gets `--lift`, `--lift-shadow` and a 1.5px inset ring of ink at 55%. `.chips-lg` sets its options at the control size, 8px 13px, from 561px. At 560px and below every option, in every tray, takes 9px at the sides (one rule), so the large tray is a plain tray there, and a tray that wraps fills each row it wraps to; on a phone held sideways, which can be wider, the opening's and the title figure's trays take the same 7px 9px. A tray is a radio group (app.js), named for its figure (Storage order for the sculpture): one Tab stop, the chosen option, and the arrow keys, Home and End move the choice. A tray hugs its options |
| Disclosure | `details.numbers` | A plain button at the small control size, line height 1.2, so it is as tall as a small button, with a chevron that turns a quarter as it opens. A chart sheet whose numbers are not already on it ends with one, Show the numbers, holding the chart's table; a hidden qualifier tells a screen reader which chart it opens |
| Instruction | `.hint`, `.mouse-only`, `.touch-only` | An instruction for a control, set in the sentence or meta line it belongs to. `.mouse-only` shows only where a pointer can hover and `.touch-only` only where none can. Paper and the page without JavaScript hide all three, so each is a whole clause, and the text around it reads whole without it |
| Breadcrumb | `.crumbs`, `.toc-btn` | The wordmark, then the chapter you are reading, which opens the contents. A mouse that rests on it for 0.11s opens them, and they close 0.26s after it leaves, so the way down to the menu keeps them open. A click, a tap or the keyboard opens them to stay, until a choice, a click elsewhere or Escape. The chapter's name arrives from the direction you scrolled, in full wherever it fits; its short form (`data-short`) takes its place only where the full name would be cut. Which names fit is measured once per bar width, from the text's fractional width (WebKit rounds `scrollWidth`), and again when the width, the text size or the fonts change, Safari's Page Zoom included, so a chapter change only writes the name. The wordmark keeps its cube and drops its word below 375px, or where large text leaves the bar narrower than 19em of its own text; narrower than 15em, the bar's Code and Paper links give the name their room too, and the contents carry the paper and the code, as they do on a phone |
| Contents | `.toc-menu`, `.toc-list` | A `--pop` sheet of `--r-lg` with 6px of padding, its rows starting under the chapter's name, no taller than the screen under the bar; rows of `--r-sm`; numbers in DM Mono; a check on the current chapter; hairline dividers. The focused row gets a `--wash-3` fill and a 2px mint-ink ring inside its edge. While it is open the digits 1 to 9, and 0 for chapter 10, choose a chapter. After a choice, focus moves to the chapter's heading. It opens at its top, with the current chapter's row in view, and moving through it never moves the page. On a phone the sheet spans the bar |
| Skip link | `.skip` | A primary `.btn` on the bar's own `--bg`, so it is opaque. It is the first Tab stop, shows only while it has focus, centered in the bar at the left edge of the wide column, and goes to the paper (`#readings`) |
| Badge | `.badge` | A pill with a `--rule` outline and ink-3 text, Inter 500 at `--fs-label`. A badge labels; it never holds content |
| Frame | `.tour-view`, `.tour-map` | `--r-sm` with a ring at `--wash-2`: a picture's edge is part of the data. Figure 1 is drawn on white, so its frames keep the light theme's `--surface`, `--ink-3`, `--teal-mark` and `--mint-ink` in both themes |
| Map part | `.map-r` | A part of the Figure 1 map, as a button: `--r-xs` with a dashed edge of ink-3 at 85%. `--teal-1` on hover, `--teal-2` pressed, and when chosen a 2px `--teal-mark` ring over `--teal-1`. Its focus ring sits 1px outside it. A part shorter than 24px grows to 24px about its middle, for a finger, and a part it would overlap gives way |
| Stage window | `.stage-window` | The stage inside the page, for a figure drawn in light: the full width of the screen and, on a screen wider than it is tall, the height of the screen under the bar, at most 1040px, so the whole moment fits in one view; `--sheet-r` corners; the stage's tokens in both themes. Its words sit on the page's grid, clear of the safe areas. Its foot holds the primary button (Repack the memory, then Restore the training layout), the Pause motion button and the state, whose dot turns coral and glows once the memory is repacked. The state line holds its two longest states unseen in the same place (`.sw-hold`), so the window keeps one height, and its foot one layout, through the whole repack. The cells take what the window leaves, at least `min(40svh, 560px)`; from 641px wide on a screen taller than wide, the window drops its screen height and the cells keep a 2 : 1.15 shape rather than stretch. A short phone tightens its spaces and flattens the cells, so the button and the state still reach the screen, and under Safari's bars on a phone held sideways the title takes `--fs-body`. The cells take focus and turn with a drag or the arrow keys. Without WebGL they are drawn with Canvas 2D (see [Moments](#moments)). The note under the window (`.sw-foot-note`) keeps a caption's measure on the column's left edge. Its sentences about the drawn cell, and the clause about the sparks in the paragraph before the window, are `.sw-cell-note`, which leaves with the cells |
| Tip | `.tip` | The one inverted surface: a fill of ink with words in the page's color, `--r-sm`, `--tip-shadow`, at most 260px wide. It speaks over a figure, so it stands apart from it. A mouse tip takes the pointer once the pointer has rested 0.4s on its mark, so the reader can move onto it, and waits 0.3s after the pointer leaves the mark. A tap's tip sits above the finger, or beside it on the roomier side when the bar leaves no room above. Escape and any scroll close a tip. On the stage it is the stage's ink with words in the stage's color |
| Meter | `.meter`, `.meter-row`, `.logit-row` | A 12px `--track` with a fill in its series' mark color, `--r-xs`; where there is a chance level, a 1.5px ink tick marks it. In a row, a label (`.small.muted`), the track and the value, set as a readout's value, in a column of fixed width (6ch, or 5ch for the two logits), so meters on one scale share a length. Inside a chart (the probes) a bar is drawn as a meter |
| Dot | `.dot` | A 10px key: `.teal`, `.coral` and `.warm` take the series' mark color, `.lav` the lavender. `.dot.ring.warm`, a ring of `--warm-mark`, is a baseline (the U-Net), drawn the same way in its chart, so it reads apart by shape as well as color |
| Table | `table.data` | Rules in `--grid` between rows, cells in ink-2, headers in Inter 500 ink-3, the first cell of each row its header, numbers right-aligned in tabular figures, and a caption for screen readers. A mean row (`.has-total`) is 600, with a `--rule` above it. At 640px and below the headers wrap |
| Scroller | `.math-display`, `.table-wrap` | A formula or a table wider than its column scrolls sideways and fades out over 32px at the edge where more of it lies (24px on the left), from `more-l` and `more-r`, which app.js sets. While it overflows it is a Tab stop, named for what it holds, or a display equation by its place (Equation 3) |
| Equation | `.math` | A MathJax drawing with a spoken label in words and its TeX in `data-tex`, after a hidden plain-text copy of it, so it can be copied and found |
| Link list | `.end-col a` | The colophon's Read and Chapters: plain ink links that turn mint-ink on hover. Each link fills its row, 29px tall for a mouse and 44px for a finger, with no gap between rows, and its focus ring takes `--r-sm` corners. Links in running text keep their underline. Every link eases its color over `--t-1` |

The interactive states are the same everywhere. Hover adds one wash step; an option in a tray takes
`--wash-1`, since its tray is `--wash-2`. Pressing adds another: `--wash-4`, `--teal-3` on a primary
button and `--wash-2` on an option, for a mouse and a finger alike, and the pressed rules come after
the hover rules. A part of a figure (the Figure 1 map) takes teal fills instead of washes. Hover
styles apply only where a pointer can hover, so they never stick after a tap; a finger gets a press
to 97% instead.

The focus ring is a 2px mint-ink outline at a 3px offset that follows the control's own corners (2px,
since Chrome draws a 2.5px outline at 2px anyway). It is resolved where the focus is, so on the stage it
is the stage's mint. In a tray it sits at offset 0, filling the gap between options and nesting inside
the tray's corners. A large block that takes the keyboard (the title, the repack cells) and a row of the
colophon's link lists give their ring `--r-sm` corners. Inside the contents, where an outline would
crowd the rows, the focused row gets a fill and an inner ring instead. The opening's sculpture reaches
under the words, so the same ring goes around its field, 12px inside it, with corners of `--r-xl` plus
12px. A focusable mark in an SVG (a rotary token) draws its ring as a 2.5px mint-ink stroke that does
not scale, the one other width. A heading that takes focus after a choice in the contents shows no ring.

On a coarse pointer every button, option and disclosure is 44px to hit without being drawn larger,
through a band its `::after` adds above and below it: 4px for a full button, and 7px for a small one, a
disclosure and an option. The wordmark's band is 5px, so its 34px are 44px, the height of the compact
bar, and the chapter's name in the bar is 45px to hit. The contents' rows, 45px under a finger, and
the colophon's link rows, 44px, get there through their own padding. A mark thinner than a finger, the
closing word's 14px memory ribbon, answers 10px above and below it. A rotary token's grab margin grows
as the grid shrinks, so the token is 46px to hit at any size, and with a token picked, a tap in a
token's margin, outside its own cell, moves the picked token to the cell under the finger.

Where one control wraps under another, their bands must not overlap, so a row gap holds both bands
whatever the width, the text size or the font's measures: the lab's wrapped tray rows sit 14px apart
under a coarse pointer, room for two 7px bands, and a Pause motion button that wraps keeps 12px from
the tray or the button above it, in the opening, the title figure and the repack window, under a
coarse pointer (and, under the two trays, on any phone held sideways). The opening's tray below 375px is
the one exception: its five orders wrap 3 + 2 only 2px apart, because on those narrow phones the
sculpture is already at its 180px floor and the first screen has no pixel to spare, so the bands take
the room instead: the first row's reaches 14px up, the second's 14px down, and the Pause motion button
under them answers 2px above and 12px below. Controls cannot be selected as text, and a long press on a
figure neither selects the words beside it nor offers to save the picture.

## Lines

Lines carry information. These are the only places they appear:

- chart axes and grids, the rules between table rows, and the rule above a mean row;
- the hairline under the top bar, which also shows reading progress in teal;
- the page's 1px rim where it meets the stage (`--page-rim-top`, `--page-rim-bottom`);
- the dividers inside the contents menu and in the colophon at the end;
- the edge of a menu, the ring of a frame, a badge's outline, and the ring of the chosen option in a
  tray;
- the short rule that leads a dashed eyebrow, and a meter's tick at chance;
- the dashed parts of the Figure 1 map, which trace the figure's own dashed boxes, and the solid
  rings of the chosen part (2px) and of the tour's spotlight (1.5px), in `--teal-mark`. The dashed
  parts are the only dashed lines outside the figures and charts.

A sheet, card, stat, readout, code block, button or tray never gets an outline. The fade at the edge
of a scroller is a mask, not a line.

## Moments

Three figures each take most of a screen, as pauses in the story, and together they tell it in order:

| Moment | Where | What it shows |
| :--- | :--- | :--- |
| Paths | The opening, `.hero` (`initPaths`) | The premise: to store a 3D field you draw one path through it. One glowing path joins memory position *i* to *i* + 1 through 512 tokens and morphs through raster, Morton, Hilbert, blocks and a repack while the volume turns |
| Two readings | The first screen of the paper, `#readings` (`initReadings`) | The idea: every letter of the title is a token with a place on the page and a place in memory, threaded together. The storage order rearranges the memory line; the words stay put |
| Repack | Chapter 5, a stage window, `#repackStage` (`initRepackStage`) | The evidence: one crop's 262,144 positions under each model. After the repack, one spark for each changed prediction, at the paper's rates: about 18 for PACK3D, about 3,215 for packed RoPE |

Each moment moves on its own only while it is in view and motion is on (see [Motion](#motion)), and
its own controls answer whether motion is on or not. A turn the reader gives a 3D figure, with a
drag or the arrow keys, pauses motion everywhere, so the view the reader chose stays put; a tap, a
scroll or a pinch that starts on a figure stops nothing. Picking an order ends a figure's own cycle,
and so does focus entering its tray (see [Motion](#motion)); in the title figure Play motion starts it
again, and the cycle also waits while a letter is picked. The title figure's note holds two lines
(3.24em), because a picked letter's indices wrap in a narrow column, and nothing below may jump.

What a moment does by itself is never announced. A change the figure makes on its own writes nothing
a screen reader speaks, or writes with `aria-live` off, and a change the reader makes writes with
`polite`, as a carousel that turns by itself does. The title figure's status line speaks only an order
the reader picked, spelled out. The repack window's state is a status line that is silent while the
window plays by itself and speaks from the reader's first press: each change of state, with both counts
after the repack. The tour's words become a live region at the reader's first step.

The opening's sculpture and the repack cells are 3D views (`role="application"`,
`aria-roledescription="3D view"`): they take focus, turn with the arrow keys, and say so in their
labels. The title is a slider over its letters, and the closing word a slider over its memory: Right
and Up step on, Left and Down step back, Page Up and Page Down jump (a row of the title, to the same
column in the other word; ten positions of the closing word), Home and End go to either end, and
Escape lets go. None of these keys scrolls the page. The 3D views and the rotary tokens leave the keys
they do not use, Page Up, Page Down, Home and End among them, to the browser, as any control does.

On a phone each moment keeps its order of reading, figure first, with its controls right under it. A
phone held sideways shows each moment in one screen under the bar (with Safari's toolbars showing, all
but the title figure; see [Layout](#layout)): the opening as a compact version of
the laptop's, the title, caption and orders on the left and the whole sculpture in the right half; the
title figure in two columns, the letters and their memory on the left and the readouts, orders and note
beside them; and the repack window with its words and counts beside the cells and their button. Where
the screen reorders a moment's parts, initPaths and initReadings move them in the page too, so Tab and
a screen reader meet them in the order they are seen, and the stylesheet sets the same order for the
first paint. A drag turns a figure only when it is sideways, so the page still scrolls and pinches.

The opening and the title draw with Canvas 2D; if the browser refuses the opening a canvas, the
opening keeps its words and drops its caption and orders. The repack draws the cell as soft points,
added together like light, with WebGL, on a canvas it makes when the figure is built, because Mobile
Safari can refuse WebGL to a canvas that has sat in the page for a while. If WebGL is refused, it asks
again a frame later on another new canvas, then draws the same points with Canvas 2D, as a still frame
that is drawn again whenever the reader turns the cells or presses the button. A lost context is
rebuilt: in place if the browser gives it back, otherwise on a new canvas after 1.5 seconds, or 0.3
seconds after the reader returns to the page. After three refusals or early losses (within 5 seconds
of a start) in a row, the figure stays on Canvas 2D. With no canvas at all, a sentence takes the cells'
place, and the counts, the strips and the button still work. These four paths, a new canvas for each
attempt, the retry, Canvas 2D and the recovery from a lost context, are what keeps the figure drawing
on an iPhone; a change to the window must keep all four. The volume is made in a worker as the reader
comes within 1,500px of the window, with the counts of each class along every row of 64 positions, from
which the memory strips are mixed; the window's first layout waits two frames after the volume
arrives, so making it never holds up the page.

## Figures

The charts are SVG, drawn by d3 in real pixels: each takes its sheet's width, down to 256px (the inside
of a sheet on a 320px phone), so its text keeps its set size, and only a narrower screen scales one
down. Each chart's final height is held in the stylesheet, or on the `svg` in the markup, before the
script draws it, so the page does not grow under the reader; where the stylesheet sets a chart's floor
and ceiling, app.js reads them from it (`heightRange`). On a phone held sideways those come down: the
result and latency charts share the screen with the control above them, and the Predictions changed
chart and the pooling figure keep under the bar, down to their tightest legible drawing (the first
closes up its rows, from 26px to as little as 19, and its heads, from 30 to 24; the second's dials
shrink to a radius of 40 at least). A chart draws again when its width changes, never when only the
height does, so a phone's toolbar showing or hiding redraws nothing; Safari's Page Zoom, which tells
only the visual viewport, redraws them too.

A chart's marks take the series' mark colors. A baseline reads apart by shape too: the U-Net is a ring,
window attention a dashed line, and PACK3D the heaviest line. A mark explains itself through
`explain()`: a mouse hovers it and the tip follows; a tap anywhere on the chart opens the tip of the
nearest mark within 26px and outlines that mark while its tip is up. A mark a mouse hovers is outlined
the same way, so the outlined mark is always the one the tip describes. A reference tick, such as chance
in the probes, never takes the pointer. The result chart draws every seed line before any mean, so a
mean always takes the pointer over a seed's line, and its series names come in once the lines are within
1% of home, because an eased-out line spends the last 40% of its time on that 1%. A chart is an image to
a screen reader (`role="img"`), named for what it shows, with its numbers in the name itself or in a
table, which `tableFrom()` builds with a hidden caption, column headers and row headers.

The lab, the title figure, the opening, the repack window and the closing word draw on canvases. Each
lays itself out when its size, the pixel ratio or the fonts change, rather than in its frames. The lab,
the title figure and the result chart repaint at once when the theme changes (`onTheme`); the other
charts color their marks with the tokens through CSS, which follow the theme by themselves, and the
figures on the stage keep their colors in both themes. The lab's two views hold their final heights in
the stylesheet too, mirroring the script's layout: eight slices to a row from 880px for a mouse and from
1000px for a finger, four from 560px, two below. On a touch screen held sideways the slices keep two
rows of four inside the screen under the bar, never narrower than 560px, so a token stays big enough
for a finger. Below 361px the lab's four orders sit two by two, so no order is squeezed.

The rotary grid is a 320-unit square that scales with its sheet; app.js sets `--u`, the units in one CSS
pixel, so its memory positions keep the data-label size on every screen. The grid, its axes and its
buttons share one left edge, 460px wide at most, so the board reads as one column; on a phone held
sideways it narrows with the screen's height (further under Safari's bars), so the grid and its buttons
share the screen under the bar. On a dial each hand shows the turn a token gets from its own index, and
the shaded arc their difference, so a move that keeps the difference turns the arc whole. A dial row
holds three dials, and with enlarged text as many as their captions leave room for.

The Figure 1 tour moves its picture, never redraws it: the overview is a picture at the screen's
density, and the vector loads once the reader rests on the figure or steps into it. Previous and Next
come first, under the figure, so they stay put while the step's text changes length. Clicking the
overview zooms into the part under the pointer, and clicking a zoomed view steps back out; the second
click of a double-click is ignored, since it would undo the first. On a phone, where the map shows only
while a part is open, a part chosen again from the map zooms back out and hands the focus on to Next.
At the end, the closing word's tray sits on the left and Build it again on the right; when they wrap,
each row starts at the left.

## The dark stage

The opening (`.hero`), the stage window (`.stage-window`), the end (`.end`), the top bar while the
stage is under its lower edge (`.topbar.on-stage`, `.topbar.on-end`, which app.js sets) and, without
JavaScript, the note above the opening (`.noscript-note`) use the stage's tokens, in both themes. They
point the page's tokens at the stage's: `--bg` is `--stage-bg` `#060A09`, `--ink` `#EEF3F1`, `--ink-2`
`#B4BEBA`, `--ink-3` `#8C9A95`, `--teal` and `--teal-mark` `#19AC8B`, and `--mint-ink` `#5FE0C3`.

The stage also sets values of its own: `--surface` `#151C1A`, `--surface-2` `#101614`, `--rule` its
ink at 14%, `--coral` and `--coral-mark` `#FF7276`, `--coral-ink` `#FF9A9E`, `--tint-teal` `#1F5F51`,
`--lift` its ink at 14% with no shadow, `--pop` `#121917` with an edge at 9% and a deeper shadow, and
a dark color scheme. Its coral is brighter than the dark page's `#C9474F`: on the stage, packed RoPE
keeps the light page's coral in both themes. It mixes its washes and teal fills again from its own ink
and teal, so any button, tray or menu placed on it works without styles of its own. Text selected on
the stage keeps the stage's full ink over the deep teal.

Behind each figure is a lavender lamp, `--lamp` mixed at 17% in the opening, 16% in the stage window,
and from 26% down to 8% at the end. Text laid over a figure has a halo of `--stage-halo`; the title's
is `--stage-bg` at 85%. Memory order in the opening and the end runs from `--mem-0` to `--mem-4`.
Where the page lifts off the stage, its rim draws the edge. The browser's own chrome follows the bar:
the page's background past either end is the stage's, and so is the strip under a phone's status bar
(past the end the body takes the stage's color too, since Safari tints its toolbar's strip from the
body), and app.js sets the theme color to the stage's or the page's, whichever is under the bar.

The root element is the one place the stage's color is written out. `html.at-top` and `html.at-end` set
the background to the literal `#060A09`, the value of `--stage-bg`, not `var(--stage-bg)`: a `var()` on
the root, switched by a class, restyles the whole document at each switch of the bar's scope, a long
style pass right where the opening hands over to the page and where the page hands over to the end. Keep
the two literals in step with `--stage-bg`, as the `theme-color` tags in the head keep theirs (the
stage's `#060A09`, and the page's `#F3F5F4` and `#0B0F0E`).

A missing address shows `404.html`: the stage alone, dark in both themes, with the bar's wordmark, an
eyebrow led by its dash (which this short eyebrow keeps at every width), a display line at 320, a
sentence in ink-2 and three buttons, to the paper's page (primary), the paper on arXiv (ghost) and the
code (plain), which wrap, balanced and centered, like the page's. It stands by itself, with copies of
the tokens it uses (the stage's colors, the washes and teal fills mixed from them, `--fs-label`,
`--fs-control`, `--fs-title`, `--ls-control`, `--wide`, `--gutter`, `--bar-h` with its 44px on a phone
held sideways, `--s-3`, `--r-sm`, `--ease` and `--t-1`), the opening's lamp at 17%, the page's focus
ring and its touch rules: no grey flash on a tap, a press to 97% where nothing can hover, 44px hit bands
on a coarse pointer, and in a contrast theme a `ButtonText` edge and a dash in `CanvasText`. Its other
spaces are its own (20px between its parts, 8px between and above its buttons); on a phone held sideways
and 340px tall or less (Safari's toolbars showing), its title steps down to 12svh at most and its spaces
to `--s-3`, so the way back stays on the first screen. GitHub Pages serves it at any depth, so its links
are absolute. Keep its copies in step with the page's tokens.

## Contrast themes and print

### Contrast themes

A contrast theme repaints every fill, shadow and mask in the system's colors, so the page draws again
what it shows with them. Buttons, options, the breadcrumb's chapter and disclosures get a 1px
`ButtonText` edge, and the chosen option is `Highlight` with `HighlightText`, ringed in `CanvasText`
when it has focus. A disclosure's chevron is drawn in `ButtonText`, so open and closed still differ. The
focused row in the contents gets a 2px `Highlight` ring. Figure 1 stays a light picture, so its map
keeps the dashed edges and the ring drawn for it, and the chosen part takes a `Highlight` edge. Series
dots, callout dots, the repack window's state dot, meters and the progress line keep their own colors, a
meter gets a `CanvasText` edge, and the current chapter's check, the menu's dividers and the dash before
an eyebrow are `CanvasText`, like the words beside them.

### Print

On paper the page uses the light palette, whatever the screen's theme. On `beforeprint`,
`initControls` (which runs before any figure starts) calls `setTheme('light')`, which sets
`data-theme` and runs every theme callback before it returns; `afterprint` restores the theme the page
had. A theme callback therefore repaints at once, never on a later frame, because a print takes its
picture before the next frame. Every chart then draws again for a 650px column (`PRINT_W`, a Letter or
A4 column inside its margins), the lab's views are drawn for the same width and scale by their
proportions, the result chart shows its repack done, and two sheets side by side print one under the
other; after printing, the screen's widths come back.

The stage, the stage window and the end take the page's palette and drop their dark fills, and the
root and the body drop the stage's color behind the page, so nothing prints as a black block, even
from the end with background graphics on. What moves or answers a pointer is left out: the bar and
tips, the opening's sculpture and its controls, the link buttons under the opening and the title
figure, the title figure's note, trays, rows of controls and the motion buttons, Replay, the tour's
buttons, map and step count, the repack window's cells, counts and foot, the closing word, the
disclosures' buttons, Copy BibTeX and Back to the top. So is every instruction for a control (`.hint`,
`.mouse-only`, `.touch-only`), every sentence about the repack window's drawn cell (`.sw-cell-note`),
the contract's meta line and the stage window's note. Words that point at something paper does not
show go in one of those, or are written so they do not point.

The stage window prints its one-sentence summary on the text column, with no padding, the column's
width and no reserved rows. Figure 1 prints whole at any step of the tour, since paper has no camera:
the picture sits still and untransformed, without the spotlight, and the step's words are its caption.
The closing line prints whole; the scrollers drop their fades, which would print the words twice; each
external link in the colophon's Read list prints its address under it, in DM Mono at `--fs-label`; and
series dots, callout dots, meters and the eyebrows' dashes keep their colors. Sheets, cards, stats,
code, callouts, the stage window, a chapter's head, the two readings and the colophon's lists are not
split across pages, and a heading or an eyebrow stays with what follows it. The rotary sheet, taller
than a page, breaks only between its grid and its dials.

### Without JavaScript

Without JavaScript the page reads in full, and nothing on it offers what cannot work. A note on the
stage above the opening says the figures need JavaScript. The `noscript` style hides the controls that
would do nothing (trays, rows of controls, the motion buttons, the tour's buttons, map and step count,
Replay, the disclosures, Copy BibTeX and the contract's checkboxes), the figures and frames the script
draws (the opening's field, the title's memory row and its note, the whole lab and the whole
rotary-dials sheet, the pooling figure's meta line and readouts, empty charts, the repack window's cells
and foot) and, as on paper, every instruction for a control (`.hint`, `.mouse-only`, `.touch-only`) and
every sentence about the drawn cell (`.sw-cell-note`). The opening takes only its words' height, Figure
1's frame fits its picture, the pooling figure's note spans its sheet, the stage window shrinks to its
one-sentence summary, the contract's cards read as a list with no Tab stops, the contents still open
from the keyboard, and the italic is declared there, since app.js would otherwise load it.

## Accessibility

- **One ring.** Every control shows the 2px mint-ink focus ring on the keyboard (see
  [Components](#components)), and a focused control never lands under the bar.
- **Every control works from the keyboard.** A tray is one Tab stop whose arrow keys, Home and End move
  the choice. The 3D views turn with the arrow keys; the title and the closing word are sliders; the
  lab's token field (`role="application"`, "token field") moves its query with the arrow keys, Page Up
  and Page Down along *z*, and Home and End to its row's ends (with Ctrl, the slice's corners); a rotary
  token is a button that the arrow keys move a cell at a time. The skip link is the first Tab stop, the
  contents answer the arrow keys, Home, End, the digits and Escape, and a scroller that overflows
  becomes a named Tab stop.
- **The page speaks only for the reader.** Live regions write what the reader changed, once, and stay
  silent for motion nobody asked for (see [Moments](#moments)). A readout or a callout writes only a
  value that changed, so a redraw is not announced, and a figure that plays by itself stops once focus
  enters it, so nothing changes under the keyboard.
- **Every figure has a name and its numbers.** A figure's title is a heading, and the outline never
  skips a level. A chart is a named image with its table under Show the numbers; an equation has a
  spoken label, its TeX and a hidden plain-text copy; the links that open a new tab say so. No two
  controls or regions share a name: each tray is named for its figure, and an overflowing display
  equation is named by its place (Equation 3).
- **Hover content can be read and dismissed.** A mouse can move onto a tip, a tip waits 0.3s after the
  pointer leaves its mark, and Escape or a scroll closes it.
- **Targets fit a finger.** Under a coarse pointer every button, option, disclosure and link row, the
  wordmark, the contents' rows and the rotary tokens are 44px or more to hit, through `::after` bands,
  padding or a grab margin, and nothing is drawn larger for it; rows that wrap keep their bands apart
  (see [Components](#components)). The exceptions are the skip link while it is hidden, links inside
  running text, the Figure 1 map's parts (24px at least) and an equation that scrolls.
- **Text can grow.** With large text or a reader's own text spacing, labels wrap rather than spill, a
  card breaks a long word, the dial rows hold fewer dials, the title figure's title shrinks just enough
  to stay in its sheet, and the bar gives the chapter's name the wordmark's room, then the room of its
  Code and Paper links. The page never scrolls sideways.
- **Motion can stop.** Pause motion stops every figure that moves on its own, and reduced motion makes
  every change instant (see [Motion](#motion)).
- **Contrast holds.** At rest, text keeps 4.5:1 against what it sits on (a large title 3:1), in both
  themes and on the stage; mint-ink is 5:1 or more on the light page and its sheets; a mark is 3:1 or
  more against its sheet; and a contrast theme draws again what fills drew.

## Performance

The benchmark run during the redesign found the site far lighter to run than the original. These rules
keep it that way.

- **The root's background is a literal.** `html.at-top` and `html.at-end` write the stage's color as
  `#060A09` (see [The dark stage](#the-dark-stage)).
- **Nothing new runs in a scroll or a frame.** While the page scrolls, the bar does one update a frame,
  and it reads every measure before it writes anything, so a scroll forces a layout only when the
  chapter changes, to replay the name's arrival. Which names fit the bar is measured once per width,
  never at a chapter change, and the reading-progress line is scaled, not resized. The other scroll
  listeners do little: they close a tip, restart a timer or, at the end, read one box to learn when the
  reader has gone a screen away. A figure lays itself out when its size, the pixel ratio or the fonts
  change (a `ResizeObserver`, `onDpr`), not in its frames, which draw; the title figure's frames read
  its letters' boxes, which costs a layout only in the frame where its cycle writes a new order. A
  change to the page adds no work to either path.
- **A figure runs only while it moves and is in view.** Paused, settled or off the screen, a figure
  stops asking for frames. Heavy work goes elsewhere: the repack volume and its strips' counts are made
  in a worker, as the reader comes within 1,500px; the closing word lays out as the reader comes within
  900px of the end, or once the page is idle; Figure 1's vector loads only when the reader rests on the
  figure or steps into it.
- **Canvases draw at the screen's density, within a budget.** A 2D canvas draws at the device's pixel
  ratio, up to 3x, within 4 million pixels. The opening's canvas covers a 2x screen at any size (from
  1500px wide its field keeps to the grid, so about 5 million pixels at most), while a 3x phone keeps
  the 4 million. The repack window's WebGL canvas draws at 2x at most, within 3 million pixels, and its
  memory strips at 2x at most. The lab's token grid stays square (see [Radius](#radius)).
- **The first screen loads little.** The page loads its scripts deferred and starts each figure in a
  task of its own; d3 is a partial build of the modules the charts use, half the bytes of the full
  build; the upright Inter is preloaded and the italic loads once the page is up. The stylesheet is
  inline and blocks the first paint, so its comments are section headers and short notes on why, about
  8 KB of the head's 86 KB (21 KB compressed); the reasons are on this page. app.js keeps its block
  headers and its notes on why; `makeScene`, the stage worker's source, is sent as text, comments and
  all, so it is edited only on purpose.
- **What was measured, on one machine.** On a Mac shared with other work, headless Chrome emulating an
  iPhone (4x slower CPU, slow 4G), with the page served compressed, the first contentful paint took a
  median of 496 ms over five interleaved runs (488 to 508), against 488 ms (476 to 500) for the site
  before the redesign and 532 ms while the stylesheet's comments ran to 27 KB. Those runs used the
  trimmed stylesheet before its last spacing and type edits, which changed the compressed head by under
  0.1 KB. Take the numbers as a comparison between builds, not a budget.

## Adding something new

- Build it from the components above. If none fits, build it from the tokens, and space it on the
  scale with the shared classes, not inline styles: a row of controls at `--s-2`, a space between two
  steps to the nearer one.
- Group with a wash and raise with the sheet shadow. Do not add a border.
- Give color only to the series it stands for: teal for PACK3D, coral for packed RoPE. Draw a mark that
  carries a value in its series' mark color, and read a token in app.js with `tok()`.
- Keep controls in Inter 500 at a control size with `--ls-control`, type on the `--fs-*` sizes at its
  role's weight, and corners on the radius scale, nested.
- Name `--ease` and a `--t-*` duration in every transition, and ease out a move that answers the
  reader. A figure that moves on its own reads the motion switch, carries a Pause motion button, has a
  still frame for reduced motion and stops once focus enters it, and what it does by itself is never
  announced.
- Write labels in sentence case, set variables and *p* and *t* in italic (upright in DM Mono labels),
  and keep dimensions, names and expressions on one line.
- Make a figure's title a heading at the level its section needs, give the figure a label and keys,
  and let a status line speak what the reader changes.
- Put every instruction for a control in a `.hint` (or `.mouse-only` and `.touch-only`), as a whole
  clause, and a sentence about a drawn figure that paper does not show in a class that hides it there
  (`.sw-cell-note`); reword anything else that points at what is not there, and hide whatever cannot
  work on paper and without JavaScript.
- Hold a figure's final height in the stylesheet, so nothing moves when its script draws it. Write a
  height that must fit under the bar with `var(--bar-h)`, and repaint at once in a theme callback.
- Give a finger 44px through `::after` bands, and where one control wraps under another, a row gap
  that holds both bands. Add no work to a scroll or a frame: lay a figure out when its size changes.
- Check it in light, in dark and on the stage, at phone width and on a phone held sideways (667 by 375,
  844 by 390, 932 by 430, and 874 by 292, Safari with its toolbars), with a mouse, a finger and the
  keyboard, with large text, in a contrast theme, on paper from either theme, and without JavaScript.
