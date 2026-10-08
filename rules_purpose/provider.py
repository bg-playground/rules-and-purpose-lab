"""Minimal optional Responses API adapter; no SDK or network needed offline."""
import json
import urllib.error
import urllib.request


class ProviderError(Exception):
    pass


def respond(model, instructions, payload, api_key):
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps({"model": model, "instructions": instructions,
                         "input": json.dumps(payload, ensure_ascii=False),
                         "store": False, "max_output_tokens": 3000}).encode(),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.load(response)
    except urllib.error.HTTPError as error:
        # Never persist raw error bodies or headers, which can include secrets.
        raise ProviderError(f"Provider HTTP {error.code}") from None
    except (urllib.error.URLError, OSError, ValueError):
        raise ProviderError("Provider connection or response decoding failed") from None
    if not isinstance(body, dict) or body.get("status") != "completed":
        raise ProviderError("Provider response was not completed")
    try:
        text = "".join(part["text"] for item in body.get("output", [])
                       if item.get("type") == "message"
                       for part in item.get("content", []) if part.get("type") == "output_text")
    except (TypeError, AttributeError, KeyError):
        raise ProviderError("Provider output structure was invalid") from None
    if not text.strip():
        raise ProviderError("Provider returned no usable text (possibly a refusal)")
    return text, {"requested_model": model, "returned_model": body.get("model"),
                  "response_id": body.get("id"), "usage": body.get("usage"),
                  "status": body["status"]}
