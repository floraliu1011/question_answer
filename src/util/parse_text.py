import sys, os
import spacy
import re

sys.path.append('/home/flora/Github/question_answer')

def parse_text(dataDir):
    """
    Read in the file specified by dataDir and parse through each sentence
    """
    with open(dataDir, 'r', encoding='utf-8') as file:
        data = file.read()
    data = data.split('\n')
    # remove sentences that are fewer than 5 words -> not likely to be a sentence
    data = [s for s in data if len(s.split(' ')) > 5]
    # remove stuff inside brackets -> ususally nonimportant and confuses the parser
    data = [re.sub(r"\s?\(.*?\)", "", s) for s in data]
    print(data)
    nlp = spacy.load('en_core_web_sm')
    parsed_data = [nlp(d) for d in data]
    return data, parsed_data
