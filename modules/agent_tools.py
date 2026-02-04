"""
Agent tools for the Research Assistant Chatbot.

Each tool is a callable that performs a specific task:
- get_company_info: Retrieve company data from mock database
- mock_web_search: Simulate web search results
- translate_document: Translate text using LLM
- generate_document: Create formatted briefing documents
- security_filter: Redact sensitive information
"""
import random
from typing import Dict, List, Any, Union

from modules.config import SECURITY_CONFIG


# Mock company database
COMPANY_DATABASE: Dict[str, Dict[str, Any]] = {
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

# Mock web search results
WEB_SEARCH_RESULTS: Dict[str, List[str]] = {
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


def _clean_input(text: str) -> str:
    """Clean up input string by removing quotes and whitespace."""
    return text.strip().strip('"').strip("'")


def get_company_info(company_name: str) -> Dict[str, Any]:
    """
    Retrieve company information from mock internal database.
    
    Args:
        company_name: Name of the company to look up
        
    Returns:
        Dictionary containing company details
    """
    company_name = _clean_input(company_name)
    
    if company_name in COMPANY_DATABASE:
        return COMPANY_DATABASE[company_name]
    
    # Generate mock data for unknown companies
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


def mock_web_search(company_name: str) -> List[str]:
    """
    Simulate web search for public products and partnerships.
    
    Args:
        company_name: Name of the company to search
        
    Returns:
        List of search result headlines
    """
    company_name = _clean_input(company_name)
    
    if company_name in WEB_SEARCH_RESULTS:
        return WEB_SEARCH_RESULTS[company_name]
    
    return [
        f"{company_name} partners with Company X",
        f"{company_name} launches new product"
    ]


def translate_document(document: str, target_language: str) -> str:
    """
    Translate document to target language using LLM.
    
    Args:
        document: Text to translate
        target_language: Target language (e.g., "German", "French")
        
    Returns:
        Translated text
    """
    # Import here to avoid circular imports
    from modules.llm_utils import hf_llm_generate
    
    prompt = (
        f"Translate the following document to {target_language}. "
        f"Only output the translation, nothing else:\n\n{document}"
    )
    return hf_llm_generate(prompt)


def generate_document(template: str, content_dict: Dict[str, Any]) -> str:
    """
    Generate a formatted briefing document from template and content.
    
    Args:
        template: Template name (currently supports "briefing")
        content_dict: Dictionary of content to include
        
    Returns:
        Formatted document string
    """
    company_name = content_dict.get('company_name', 'Unknown')
    doc_parts = [f"=== COMPANY BRIEFING: {company_name} ===\n"]
    
    for key, value in content_dict.items():
        formatted_key = key.replace('_', ' ').title()
        if isinstance(value, list):
            doc_parts.append(f"{formatted_key}: {', '.join(str(v) for v in value)}")
        else:
            doc_parts.append(f"{formatted_key}: {value}")
    
    doc_parts.append("\n=== END OF BRIEFING ===")
    return "\n".join(doc_parts)


def security_filter(document: Union[str, Any]) -> str:
    """
    Filter sensitive terms from document.
    
    Args:
        document: Document to filter (will be converted to string)
        
    Returns:
        Filtered document with sensitive terms redacted
    """
    if not document:
        return "[ERROR: No document to filter]"
    
    doc_str = str(document)
    
    for term in SECURITY_CONFIG.sensitive_terms:
        doc_str = doc_str.replace(term, "[REDACTED]")
    
    return f"[SECURITY FILTERED]\n{doc_str}"
