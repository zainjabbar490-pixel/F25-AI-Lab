"""TASK 1: Tokenization and a small FAQ chatbot.
Run: python3 task1.py
Optional interactive FAQ: python3 task1.py --interactive
"""

import argparse
import math
import re
from collections import Counter

# Six kinds of text for the tokenization exercise.
# Unicode characters are written as escape codes so Windows terminals are safer.
EXAMPLES = [
    "Hello, world!",                         # punctuation
    "I can't believe it's working.",          # contraction
    "Email sara.test@example.com",            # email
    "https://example.org/page?q=1",           # URL
    "Good morning \U0001F600\U0001F44D\U0001F3FD\U0001F469\u200d\U0001F4BB",  # emoji
    "\u0627\u0644\u0633\u0644\u0627\u0645 \u0639\u0644\u06cc\u06a9\u0645\u060c \u0622\u067e \u06a9\u06cc\u0633\u06d2 \u06c1\u06cc\u06ba\u061f",  # Urdu
]

# A tiny FAQ: each question is paired with its answer.
FAQ = {
    "How do I reset my password?": "Use the reset link on the sign-in page.",
    "When is the library open?": "The library is open Monday to Saturday.",
    "How do I contact support?": "Use the support portal or email.",
}


def show_tokens():
    """Split each example into word-like pieces, punctuation, and emoji."""
    print("=== TOKENIZATION ===")

    # \w matches Unicode letters and numbers. The second part catches punctuation.
    token_pattern = re.compile(r"\w+(?:['\u2019]\w+)*|[^\w\s]", re.UNICODE)

    for text in EXAMPLES:
        tokens = token_pattern.findall(text)
        # ascii() prints Urdu/emoji as safe escape codes on limited terminals.
        print("Text:", ascii(text))
        print("Tokens:", ascii(tokens))
        print("Count:", len(tokens), "\n")

    # This is optional: the rest of the program works without tiktoken.
    try:
        import tiktoken
        encoder = tiktoken.get_encoding("cl100k_base")
        print("Optional model-token counts:", [len(encoder.encode(t)) for t in EXAMPLES])
    except ImportError:
        print("Optional model tokenizer is not installed; regex example still works.")

    print("Note: regex is not a complete multilingual tokenizer. It may split URLs and joined emoji differently from a model tokenizer.\n")


def faq_answer(user_question):
    """Return an exact answer, a suggested FAQ question, or a safe fallback."""
    # Convert words to lowercase so Password and password match.
    words = lambda text: re.findall(r"\w+", text.lower())

    # IDF: words that occur in fewer FAQ questions get a higher score.
    question_words = [set(words(question)) for question in FAQ]
    document_frequency = Counter(word for word_set in question_words for word in word_set)
    number_of_questions = len(FAQ)
    idf = {
        word: math.log((number_of_questions + 1) / (count + 1)) + 1
        for word, count in document_frequency.items()
    }

    cleaned_question = user_question.strip().lower()

    # Exact question match: answer directly.
    for question, answer in FAQ.items():
        if cleaned_question == question.lower():
            return "Exact answer: " + answer

    # Empty input should not be compared with FAQ questions.
    user_words = set(words(user_question))
    if not user_words:
        return "Please enter a question."

    # Find the FAQ question with the largest IDF-weighted word overlap.
    best_question = None
    best_score = 0
    for question in FAQ:
        overlap = user_words.intersection(words(question))
        score = sum(idf.get(word, 1) for word in overlap)
        if score > best_score:
            best_score = score
            best_question = question

    if best_question is None:
        return "Unsupported question; please contact support."

    # Do not give an answer to a non-exact question without confirmation.
    return "Did you mean '" + best_question + "'? Please confirm before I answer."


def show_faq(interactive=False):
    """Show an exact match, a suggestion, and an empty-input example."""
    print("=== IDF FAQ CHATBOT ===")
    for sample in ["How do I reset my password?", "I forgot my password", ""]:
        print("Question:", repr(sample))
        print("Reply:", faq_answer(sample), "\n")

    if interactive:
        while True:
            question = input("FAQ question (type quit to stop): ").strip()
            if question.lower() == "quit":
                break

            reply = faq_answer(question)
            print(reply)

            # Ask before returning an answer to a suggested, non-exact question.
            if reply.startswith("Did you mean"):
                confirmation = input("Use this suggested FAQ? (y/n): ").strip().lower()
                if confirmation == "y":
                    suggested = reply.split("'", 2)[1]
                    print(FAQ[suggested])
                else:
                    print("Okay. Please rephrase your question.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive", action="store_true")
    options = parser.parse_args()

    show_tokens()
    show_faq(options.interactive)


if __name__ == "__main__":
    main()
