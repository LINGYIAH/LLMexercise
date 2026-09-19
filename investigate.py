import json
import ollama
from parse_data import load_items, get_unclaimed_items, save_result

def build_prompt(description, available_items):
    """build system prompt and user prompt"""
    system_prompt = """You are a lost-and-found assistant. 
Rules:
- Use only the given JSON file.
- Not all details must match to be a possible match.
- Return ONLY JSON with exactly this structure:
{
    "matches": ["ITEM_ID"],
    "confidence": "LOW"
}
- "matches" contains all possible match IDs.
- "confidence" must be exactly one of: LOW, MEDIUM, HIGH.
- If no match, return an empty list."""

    user_prompt = f"""The user lost: {description}

Available items in the lost-and-found database:
{json.dumps(available_items, indent=2)}

Find all possible matches."""

    return system_prompt, user_prompt

def ask_qwen(system_prompt, user_prompt):
    """use Ollama's Qwen model"""
    response = ollama.chat(
    model="qwen3:4b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.message.content

def parse_response(response_text):
    """analyzeJSON"""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start != -1 and end != 0:
            return json.loads(response_text[start:end])
        return None

def validate_result(result, available_items):
    """legal or not legal"""
    if not isinstance(result, dict):
        return False
    if "matches" not in result or "confidence" not in result:
        return False
    if not isinstance(result["matches"], list):
        return False
    if result["confidence"] not in ("LOW", "MEDIUM", "HIGH"):
        return False
    valid_ids = {item["id"] for item in available_items}
    for match_id in result["matches"]:
        if match_id not in valid_ids:
            return False
    return True

def display_matches(result, available_items):
    """show the match solution"""
    print("\nMATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {result['confidence']}")
    
    if not result["matches"]:
        print("\nNo matches found.")
        return
    
    print("\nPossible matches:")
    for match_id in result["matches"]:
        for item in available_items:
            if item["id"] == match_id:
                print(f"\nID: {item['id']}")
                print(f"Item: {item['item']}")
                print(f"Color: {item['color']}")
                print(f"Location: {item['location']}")
                print(f"Date found: {item['date']}")
                break

def main():
    filename = "found_items.json"
    items = load_items(filename)
    unclaimed = get_unclaimed_items(items)
    
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    
    description = input("\nDescribe the item you lost: ")
    
    print("\nSearching for possible matches...")
    system_prompt, user_prompt = build_prompt(description, unclaimed)
    response = ask_qwen(system_prompt, user_prompt)
    result = parse_response(response)
    
    if result and validate_result(result, unclaimed):
        display_matches(result, unclaimed)
        save_result(result, "output/match_result.json")
        print("\nResult saved to output/match_result.json")
    else:
        print("\nError: Could not get a valid response from the model.")

if __name__ == "__main__":
    main()