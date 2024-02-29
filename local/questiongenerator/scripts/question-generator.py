from transformers import pipeline
import torch
import fitz
import sys
import csv

def extract_text_from_page(page):
    return page.get_text()

def file_to_text(filepath):
    text = ""
    with fitz.open(filepath) as pdf_document:
        num_pages = pdf_document.page_count

        for page_num in range(num_pages):
            page = pdf_document[page_num]
            text += extract_text_from_page(page)

    return text

def bubble_sort(arr):
    n = len(arr)

    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if len(arr[j][0]) > len(arr[j + 1][0]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    return arr

def generate_questions(filepath, questionsNum):
    input_text = file_to_text(filepath)

    seed_value = hash(input_text) % (2**32 - 1)
    torch.manual_seed(seed_value)

    question_generator = pipeline("text2text-generation", model="voidful/bart-eqg-question-generator")
    qa_generator = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

    questions = question_generator(input_text, max_length=100, num_return_sequences=questionsNum)
    generated_questions = [question['generated_text'].strip().capitalize() for question in questions]

    generated_question_answers = []
    for generated_question in generated_questions:
        qa_result = qa_generator(question=generated_question, context=input_text)
        answer = qa_result['answer'].replace('\n', ' ').capitalize()
        generated_question_answers.append([generated_question, answer])

    sorted_questions = bubble_sort(generated_question_answers)

    save_dataset_to_csv(sorted_questions)

    print(sorted_questions)

def save_dataset_to_csv(dataset):
    csv_filename = "/opt/homebrew/var/www/moodle/local/questiongenerator/scripts/questions.csv"
    with open(csv_filename, 'a', newline='') as csvfile:
        fieldnames = ['Id', 'Question', 'Answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        last_index = 0

        try:
            with open(csv_filename, 'r') as csvfile_read:
                reader = csv.DictReader(csvfile_read)
                if 'Id' in reader.fieldnames:
                    for row in reader:
                        last_index = max(last_index, int(row['Id']))
        except FileNotFoundError:
            pass

        for idx, q_instance in enumerate(dataset, start=last_index + 1):
            writer.writerow({'Id': idx, 'Question': q_instance[0], 'Answer': q_instance[1]})

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_questions_script_path.py <file_path> <questionsNum>")
        sys.exit(1)

    file_path = sys.argv[1]
    questionsNum = int(sys.argv[2])
    generate_questions(file_path, questionsNum)

