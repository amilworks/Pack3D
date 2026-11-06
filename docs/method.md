# Method walkthrough

PACK3D separates three objects: a field of tokens, their coordinate-defined
attention graph, and the order in which they are stored. Start with
[examples/minimal_attention.py](../examples/minimal_attention.py), then read the
functions in [the code guide](code_guide.md).

## One small field

Take a `4 x 4 x 4` token grid with 32 channels and batch size one. There are 64
tokens. With `2 x 2 x 2` fine blocks, there are eight blocks with eight canonical
slots each. Pooling two fine summaries gives four final summaries. A radius-one
query has at most 27 local neighbors, fewer at the boundary.

`build_layout((4, 4, 4), block_shape=(2, 2, 2), pool_size=2)` returns:

| Tensor | Shape | Meaning |
| --- | --- | --- |
| `order` | `[64]` | Raster index of each packed row |
| `coords` | `[64, 3]` | Coordinate of that row, in `(z,y,x)` order |
| `geometry.neighbors` | `[64, 27]` | Packed neighbor indices; `-1` means absent |
| `geometry.blocks` | `[8, 8]` | Packed members by fine block and canonical slot |
| `geometry.reverse_neighbors` | `[64, max_reverse_degree]` | Queries that use a key, for backward |

For example, in native Morton order the first fine block contains coordinates
`(0,0,0), (1,0,0), (0,1,0), (1,1,0), (0,0,1), (1,0,1), (0,1,1), (1,1,1)`.
The corner query at `(0,0,0)` has eight valid local neighbors. A query at `(1,1,1)`
has 27. These facts do not depend on the tokens' memory positions.

## Project and rotate

The layer normalizes the input and projects one query stream and separate local
and global key/value streams. With two query heads, one KV head, and head
dimension 16, `Q` has shape `[1,2,64,16]`; each K/V stream has shape `[1,1,64,16]`.
Grouped-query attention shares each KV head across its assigned query heads.

Axial RoPE rotates pairs of channels using the token's grid coordinate. All
pairs are active: a 64-dimensional head uses `(11,11,10)` pairs across the three
axes. Frequencies restart on each axis with base 10,000. Values are unrotated.
The packed-position control instead assigns all pairs to sequence position.

## Compress in two stages

For fine block `j`, use a scalar score per token and KV head:

$$a_{ju}=\operatorname{softmax}_{u\in B_j}
\left(w^\top R(c_u)k_u/\tau+b_{s_j(u)}\right).$$

The learned vector `w` and canonical-slot bias are shared across blocks. The
weights depend on content, but not on the current query. Apply the same weights
to rotated keys and unrotated values. The second stage averages valid fine
summaries within each coarse group. Empty fine blocks contribute neither mass
nor a count; an entirely empty coarse group is rejected.

The reference exposes this operation as `compress_summaries`. Its outputs have
shape `[1,1,4,16]` in this example. The optimized backend performs the two stages
in a staged kernel pipeline without storing the full token-to-summary score map.

## Attend and combine

Local attention computes exact softmax on the supplied neighborhood graph.
Global attention computes softmax over all four final summaries. Summary supports
can overlap the local neighborhood; the branches do not partition a single
softmax distribution.

The principal contract combines them as

$$o_i=s_L\odot o_i^L+g_{iG}s_G\odot o_i^G.$$

The channel scales initialize to 1 and 0.25. The global gate comes from a
token/head-wise softmax. Output projection and an outer residual complete the
clean attention layer. Task decoders and feed-forward blocks are separate.
The earlier Allen-6 recipe instead uses a convex branch mixture; do not apply
that description to the principal Allen-15 recipe.

## Repack without changing the operator

`changed = layout.repack(permutation)` makes new row `i` equal old row
`permutation[i]`. It transports coordinates and neighbor indices and rewrites
token references in blocks without changing canonical slots or coarse groups.
Invert the permutation before comparing outputs. The example
[repacking_equivariance.py](../examples/repacking_equivariance.py) checks both
outputs and gradients.

Calling `build_layout` with another layout name is different: raster blocks are
consecutive chunks of the requested volume, whereas native blocks follow the
coordinate shape. The resulting summary partitions can differ. Read
[the theory boundaries](theory.md) before treating that switch as an invariance
test.
