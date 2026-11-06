"""Non-destructive, offline training with the corrected paper backend."""
import argparse
import os
import sys
from common import device_from_name, load_recipe, paper_modules, prepare_run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--output", required=True, help="new directory; existing paths are refused")
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    args = parser.parse_args()
    cfg = load_recipe(args.config)
    device = device_from_name(args.device)
    if device.type == "cpu" and cfg["model"].get("local_attention_backend") == "triton":
        raise ValueError("this recipe requires CUDA; use the explicit smoke recipe for CPU")
    cfg, output, path = prepare_run(cfg, args.manifest, args.data_root, args.output)
    _, trainer = paper_modules(cfg, device)
    os.chdir(output)
    sys.argv = ["paper_train", "--config", str(path), "--wandb-mode", "disabled"]
    return trainer.main()


if __name__ == "__main__":
    raise SystemExit(main())
