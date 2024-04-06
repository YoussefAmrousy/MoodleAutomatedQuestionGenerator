import xml.etree.ElementTree as ET
import sys
from transformers import pipeline
import fitz
import json
import google.generativeai as genai

genai.configure(api_key='AIzaSyBPDvekJS5kzrsriJDktZCvAy-50ui5tuU')
model = genai.GenerativeModel('gemini-pro')
generated_question_answers = []

def save_questions_to_xml(generated_question_answers, filepath):
    
    root = ET.Element('quiz')
    
    for question, answer, difficulty in generated_question_answers:        
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

def create_questions_shortanswer(input_text: str, questionsNum: int, question_generator_pipeline: any):
    if len(input_text) <= 512:
        questions = question_generator_pipeline(input_text, max_length=30, num_return_sequences=questionsNum, num_beams=10)
        created_questions = [question['generated_text'].strip().capitalize() for question in questions]
    else:
        text_segments = [input_text[i:i+512] for i in range(0, len(input_text), 512)]
        created_questions = []
        for segment in text_segments:
            questions = question_generator_pipeline(segment, max_length=30, num_return_sequences=questionsNum, num_beams=10)
            for question in questions:
                created_questions.append(question['generated_text'].strip().capitalize())

            if len(created_questions) >= questionsNum:
                break
        
    return created_questions

def create_answer(input_text: str, question: str, question_answer_pipeline: any):
    qa_result = question_answer_pipeline(question=question, context=input_text)
    return qa_result['answer'].replace('\n', ' ').capitalize()

def generate_questions(filepath: str, questionsNum: int, difficulty):
    input_text: str = file_to_text(filepath)

    question_generator_pipeline = pipeline("text2text-generation", model="voidful/bart-eqg-question-generator")
    question_answer_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

    questions = create_questions_shortanswer(input_text, questionsNum, question_generator_pipeline)
    for question in questions:
        answer = create_answer(input_text, question, question_answer_pipeline)
        check_difficulty(question, answer, difficulty)

    output_json = json.dumps(generated_question_answers)
    print(output_json)
    
    return generated_question_answers

def check_difficulty(question: str, answer: str, difficulty: str):
    response = model.generate_content(question + " " + answer + " Is this question " + difficulty + ", ANSWER WITH Yes or NO ONLY WITH NO WORDS BEFORE OR AFTER?")
    if response.text == "Yes":
        generated_question_answers.append((question, answer, difficulty))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_questions_script_path.py <file_path> <questionsNum> <difficulty>")
        sys.exit(1)

    file_path = sys.argv[1]
    questionsNum = int(sys.argv[2])
    difficulty = sys.argv[3]

    generated_question_answers = generate_questions(file_path, questionsNum, difficulty)

    save_questions_to_xml(generated_question_answers, "generated_questions") # To save in the moodle question bank

