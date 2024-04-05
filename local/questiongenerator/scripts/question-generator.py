import xml.etree.ElementTree as ET
import sys
from transformers import pipeline
import torch
import fitz  # PyMuPDF
import json
# ... (your existing code for question and answer generation) ...

def save_questions_to_xml(generated_question_answers, filepath):
    root = ET.Element('quiz')
    for question, answer in generated_question_answers:
        question_element = ET.SubElement(root, 'question', type='shortanswer')
        ET.SubElement(question_element, 'name').text = question
        ET.SubElement(question_element, 'questiontext', format='html').text = question
        ET.SubElement(question_element, 'answer', format='html').text = answer
    tree = ET.ElementTree(root)
    tree.write(filepath + '.xml', encoding='utf-8')


def extract_text_from_page(page):
    return page.get_text()

def file_to_text(filepath):
    text = ""
    with fitz.open(filepath) as pdf_document:
        num_pages = pdf_document.page_count

        for page_num in range(num_pages):
            page = pdf_document[page_num]
            text += extract_text_from_page(page)

    return text

def generate_questions(filepath, questionsNum):
    input_text = file_to_text(filepath)

    seed_value = hash(input_text) % (2**32 - 1)
    torch.manual_seed(seed_value)

    question_generator = pipeline("text2text-generation", model="t5-small")
    qa_generator = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

    generated_question_answers = []

    # If the input text is short, generate questions directly
    if len(input_text) <= 512:
        questions = question_generator(input_text, max_length=30, num_return_sequences=questionsNum, num_beams=10)
        for question in questions:
            question_text = question['generated_text'].strip().capitalize()
            qa_result = qa_generator(question=question_text, context=input_text)
            answer = qa_result['answer'].replace('\n', '').capitalize()
            generated_question_answers.append((question_text, answer))
    else:
        # Split the input text into smaller segments
        text_segments = [input_text[i:i+512] for i in range(0, len(input_text), 512)]

        for segment in text_segments:
            questions = question_generator(input_text, max_length=30, num_return_sequences=questionsNum, num_beams=10)
            for question in questions:
                question_text = question['generated_text'].strip().capitalize()
                qa_result = qa_generator(question=question_text, context=segment)
                answer = qa_result['answer'].replace('\n', '').capitalize()
                generated_question_answers.append((question_text, answer))

            # Break early if we've generated the desired number of questions
            if len(generated_question_answers) >= questionsNum:
                break

    # Trim the list if it exceeds the desired number of questions
    generated_question_answers = generated_question_answers[:questionsNum]

    output_json = json.dumps(generated_question_answers)
    print(output_json)
    
    return generated_question_answers


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_questions_script_path.py <file_path> <questionsNum>")
        sys.exit(1)

    file_path = sys.argv[1]
    questionsNum = int(sys.argv[2])

    # Call the generate_questions function and capture the returned value
    generated_question_answers = generate_questions(file_path, questionsNum)

    # Use the captured value in the save_questions_to_xml function call
    save_questions_to_xml(generated_question_answers, "generated_questions")

