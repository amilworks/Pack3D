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
weights in backward, and accumulate reductions in FP32. Indexed local K/V
gradients use reverse adjacency. Global K/V gradients use bounded split-query partials. This
path does not store an `N x M` score matrix or an all-query `N x w x d` gathered
local-feature tensor and does not call SDPA. Geometry and split-reduction buffers
still consume memory. Multiple launches are used, not one whole-layer kernel.

The public Triton layer rotates projected queries and keys directly into the
head-major layout consumed by attention. On 3D grids it shares a table of
sines and cosines indexed by axis coordinate across heads and projections.
Each FP32 table is at most 64 KiB. A process-wide cache retains up to 16 entries
across CUDA streams, keyed by stream (including device), axis sizes and pair allocation.
Repeated encoder blocks on the same stream reuse the table. Larger grids and packed
positions share just the frequencies and compute rotations on the fly. CUDA graph
capture builds its own replay-local data. Backward applies the inverse rotation. Both paths use
the same per-axis FP32 frequencies as the reference. Values pass through
without rotation.

Gradient-free execution skips the global branch output and both softmax
normalizers saved for backward. With gradients enabled, the global query
gradient is added directly to the local query gradient in its owning kernel.
Projections, gates, normalization, outer residuals, and final reductions use
PyTorch. The historical model retains its own rotary code and SDPA global path.

## Tiled local attention on vision grids

`build_layout` records when the local graph is a complete radius-one voxel
neighborhood. With FP16 or BF16 projections, `backend="triton"` processes
2 × 2 × 4 voxels together. The 16 queries share a halo of up to 96 key/value
positions. A coordinate mask selects each query's original neighbors, including at
faces, edges and corners. Backward reuses the same voxel coordinates and mask.
The fast path starts at 4,096 tokens and requires at least 2 × 2 × 4 voxels
along the corresponding axes. Raster order uses voxel strides directly. Other
orders use one additional 32-bit packed index per voxel. `layout.repack(p)`
composes that map with the permutation, preserving the local graph, canonical
fine slots and coarse groups. Returning to raster order recovers direct strides.

Use standard PyTorch autocast or convert the layer and input to the same
supported precision. Custom graphs from `prepare_geometry`, smaller or thinner
grids, other radii, and FP32 use indexed kernels. The tiled and indexed reductions
can round differently. [Numerical checks and H200 timings](../benchmarks/results/h200_vision_2026-11-18.md)

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
