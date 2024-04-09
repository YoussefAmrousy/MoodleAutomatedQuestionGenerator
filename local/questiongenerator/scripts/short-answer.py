import sys
from transformers import pipeline
import json
from shared import *

generated_question_answers = []


def create_questions_shortanswer(input_text: str, questionsNum: int,
                                 question_generator_pipeline: any):
    if len(input_text) <= 512:
        questions = question_generator_pipeline(
            input_text,
            max_length=30,
            num_return_sequences=questionsNum,
            num_beams=10)
        created_questions = [
            question['generated_text'].strip().capitalize()
            for question in questions
        ]
    else:
        text_segments = [
            input_text[i:i + 512] for i in range(0, len(input_text), 512)
        ]
        created_questions = []
        for segment in text_segments:
            questions = question_generator_pipeline(segment,
                                                    max_length=30,
                                                    num_return_sequences=1,
                                                    num_beams=10)
            for question in questions:
                created_questions.append(
                    question['generated_text'].strip().capitalize())

            if len(created_questions) >= questionsNum:
                break

    return created_questions


def create_answer(input_text: str, question: str,
                  question_answer_pipeline: any):
    qa_result = question_answer_pipeline(question=question, context=input_text)
    return qa_result['answer'].replace('\n', ' ').capitalize()


def generate_questions(filepath: str, questionsNum: int, difficulty: str):
    input_text: str = file_to_text(filepath)

    question_generator_pipeline = pipeline(
        "text2text-generation", model="voidful/bart-eqg-question-generator")
    question_answer_pipeline = pipeline(
        "question-answering",
        model="bert-large-uncased-whole-word-masking-finetuned-squad")

    questions = create_questions_shortanswer(input_text, questionsNum,
                                             question_generator_pipeline)
    for question in questions:
        answer = create_answer(input_text, question, question_answer_pipeline)
        difficultyCheck = check_difficulty(question, answer, difficulty)
        if (difficultyCheck):
            generated_question_answers.append((question, answer, difficulty))

    questions_json = json.dumps(generated_question_answers)
    print(questions_json)

    return generated_question_answers


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python generate_questions_script_path.py <file_path> <questionsNum> <difficulty>"
        )
        sys.exit(1)

    file_path = sys.argv[1]
    questionsNum = int(sys.argv[2])
    difficulty = sys.argv[3]

    generated_question_answers = generate_questions(file_path, questionsNum,
                                                    difficulty)

    save_questions_to_xml(
        generated_question_answers,
        "generated_questions")  # To save in the moodle question bank
