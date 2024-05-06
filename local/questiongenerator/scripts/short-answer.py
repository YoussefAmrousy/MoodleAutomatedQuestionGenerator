import sys
import json
from transformers import pipeline
from shared import file_to_text, create_shortanswer_question

generated_question_answers = []


def create_shortanswer_questions(input_text, questions_num: int,
                                 difficulty: str):
    questions = []
    if len(input_text) <= 512:
        generator = (create_shortanswer_question(input_text, difficulty)
                     for _ in range(questions_num))
    else:
        text_segments = [
            input_text[i:i + 512] for i in range(0, len(input_text), 512)
        ]
        generator = (create_shortanswer_question(segment, difficulty)
                     for segment in text_segments)

    for question in generator:
        questions.append(question)
        if len(questions) >= questions_num:
            break

    return questions


def create_answer(input_text: str, question: str,
                  question_answer_pipeline: pipeline):
    qa_result = question_answer_pipeline(question=question, context=input_text)
    return qa_result['answer'].replace('\n', ' ').capitalize()


def generate_questions(filepath: str, questions_num: int, difficulty: str):
    input_text: str = file_to_text(filepath)

    question_answer_pipeline = pipeline(
        "question-answering",
        model="bert-large-uncased-whole-word-masking-finetuned-squad")

    questions = create_shortanswer_questions(input_text, questions_num,
                                             difficulty)
    if (len(questions) == 0):
        return []

    for question in questions:
        answer = create_answer(input_text, question, question_answer_pipeline)
        generated_question_answers.append((question, answer, difficulty))

    questions_json = json.dumps(generated_question_answers)
    print(questions_json)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python generate_questions_script_path.py <file_path> <questions_num> <difficulty>"
        )
        sys.exit(1)

    file_path = sys.argv[1]
    questions_num = int(sys.argv[2])
    difficulty = sys.argv[3]

    generate_questions(file_path, questions_num, difficulty)
