"""Opt-in CUDA tests: PACK3D_TEST_CUDA=1 CUDA_VISIBLE_DEVICES=<authorized GPU>."""

import os

import pytest
import torch

from pack3d import (
    pack3d_reference, pack3d_streamed, prepare_geometry,
)


@pytest.fixture(scope="module")
def gpu():
    if os.environ.get("PACK3D_TEST_CUDA") != "1":
        pytest.skip("CUDA tests require explicit PACK3D_TEST_CUDA=1")
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not visible:
        pytest.fail("set CUDA_VISIBLE_DEVICES explicitly")
    if not torch.cuda.is_available():
        pytest.fail("explicit CUDA test requested but CUDA is unavailable")
    total = torch.cuda.get_device_properties(0).total_memory
    torch.cuda.set_per_process_memory_fraction(min(4 * 1024**3 / total, 0.5), 0)
    return torch.device("cuda:0")


def make_case(n=37, d=16, b=2, h=4, g=2, volume=4, pool=3,
              dtype=torch.float32, device="cpu", seed=18):
    gen = torch.Generator().manual_seed(seed)
    nb = torch.full((n, 5), -1, dtype=torch.int32)
    for i in range(n):
        edges = sorted({i, (i + 1) % n, max(i - 2, 0)})
        nb[i, :len(edges)] = torch.tensor(edges)
    nb[0] = -1  # All-masked local row and intentionally asymmetric graph.
    blocks = torch.full(((n + volume - 1) // volume, volume), -1, dtype=torch.int32)
    blocks.flatten()[:n] = torch.arange(n)
    geometry = prepare_geometry(nb, blocks, pool).to(device)
    shapes = [(b, h, n, d)] + [(b, g, n, d)] * 4 + [(d,), (volume,), (b, h, n), (d,), (d,)]
    inputs = []
    for index, shape in enumerate(shapes):
        t = torch.randn(shape, generator=gen) * (0.2 if index in (5, 6) else 0.5)
        if index == 7:
            t = t.sigmoid()
        if index == 8:
            t += 1
        if index == 9:
            t += 0.25
        inputs.append(t.to(device=device, dtype=dtype).requires_grad_())
    return inputs, geometry


def test_reference_gradcheck():
    inputs, geometry = make_case(n=3, b=1, h=1, g=1, volume=2, pool=2, dtype=torch.float64)
    assert torch.autograd.gradcheck(lambda *args: pack3d_reference(*args, geometry, temperature=0.7),
                                   tuple(inputs), fast_mode=True)


def test_geometry_guards():
    inputs, geometry = make_case()
    with pytest.raises(ValueError, match="partition"):
        prepare_geometry(geometry.neighbors, torch.zeros_like(geometry.blocks), 3)
    with pytest.raises(ValueError, match="out-of-range"):
        prepare_geometry(geometry.neighbors + 1000, geometry.blocks, 3)
    with pytest.raises(ValueError, match="CUDA"):
        pack3d_streamed(*inputs, geometry)
    geometry.blocks[0, 0] = 0
    with pytest.raises(RuntimeError, match="changed"):
        pack3d_reference(*inputs, geometry)


@pytest.mark.parametrize("dtype", [torch.float32, torch.float16, torch.bfloat16])
@pytest.mark.parametrize("shape", [(37, 16, 2, 4, 2, 4, 3), (131, 64, 1, 8, 2, 16, 2),
                                  (19, 32, 1, 2, 2, 3, 1), (21, 128, 1, 2, 1, 4, 4)])
def test_forward_and_every_gradient(gpu, dtype, shape):
    inputs, geometry = make_case(*shape, dtype=dtype, device=gpu)
    refs = [t.detach().clone().requires_grad_() for t in inputs]
    got = pack3d_streamed(*inputs, geometry, temperature=0.7)
    expected = pack3d_reference(*refs, geometry, temperature=0.7)
    torch.manual_seed(91)
    upstream = torch.randn_like(got)
    grads = torch.autograd.grad(got, inputs, upstream)
    ref_grads = torch.autograd.grad(expected, refs, upstream)
    tol = 3e-5 if dtype == torch.float32 else (0.005 if dtype == torch.float16 else 0.035)
    names = ["output", "q", "kl", "vl", "kg", "vg", "pool_weight", "slot_bias", "gate", "local_scale", "global_scale"]
    for name, actual, reference in zip(names, [got, *grads], [expected, *ref_grads]):
        assert torch.isfinite(actual).all(), name
        err = (actual.float() - reference.float()).norm() / reference.float().norm().clamp_min(1e-8)
        maxerr = (actual.float() - reference.float()).abs().max()
        print(f"{dtype} {shape} {name}: relative_L2={err.item():.6g} max_abs={maxerr.item():.6g}")
        assert err < tol, (name, err.item(), tol)
        if dtype == torch.float32:
            torch.testing.assert_close(actual, reference, atol=3e-5, rtol=3e-5)


def test_repacking_forward_and_gradients(gpu):
    inputs, geom = make_case(device=gpu)
    n = geom.num_tokens
    p = torch.randperm(n, generator=torch.Generator().manual_seed(3)).to(gpu)
    inv = torch.argsort(p)
    nb = geom.neighbors[p]
    nb = torch.where(nb >= 0, inv[nb.clamp_min(0)], -1)
    blocks = torch.where(geom.blocks >= 0, inv[geom.blocks.clamp_min(0)], -1)
    # Preserve canonical slots and both levels of summary membership.
    other = prepare_geometry(nb, blocks, geom.pool_size).to(gpu)
    transformed = [t.detach().clone() for t in inputs]
    for i in range(5):
        transformed[i] = inputs[i].detach()[:, :, p].contiguous()
    transformed[7] = inputs[7].detach()[:, :, p].contiguous()
    transformed = [t.requires_grad_() for t in transformed]
    y = pack3d_streamed(*inputs, geom)
    yp = pack3d_streamed(*transformed, other)
    torch.testing.assert_close(y, yp[:, :, inv], atol=3e-6, rtol=3e-6)
    dy = torch.randn_like(y)
    grads = torch.autograd.grad(y, inputs, dy)
    grads_p = torch.autograd.grad(yp, transformed, dy[:, :, p].contiguous())
    for i, (g, gp) in enumerate(zip(grads, grads_p)):
        if i < 5 or i == 7:
            gp = gp[:, :, inv]
        torch.testing.assert_close(g, gp, atol=3e-5, rtol=3e-5)


def test_strided_inputs_and_optimization(gpu):
    inputs, geom = make_case(n=67, device=gpu)
    # Same shapes, noncontiguous channel strides.
    inputs = [t.detach().repeat_interleave(2, -1)[..., ::2].requires_grad_() for t in inputs]
    assert not inputs[0].is_contiguous()
    opt = torch.optim.SGD(inputs, lr=0.01)
    initial = [t.detach().clone() for t in inputs]
    for _ in range(3):
        opt.zero_grad()
        loss = pack3d_streamed(*inputs, geom).float().square().mean()
        loss.backward()
        assert all(t.grad is not None and torch.isfinite(t.grad).all() for t in inputs)
        opt.step()
    assert all(not torch.equal(a, t) for a, t in zip(initial, inputs))


def test_multitile_multisplit_and_empty_fine_block(gpu):
    inputs, geom = make_case(n=2053, b=1, h=4, g=2, volume=8, pool=2, device=gpu)
    blocks = torch.cat((torch.full_like(geom.blocks[:1], -1), geom.blocks))
    geom = prepare_geometry(geom.neighbors, blocks, 2).to(gpu)
    refs = [t.detach().clone().requires_grad_() for t in inputs]
    y, yr = pack3d_streamed(*inputs, geom), pack3d_reference(*refs, geom)
    dy = torch.randn_like(y)
    ga, gb = torch.autograd.grad(y, inputs, dy), torch.autograd.grad(yr, refs, dy)
    torch.testing.assert_close(y, yr, atol=2e-5, rtol=2e-5)
    for a, b in zip(ga, gb):
        torch.testing.assert_close(a, b, atol=1e-4, rtol=1e-4)


@pytest.mark.parametrize("layout", ["raster_block", "native_block_morton"])
@pytest.mark.parametrize("precision", ["fp32", "mixed", "bf16"])
def test_existing_layer_outputs_and_parameter_gradients(gpu, layout, precision):
    import copy
    from hypernsa.attention.hypernsa_morton import HypergridMortonSparseAttention
    from hypernsa.attention.streamed_adapter import StreamedPACK3D

    torch.manual_seed(15)
    original = HypergridMortonSparseAttention(
        dim=64, grid_shape=(4, 4, 8), heads=4, kv_heads=2, dim_head=16,
        block_shape=(1, 2, 2), local_radius=1, num_summary_atoms=1,
        num_selected_blocks=0, layout=layout, separate_branch_kv=True,
        packed_branch_kv_projection=True, atom_assignment_mode="single_atom",
        enabled_branches=("local", "compressed"), branch_output_norm="none",
        branch_layer_scale=True, branch_layer_scale_init=(1., .25, 0.),
        branch_mixer_mode="local_residual_global", pos_encoding="axial_rope",
        coarse_summary_pool_size=4, coarse_attention_backend="sdpa",
    ).to(device=gpu, dtype=torch.bfloat16 if precision == "bf16" else torch.float32)
    candidate = StreamedPACK3D(copy.deepcopy(original))
    x = torch.randn(1, 4, 4, 8, 64, device=gpu, dtype=original.to_q.weight.dtype, requires_grad=True)
    xc = x.detach().clone().requires_grad_()
    with torch.autocast("cuda", dtype=torch.bfloat16, enabled=precision == "mixed"):
        y, yc = original(x), candidate(xc)
    dy = torch.randn_like(y)
    y.backward(dy)
    yc.backward(dy)
    tolerance = 4e-5 if precision == "fp32" else 0.035
    for name, a, b in [("output", y, yc), ("input grad", x.grad, xc.grad)]:
        err = (a - b).float().norm() / a.float().norm().clamp_min(1e-8)
        assert err < tolerance, (name, err.item())
    for (name, a), (_, b) in zip(original.named_parameters(), candidate.layer.named_parameters()):
        if a.grad is None or b.grad is None:
            assert a.grad is b.grad is None, name
        elif a.grad.norm() > 1e-7:
            err = (a.grad - b.grad).float().norm() / a.grad.float().norm()
            assert err < tolerance, (name, err.item())
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16, enabled=precision == "mixed"):
        assert torch.isfinite(candidate(x.detach())).all()
    candidate.layer.coarse_summary_pool_size = 2
    with pytest.raises(RuntimeError, match="layout"):
        candidate(x.detach())


def test_saved_state_is_linear_and_deterministic(gpu, monkeypatch):
    inputs, geom = make_case(n=2053, b=1, h=2, g=1, d=16, device=gpu)
    def forbidden(*args, **kwargs):
        raise AssertionError("new backend called SDPA")
    monkeypatch.setattr(torch.nn.functional, "scaled_dot_product_attention", forbidden)
    saved = []
    def record(t):
        saved.append(tuple(t.shape))
        return t
    with torch.autograd.graph.saved_tensors_hooks(record, lambda t: t):
        y = pack3d_streamed(*inputs, geom)
    assert len(saved) == 19
    assert all(not (geom.num_tokens in s and geom.num_summaries in s) for s in saved)
    dy = torch.randn_like(y)
    g1 = torch.autograd.grad(y, inputs, dy, retain_graph=True)
    g2 = torch.autograd.grad(y, inputs, dy)
    for a, b in zip(g1, g2):
        assert torch.equal(a, b)


def test_extreme_finite_logits_and_mixed_parameter_dtypes(gpu):
    inputs, geom = make_case(n=97, b=1, h=4, g=2, volume=16, pool=4, device=gpu)
    with torch.no_grad():
        for t in inputs[:3]:
            t.mul_(8)
        inputs[5].mul_(30)
    refs = [t.detach().clone().requires_grad_() for t in inputs]
    y = pack3d_streamed(*inputs, geom, temperature=.03)
    yr = pack3d_reference(*refs, geom, temperature=.03)
    dy = torch.randn_like(y)
    gs = torch.autograd.grad(y, inputs, dy)
    gr = torch.autograd.grad(yr, refs, dy)
    for a, b in zip([y, *gs], [yr, *gr]):
        assert torch.isfinite(a).all()
        torch.testing.assert_close(a, b, atol=2e-4, rtol=2e-4)


def test_adapter_rejects_unsupported_and_zero_gate(gpu):
    from hypernsa.attention.hypernsa_morton import HypergridMortonSparseAttention
    from hypernsa.attention.streamed_adapter import StreamedPACK3D
    layer = HypergridMortonSparseAttention(
        dim=16, grid_shape=(2, 2, 2), block_shape=(1, 1, 2), heads=1, kv_heads=1,
        dim_head=16, num_summary_atoms=1, atom_assignment_mode="single_atom",
        enabled_branches=("local", "compressed"), pos_encoding="axial_rope",
        branch_mixer_mode="local_residual_global",
    ).to(gpu)
    adapter = StreamedPACK3D(layer)
    layer.branch_output_norm = "per_branch_rmsnorm"
    with pytest.raises(ValueError, match="contract"):
        adapter(torch.randn(1, 8, 16, device=gpu))
    layer.branch_output_norm = "none"
    with torch.no_grad():
        layer.gate_proj.bias[0] = -1000
    with pytest.raises(RuntimeError, match="exact-zero"):
        adapter(torch.randn(1, 8, 16, device=gpu))


def test_mutated_saved_geometry_fails_backward(gpu):
    inputs, geom = make_case(device=gpu)
    y = pack3d_streamed(*inputs, geom)
    geom.neighbors[1, 0] = 1
    with pytest.raises(RuntimeError, match="changed"):
        y.sum().backward()


@pytest.mark.parametrize("dtype", [torch.float32, torch.float16, torch.bfloat16])
def test_singleton_summary_has_no_query_or_key_gradient(gpu, dtype):
    inputs, geom = make_case(n=1, b=1, h=1, g=1, volume=1, pool=1,
                             dtype=dtype, device=gpu)
    y = pack3d_streamed(*inputs, geom)
    grads = torch.autograd.grad(y, inputs, torch.randn_like(y))
    # Local row is empty; attention to exactly one summary is its value,
    # independent of any query, key, or pooling score.
    for index in (0, 1, 2, 3, 5, 6):
        assert torch.count_nonzero(grads[index]) == 0, (index, grads[index].abs().max().item())


@pytest.mark.parametrize("dtype", [torch.float32, torch.bfloat16])
def test_standalone_layer_and_repacked_layout(gpu, dtype):
    import copy
    from pack3d import PACK3DAttention, build_layout
    torch.manual_seed(52)
    layout = build_layout((4, 4, 4), pool_size=2).to(gpu)
    layer = PACK3DAttention(32, heads=2, kv_heads=1, head_dim=16, backend="triton").to(gpu, dtype)
    ref = copy.deepcopy(layer)
    ref.backend = "reference"
    x = torch.randn(1, 64, 32, device=gpu, dtype=dtype, requires_grad=True)
    xr = x.detach().clone().requires_grad_()
    y, expected = layer(x, layout), ref(xr, layout)
    upstream = torch.randn_like(y)
    actual_grads = torch.autograd.grad(y, (x, *layer.parameters()), upstream)
    expected_grads = torch.autograd.grad(expected, (xr, *ref.parameters()), upstream)
    tolerance = 3e-5 if dtype == torch.float32 else .035
    for a, b in zip([y, *actual_grads], [expected, *expected_grads]):
        error = (a.float() - b.float()).norm() / b.float().norm().clamp_min(1e-7)
        assert error < tolerance, error.item()
    p = torch.randperm(64)
    changed = layout.repack(p)
    with torch.no_grad():
        yp = layer(x[:, p], changed)[:, p.argsort()]
    torch.testing.assert_close(yp, y, rtol=tolerance, atol=tolerance)


def test_paper_backend_executes_requested_local_triton(gpu):
    from hypernsa.attention.hypernsa_morton import HypergridMortonSparseAttention
    layer = HypergridMortonSparseAttention(
        dim=32, grid_shape=(4, 4, 8), heads=2, kv_heads=1, dim_head=16,
        block_shape=(1, 2, 2), num_summary_atoms=1, num_selected_blocks=0,
        atom_assignment_mode="single_atom", enabled_branches=("local", "compressed"),
        pos_encoding="axial_rope", branch_mixer_mode="local_residual_global",
        branch_layer_scale=True, branch_layer_scale_init=(1., .25, 0.),
        local_attention_backend="triton", coarse_attention_backend="sdpa",
        coarse_summary_pool_size=4, use_triton_kernel=True, separate_branch_kv=True,
        packed_branch_kv_projection=True,
    ).to(gpu)
    x = torch.randn(1, 4, 4, 8, 32, device=gpu, requires_grad=True)
    y, aux = layer(x, return_aux=True)
    assert aux["local_attention_backend_actual"] == "triton_local"
    y.square().mean().backward()
    assert torch.isfinite(x.grad).all()
