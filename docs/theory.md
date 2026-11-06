# Theory and implementation contract

The mathematical statements concern a deterministic operator with transported
geometry. Numerical tests exercise the implementation; they do not replace the
proofs. The [method walkthrough](method.md) supplies a concrete small example.

## Relative geometry through compression

Let `R(c)` be the direct sum of axial planar rotations. Since rotations for each
pair add angles, $R(c_i)^\top R(c_u)=R(c_u-c_i)$. For nonnegative scalar effective
weights $A_{gu}$ summing to one over summary support $S_g$, define

$$\widetilde{k}_g^R=\sum_{u\in S_g} A_{gu}R(c_u)k_u,\qquad
\widetilde{v}_g=\sum_{u\in S_g} A_{gu}v_u.$$

Distributing the inner product through the first sum gives

$$ (R(c_i)q_i)^\top\widetilde{k}_g^R
=\sum_{u\in S_g} A_{gu}q_i^\top R(c_u-c_i)k_u. $$

For the implemented two-stage pool, $A_{gu}=a_{ju}/|J_g|$ when token `u` belongs
to fine block `j` in coarse group `g`; empty fine blocks are excluded from
$J_g$. This identity holds for the realized learned weights. Their dependence
on rotated content means the whole pooling rule need not be translation
equivariant. It also does not make compression lossless or summary softmax
equal to token-level dense softmax.

## Packing equivariance

Let $P$ permute token rows, $P_F$ permute fine summaries, and $P_S$ permute coarse
summaries. Transport coordinates and validity with the tokens, the local edges,
both summary memberships, and every canonical slot parameter. Require shared
tokenwise maps and a weight rule that re-enumerates weights with their members.
Then fine pooling $A_F$ and coarse pooling $C$ transform as

$$A_F'=P_F A_F P^\top,\qquad C'=P_S C P_F^\top.$$

Thus $A'=C'A_F'=P_S A P^\top$. Rotated keys and queries transform by token row
permutation, so

$$\widetilde K'=A'PK=P_S\widetilde K,\qquad
S'=PSP_S^\top.$$

Row softmax commutes with row/column permutations. Multiplication by the
similarly permuted summary values cancels $P_S$. Transported local edges yield
the same row-permutation property for local attention. Shared gates, channel
scales, projections, and residuals preserve it.

The weight **vector is equivariant** under member enumeration; the weighted
aggregate is invariant. Content dependence is allowed. An arbitrary in-memory
slot bias is not: the canonical slot must remain attached to its token. The
release's `TokenLayout.repack` preserves these identities explicitly. Random
masks, if introduced in another model, must also be transported or disabled.

Floating-point reduction order can introduce small differences. This theorem
is not a promise of bitwise equality or equality between models retrained under
different random schedules. Coordinate-indexed learned embeddings can satisfy
the same property; it is not unique to RoPE.

## Summary-center rotation

Holding the weights fixed, rotating a pooled key at center $\bar c_g$ instead
of rotating each token before pooling has scaled-logit error at most

$$\frac{\|q_i\|}{\sqrt{d_h}}
\sum_{u\in S_g} A_{gu}\|R(c_u)-R(\bar c_g)\|\|k_u\|.$$

Apply the triangle inequality and use orthogonality of $R(c_i)$ to obtain the
bound. The support is the final pooled summary, not just the fine block. A
different content-weight rule introduces an additional difference. Natural-data
experiments do not establish that exact token-before-compression is necessary
for every segmentation task.

## Complexity and boundaries

With `N` tokens, at most `w` local neighbors, `M` final summaries, query heads
$H_q$, KV heads $H_{kv}$, and head dimension $d_h$, attention and pooling work is

$$\Theta(H_qNwd_h)+\Theta(H_qNMd_h)+\Theta(H_{kv}Nd_h).$$

With fine volume `v` and coarse factor `p`, $M\simeq N/(vp)$. The global term is
reduced quadratic at fixed `v,p`. Streaming avoids storing all scores; it does
not remove their arithmetic. The release backend and the historical SDPA path
also have different memory contracts; see [backends.md](backends.md).
