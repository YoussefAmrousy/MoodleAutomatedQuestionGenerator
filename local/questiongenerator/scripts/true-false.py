from transformers import pipeline
import torch
import fitz
import sys
import csv
import streamlit as st
import random


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

def generate_questions(filepath, questionsNum):
    input_text = file_to_text(filepath)

    seed_value = hash(input_text) % (2**32 - 1)
    torch.manual_seed(seed_value)

    question_generator = pipeline("text2text-generation", model="voidful/bart-eqg-question-generator")
    qa_generator = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

    questions = question_generator(input_text, max_length=100, num_return_sequences=questionsNum)
    generated_questions = [question['generated_text'].strip().capitalize() for question in questions]

    questions_with_options = []
    for generated_question in generated_questions:
        qa_result = qa_generator(question=generated_question, context=input_text)
        answer = qa_result['answer'].replace('\n', ' ').capitalize()
        options = ['True', 'False']
        correct_answer = random.choice(options)
        options.remove(correct_answer)
        options.insert(random.randint(0, 1), answer)
        questions_with_options.append([generated_question, options, correct_answer])
        
    save_dataset_to_csv(questions_with_options)
    print(questions_with_options)


def save_dataset_to_csv(dataset):
    csv_filename = "/usr/local/var/www/moodle/local/questiongenerator/scripts/questions.csv"
    with open(csv_filename, 'a', newline='') as csvfile:
        fieldnames = ['Id', 'Question', 'Option1', 'Option2', 'CorrectAnswer']
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

        for idx, (question, options, correct_answer) in enumerate(dataset, start=last_index + 1):
            writer.writerow({
                'Id': idx,
                'Question': question,
                'Option1': options[0],
                'Option2': options[1],
                'CorrectAnswer': correct_answer
            })
 
 
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_questions_script_path.py <file_path> <questionsNum>")
        sys.exit(1)

    file_path = sys.argv[1]
    questionsNum = int(sys.argv[2])
    generate_questions(file_path, questionsNum)
 