# The website's design system

The website in [website/](../website/) is built from one small design system. Its tokens sit at the top
of the `<style>` block in `website/index.html`, and every component below is written in those tokens.
This page says what each token and component is for, so the next figure, section or control can be
built from the same parts.

When something needs a value the system does not have, add a token, to the stylesheet and to this
page, instead of writing a one-off value into a rule.

## Principles

1. **The page is a sheet of paper lifted off a dark stage.** The reading column and its figures sit on
   the sheet. The stage shows at the opening, through one window in the result chapter, and at the
   end, and it is dark in both themes.
2. **Fills, not outlines.** A group is a wash of ink, a figure sits on a sheet with a soft shadow, a
   chosen option is lifted out of its tray. Nothing gets a border to look like a box. Lines are kept
   for information; the list is under [Lines](#lines).
3. **Color carries meaning.** Teal is PACK3D, the coordinate, the primary action and where you are.
   Coral is packed RoPE and the memory position. Orange and green are the query and key in the lab.
   Lavender is the third model, separable PE, and the stage's lamp. Warm grey is a baseline.
   Everything else is ink.
4. **A choice is lifted; the current place is checked.** The chosen option in a tray is raised out of
   it, and the current chapter in the contents carries a check. Nothing is shown as chosen by turning
   it black or white.
5. **Controls speak in one voice.** Every control is set in Inter 500 at one of two sizes. Choosing an
   option never changes its weight, so no word shifts when it is pressed.
6. **Corners nest.** An inner corner is the outer corner less the padding between them: a tray of 13px
   with 3px of padding holds options of 10px.
7. **Motion answers the reader.** A state change eases out in 0.15 to 0.4 seconds. Hover changes only
   a fill and the ink, never a size or a position; the one thing a hover opens is the contents, and
   only after the mouse rests. With reduced motion, every change is instant.
8. **Precision in type.** Numbers use tabular figures. Labels for data are set in DM Mono. Capitals are
   kept for eyebrows and never set text that holds a variable: an uppercase label would turn the
   variable *z* into *Z*.

## Tokens

### Color

| Token | Light | Dark | Use |
| :--- | :--- | :--- | :--- |
| `--bg` | `#F3F5F4` | `#0B0F0E` | The page |
| `--surface` | `#FFFFFF` | `#121816` | Sheets and cards |
| `--ink`, `--ink-2`, `--ink-3` | `#0F1513`, `#444D49`, `#5F6964` | `#E8EEEB`, `#B9C2BE`, `#93A09A` | Text, secondary text, labels and captions |
| `--rule` | `#D5D8D2` | `#2D3633` | The hairline under the bar, a badge's outline, reference lines and dial faces in the figures |
| `--grid` | `#E4EBE8` | `#202927` | Chart grids and table rules |
| `--teal` | `#00B796` | `#19AC8B` | PACK3D, the primary action, the focus ring |
| `--mint-ink` | `#00735D` | `#5FE0C3` | Teal text: eyebrows, primary buttons, the current-chapter check |
| `--coral` | `#FF7276` | `#C9474F` | Packed RoPE |
| `--coral-ink` | `#C2414A` | `#FF8F94` | Coral text: what a sequence-indexed model reads, its count of changed predictions |
| `--orange`, `--green` | `#FFAA4D`, `#8FE07A` | `#FFB15E`, `#7BD866` | The query and the key in the lab |
| `--lav` | `#997ADB` | `#9479D8` | Separable PE, the members of a block in the summary figure |
| `--warm`, `--neutral-2` | `#9E978E`, `#5F5B56` | `#A39C93`, `#D2CCC4` | Baselines: the U-Net, SDPA, window attention, ablations |
| `--tint-teal`, `--tint-coral` | `#8EDDCB`, `#FFB4B6` | `#1F5F51`, `#6B2F33` | The faint per-seed marks behind a series; text selection |
| `--track` | `#EEF1EF` | `#1C2422` | The empty part of a meter or a bar |

### Fills

Fills are the ink, or teal or coral, mixed at low strength with nothing. Because they are partly
transparent, one fill works on any surface and in either theme.

| Token | Strength | Use |
| :--- | :--- | :--- |
| `--wash-1` | ink 4.5% | A group at rest: stats, readouts, code, choice cards, frames |
| `--wash-2` | ink 7% | Trays, quiet buttons at rest, hover on a row or a plain button |
| `--wash-3` | ink 10% | Hover on a quiet button, a menu button while its menu is open |
| `--wash-4` | ink 14% | Pressed |
| `--teal-1`, `--teal-2`, `--teal-3` | teal 15%, 22%, 28% | A primary button at rest, on hover and pressed; a PACK3D callout |
| `--coral-1` | coral 14% | A packed RoPE callout |

### Elevation

| Token | What it raises | Light | Dark |
| :--- | :--- | :--- | :--- |
| `--sheet-shadow` | Sheets and cards | A soft shadow | A faint edge of light and a deep shadow |
| `--lift`, `--lift-shadow` | The chosen option in a tray | White with a hairline shadow | Ink at 13% |
| `--pop`, `--pop-rule`, `--pop-shadow` | Menus | White, a 9% edge, a wide shadow | A raised surface, a 9% edge, a deep shadow |

### Radius

| Token | Size | Use |
| :--- | :--- | :--- |
| `--r-xs` | 6px | Marks: meters, the memory ribbon |
| `--r-sm` | 10px | Controls and rows: options in a tray, menu rows, readouts, frames, tips, disclosures |
| `--r-md` | 13px | Groups: trays (10 + 3), stats, code, callouts, choice cards |
| `--r-lg` | 16px | Small sheets: the contents menu (10 + 6), cards that sit on the page |
| `--r-xl` | 20px | Sheets: the benches that hold the figures |
| `--sheet-r` | 22 to 48px | The page itself, where it meets the stage |
| (pill) | 999px | Buttons and badges |

### Type

| Role | Set in | Where |
| :--- | :--- | :--- |
| Display | Inter 320 to 380, tight tracking | The title, the closing line |
| Heading | Inter 480 | Chapter headings |
| Title | Inter 600 | Sheet titles, card titles, stat names, callout titles |
| Body | Inter 400, 1.05rem, line height 1.62 | The reading column |
| Lede | Inter 400, 1.18 to 1.42rem | The first paragraph of a chapter |
| Control | Inter 500, `--fs-control` (0.9rem) | Buttons, the breadcrumb, menu rows, the two encodings |
| Small control | Inter 500, `--fs-control-sm` (0.84rem) | Options in a tray, small buttons, disclosures |
| Meta | Inter 500, `--fs-meta` (0.8rem), ink-3 | Figure labels, the quieter words in a control |
| Caption | Inter 400, 0.84rem, ink-3 | The note under a figure |
| Data label | DM Mono, 0.74 to 0.8rem, ink-3 | Readout labels, chapter numbers in the contents, the readouts in the opening and at the end |
| Chart text | Inter, 13px, tabular figures | Axis values and labels inside the charts |
| Eyebrow | Inter 600, 0.72 to 0.74rem, capitals, tracking 0.12 to 0.14em | Chapter and section labels, in mint-ink; the headings of the colophon |

### Motion

| Token | Value | Use |
| :--- | :--- | :--- |
| `--ease` | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Every state change |
| `--t-1` | 0.15s | A fill on hover |
| `--t-2` | 0.25s | A change of state: a lift, a callout, a chevron, a menu |
| `--t-3` | 0.4s | A change of place: the chapter name in the breadcrumb, the bar moving between stage and page, a meter's fill |

Three motions run longer, and each plays once, in answer to the page arriving or to the reader: the
opening (about 7 seconds), the Figure 1 tour's camera (1.1 seconds) and the closing word (about
1 second). With reduced motion, every transition and animation is instant, and the opening shows a
still frame.

