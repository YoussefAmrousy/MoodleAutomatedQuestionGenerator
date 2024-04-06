import xml.etree.ElementTree as ET
from transformers import pipeline
import torch
import fitz
import sys
import os
from transformers import pipeline
import torch
import fitz  # PyMuPDF
import json
# ... (your existing code for question and answer generation) ...


def save_questions_to_xml(generated_question_answers, filepath):
    print("Executing the updated save_questions_to_xml function...")  # Diagnostic print
    
    root = ET.Element('quiz')
    
    for question, answer in generated_question_answers:
        print(f"Adding question: {question}")  # Diagnostic print
        
        question_element = ET.SubElement(root, 'question', type='shortanswer')
        
        name_element = ET.SubElement(question_element, 'name')
        ET.SubElement(name_element, 'text').text = question
        
        questiontext_element = ET.SubElement(question_element, 'questiontext', format='html')
        ET.SubElement(questiontext_element, 'text').text = f"<![CDATA[{question}]]>"
        
        answer_element = ET.SubElement(question_element, 'answer', fraction="100", format='moodle_auto_format')
        ET.SubElement(answer_element, 'text').text = answer
        
        ET.SubElement(question_element, 'generalfeedback', format='html').text = "<![CDATA[]]>"
        ET.SubElement(question_element, 'defaultgrade').text = "1.0000000"
        ET.SubElement(question_element, 'penalty').text = "0.3333333"
        ET.SubElement(question_element, 'hidden').text = "0"
        ET.SubElement(question_element, 'usecase').text = "0"

    tree = ET.ElementTree(root)
    tree.write(filepath + '.xml', encoding='utf-8', xml_declaration=True)
    print(f"XML file saved as {filepath}.xml")  # Diagnostic print




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
    print("Starting script...")  # Diagnostic print at the start
    if len(sys.argv) != 3:
        print("Usage: python generate_questions_script_path.py <file_path> <questionsNum>")
        sys.exit(1)

    file_path = sys.argv[1]
    questionsNum = int(sys.argv[2])

    print(f"Generating questions for: {file_path} with {questionsNum} questions.")  # Diagnostic print

    generated_question_answers = generate_questions(file_path, questionsNum)

    print("Generated question and answers, proceeding to save...")  # Diagnostic print
    
    save_questions_to_xml(generated_question_answers, "generated_questions")
