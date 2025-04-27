import time
import traceback
from nltk.translate.bleu_score import sentence_bleu
from sklearn.metrics import f1_score
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Import your agents
from clerk_agent import ClerkAgent
from defendant_agent import DefendantAgent
from judge_agent import JudgeAgent
from lawyer_agent import LawyerAgent
from plaintiff_agent import PlaintiffAgent
from witness_agent import WitnessAgent

# Load a small language model for perplexity calculation
tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
model = GPT2LMHeadModel.from_pretrained("distilgpt2")
model.eval()

def calculate_perplexity(text):
    encodings = tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**encodings, labels=encodings["input_ids"])
    loss = outputs.loss
    return torch.exp(loss).item()

# Setup agent instances
judge_config = {"name": "Judge John Doe", "experience": "15 years", "specialization": "Civil Law"}
lawyer_config = {"name": "Lawyer Jane Smith", "experience": "10 years", "specialization": "Contract Law"}
witness_config = {"name": "Witness Alex Brown", "testimony": "I saw the defendant breach the contract on June 5th."}

agents = {
    "ClerkAgent": ClerkAgent(),
    "DefendantAgent": DefendantAgent(),
    "JudgeAgent": JudgeAgent(judge_config),
    "LawyerAgent": LawyerAgent(lawyer_config),
    "PlaintiffAgent": PlaintiffAgent(),
    "WitnessAgent": WitnessAgent(witness_config)
}

# Mock test contexts and reference outputs
test_contexts = {
    "ClerkAgent": {"phase": "evidence", "evidence_id": "101"},
    "DefendantAgent": {"phase": "opening"},
    "JudgeAgent": "An objection has been raised: hearsay.",
    "LawyerAgent": "Objection: leading the witness.",
    "PlaintiffAgent": {"phase": "opening"},
    "WitnessAgent": "What did you observe on the day of the incident?"
}

expected_outputs = {
    "ClerkAgent": "Evidence marked as Exhibit 101 for identification.",
    "DefendantAgent": "Your Honor, we dispute the plaintiff's claims.",
    "JudgeAgent": "The objection is sustained.",
    "LawyerAgent": "Objection, your honor, leading the witness.",
    "PlaintiffAgent": "Your Honor, this is a case of breach of contract.",
    "WitnessAgent": "I observed that the defendant failed to deliver the goods."
}

def simple_f1(reference: str, prediction: str) -> float:
    ref_tokens = reference.lower().split()
    pred_tokens = prediction.lower().split()
    common = set(ref_tokens) & set(pred_tokens)
    if not ref_tokens or not pred_tokens:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

# Evaluate each agent
results = {}

for name, agent in agents.items():
    start = time.time()
    try:
        if name == "JudgeAgent":
            response = agent.rule_on_objection(test_contexts[name])
        elif name == "LawyerAgent":
            response = agent.raise_objection(test_contexts[name])
        elif name == "WitnessAgent":
            response = agent.respond_to_question(test_contexts[name])
        else:
            response = agent.generate_response(test_contexts[name])
        success = True
    except Exception as e:
        response = traceback.format_exc()
        success = False
    end = time.time()

    reference = expected_outputs[name]
    bleu = sentence_bleu([reference.split()], response.split())
    f1 = simple_f1(reference, response)
    perplexity = calculate_perplexity(response) if success else float('inf')

    results[name] = {
        "success": success,
        "response": response,
        "time_taken_sec": round(end - start, 4),
        "bleu_score": round(bleu, 4),
        "f1_score": round(f1, 4),
        "perplexity": round(perplexity, 2)
    }

# Print evaluation results
print("\nDeep Evaluation Results:")
for agent_name, result in results.items():
    print(f"\nAgent: {agent_name}")
    print(f"Success: {result['success']}")
    print(f"Time Taken: {result['time_taken_sec']} sec")
    print(f"BLEU Score: {result['bleu_score']}")
    print(f"F1 Score: {result['f1_score']}")
    print(f"Perplexity: {result['perplexity']}")
    print(f"Response:\n{result['response']}")
