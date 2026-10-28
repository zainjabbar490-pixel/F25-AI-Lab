"""TASK 3: Evaluate a document retrieval chatbot.
Run: python3 task3.py
Run with interactive questions: python3 task3.py --interactive
"""

import argparse
import math
import re
from collections import Counter

WORD_PATTERN = re.compile(r"\w+(?:['\u2019]\w+)*", re.UNICODE)

# Five synthetic policy documents, each with a rule and an exception.
BASE_DOCUMENTS = {
    "D1": ("Library policy", "Members may borrow up to five books for fourteen days. Renew once if nobody reserved the item. Exception: staff may extend a loan for accessibility needs, even if it is reserved."),
    "D2": ("Password policy", "Use unique passwords and multi-factor authentication. Never share a one-time code. Report suspected compromise immediately. Exception: emergency accounts follow the approved incident procedure."),
    "D3": ("Travel policy", "Submit claims within thirty days with lodging and transport receipts. Economy travel is the default. Exception: a director may approve a documented urgent booking outside the normal limit."),
    "D4": ("Data retention policy", "Project files are kept seven years after closure. Legal holds pause deletion until released. Exception: a longer statutory period overrides the standard schedule."),
    "D5": ("Support policy", "Critical incidents are acknowledged within one hour; routine requests within two business days. Include affected service and contact details. Exception: safety outages are escalated immediately by phone."),
}
PADDING_SENTENCE = "Keep a clear record of decisions and consult the responsible team when guidance is uncertain."

# The expected document ID is the manually assigned correct source.
# None means the question is unanswerable from this synthetic document set.
DEVELOPMENT_QUESTIONS = [
    ("How often can I renew a library book?", "D1"),
    ("What if my password is compromised?", "D2"),
    ("Which receipts are required for travel?", "D3"),
    ("Does policy cover solar panels?", None),
]
HELD_OUT_QUESTIONS = [
    ("When does deletion pause?", "D4"),
    ("How soon are critical support incidents acknowledged?", "D5"),
    ("Can accessibility needs change a library loan?", "D1"),
    ("What is the annual leave allowance?", None),
]


def make_documents():
    """Create documents with 150–200 words each for the exercise."""
    documents = {}
    for doc_id, (title, rule_and_exception) in BASE_DOCUMENTS.items():
        text = title + ". " + rule_and_exception + " "
        while len(WORD_PATTERN.findall(text)) < 150:
            text += PADDING_SENTENCE + " "
        documents[doc_id] = text.strip()
    return documents


def word_windows(text, window_size=40, stride=10):
    """Make 40-word windows, moving forward 10 words each time."""
    words = list(WORD_PATTERN.finditer(text))
    for start_index in range(0, len(words), stride):
        window = words[start_index:start_index + window_size]
        if not window:
            break
        start_char = window[0].start()
        end_char = window[-1].end()
        yield start_char, end_char, text[start_char:end_char]
        if start_index + window_size >= len(words):
            break


def sentence_windows(text, word_limit=40):
    """Group sentences up to 40 words; split any overlong sentence."""
    sentences = re.finditer(r"[^.!?]+(?:[.!?]+|$)", text)
    group = []
    group_size = 0

    for match in sentences:
        sentence = match.group().strip()
        if not sentence:
            continue
        start = match.start() + len(match.group()) - len(match.group().lstrip())
        size = len(WORD_PATTERN.findall(sentence))

        if size > word_limit:
            if group:
                first, last = group[0][0], group[-1][1]
                yield first, last, text[first:last].strip()
                group, group_size = [], 0
            # Offsets from word_windows are relative to this sentence.
            for a, b, chunk in word_windows(sentence, word_limit, word_limit):
                yield start + a, start + b, chunk
        elif group_size + size > word_limit:
            first, last = group[0][0], group[-1][1]
            yield first, last, text[first:last].strip()
            group = [(start, match.end())]
            group_size = size
        else:
            group.append((start, match.end()))
            group_size += size

    if group:
        first, last = group[0][0], group[-1][1]
        yield first, last, text[first:last].strip()


