import fitz
import xml.etree.ElementTree as ET
from openai import OpenAI


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


def create_shortanswer_question(input_text, difficulty: str):
    message = input_text + ", Create a " + difficulty + " short answer question without its answer and I want this quesiton for a quiz and ignnore irrelevant information. I want you to return only the question not any other text around the question because I will add it into a database automatically."
    question = generate_response(message)
    response_parts = question.split(":", 1)
    if len(response_parts) > 1:
        question = response_parts[1].strip()
    else:
        response_parts = question.split("\n", 1)
        if len(response_parts) > 1:
            question = response_parts[1].strip()
    return question


def create_true_false_question(input_text, difficulty: str):
    message = input_text + ", Create a " + difficulty + " question"
    system_message = "You are an experienced teacher that generates quiz based on the text provided, Respond with a true/false question and answer based on the text provided. provide your answer in a json format like this {'Question': The question, 'Answer': The answer}."
    question = generate_response(message, system_message)

    return question


def generate_response(message):
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    completion = client.chat.completions.create(
        model="TheBloke/Llama-2-7B-Chat-GGUF",
        messages=[
            {
                "role":
                "system",
                "content":
                "You are an experienced teacher and you are creating a quiz for your students. You want to create a question based on the text you provided. The question should be relevant to the text and should depend on the difficulty level you specified. The response should consist of the question only"
            },
            {
                "role": "user",
                "content": message
            },
        ],
    )

    response = completion.choices[0].message.content
    return response
