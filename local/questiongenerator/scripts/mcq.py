import spacy
from PyPDF2 import PdfReader
import random
from collections import Counter

# Load English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def generate_mcqs_from_pdf(pdf_path, num_questions=5):
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Process the text with spaCy
    doc = nlp(text)

    # Extract sentences from the text
    sentences = [sent.text for sent in doc.sents]

    # Randomly select sentences to form questions
    selected_sentences = random.sample(sentences, min(num_questions, len(sentences)))

    # Initialize list to store generated MCQs
    mcqs = []

    # Generate MCQs for each selected sentence
    for sentence in selected_sentences:
        # Process the sentence with spaCy
        sent_doc = nlp(sentence)

        # Extract entities (nouns) from the sentence
        nouns = [token.text for token in sent_doc if token.pos_ == "NOUN"]

        # Ensure there are enough nouns to generate MCQs
        if len(nouns) < 2:
            continue

        # Count the occurrence of each noun
        noun_counts = Counter(nouns)

        # Select the most common noun as the subject of the question
        if noun_counts:
            subject = noun_counts.most_common(1)[0][0]

            # Generate the question stem
            question_stem = sentence.replace(subject, "__________")

            # Generate answer choices
            answer_choices = [subject]

            # Add some random words from the text as distractors
            for _ in range(3):
                distractor = random.choice(list(set(nouns) - set([subject])))
                answer_choices.append(distractor)

            # Shuffle the answer choices
            random.shuffle(answer_choices)

            # Append the generated MCQ to the list
            correct_answer = chr(64 + answer_choices.index(subject) + 1)  # Convert index to letter
            mcqs.append((question_stem, answer_choices, correct_answer))

    return mcqs

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python generate_mcqs_from_pdf.py <pdf_file_path> <num_questions>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    num_questions = int(sys.argv[2])

    mcqs = generate_mcqs_from_pdf(pdf_path, num_questions)

    print("Generated MCQs:")
    for i, mcq in enumerate(mcqs, start=1):
        question_stem, answer_choices, correct_answer = mcq
        print(f"Q{i}: {question_stem}?")
        for j, choice in enumerate(answer_choices, start=1):
            print(f"{chr(64+j)}: {choice}")
        print(f"Correct Answer: {correct_answer}\n")
