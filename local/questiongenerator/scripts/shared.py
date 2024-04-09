import fitz
import xml.etree.ElementTree as ET
import google.generativeai as genai

genai.configure(api_key='AIzaSyBPDvekJS5kzrsriJDktZCvAy-50ui5tuU')
model = genai.GenerativeModel('gemini-pro')


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


def save_questions_to_xml(generated_question_answers, filepath):
    root = ET.Element('quiz')

    for question, answer, difficulty in generated_question_answers:
        question_element = ET.SubElement(root, 'question', type='shortanswer')

        name_element = ET.SubElement(question_element, 'name')
        ET.SubElement(name_element, 'text').text = question

        questiontext_element = ET.SubElement(question_element,
                                             'questiontext',
                                             format='html')
        ET.SubElement(questiontext_element,
                      'text').text = f"<![CDATA[{question}]]>"

        answer_element = ET.SubElement(question_element,
                                       'answer',
                                       fraction="100",
                                       format='moodle_auto_format')
        ET.SubElement(answer_element, 'text').text = answer

        ET.SubElement(question_element, 'generalfeedback',
                      format='html').text = "<![CDATA[]]>"
        ET.SubElement(question_element, 'defaultgrade').text = "1.0000000"
        ET.SubElement(question_element, 'penalty').text = "0.3333333"
        ET.SubElement(question_element, 'hidden').text = "0"
        ET.SubElement(question_element, 'usecase').text = "0"

    tree = ET.ElementTree(root)
    tree.write(filepath + '.xml', encoding='utf-8', xml_declaration=True)


def check_difficulty(question: str, answer: str, difficulty: str):
    message = question + ", " + answer + ", Is this question " + str(
        difficulty
    ) + ", ANSWER WITH Yes or NO ONLY WITH NO WORDS BEFORE OR AFTER?"
    response = model.generate_content(message)
    if response.text == "Yes":
        return True
    return False

def is_question_relevant(question: str, text):
    message = question + ", " + text + ", Is this question relevant and can be used in an exam?, ANSWER WITH Yes or NO ONLY WITH NO WORDS BEFORE OR AFTER?"
    response = model.generate_content(message)
    if response.text == "Yes":
        return True
    return False
