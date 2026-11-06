"""Explicit first-order backward, without dense or SDPA fallback."""
import os
import torch
from torch.autograd.function import once_differentiable
from ...geometry import Pack3DGeometry
from ..._validation import _validate_inputs

class _Pack3D(torch.autograd.Function):
    @staticmethod
    def forward(ctx, q, kl, vl, kg, vg, weight, bias, gate, sl, sg, geometry, temperature):
        from . import kernels

        inputs = tuple(t.contiguous() for t in (q, kl, vl, kg, vg, weight, bias, gate, sl, sg))
        output, saved = kernels.forward(*inputs, geometry, temperature)
        ctx.save_for_backward(*inputs, *saved, *geometry.tensors)
        ctx.geometry, ctx.temperature = geometry, temperature
        return output

    @staticmethod
    @once_differentiable
    def backward(ctx, dout):
        from . import kernels

        ctx.geometry.check_unmodified()
        saved = ctx.saved_tensors
        grads = kernels.backward(dout.contiguous(), saved[:10], saved[10:-3],
                                 ctx.geometry, ctx.temperature)
        return (*grads, None, None)


def pack3d_streamed(q, kl, vl, kg, vg, weight, bias, gate, sl, sg,
                   geometry: Pack3DGeometry, *, temperature=1.0, backend="triton"):
    """Local-residual/global-gated one-atom PACK3D, including learned pooling.

    ``gate`` is the already computed global branch gate. Scales have shape
    [head_dim] and are shared over heads, matching the Allen-15 implementation.
    Unsupported inputs raise; no dense, CPU, or SDPA fallback is implicit.
    Higher-order gradients, dropout, and selected-token refinement are excluded.
    """
    _validate_inputs(q, kl, vl, kg, vg, weight, bias, gate, sl, sg, geometry, temperature)
    if backend == "interpret":
        if os.environ.get("TRITON_INTERPRET") != "1" or q.device.type != "cpu" or q.dtype != torch.float32:
            raise ValueError("interpret requires TRITON_INTERPRET=1 and CPU fp32 inputs")
    elif backend == "triton":
        if os.environ.get("TRITON_INTERPRET") == "1":
            raise ValueError("interpreter mode cannot attest a CUDA backend")
        if q.device.type != "cuda" or q.dtype not in (torch.float32, torch.float16, torch.bfloat16):
            raise ValueError("triton backend requires CUDA fp32/fp16/bf16 Q/K/V")
        if torch.cuda.get_device_capability(q.device)[0] < 8:
            raise ValueError("this backend targets Ampere or newer NVIDIA GPUs")
    else:
        raise ValueError(f"unknown explicit backend {backend!r}")
    return _Pack3D.apply(q, kl, vl, kg, vg, weight, bias, gate, sl, sg, geometry, float(temperature))


