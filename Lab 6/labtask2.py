"""TASK 2: Split synthetic documents into chunks.
Run: python3 task2.py
"""

import re
from collections import Counter

# Recognize Unicode word-like tokens while keeping common contractions together.
WORD_PATTERN = re.compile(r"\w+(?:['\u2019]\w+)*", re.UNICODE)

# Three synthetic documents. Each one includes a policy rule and an exception.
BASE_DOCUMENTS = {
    "D1": "Library policy. Members may borrow five books for fourteen days. Renew once if nobody reserved the item. Exception: staff may extend a loan for accessibility needs, even if it is reserved.",
    "D2": "Password policy. Use a unique password and multi-factor authentication. Never share a one-time code. Exception: emergency accounts follow the approved incident procedure.",
    "D3": "Travel policy. Submit claims within thirty days with required receipts. Economy travel is the default. Exception: a director may approve a documented urgent booking outside the normal limit.",
}

# Extra text makes each synthetic document long enough for the lab requirement.
PADDING_SENTENCE = "Keep a clear record of decisions and consult the responsible team when guidance is uncertain."


def make_documents():
    """Extend each base document to 150 or more words."""
    documents = {}
    for doc_id, starting_text in BASE_DOCUMENTS.items():
        text = starting_text + " "
        while len(WORD_PATTERN.findall(text)) < 150:
            text += PADDING_SENTENCE + " "
        documents[doc_id] = text.strip()
    return documents


def word_windows(text, window_size=40, stride=10):
    """Return word windows and their start/end character positions.

    A 40-word window and a 10-word stride means adjacent windows overlap
    by 30 words. Character offsets point back into the original document.
    """
    word_matches = list(WORD_PATTERN.finditer(text))

    for first_word in range(0, len(word_matches), stride):
        window = word_matches[first_word:first_word + window_size]
        if not window:
            break

        start_char = window[0].start()
        end_char = window[-1].end()
        chunk_text = text[start_char:end_char]
        yield start_char, end_char, chunk_text

        # Do not create an extra empty/duplicate window after the final full one.
        if first_word + window_size >= len(word_matches):
            break


def sentence_windows(text, word_limit=40):
    """Keep whole sentences together when possible; split overlong sentences."""
    sentence_matches = re.finditer(r"[^.!?]+(?:[.!?]+|$)", text)
    current_sentences = []
    current_word_count = 0

    for match in sentence_matches:
        sentence = match.group().strip()
        if not sentence:
            continue

        # Find the real start of the sentence in the original document.
        sentence_start = match.start() + len(match.group()) - len(match.group().lstrip())
        sentence_word_count = len(WORD_PATTERN.findall(sentence))

        # If a single sentence is too long, flush the current group and split it.
        if sentence_word_count > word_limit:
            if current_sentences:
                start = current_sentences[0][0]
                end = current_sentences[-1][1]
                yield start, end, text[start:end].strip()
                current_sentences = []
                current_word_count = 0

            for local_start, local_end, chunk in word_windows(sentence, word_limit, word_limit):
                yield sentence_start + local_start, sentence_start + local_end, chunk

        # Start a new chunk if this sentence would exceed the word limit.
        elif current_word_count + sentence_word_count > word_limit:
            start = current_sentences[0][0]
            end = current_sentences[-1][1]
            yield start, end, text[start:end].strip()

            current_sentences = [(sentence_start, match.end())]
            current_word_count = sentence_word_count

        # Otherwise add the sentence to the current chunk.
        else:
            current_sentences.append((sentence_start, match.end()))
            current_word_count += sentence_word_count

    # Return the last group of sentences, if one remains.
    if current_sentences:
        start = current_sentences[0][0]
        end = current_sentences[-1][1]
        yield start, end, text[start:end].strip()


def show_chunks():
    documents = make_documents()
    print("Document word counts:", {
        doc_id: len(WORD_PATTERN.findall(text))
        for doc_id, text in documents.items()
    })

    # Compare fixed-size word chunks with sentence-aware chunks.
    for method_name, chunk_function in [
        ("word", word_windows),
        ("sentence", sentence_windows),
    ]:
        all_chunks = []

        for doc_id, text in documents.items():
            for number, (start, end, chunk_text) in enumerate(chunk_function(text), start=1):
                chunk_id = f"{doc_id}-{method_name[0].upper()}{number}"
                all_chunks.append((chunk_id, doc_id, start, end, chunk_text))

        # Repeated chunks can happen because the sample documents contain padding.
        counts = Counter(row[4] for row in all_chunks)
        repeated = sum(1 for count in counts.values() if count > 1)
        sizes = [len(WORD_PATTERN.findall(row[4])) for row in all_chunks[:5]]
        print(f"\n{method_name} chunks: {len(all_chunks)}")
        print("First chunk sizes:", sizes, "Repeated chunk texts:", repeated)

        # Show chunk ID, source document, character offsets, and a short preview.
        for chunk_id, doc_id, start, end, chunk_text in all_chunks[:2]:
            print(chunk_id, doc_id, f"characters {start}:{end}", repr(chunk_text[:70]))


def show_edge_cases():
    print("\nEdge cases (40-word window):")
    examples = [
        ("empty text", ""),
        ("short document", "Only a few words are here."),
        ("sentence longer than 40 words", " ".join(["word"] * 55) + "."),
    ]

    for label, text in examples:
        chunks = list(word_windows(text))
        sizes = [len(WORD_PATTERN.findall(chunk[2])) for chunk in chunks]
        print(label, "-> word counts per chunk:", sizes)


if __name__ == "__main__":
    show_chunks()
    show_edge_cases()
