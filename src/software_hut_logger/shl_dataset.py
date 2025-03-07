import argparse
import json
from pathlib import Path

from datasets import load_dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_dir", type=str, default="example_dataset")
    parser.add_argument("--num_samples", type=int, default=-1)
    args = parser.parse_args()

    dataset = load_dataset("wmt14", "de-en", split="train")
    if not args.num_samples == -1:
        dataset = dataset.select(range(args.num_samples))

    dataset = dataset.to_list()

    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    save_file = save_dir / "example_train_dataset.jsonl"
    with open(save_file, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"Dataset saved to {save_file}")

if __name__ == "__main__":
    main()