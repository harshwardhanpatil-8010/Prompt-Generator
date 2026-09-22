from datasets import load_dataset

DATASETS = {
    "vulcan": "xlelords/vulcan",
    "websight": "HuggingFaceM4/WebSight",
    "webui": "xlelords/webui",
    "frontend_coding": "Reubencf/frontend-coding"
}

for name, dataset_id in DATASETS.items():
    print("\n" + "=" * 80)
    print(name.upper())
    print("=" * 80)

    try:
        dataset = load_dataset(
            dataset_id,
            split="train",
            streaming=True
        )

        first = next(iter(dataset))

        print("Columns:")
        print(list(first.keys()))

        print("\nExample:")
        for key, value in first.items():
            if isinstance(value, str):
                print(f"\n{key}:")
                print(value[:1000])
            else:
                print(f"\n{key}:")
                print(type(value))
                print(str(value)[:1000])

    except Exception as e:
        print(f"ERROR: {e}")







