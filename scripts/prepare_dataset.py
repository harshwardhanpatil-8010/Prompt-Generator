import json
import os
import random
from datasets import load_dataset

OUTPUT_DIR = "data/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

WEB_SIGHT_SAMPLES = 10000
VULCAN_SAMPLES = 4750
WEBUI_SAMPLES = 2000
FRONTEND_SAMPLES = 87

random.seed(42)

records = []


def add_record(instruction, response, source):
    if not instruction or not response:
        return

    instruction = str(instruction).strip()
    response = str(response).strip()

    if len(instruction) < 20:
        return

    if len(response) < 50:
        return

    records.append({
        "instruction": instruction,
        "response": response,
        "source": source
    })


def process_vulcan():
    dataset = load_dataset(
        "xlelords/vulcan",
        split="train",
        streaming=True
    )

    count = 0

    for item in dataset:
        if count >= VULCAN_SAMPLES:
            break

        messages = item.get("messages")

        if not messages:
            continue

        user_message = None
        assistant_message = None

        for message in messages:
            role = message.get("role")
            content = message.get("content", "")

            if role == "user" and user_message is None:
                user_message = content

            if role == "assistant":
                assistant_message = content

        if user_message and assistant_message:
            prompt = (
                "Transform the following frontend website requirement "
                "into a detailed implementation-ready prompt for an AI "
                "website generation agent.\n\n"
                f"Requirement:\n{user_message}"
            )

            add_record(
                prompt,
                assistant_message,
                "vulcan"
            )

            count += 1

    print(f"Vulcan processed: {count}")


def process_websight():
    dataset = load_dataset(
        "HuggingFaceM4/WebSight",
        split="train",
        streaming=True
    )

    count = 0

    for item in dataset:
        if count >= WEB_SIGHT_SAMPLES:
            break

        idea = item.get("llm_generated_idea")
        html = item.get("html") or item.get("text")

        if not idea or not html:
            continue

        prompt = (
            "Create a detailed website-generation specification "
            "from the following website idea. Infer the likely "
            "pages, sections, layout, components, functionality, "
            "responsive behavior, and visual requirements.\n\n"
            f"Website idea:\n{idea}"
        )

        response = (
            "Create a website based on this concept:\n\n"
            f"{idea}\n\n"
            "The implementation should reflect the structure, "
            "components, layout, styling, and functionality "
            "appropriate for this type of website."
        )

        add_record(
            prompt,
            response,
            "websight"
        )

        count += 1

    print(f"WebSight processed: {count}")


def process_webui():
    dataset = load_dataset(
        "xlelords/webui",
        split="train",
        streaming=True
    )

    count = 0

    for item in dataset:
        if count >= WEBUI_SAMPLES:
            break

        title = item.get("title")
        category = item.get("category")
        description = item.get("meta_description")
        elements = item.get("elements")
        colors = item.get("colors")
        fonts = item.get("fonts")

        if not title:
            continue

        prompt = (
            "Create a detailed website-generation prompt for "
            "the following website.\n\n"
            f"Title: {title}\n"
            f"Category: {category}\n"
            f"Description: {description}\n"
            f"UI Elements: {elements}\n"
            f"Colors: {colors}\n"
            f"Fonts: {fonts}"
        )

        response = (
            f"Create a {category or 'modern'} website titled "
            f"'{title}'.\n\n"
            f"Website description:\n{description or ''}\n\n"
            f"Use appropriate UI elements such as:\n"
            f"{elements or ''}\n\n"
            f"Use a coherent visual system with suitable colors "
            f"and typography."
        )

        add_record(
            prompt,
            response,
            "webui"
        )

        count += 1

    print(f"webui processed: {count}")


def process_frontend_coding():
    dataset = load_dataset(
        "Reubencf/frontend-coding",
        split="train",
        streaming=True
    )

    count = 0

    for item in dataset:
        if count >= FRONTEND_SAMPLES:
            break

        prompt_value = item.get("prompt")
        response_value = item.get("response") or item.get("code")

        if prompt_value and response_value:
            add_record(
                str(prompt_value),
                str(response_value),
                "frontend-coding"
            )

            count += 1

    print(f"frontend-coding processed: {count}")


process_vulcan()
process_websight()
process_webui()
process_frontend_coding()

random.shuffle(records)

seen = set()
deduplicated = []

for record in records:
    key = (
        record["instruction"].lower().strip(),
        record["response"].lower().strip()
    )

    if key in seen:
        continue

    seen.add(key)
    deduplicated.append(record)

random.shuffle(deduplicated)

total = len(deduplicated)

train_end = int(total * 0.9)
validation_end = int(total * 0.95)

train_data = deduplicated[:train_end]
validation_data = deduplicated[train_end:validation_end]
test_data = deduplicated[validation_end:]

with open(
    f"{OUTPUT_DIR}/train.jsonl",
    "w",
    encoding="utf-8"
) as file:
    for record in train_data:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

with open(
    f"{OUTPUT_DIR}/validation.jsonl",
    "w",
    encoding="utf-8"
) as file:
    for record in validation_data:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

with open(
    f"{OUTPUT_DIR}/test.jsonl",
    "w",
    encoding="utf-8"
) as file:
    for record in test_data:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

print("\nDataset complete")
print(f"Total: {total}")
print(f"Train: {len(train_data)}")
print(f"Validation: {len(validation_data)}")
print(f"Test: {len(test_data)}")
