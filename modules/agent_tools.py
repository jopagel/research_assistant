"""
Agent tools for the Research Assistant Chatbot.
"""
import random

def get_company_info(company_name):
    """Simulate retrieval of company info from internal DB."""
    # Clean up company name (remove quotes if present)
    company_name = company_name.strip().strip('"').strip("'")
    
    # Mocked data with more realistic info
    company_data = {
        "Tesla": {
            "name": "Tesla",
            "industry": "Electric Vehicles & Clean Energy",
            "founded": "2003",
            "ceo": "Elon Musk",
            "headquarters": "Austin, Texas",
            "products": ["Model S", "Model 3", "Model X", "Model Y", "Cybertruck", "Powerwall"],
            "revenue": "$96.8 billion (2023)",
            "employees": "140,000+",
            "risk_category": "Medium"
        },
        "Apple": {
            "name": "Apple",
            "industry": "Consumer Electronics & Software",
            "founded": "1976",
            "ceo": "Tim Cook",
            "headquarters": "Cupertino, California",
            "products": ["iPhone", "iPad", "Mac", "Apple Watch", "AirPods"],
            "revenue": "$383 billion (2023)",
            "employees": "160,000+",
            "risk_category": "Low"
        }
    }
    
    if company_name in company_data:
        return company_data[company_name]
    
    # Default mock data for unknown companies
    return {
        "name": company_name,
        "industry": random.choice(["Automotive", "Tech", "Finance", "Healthcare"]),
        "founded": "Unknown",
        "ceo": "Unknown",
        "headquarters": "Unknown",
        "products": ["Product A", "Product B"],
        "revenue": "Unknown",
        "employees": "Unknown",
        "risk_category": random.choice(["Low", "Medium", "High"])
    }

def mock_web_search(company_name):
    """Simulate web search for public products/partnerships."""
    # Clean up company name (remove quotes if present)
    company_name = company_name.strip().strip('"').strip("'")
    
    search_results = {
        "Tesla": [
            "Tesla announces record Q4 deliveries of 484,000 vehicles",
            "Tesla partners with Panasonic for battery production",
            "Tesla Cybertruck production ramps up at Gigafactory Texas",
            "Tesla expands Supercharger network to 50,000 stations globally"
        ],
        "Apple": [
            "Apple launches Vision Pro mixed reality headset",
            "Apple partners with OpenAI for AI features in iOS",
            "Apple reports strong iPhone 15 sales in Q4",
            "Apple expands services revenue to record $85 billion"
        ]
    }
    
    if company_name in search_results:
        return search_results[company_name]
    
    return [f"{company_name} partners with Company X", f"{company_name} launches new product"]

from modules.llm_utils import hf_llm_generate

def translate_document(document, target_language):
    """Use LLM to translate document to target language."""
    prompt = f"Translate the following document to {target_language}. Only output the translation, nothing else:\n\n{document}"
    return hf_llm_generate(prompt)

def generate_document(template, content_dict):
    """Generate briefing document from template and content."""
    # Create a proper briefing document regardless of template name
    doc_parts = [f"=== COMPANY BRIEFING: {content_dict.get('company_name', 'Unknown')} ===\n"]
    
    for key, value in content_dict.items():
        # Format the key nicely
        formatted_key = key.replace('_', ' ').title()
        if isinstance(value, list):
            doc_parts.append(f"{formatted_key}: {', '.join(value)}")
        else:
            doc_parts.append(f"{formatted_key}: {value}")
    
    doc_parts.append("\n=== END OF BRIEFING ===")
    return "\n".join(doc_parts)

def security_filter(document):
    """Filter sensitive terms from document."""
    if not document:
        return "[ERROR: No document to filter]"
    
    # Convert to string if needed
    doc_str = str(document)
    
    sensitive_terms = ["Project Falcon", "Internal-Only", "Confidential", "SECRET"]
    for term in sensitive_terms:
        doc_str = doc_str.replace(term, "[REDACTED]")
    
    return f"[SECURITY FILTERED]\n{doc_str}"
