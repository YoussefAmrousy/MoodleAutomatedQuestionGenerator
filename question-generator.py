from transformers import pipeline
import torch
import fitz

def file_to_text(file):
    text = ""
    with fitz.open(file) as pdf_document:
        num_pages = pdf_document.page_count

        for page_num in range(num_pages):
            page = pdf_document[page_num]
            text += page.get_text()

    return text

def generate_questions(file):
    input_text = file_to_text(file)

    seed_value = hash(input_text) % (2**32 - 1)
    torch.manual_seed(seed_value)

    question_generator = pipeline("text2text-generation", model="voidful/bart-eqg-question-generator")
    qa_generator = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")
    
    questions = question_generator(input_text, max_length=100, num_return_sequences=1)
    generated_questions = [question['generated_text'].strip() for question in questions]

    generated_question_answers = []
    for generated_question in generated_questions:
        qa_result = qa_generator(question=generated_question, context=input_text)
        answer = qa_result['answer']
        generated_question_answers.append((generated_question, answer))

    return generated_question_answers
