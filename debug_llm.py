# save as debug_llm.py and run: python debug_llm.py
from llm import get_llm_response

result = get_llm_response("Do you sell insurance plans?")
print(f"Answered: {result['answered']}")
print(f"Source: {result['source']}")
print(f"Answer: {result['answer']}")