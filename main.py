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

with open("prompt.json", "r") as f:
    PROMPTS = json.load(f)


def run_model(prompt, image_paths):
    uploaded = []

    for path in image_paths:
        with open(path, "rb") as f:
            obj = replicate.files.create(f)
            uploaded.append(obj.urls["get"])

    output = client.run(
        "black-forest-labs/flux-2-max",
        input={
            "prompt": prompt,
            "input_images": uploaded,
            "aspect_ratio": "1:1",
            "output_format": "webp",
            "output_quality": 100
        }
    )

    if isinstance(output, list):
        return output[0]

    return str(output)


def download(url, name):
    urllib.request.urlretrieve(url, name)
    return name


def generate_image(mode, image_paths, submode=None):

    results = []

    # TRYON
    if mode == "tryon":
        base = PROMPTS["tryon"]["prompt"]

        style_map = {
            "indian": PROMPTS["tryon"]["model_styles"]["indian_traditional"],
            "western": PROMPTS["tryon"]["model_styles"]["western_modern"],
            "bridal": PROMPTS["tryon"]["model_styles"]["bridal"]
        }

        prompt = base + "\n\n" + style_map.get(submode, "")

        url = run_model(prompt, image_paths)
        file = download(url, "output_tryon.webp")

        return [file]

    # REDESIGN (single variation)
    elif mode == "redesign":
        base = PROMPTS["redesign"]["system_instruction"]

        prompt = base + "\n\n" + PROMPTS["redesign"][submode]

        url = run_model(prompt, image_paths)
        file = download(url, f"output_redesign_{submode}.webp")

        return [file]

    # SOCIAL
    elif mode == "social":
        mapping = {
            "post": "instagram_post",
            "story": "instagram_story",
            "fb": "facebook"
        }

        key = mapping.get(submode, "instagram_post")

        prompt = PROMPTS["social"][key]

        url = run_model(prompt, image_paths)
        file = download(url, "output_social.webp")

        return [file]

    else:
        raise ValueError("Invalid mode")
