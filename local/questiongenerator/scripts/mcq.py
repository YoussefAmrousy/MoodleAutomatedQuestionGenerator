from builtins import str
import sys
from PyPDF2 import PdfFileReader
from builtins import str
import re
import nltk
from nltk import sent_tokenize
import gensim
import gensim.downloader as api
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize, word_tokenize
import random
import numpy as np
import xml.etree.ElementTree as ET
import fitz
import spacy
nltk.download("corpora/stopwords")
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer


def save_questions_to_xml(generated_question_answers, filepath):
    root = ET.Element('quiz')
    for question, answer, options in generated_question_answers:
        question_element = ET.SubElement(root, 'question', type='mcq')
        ET.SubElement(question_element, 'name').text = question
        ET.SubElement(question_element, 'questiontext', format='html').text = question
        ET.SubElement(question_element, 'answer', format='html').text = str(answer).lower()
        ET.SubElement(question_element, 'options', format='html').text = str(options).lower()
    tree = ET.ElementTree(root)
    tree.write(filepath + '.xml', encoding='utf-8')

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


def txt2questions(doc: str, n=5, o=4) -> dict:
    """ Get all questions and options """

    qGen = QuestionGeneration(n, o)
    q = qGen.generate_questions_dict(doc)
    for i in range(len(q)):
        temp = []
        for j in range(len(q[i + 1]['options'])):
            temp.append(q[i + 1]['options'][j + 1])
        # print(temp)
        q[i + 1]['options'] = temp
    return q

class QuestionGeneration:

    def generate_mcq_question(self, num_questions, num_options):
        self.num_questions = num_questions
        self.num_options = num_options
        self.question_extractor = QuestionExtractor(num_questions)

    def clean_text(self, text):
        text = text.replace('\n', ' ')  # remove newline chars
        sentences = sent_tokenize(text)
        cleaned_text = ""
        for sentence in sentences:
            # remove non alphanumeric chars
            cleaned_sentence = re.sub(r'([^\s\w]|_)+', '', sentence)

            # substitute multiple spaces with single space
            cleaned_sentence = re.sub(' +', ' ', cleaned_sentence)
            cleaned_text += cleaned_sentence

            if cleaned_text[-1] == ' ':
                cleaned_text[-1] = '.'
            else:
                cleaned_text += '.'

            cleaned_text += ' '  # pad with space at end
        return cleaned_text

    def generate_questions_dict(self, document):
#        document = self.clean_text(document)
        self.questions_dict = self.question_extractor.get_questions_dict(
            document)
        self.incorrect_answer_generator = IncorrectAnswerGenerator(document)

        for i in range(1, self.num_questions + 1):
            if i not in self.questions_dict:
                continue
            self.questions_dict[i]["options"] \
                = self.incorrect_answer_generator.get_all_options_dict(
                self.questions_dict[i]["answer"],
                self.num_options
            )

        return self.questions_dict
    
class IncorrectAnswerGenerator:
    ''' This class contains the methods
    for generating the incorrect answers
    given an answer
    '''

    def __init__(self, document):
        # model required to fetch similar words
        self.model = api.load("glove-wiki-gigaword-100")
        self.all_words = []
        for sent in sent_tokenize(document):
            self.all_words.extend(word_tokenize(sent))
        self.all_words = list(set(self.all_words))

    def get_all_options_dict(self, answer, num_options):
        ''' This method returns a dict
        of 'num_options' options out of
        which one is correct and is the answer
        '''
        options_dict = dict()
        try:
            similar_words = self.model.similar_by_word(answer, topn=15)[::-1]

            for i in range(1, num_options + 1):
                options_dict[i] = similar_words[i - 1][0]

        except BaseException:
            self.all_sim = []
            for word in self.all_words:
                if word not in answer:
                    try:
                        self.all_sim.append(
                            (self.model.similarity(answer, word), word))
                    except BaseException:
                        self.all_sim.append(
                            (0.0, word))
                else:
                    self.all_sim.append((-1.0, word))

            self.all_sim.sort(reverse=True)

            for i in range(1, num_options + 1):
                options_dict[i] = self.all_sim[i - 1][1]

        replacement_idx = random.randint(1, num_options)

        options_dict[replacement_idx] = answer

        return options_dict
    
