"""PACK3D: geometry-aware local-global attention over packed 3D token fields."""
from .attention import PACK3DAttention
from .geometry import Pack3DGeometry, TokenLayout, build_layout, prepare_geometry
from .reference import pack3d_reference
from .backends.triton.autograd import pack3d_streamed

__version__ = "0.1.0"
__all__ = ["PACK3DAttention", "Pack3DGeometry", "TokenLayout", "build_layout",
           "prepare_geometry", "pack3d_reference", "pack3d_streamed"]
