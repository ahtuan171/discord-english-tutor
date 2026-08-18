import json
import re


def extract_json(text: str):
    """Pull a JSON object/array out of an LLM response that may be wrapped in
    ```json fences or surrounded by extra prose, and parse it."""
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    candidate = fence_match.group(1) if fence_match else text

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    start_chars = "[{"
    for i, ch in enumerate(candidate):
        if ch in start_chars:
            for j in range(len(candidate), i, -1):
                chunk = candidate[i:j]
                try:
                    return json.loads(chunk)
                except json.JSONDecodeError:
                    continue
    raise ValueError(f"Could not extract JSON from LLM response: {text[:300]!r}")
