import json

def parse_llm_response(response_text: str) -> dict:
    """
    Parse the LLM response and extract answer and citations
    """
    try:
        # Try to parse as JSON first
        if response_text.strip().startswith('{'):
            import json
            parsed = json.loads(response_text)
            return {
                'answer': parsed.get('answer', response_text),
                'citations': parsed.get('citations', [])
            }
        
        # If not JSON, return as plain text
        return {
            'answer': response_text,
            'citations': []
        }
        
    except Exception as e:
        # If parsing fails, return the original text
        return {
            'answer': response_text,
            'citations': []
        }
