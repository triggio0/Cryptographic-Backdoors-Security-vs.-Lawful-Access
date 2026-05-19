import argparse
import json
from pathlib import Path

from src.loader import load_json
from src.engine import evaluate_requests

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input directory")
    parser.add_argument("--output", required=False, help="Output JSON file", default="output/output.json")
    return parser.parse_args()

def main():
    args = parse_args()
    input_dir = Path(args.input)

    try:
        subjects = load_json(input_dir / "subjects.json")
        resources = load_json(input_dir / "resources.json")
        policies = load_json(input_dir / "policies.json")
        requests = load_json(input_dir / "requests.json")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except ValueError as e:
        print(f"Error: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
        return


    subject_map = {s["id"]: s for s in subjects["subjects"]}
    resource_map = {r["id"]: r for r in resources["resources"]}

    result = evaluate_requests(
        requests["requests"],
        subject_map,
        resource_map,
        policies["policies"]
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Done. Results written to {output_path}")


if __name__ == "__main__":
    main()