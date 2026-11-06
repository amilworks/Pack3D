# Corrections carried into the release

These changes are part of the scientific record, not just repository cleanup.

- **Packed RoPE:** the earlier control had no active rotary pairs. The paper
  reproduction wrapper assigns all pairs to sequence position and verifies a
  nonzero runtime transform. Corrected fixed-layout results do not establish
  axial superiority.
- **Summary permutations:** jointly permuting summary keys and values is a
  set-order invariance, not a destructive intervention. An earlier evaluator
  shared late-bound state across layers. That summary-order claim is withdrawn;
  corrected zeroing and cross-sample interventions establish branch dependence.
- **Threshold baseline:** the corrected intensity thresholds are fitted on
  training crops and evaluated on validation, rather than selected on validation.
- **Fusion and supervision:** Allen-15 uses a local residual with a gated global
  addend and full token-grid supervision. Earlier Allen-6 uses a convex mixer and
  a central target region. Their intervention magnitudes are not interchangeable.
- **Layout and summary counts:** principal Allen runs used `raster_block`.
  The nominal `(1,4,4)` block shape supplies volume 16 for raster strips, not
  native shaped blocks. Fine summaries are pooled again: 16,384 become 1,024.
- **Frequency allocation:** head dimension 64 uses balanced `(11,11,10)` pairs,
  not extent-proportional allocation.
- **Execution:** the historical code has separate summary autograd and SDPA
  global attention, not a single fused whole-operator backward. The optional
  explicit-backward release path is a newer implementation.
- **Scope:** fixed-layout natural-data nulls and the limited medical Dice
  consequences remain visible. Results support separating geometry from storage,
  not universal segmentation superiority or a universal sparse-attention speed law.

Private reviewer correspondence and internal discussion are not included.