def build_chunks(documents, method):
    """Create chunk records with chunk ID, document ID, and source offsets."""
    chunk_function = word_windows if method == "word" else sentence_windows
    records = []
    for doc_id, text in documents.items():
        for number, (start, end, chunk_text) in enumerate(chunk_function(text), start=1):
            records.append({
                "id": f"{doc_id}-{method[0].upper()}{number}",
                "source": doc_id,
                "start": start,
                "end": end,
                "text": chunk_text,
            })
    return records


def make_tfidf_vectors(texts):
    """Build simple TF-IDF vectors using only Python's standard library."""
    term_counts = []
    for text in texts:
        words = [word.lower() for word in WORD_PATTERN.findall(text)]
        term_counts.append(Counter(words))

    # Document frequency: count how many chunks contain each word.
    document_frequency = Counter()
    for counts in term_counts:
        for word in counts:
            document_frequency[word] += 1

    total_chunks = len(term_counts)
    inverse_document_frequency = {
        word: math.log((total_chunks + 1) / (count + 1)) + 1
        for word, count in document_frequency.items()
    }

    def vectorize(counts):
        # TF-IDF = word frequency weight multiplied by inverse document frequency.
        vector = {}
        for word, count in counts.items():
            term_frequency = 1 + math.log(count)
            vector[word] = term_frequency * inverse_document_frequency.get(word, 0)

        # Normalize vector length so longer chunks do not automatically win.
        length = math.sqrt(sum(value * value for value in vector.values())) or 1
        return {word: value / length for word, value in vector.items()}

    vectors = [vectorize(counts) for counts in term_counts]
    return vectors, vectorize


def retrieve(question, chunks, tfidf_model):
    """Return the best matching chunk and its similarity score."""
    chunk_vectors, vectorize = tfidf_model
    question_words = [word.lower() for word in WORD_PATTERN.findall(question)]
    question_vector = vectorize(Counter(question_words))

    best_index = 0
    best_score = -1
    for index, chunk_vector in enumerate(chunk_vectors):
        # Cosine similarity is the dot product of normalized TF-IDF vectors.
        score = sum(value * chunk_vector.get(word, 0)
                    for word, value in question_vector.items())
        if score > best_score:
            best_index = index
            best_score = score

    return best_score, chunks[best_index]


def calculate_metrics(labeled_questions, chunks, tfidf_model, threshold):
    """Calculate precision, recall, and F1 for accepted retrieval results."""
    true_positive = false_positive = false_negative = 0

    for question, expected_doc in labeled_questions:
        score, result = retrieve(question, chunks, tfidf_model)
        accepted = score >= threshold
        correct_source = expected_doc is not None and result["source"] == expected_doc

        if accepted and correct_source:
            true_positive += 1
        elif accepted:
            # Includes wrong-document answers and accepted unanswerable questions.
            false_positive += 1
        elif expected_doc is not None:
            false_negative += 1

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return precision, recall, f1


def choose_threshold_on_development(chunks, tfidf_model):
    """Choose the threshold using development questions only, never held-out ones."""
    scores = [retrieve(question, chunks, tfidf_model)[0]
              for question, _ in DEVELOPMENT_QUESTIONS]
    possible_thresholds = sorted(set([0, max(scores) + 1] + scores))

    # Prefer the threshold with best development F1; on ties choose the higher one.
    return max(
        possible_thresholds,
        key=lambda value: (calculate_metrics(
            DEVELOPMENT_QUESTIONS, chunks, tfidf_model, value)[2], value)
    )


