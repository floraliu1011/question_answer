import sys, os
import spacy
import neuralcoref
import pyinflect
import re
import codecs

sys.path.append('/home/flora/Github/question_answer')
nlp = spacy.load('en_core_web_sm')
coref = neuralcoref.NeuralCoref(nlp.vocab)

nlp.add_pipe(coref, name='neuralcoref')


def parse_text(dataDir):
    """
    Read in the file specified by dataDir and parse through each sentence
    """
    with codecs.open(dataDir, mode='r', encoding='utf-8') as file:
        data = file.read()
    data = data.split('\n')
    # remove sentences that are fewer than 5 words -> not likely to be a sentence
    data = [s for s in data if len(s.split(' ')) > 5]
    # remove stuff inside brackets -> ususally nonimportant and confuses the parser
    data = [re.sub(r"\s?\(.*?\)", "", s) for s in data]
    print(data)
    parsed_data = [nlp(d) for d in data]
    return data, parsed_data
