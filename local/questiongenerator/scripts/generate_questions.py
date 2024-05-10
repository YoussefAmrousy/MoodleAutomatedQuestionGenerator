
import sys
from shared import file_to_text, generate_response_gemini, generate_json_question_answer
from datetime import datetime

def save_questions_to_gift(question_data, filename):
    """
    Saves questions in GIFT format to a specified file. Handles string and list of dictionaries.
    """
    import json  # Import json for handling string to json conversion if necessary

    # Check if question_data is a string and convert it to a list of dictionaries if so
    if isinstance(question_data, str):
        try:
            question_data = json.loads(question_data)
        except json.JSONDecodeError:
            print("Error: Could not decode question_data from string to JSON.")
            return False

    # Check if question_data is a list and contains dictionaries
    if not isinstance(question_data, list) or not all(isinstance(item, dict) for item in question_data):
        print("Error: Expected a list of dictionaries for question_data.")
        return False  # Indicate failure to process

    with open(filename, 'w') as file:
        for question in question_data:
            if question['type'] == "Multiple Choice":
                options = ' '.join(f"~{option}" for option in question['options'].values())
                correct = f"={question['options'][question['correct_answer']]}"
                options = options.replace(f"~{correct[1:]}", correct)  # Replace the correct answer with formatted one
                gift_text = f"::{question['question']}::{question['question']} {options}\n"
            elif question['type'] == "True/False":
                answer = 'TRUE' if question['answer'].lower() == 'true' else 'FALSE'
                gift_text = f"::{question['question']}::{answer}\n"
            elif question['type'] == "Short Answer":
                gift_text = f"::{question['question']}:: = {question['answer']}\n"
            file.write(gift_text)

    print(f"Questions successfully saved to {filename}.")
    return True  # Indicate successful processing


def generate_questions(filepath: str, question_type: str, num_questions: int,
                       difficulty: str):
    if (question_type == "MultipleChoice"):
        question_type = "Multiple Choice"
    elif (question_type == "TrueFalse"):
        question_type = "True/False"
    elif (question_type == "ShortAnswer"):
        question_type = "Short Answer"
    input_text: str = file_to_text(filepath)
    response = generate_response_gemini(input_text, question_type,
                                        num_questions, difficulty)
    question_answer_json = generate_json_question_answer(
        response, difficulty, question_type)
    print(question_answer_json)

    filename = f"generated_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gift"
    full_path = f"moodle/{filename}"
    
    if not save_questions_to_gift(question_answer_json, filename):
       print("Failed to save questions.")
    else:
            print(filename)  # This will be captured by PHP


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python generate_questions_script_path.py <file_path> <question_type> <questions_num> <difficulty>"
        )
        sys.exit(1)

    file_path = sys.argv[1]
    question_type = sys.argv[2]
    num_questions = int(sys.argv[3])
    difficulty = sys.argv[4]

    generate_questions(file_path, question_type, num_questions, difficulty)
