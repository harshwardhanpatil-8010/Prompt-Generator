import json
import os

FILES = [
    "data/processed/train.jsonl",
    "data/processed/validation.jsonl",
    "data/processed/test.jsonl"
]

for filename in FILES:
    print("\n" + "=" * 60)
    print(filename)
    print("=" * 60)

    if not os.path.exists(filename):
        print("File does not exist")
        continue

    count = 0
    invalid = 0

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            try:
                record = json.loads(line)

                if (
                    "instruction" not in record
                    or "response" not in record
                    or not record["instruction"]
                    or not record["response"]
                ):
                    invalid += 1

                count += 1

            except json.JSONDecodeError:
                invalid += 1

    print(f"Examples: {count}")
    print(f"Invalid: {invalid}")
