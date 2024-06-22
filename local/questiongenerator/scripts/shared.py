import fitz
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from prompt_parts import generate_prompt_parts


def _extract_text_from_page(page: any):
    return page.get_text()


def file_to_text(filepath: str):
    text = ""
    with fitz.open(filepath) as pdf_document:
        num_pages = pdf_document.page_count

        for page_num in range(num_pages):
            page = pdf_document[page_num]
            text += _extract_text_from_page(page)

    return text


def generate_response_gemini(input_text, question_type: str,
                             num_questions: int, difficulty: str):
    load_dotenv()

    genai.configure(api_key=os.getenv("API_KEY"))

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    input = _generate_input(input_text, num_questions, question_type,
                            difficulty)
    prompt_parts = generate_prompt_parts(input)

    response = model.generate_content(prompt_parts)
    return response.text


def _generate_input(input_text, num_questions: int, question_type: str,
                    difficulty: str):
    if (question_type == "Multiple Choice"):
        input = input_text + "\n Generate " + str(
            num_questions
        ) + " " + difficulty + " multiple choice question with four answers and one answer only is correct"
    elif (question_type == "Short Answer"):
        input = input_text + "\n Generate " + str(
            num_questions
        ) + " " + difficulty + " short answer question with its answer"
    elif (question_type == "True/False"):
        input = input_text + "\n Generate " + str(
            num_questions
        ) + " " + difficulty + " true/false question with their answers"
    return input


def append_metadata_to_questions(json_data, difficulty: str, question_type: str):
    data = json.loads(json_data)

    for question in data['questions']:
        question['difficulty'] = difficulty.capitalize()
        question['type'] = question_type

    updated_json_data = json.dumps(data, indent=2)

    return updated_json_data