def compare_local_embeddings(documents):
    """Compare embeddings only when their package and model are already available."""
    try:
        from sentence_transformers import SentenceTransformer
        encoder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    except Exception:
        print("Optional embedding model not installed/cached; skipping that comparison.")
        return

    for method in ["word", "sentence"]:
        chunks = build_chunks(documents, method)
        # normalize_embeddings makes dot product equal cosine similarity.
        raw_vectors = encoder.encode(
            [chunk["text"] for chunk in chunks], normalize_embeddings=True
        )
        chunk_vectors = [
            {index: float(value) for index, value in enumerate(vector)}
            for vector in raw_vectors
        ]

        def embed_question(word_counts):
            # Convert the question's word counter back to text for the model.
            question_text = " ".join(
                word for word, count in word_counts.items() for _ in range(count)
            )
            vector = encoder.encode([question_text], normalize_embeddings=True)[0]
            return {index: float(value) for index, value in enumerate(vector)}

        embedding_model = (chunk_vectors, embed_question)
        threshold = choose_threshold_on_development(chunks, embedding_model)
        dev = calculate_metrics(DEVELOPMENT_QUESTIONS, chunks, embedding_model, threshold)
        test = calculate_metrics(HELD_OUT_QUESTIONS, chunks, embedding_model, threshold)
        print(f"{method.title()} chunks + embeddings; dev threshold={threshold:.3f}")
        print("Embedding development P/R/F1:", tuple(round(x, 2) for x in dev))
        print("Embedding held-out P/R/F1:", tuple(round(x, 2) for x in test))


def run_evaluation(interactive=False):
    documents = make_documents()
    print("Document word counts:", {
        doc_id: len(WORD_PATTERN.findall(text))
        for doc_id, text in documents.items()
    })

    sentence_setup = None
    for method in ["word", "sentence"]:
        chunks = build_chunks(documents, method)
        tfidf_model = make_tfidf_vectors([chunk["text"] for chunk in chunks])
        threshold = choose_threshold_on_development(chunks, tfidf_model)

        print(f"\n{method.title()} chunks + TF-IDF; chunks={len(chunks)}")
        print("Development threshold:", round(threshold, 3))
        dev = calculate_metrics(DEVELOPMENT_QUESTIONS, chunks, tfidf_model, threshold)
        test = calculate_metrics(HELD_OUT_QUESTIONS, chunks, tfidf_model, threshold)
        print("Development precision / recall / F1:", tuple(round(x, 2) for x in dev))
        print("Held-out precision / recall / F1:", tuple(round(x, 2) for x in test))
        print("Held-out questions were not used to tune the threshold.")

        if method == "sentence":
            sentence_setup = (chunks, tfidf_model, threshold)

    compare_local_embeddings(documents)
    print("\nThese numbers evaluate retrieval, not an answer-generating AI model.")
    print("A low match on an unanswerable question should be refused, not stated as fact.")
    print("FAQ matching suits a few fixed questions; document retrieval finds relevant passages in longer policies.")
    print("If an FAQ conflicts with a newer policy, check exceptions and use the current approved source.\n")

    if interactive and sentence_setup:
        run_interactive_chat(*sentence_setup)


def run_interactive_chat(chunks, tfidf_model, threshold):
    """Show a possible source, and do not assert it without user confirmation."""
    while True:
        question = input("Document question (type quit to stop): ").strip()
        if question.lower() == "quit":
            break
        if not question:
            print("Please enter a question.")
            continue

        score, result = retrieve(question, chunks, tfidf_model)
        if score < threshold:
            print("No reliable match. No answer asserted.")
            continue

        print("Possible source:", result["source"], "chunk:", result["id"])
        print("Character offsets:", result["start"], "to", result["end"])
        print("Text:", result["text"])
        confirmation = input("Is this the right current source? (y/n): ").strip().lower()
        if confirmation == "y":
            print("Use only the shown text; check its exception and current version.")
        else:
            print("No answer asserted. Please rephrase or ask a human.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive", action="store_true")
    options = parser.parse_args()
    run_evaluation(options.interactive)


if __name__ == "__main__":
    main()
