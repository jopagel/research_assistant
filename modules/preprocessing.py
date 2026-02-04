"""
Module for preprocessing data for the Research Assistant Chatbot.
"""
import re

def preprocess(data):
    """
    Cleans and tokenizes text data.
    Args:
        data (list): List of text samples.
    Returns:
        list: List of tokenized samples.
    """
    print("Preprocessing data...")
    processed = []
    for d in data:
        # Lowercase, remove punctuation, split into tokens
        clean = re.sub(r'[^\w\s]', '', d.lower())
        tokens = clean.split()
        processed.append(tokens)
    return processed
