import os
import sys
import json
import xml.etree.ElementTree as ET

def save_questions_to_xml(generated_question_answers):
    root = ET.Element('quiz')

    for question_data in generated_question_answers:
        question_element = ET.SubElement(root, 'question', type='shortanswer')

        name_element = ET.SubElement(question_element, 'name')
        ET.SubElement(name_element, 'text').text = question_data['question']

        questiontext_element = ET.SubElement(question_element, 'questiontext', format='html')
        ET.SubElement(questiontext_element, 'text').text = f"<![CDATA[{question_data['question']}]]>"

        if question_data['type'] == 'Multiple Choice':
            for option in question_data['options']:
                answer_element = ET.SubElement(question_element, 'answer', fraction="100" if option == question_data['correct_answer'] else "0", format='moodle_auto_format')
                ET.SubElement(answer_element, 'text').text = option
        else:
            answer_element = ET.SubElement(question_element, 'answer', fraction="100", format='moodle_auto_format')
            ET.SubElement(answer_element, 'text').text = question_data['answer']

        ET.SubElement(question_element, 'generalfeedback', format='html').text = "<![CDATA[]]>"
        ET.SubElement(question_element, 'defaultgrade').text = "1.000000"
        ET.SubElement(question_element, 'penalty').text = "0.3333333"
        ET.SubElement(question_element, 'hidden').text = "0"

    tree = ET.ElementTree(root)

    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') if os.name == 'nt' else os.path.join(os.path.expanduser('~'), 'Desktop')
    xml_file_path = os.path.join(desktop_path, 'questions.xml')

    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    print(xml_file_path)

if __name__ == '__main__':
    input_file = sys.argv[1]

    with open(input_file, 'r') as file:
        generated_question_answers = json.load(file)

    save_questions_to_xml(generated_question_answers)
