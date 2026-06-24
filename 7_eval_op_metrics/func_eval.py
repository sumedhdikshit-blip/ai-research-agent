from langsmith import Client, evaluate, traceable
from inventory_agent import run
from utils import cosine_similarity
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


@traceable
def target(inputs: dict) -> dict:
    question = inputs["question"]
    answer = run(question)
    return {"answer": answer}


client = Client()
dataset_name = "inventorydata"

if not client.has_dataset(dataset_name=dataset_name):
    client.create_dataset(dataset_name=dataset_name)
    client.create_examples(
        dataset_name=dataset_name,
        examples=[
            {
                "inputs": {"question": "What is the stock status of iPhone 15?"},
                "outputs": {"answer": "The iPhone 15 is currently in stock with 50 units available."},
            },
            {
                "inputs": {"question": "Is AirPods Pro available?"},
                "outputs": {"answer": "AirPods Pro is not found in our inventory."},
            },
            {
                "inputs": {"question": "How many iPhone 15 units are available?"},
                "outputs": {"answer": "The iPhone 15 is currently in stock with 50 units available."},
            },
            {
                "inputs": {"question": "Do you have Samsung Galaxy S23?"},
                "outputs": {"answer": "Yes, Samsung Galaxy S23 is in stock with 30 units available."},
            },
            {
                "inputs": {"question": "Can you tell me the recipe of Vada Pav?"},
                "outputs": {"answer": "Sorry, I can only help with inventory related questions."},
            },
        ],
    )


def semantic_match(outputs: dict, reference_outputs: dict) -> dict:
    expected = reference_outputs["answer"]
    actual = outputs["answer"]
    score = cosine_similarity(expected, actual)
    return {
        "key": "semantic_match",
        "score": score
    }


evaluate(
    target,
    data=dataset_name,
    evaluators=[semantic_match],
    experiment_prefix="inventory_agent_eval_llama-3.1-8b",
    client=client,
)