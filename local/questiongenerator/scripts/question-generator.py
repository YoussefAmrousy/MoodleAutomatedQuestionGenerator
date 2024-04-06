import xml.etree.ElementTree as ET
import sys
from transformers import pipeline
import torch
import fitz  # PyMuPDF
import json
# ... (your existing code for question and answer generation) ...

def save_questions_to_xml(generated_question_answers: any, filepath: str):
    root = ET.Element('quiz')
    for question, answer in generated_question_answers:
        question_element = ET.SubElement(root, 'question', type='shortanswer')
        ET.SubElement(question_element, 'name').text = question
        ET.SubElement(question_element, 'questiontext', format='html').text = question
        ET.SubElement(question_element, 'answer', format='html').text = answer
    tree = ET.ElementTree(root)
    tree.write(filepath + '.xml', encoding='utf-8')

def extract_text_from_page(page: any):
    return page.get_text()

def file_to_text(filepath: str):
    text = ""
    with fitz.open(filepath) as pdf_document:
        num_pages = pdf_document.page_count

        for page_num in range(num_pages):
            page = pdf_document[page_num]
            text += extract_text_from_page(page)

    return text

def create_questions(input_text: str, questionsNum: int):
    question_generator = pipeline("text2text-generation", model="voidful/bart-eqg-question-generator")
    if len(input_text) <= 512:
        questions = question_generator(input_text, max_length=30, num_return_sequences=questionsNum, num_beams=10)
        created_questions = [question['generated_text'].strip().capitalize() for question in questions]
    else:
        text_segments = [input_text[i:i+512] for i in range(0, len(input_text), 512)]
        created_questions = []
        for segment in text_segments:
            questions = question_generator(segment, max_length=30, num_return_sequences=questionsNum, num_beams=10)
            for question in questions:
                created_questions.append(question['generated_text'].strip().capitalize())

            if len(created_questions) >= questionsNum:
                break
        
    return created_questions

def create_answer(input_text: str, question: str):
    qa_generator = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")
    qa_result = qa_generator(question=question, context=input_text)
    return qa_result['answer'].replace('\n', ' ').capitalize()


def generate_questions(filepath: str, questionsNum: int):
    input_text: str = file_to_text(filepath)

    questions = create_questions(input_text, questionsNum)
    question_answers_pairs = []
    for question in questions:
        answer = create_answer(input_text, question)
        question_answers_pairs.append((question, answer))

    question_answers_pairs = question_answers_pairs[:questionsNum]

    output_json = json.dumps(question_answers_pairs)
    print(output_json)
    
    return question_answers_pairs


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_questions_script_path.py <file_path> <questionsNum>")
        sys.exit(1)

    file_path = sys.argv[1]
    questionsNum = int(sys.argv[2])

    generated_question_answers = generate_questions(file_path, questionsNum)

    save_questions_to_xml(generated_question_answers, "generated_questions") # To save in the moodle question bank

