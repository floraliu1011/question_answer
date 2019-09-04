import sys, os
import spacy

sys.path.append('/home/flora/Github/question_answer')

def parse_text(dataDir):

    with open(dataDir, 'r', encoding='utf-8') as file:
        data = file.read()
    data = data.split('\n')
    data = [s for s in data if len(s.split(' ')) > 5]
    nlp = spacy.load('en_core_web_sm')
    parsed_data = [nlp(d) for d in data]
    return data, parsed_data