## Components

| Component | Class | Made of |
| :--- | :--- | :--- |
| Sheet | `.bench` | `--surface`, `--r-xl`, `--sheet-shadow`, 16 to 28px of padding. A title and a meta line on top, a caption below |
| Card on the page | `.claim` | `--surface`, `--r-lg`, `--sheet-shadow` |
| Stat | `.bignum` | `--wash-1`, `--r-md`. The name with its series dot, the value in display weight with tabular figures, the change in ink-3 |
| Readout | `.readout` | `--wash-1`, `--r-sm`. A data label over a tabular value |
| Callout | `.verdict`, `.verdict.off` | `--teal-1` or `--coral-1`, `--r-md`. The title carries a dot of the same color |
| Code | `pre.code` | `--wash-1`, `--r-md`, DM Mono 0.82rem |
| Choice card | `.tag` | `--wash-1`, `--wash-2` on hover, `--r-md`, a teal checkbox |
| Button | `.btn` | A pill. Primary: `--teal-1` with mint-ink text. `.ghost`: `--wash-2`. `.plain`: no fill until hover. `.sm`: the small control size |
| Tray of options | `.chips` with `.chip`; `.seg` in the opening | A `--wash-2` tray of `--r-md` with 3px of padding; options of `--r-sm`; the chosen one gets `--lift` |
| Disclosure | `details.numbers` | A plain button with a chevron that turns a quarter as it opens |
| Breadcrumb | `.crumbs`, `.toc-btn` | The wordmark, then the chapter you are reading, which opens the contents. A mouse that rests on it for 0.11s opens them, and they close 0.26s after it leaves, so the way down to the menu keeps them open. A click, a tap or the keyboard opens them to stay, until a choice, a click elsewhere or Escape |
| Contents | `.toc-menu`, `.toc-list` | A `--pop` sheet of `--r-lg` with 6px of padding; rows of `--r-sm`; numbers in DM Mono; a check on the current chapter; hairline dividers |
| Badge | `.badge` | The one outlined element: a pill with a `--rule` outline and ink-3 text. A badge labels; it never holds content |
| Frame | `.tour-view`, `.tour-map` | `--r-sm` with a ring at `--wash-2`: a picture's edge is part of the data |
| Stage window | `.stage-window` | The stage inside the page, for a figure drawn in light: the full width of the screen and most of its height, `--sheet-r` corners, the stage's tokens in both themes |
| Tip | `.tip` | The one inverted surface, ink on the page color, `--r-sm`. It speaks over a figure, so it stands apart from it |
| Meter | `.meter` | `--track` with a teal or coral fill, `--r-xs` |
| Table | `table.data` | Rules in `--grid` between rows, headers in Inter 500 ink-3, numbers right-aligned in tabular figures |

