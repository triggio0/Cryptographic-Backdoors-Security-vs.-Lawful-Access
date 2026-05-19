import argparse
import json
from pathlib import Path

from src.loader import load_json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=False, help="Input directory", default="technical-project/input")
    parser.add_argument("--output", required=False, help="Output JSON file", default="technical-project/output.json")
    return parser.parse_args()

def main():
    args = parse_args()
    input_dir = Path(args.input)

    subjects = load_json(input_dir / "subjects.json")
    resources = load_json(input_dir / "resources.json")
    policies = load_json(input_dir / "policies.json")
    requests = load_json(input_dir / "requests.json")

    print(subjects)
    print(resources)
    print(policies)
    print(requests)

    result = {} # evaluate_requests

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()