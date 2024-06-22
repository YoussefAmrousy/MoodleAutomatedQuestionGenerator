import sys
from shared import file_to_text, generate_response_gemini, append_metadata_to_questions


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
    final_response = append_metadata_to_questions(response, difficulty,
                                                  question_type)
    print(final_response)


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