class QuestionExtractor:
    ''' This class contains all the methods
    required for extracting questions from
    a given document
    '''

    def __init__(self, num_questions):

        self.num_questions = num_questions

        # hash set for fast lookup
        self.stop_words = set(stopwords.words('english'))

        # named entity recognition tagger
        self.ner_tagger = spacy.load('en_core_web_md')

        self.vectorizer = TfidfVectorizer()

        self.questions_dict = dict()

    def get_questions_dict(self, document):
        '''
        Returns a dict of questions in the format:
        question_number: {
            question: str
            answer: str
        }

        Params:
            * document : string
        Returns:
            * dict
        '''
        # find candidate keywords
        self.candidate_keywords = self.get_candidate_entities(document)

        # set word scores before ranking candidate keywords
        self.set_tfidf_scores(document)

        # rank the keywords using calculated tf idf scores
        self.rank_keywords()

        # form the questions
        self.form_questions()

        return self.questions_dict

    def get_filtered_sentences(self, document):
        ''' Returns a list of sentences - each of
        which has been cleaned of stopwords.
        Params:
                * document: a paragraph of sentences
        Returns:
                * list<str> : list of string
        '''
        sentences = sent_tokenize(document)  # split documents into sentences

        return [self.filter_sentence(sentence) for sentence in sentences]

    def filter_sentence(self, sentence):
        '''Returns the sentence without stopwords
        Params:
                * sentence: A string
        Returns:
                * string
        '''
        words = word_tokenize(sentence)
        return ' '.join(w for w in words if w not in self.stop_words)

    def get_candidate_entities(self, document):
        ''' Returns a list of entities according to
        spacy's ner tagger. These entities are candidates
        for the questions

        Params:
                * document : string
        Returns:
                * list<str>
        '''
        entities = self.ner_tagger(document)
        entity_list = []

        for ent in entities.ents:
            entity_list.append(ent.text)

        return list(set(entity_list))  # remove duplicates

    def set_tfidf_scores(self, document):
        ''' Sets the tf-idf scores for each word'''
        self.unfiltered_sentences = sent_tokenize(document)
        self.filtered_sentences = self.get_filtered_sentences(document)

        self.word_score = dict()  # (word, score)

        # (word, sentence where word score is max)
        self.sentence_for_max_word_score = dict()

        tf_idf_vector = self.vectorizer.fit_transform(self.filtered_sentences)
        feature_names = self.vectorizer.get_feature_names_out()
        tf_idf_matrix = tf_idf_vector.todense().tolist()

        num_sentences = len(self.unfiltered_sentences)
        num_features = len(feature_names)

        for i in range(num_features):
            word = feature_names[i]
            self.sentence_for_max_word_score[word] = ""
            tot = 0.0
            cur_max = 0.0

            for j in range(num_sentences):
                tot += tf_idf_matrix[j][i]

                if tf_idf_matrix[j][i] > cur_max:
                    cur_max = tf_idf_matrix[j][i]
                    self.sentence_for_max_word_score[word] = self.unfiltered_sentences[j]

            # average score for each word
            self.word_score[word] = tot / num_sentences

    def get_keyword_score(self, keyword):
        ''' Returns the score for a keyword
        Params:
            * keyword : string of possible several words
        Returns:
            * float : score
        '''
        score = 0.0
        for word in word_tokenize(keyword):
            if word in self.word_score:
                score += self.word_score[word]
        return score

    def get_corresponding_sentence_for_keyword(self, keyword):
        ''' Finds and returns a sentence containing
        the keywords
        '''
        words = word_tokenize(keyword)
        for word in words:

            if word not in self.sentence_for_max_word_score:
                continue

            sentence = self.sentence_for_max_word_score[word]

            all_present = True
            for w in words:
                if w not in sentence:
                    all_present = False

            if all_present:
                return sentence
        return ""

    def rank_keywords(self):
        '''Rank keywords according to their score'''
        self.candidate_triples = []  # (score, keyword, corresponding sentence)

        for candidate_keyword in self.candidate_keywords:
            self.candidate_triples.append([
                self.get_keyword_score(candidate_keyword),
                candidate_keyword,
                self.get_corresponding_sentence_for_keyword(candidate_keyword)
            ])

        self.candidate_triples.sort(reverse=True)

    def form_questions(self):
        ''' Forms the question and populates
        the question dict
        '''
        used_sentences = list()
        idx = 0
        cntr = 1
        num_candidates = len(self.candidate_triples)
        while cntr <= self.num_questions and idx < num_candidates:
            candidate_triple = self.candidate_triples[idx]

            if candidate_triple[2] not in used_sentences:
                used_sentences.append(candidate_triple[2])

                self.questions_dict[cntr] = {
                    "question": candidate_triple[2].replace(
                        candidate_triple[1],
                        '_' * len(candidate_triple[1])),
                    "answer": candidate_triple[1]
                }

                cntr += 1
            idx += 1
    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_questions_script_path.py <file_path> <num_questions> <num_options>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_questions = int(sys.argv[2])
    num_options = sys.argv[3]

    generated_question_answers = QuestionGeneration(file_path, num_questions, num_options)

    save_questions_to_xml(generated_question_answers, "generated_questions")