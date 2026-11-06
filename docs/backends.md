# Execution backends

## Choose explicitly

| Path | Included implementation | Intended use |
| --- | --- | --- |
| `reference` | Small differentiable PyTorch oracle | Teaching, CPU examples, numerical checks |
| `triton` | Staged pooling/local/global forward and explicit backward | Optional NVIDIA GPU execution of the principal contract |
| Paper backend | Frozen historical model and custom-local/SDPA-global execution | Published checkpoint and training-recipe compatibility |

The historical backend was used for the reported experiments. The new streamed
path was not. Switching paths is not evidence of a newly measured segmentation
score or speedup.

## Streamed contract

Projected Q and both key streams arrive rotated; values are unrotated. One
learned scalar-weighted fine atom is followed by a mean of valid fine summaries.
Both local and global attention use grouped-query heads. Fusion retains the
channel-scaled local residual and adds the gated, channel-scaled global output.

The kernels stream global online softmax, recompute probabilities and pooling
weights in backward, and accumulate reductions in FP32. Local K/V gradients use
reverse adjacency; global K/V gradients use bounded split-query partials. This
path does not store an `N x M` score matrix or an all-query `N x w x d` gathered
local-feature tensor and does not call SDPA. Geometry and split-reduction buffers
still consume memory. Multiple launches are used, not one whole-layer kernel.

Projections, RoPE, gates, normalization, outer residuals, and small final
reductions remain PyTorch operations. In the historical path, summary autograd
is separate and the global SDPA backend determines its allocation behavior.

## Support and validation

- CUDA FP32, FP16, and BF16; compute capability >= 8 is checked at entry.
- Head dimensions 16, 32, 64, 128; query-head count divisible by KV-head count.
- At most 64 canonical fine slots, 128 local and reverse neighbors, pool factor
  1..32, and bounded register/indexing budgets checked before launch.
- All tokens occur exactly once in the fine partition. Fine blocks may be empty;
  an entirely empty coarse group is rejected. All-masked local rows produce zero.
- First-order gradients only for the Triton path. No dropout, distributed
  validation, arbitrary branch-normalization variants, or selected-token branch.
- The historical adapter has a narrower contract: unpadded 3D, axial
  token-before-compression, principal residual fusion, and no auxiliary losses.

The measured development target is H200 with PyTorch 2.11.0+cu126 and Triton 3.6.0.
The hardware entry check is not a validation claim for every Ampere-or-newer GPU.
Validation covers outputs, every supported gradient, reference gradcheck,
repacking, historical-layer parity, optimizer steps, extreme finite logits,
masked and singleton cases, and CUDA memcheck. See the release's
[validation record](validation.md) for exact checks and remaining gaps.

The reference and low-precision kernels are not bitwise equal. Shared-device
timings are provisional. The benchmark script records its complete measured
scope and intentionally does not label its timings publication-quality.
