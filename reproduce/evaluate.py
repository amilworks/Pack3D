"""Full-validation evaluation of a supplied, tensor-only paper checkpoint."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import torch
from common import clean_evaluation, create_model, device_from_name, load_recipe, paper_modules, prepare_run


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    interventions = parser.add_mutually_exclusive_group()
    interventions.add_argument("--layout", choices=("raster_block", "native_block_morton"))
    interventions.add_argument("--pure-repack-seed", type=int)
    args = parser.parse_args()
    cfg = load_recipe(args.config)
    state = torch.load(Path(args.checkpoint).resolve(), map_location="cpu", weights_only=True)
    if not isinstance(state, dict) or not isinstance(state.get("model"), dict):
        raise ValueError("checkpoint must contain a model state dict")
    trained = state.get("config", {}).get("model")
    if trained is None or any(trained.get(k) != v for k, v in cfg["model"].items()):
        raise ValueError("recipe/model contract differs from the checkpoint's training config")
    device = device_from_name(args.device)
    cfg, output, _ = prepare_run(cfg, args.manifest, args.data_root, args.output)
    attention, trainer = paper_modules(cfg, device)
    _, val, meta = trainer.make_loaders(cfg)
    cfg["training"]["eval_batches"] = len(val)
    original_layout = attention.make_block_layout
    changed_cfg = deepcopy(cfg)
    if args.layout:
        changed_cfg["model"]["layout"] = args.layout
    if args.pure_repack_seed is not None:
        from repack import permute_coarse_groups
        pool = int(cfg["model"]["coarse_summary_pool_size"])
        def changed_layout(*a, **kw):
            return permute_coarse_groups(original_layout(*a, **kw), pool,
                                         permutation_seed=args.pure_repack_seed)
        attention.make_block_layout = changed_layout
    try:
        model = create_model(changed_cfg, meta, trainer, device)
    finally:
        attention.make_block_layout = original_layout
    model.load_state_dict(state["model"], strict=True)
    result = clean_evaluation(trainer.evaluate(model, val, device, changed_cfg, int(meta["num_classes"])))
    result.update({"validation_cases": len(val.dataset), "seed": cfg.get("seed"),
                   "checkpoint_step": state.get("step"), "layout": changed_cfg["model"]["layout"],
                   "training_layout": cfg["model"]["layout"],
                   "pure_repack_seed": args.pure_repack_seed, "retraining": False,
                   "checkpoint_sha256": sha256_file(args.checkpoint),
                   "recipe_sha256": sha256_file(args.config),
                   "manifest_sha256": sha256_file(args.manifest)})
    (output / "metrics.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
