import urllib.request
import replicate
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = replicate.Client(
    api_token=os.getenv("REPLICATE_API_TOKEN"),
    timeout=180.0
)


# ---------- LOAD PROMPTS ----------
with open("prompt.json", "r") as f:
    PROMPTS = json.load(f)


# ---------- ASPECT RATIO MAPPING ----------
def get_aspect_ratio(mode, submode):
    if mode == "social":
        if submode == "instagrampost":
            return "1:1"
        elif submode == "instagramstory":
            return "9:16"
        elif submode == "facebook":
            return "1.91:1"

    # default
    return "1:1"


# ---------- PROMPT BUILDER ----------
def get_prompt(mode, submode=None):
    if mode == "tryon":
        base = PROMPTS["tryon"]["prompt"]

        # optional styling
        if submode and submode in PROMPTS["tryon"].get("model_styles", {}):
            style = PROMPTS["tryon"]["model_styles"][submode]
            return base + "\n\n" + style

        return base

    elif mode == "redesign":
        system = PROMPTS["redesign"]["system_instruction"]
        variation = PROMPTS["redesign"].get(submode, "")

        return system + "\n\n" + variation

    elif mode == "social":
        return PROMPTS["social"].get(submode, "")

    return ""


# ---------- GENERATE ----------
def generate_image(mode, image_paths, submode=None):
    """
    mode: tryon | redesign | social
    submode: depends on mode
    """

    prompt = get_prompt(mode, submode)
    aspect_ratio = get_aspect_ratio(mode, submode)

    uploaded_urls = []

    # Upload images
    for path in image_paths:
        with open(path, "rb") as f:
            file_obj = replicate.files.create(f)
            uploaded_urls.append(file_obj.urls["get"])

    outputs = []

    # Redesign → generate 4 separate images
    if mode == "redesign":
        for key in ["A", "B", "C", "D"]:
            var_prompt = get_prompt("redesign", key)

            output = client.run(
                "black-forest-labs/flux-2-max",
                input={
                    "prompt": var_prompt,
                    "input_images": uploaded_urls,
                    "aspect_ratio": "1:1",  # redesign always square
                    "output_format": "webp",
                    "output_quality": 100,
                }
            )

            file_path = f"result_{key}.webp"
            urllib.request.urlretrieve(str(output), file_path)
            outputs.append(file_path)

        return outputs

    # TryOn / Social → single output
    else:
        output = client.run(
            "black-forest-labs/flux-2-max",
            input={
                "prompt": prompt,
                "input_images": uploaded_urls,
                "aspect_ratio": aspect_ratio,  # 🔥 FIX HERE
                "output_format": "webp",
                "output_quality": 100,
            }
        )

        file_path = "result.webp"
        urllib.request.urlretrieve(str(output), file_path)

        return [file_path]
