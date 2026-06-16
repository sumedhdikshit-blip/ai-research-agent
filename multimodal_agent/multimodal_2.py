from dotenv import load_dotenv
import json
import base64
from pathlib import Path

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0)


def get_item_code(item_name: str) -> str:
    if item_name == "sari":
        return "ITM001"
    if item_name == "t-shirt":
        return "ITM002"
    if item_name == "jeans":
        return "ITM003"
    if item_name == "jacket":
        return "ITM004"
    return "ITM999"


def encode_image_to_data_url(path: Path) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


base_dir = Path(__file__).parent  # fixed: points to script's folder, not cwd
img1_url = encode_image_to_data_url(base_dir / "images" / "image1.jpg")
img2_url = encode_image_to_data_url(base_dir / "images" / "image2.jpg")
img3_url = encode_image_to_data_url(base_dir / "images" / "image3.jpg")


SYSTEM_PROMPT = """For each image return a JSON array of records. Each record must have:
    - item_name: one of sari, t-shirt, jeans, jacket
    - color: the dominant color of the clothing item
    - gender: male, female, or unisex
    - age_category: adult or child

Output only a raw JSON array. No preamble, no markdown, no code fences."""

human_content = [
    {"type": "text", "text": "Analyze each image and return a JSON array of records as instructed."},
    {"type": "image_url", "image_url": {"url": img1_url}},
    {"type": "image_url", "image_url": {"url": img2_url}},
    {"type": "image_url", "image_url": {"url": img3_url}},
]

response = llm.invoke([
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(content=human_content),
])

records = json.loads(response.content)

for record in records:
    record["item_code"] = get_item_code(record["item_name"])

print(json.dumps(records, indent=2))