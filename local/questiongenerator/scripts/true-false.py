from transformers import pipeline
import sys
import json
from shared import file_to_text


def create_questions_true_false(input_text: str, questions_num: int,
                                question_generator_pipeline: pipeline):
    text_segments = [
        input_text[i:i + 512] for i in range(0, len(input_text), 512)
    ]
    num_beams = max(1, questions_num // len(text_segments))
    generated_questions = []
    for segment in text_segments:
        questions = question_generator_pipeline(segment,
                                                max_length=100,
                                                num_return_sequences=1,
                                                num_beams=num_beams)

        generated_questions.extend([
            question['generated_text'].strip().capitalize()
            for question in questions
        ])

        if len(generated_questions) >= questions_num:
            return generated_questions[:questions_num]

    return generated_questions


def create_answer(input_text: str, question: str,
                  question_answer_pipeline: any):
    qa_result = question_answer_pipeline(question=question, context=input_text)
    return qa_result['answer'].replace('\n', ' ').capitalize()


def generate_true_false_questions(filepath, questions_num):
    input_text = file_to_text(filepath)

    question_generator = pipeline(
        "text2text-generation",
        model="mrm8488/t5-base-finetuned-question-generation-ap")

    qa_generator = pipeline("question-answering",
                            model="deepset/roberta-base-squad2")

    questions = create_questions_true_false(input_text, questions_num,
                                            question_generator)
    generated_question_answers = []
    for question in questions:
        answer = create_answer(input_text, question, qa_generator)
        is_true = answer.lower() in question.lower()
        generated_question_answers.append([question, is_true])

    return generated_question_answers


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python generate_questions_script_path.py <file_path> <questions_num>"
        )
        sys.exit(1)

    file_path = sys.argv[1]
    questions_num = int(sys.argv[2])

    generated_question_answers = generate_true_false_questions(
        file_path, questions_num)

    output_json = json.dumps(generated_question_answers)
    print(output_json)
