from transformers import pipeline
import torch
import xml.etree.ElementTree as ET
import sys
import fitz 
import json

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

def generate_true_false_questions(filepath, questionsNum):
    input_text = file_to_text(filepath)

    seed_value = hash(input_text) % (2**32 - 1)
    torch.manual_seed(seed_value)

    question_generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")
    qa_generator = pipeline("question-answering", model="deepset/roberta-base-squad2")

    generated_question_answers = []

    # Split the input text into smaller segments
    text_segments = [input_text[i:i + 512] for i in range(0, len(input_text), 512)]

    for segment in text_segments:
        num_beams = max(1, questionsNum // len(text_segments))

        questions = question_generator(
            segment,
            max_length=100,
            num_return_sequences=num_beams,
            num_beams=num_beams
        )
        for question in questions:
            question_text = question['generated_text'].strip().capitalize()
            qa_result = qa_generator(question=question_text, context=segment)
            answer = qa_result['answer'].strip().capitalize()
            is_true = answer.lower() in question_text.lower()
            generated_question_answers.append([question_text, is_true])

        if len(generated_question_answers) >= questionsNum:
            break

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
    
    generated_question_answers = generate_true_false_questions(file_path, questionsNum)
    save_questions_to_xml(generated_question_answers, "generated_true_false_questions")
   