The interactive states are the same everywhere: hover adds one wash step and pressing adds another.
The focus ring is a 2.5px teal outline that follows the control's own corners; inside the contents,
where an outline would crowd the rows, the focused row gets a fill and a thin teal ring instead. A
finger gets a slight press instead of a hover.

## Lines

Lines carry information. These are the only places they appear:

- chart axes and grids, and the rules between table rows;
- the hairline under the top bar, which also shows reading progress in teal;
- the dividers inside the contents menu and in the colophon at the end;
- the edge of a menu, the ring of a frame and a badge's outline;
- the dashed regions of the Figure 1 map, which trace the figure's own dashed boxes. These are the
  only dashed lines outside the figures and charts.

A sheet, card, stat, readout, code block, button or tray never gets an outline.

## Moments

Three figures each take most of a screen, as pauses in the story, and together they tell it in order:

| Moment | Where | What it shows |
| :--- | :--- | :--- |
| Paths | The opening, `.hero` (`initPaths`) | The premise: to store a 3D field you draw one path through it. One glowing path joins memory position *i* to *i* + 1 through 512 tokens and morphs through raster, Morton, Hilbert, blocks and a repack while the volume turns |
| Two readings | The first screen of the paper, `#readings` (`initReadings`) | The idea: every letter of the title is a token with a place on the page and a place in memory, threaded together. The storage order rearranges the memory line; the words stay put |
| Repack | Chapter 5, a stage window, `#repackStage` (`initRepackStage`) | The evidence: one crop's 262,144 positions under each model. After the repack, one spark for each changed prediction, at the paper's rates: about 18 for PACK3D, about 3,215 for packed RoPE |

Each moment plays by itself when it comes into view and stops as soon as the reader takes its controls.
Each pauses while off screen. With reduced motion, each shows a still frame that still answers its
controls. On a phone each keeps its order of reading, figure first, and stays inside one screen's
width; a drag on a figure turns it only when it is sideways, so the page still scrolls.

## The dark stage

The opening (`.hero`), the stage window (`.stage-window`), the end (`.end`) and the top bar while it sits over the stage use the stage's
tokens, in both themes: `--bg` `#060A09`, `--ink` `#EEF3F1`, `--ink-2` `#B4BEBA`, `--ink-3` `#8C9A95`,
`--teal` `#19AC8B` and `--mint-ink` `#5FE0C3`, with a lavender lamp behind the figure. The stage also
mixes its fills again from its own ink, so any button, tray or menu placed on it works without styles
of its own.

## Adding something new

- Build it from the components above. If none fits, build it from the tokens.
- Group with a wash and raise with the sheet shadow. Do not add a border.
- Give color only to the series it stands for: teal for PACK3D, coral for packed RoPE.
- Keep controls in Inter 500 at a control size, and corners on the radius scale, nested.
- Write labels in sentence case, and keep variables in their own case.
- Check it in light, in dark and on the stage, at phone width, and with a mouse, a finger and the
  keyboard.
