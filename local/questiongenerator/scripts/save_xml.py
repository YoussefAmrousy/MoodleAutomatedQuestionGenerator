import os
import xml.etree.ElementTree as ET

def save_questions_to_xml(generated_question_answers):
    root = ET.Element('quiz')

    for question, answer in generated_question_answers:
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

    # Determine the user's home directory
    home_dir = os.path.expanduser("~")

    # Construct the path to the desktop directory
    if os.name == 'posix':  # macOS or Linux
        desktop_path = os.path.join(home_dir, 'Desktop')
    elif os.name == 'nt':  # Windows
        desktop_path = os.path.join(home_dir, 'Desktop')
    else:
        raise RuntimeError("Unsupported operating system")

    # Create the directory if it doesn't exist
    os.makedirs(desktop_path, exist_ok=True)

    # Construct the full file path for the XML file
    xml_filename = 'generated_questions.xml'
    xml_filepath = os.path.join(desktop_path, xml_filename)

    # Write the XML file
    tree = ET.ElementTree(root)
    tree.write(xml_filepath, encoding='utf-8', xml_declaration=True)

    return xml_filepath

# Example usage:
# Replace this with your actual generated question answers
generated_question_answers = [("Sample question 1?", "Sample answer 1"),
                              ("Sample question 2?", "Sample answer 2")]

# Call the function to save questions to XML on the desktop
xml_filepath = save_questions_to_xml(generated_question_answers)

print(f"XML file saved as: {xml_filepath}")
