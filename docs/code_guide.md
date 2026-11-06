# Reading the code

Read the core in this order. The wheel installs only `src/pack3d`; experiment
scripts and the frozen historical namespace are not imported by the core.

| Mathematical object | Implementation | Regression coverage |
| --- | --- | --- |
| Field, packing, local graph, canonical slots | [geometry.py](../src/pack3d/geometry.py): `build_layout`, `TokenLayout.repack` | [test_geometry.py](../tests/test_geometry.py) |
| Axial coordinate rotation | [rope.py](../src/pack3d/rope.py): `axial_rope` | [test_rope.py](../tests/test_rope.py) |
| Learned fine weights and coarse mean | [compression.py](../src/pack3d/compression.py): `compress_summaries` | [test_compression.py](../tests/test_compression.py) |
| Exact local softmax, summary softmax, fusion | [reference.py](../src/pack3d/reference.py): `pack3d_reference` | [test_reference.py](../tests/test_reference.py), reference gradcheck in [test_triton.py](../tests/test_triton.py) |
| Projections, normalization, gate, outer residual | [attention.py](../src/pack3d/attention.py): `PACK3DAttention` | [test_repacking.py](../tests/test_repacking.py) |
| Explicit streamed backward | [autograd.py](../src/pack3d/backends/triton/autograd.py), [kernels.py](../src/pack3d/backends/triton/kernels.py) | [test_triton.py](../tests/test_triton.py) |

`Pack3DGeometry` validates neighbor and block indices once on CPU. `-1` is padding;
no token may be missing or duplicated in the fine partition. Reverse adjacency
supports race-free local key/value gradients. Tensor-version checks detect
ordinary in-place metadata mutations before execution and backward.

`TokenLayout` adds coordinates and pack/unpack operations for complete unpadded
3D grids. Its builder requires divisibility by block shape. The lower-level
geometry API supports ragged and empty fine blocks under the documented limits.
Do not mutate metadata through `.data` or external storage aliases; those can
bypass PyTorch's version counters.

The reference deliberately materializes small intermediate tensors and keeps
FP64 for gradcheck. It is a correctness oracle, not a benchmark implementation.
The optimized kernel does not call the reference. Backend choice is explicit:
`reference` or `triton`; no automatic dense fallback is allowed.

The cleaned layer uses two active gate outputs and four K/V projections. The
historical layer contains inactive selected-branch parameter slots as well.
Their state-dict namespaces and parameter inventories are therefore different;
do not directly load a historical checkpoint into `PACK3DAttention`. Use
[the paper reproduction path](../reproduce/README.md) and its optional
[streamed adapter](../reproduce/paper_backend/hypernsa/attention/streamed_adapter.py).
The adapter retains original parameter objects and adds a `layer.` state-dict
prefix. Load the original checkpoint before wrapping.
