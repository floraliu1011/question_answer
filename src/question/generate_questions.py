# %%
import os
import sys
import spacy
# from pattern.en import conjugate
import logging
import neuralcoref
# nltk.download('averaged_perceptron_tagger')
sys.path.append('/home/flora/Github/question_answer/src')
import util.parse_text as pt

# from src.util.parse_text import parse_text

nlp = spacy.load("en")
coref = neuralcoref.NeuralCoref(nlp.vocab)

nlp.add_pipe(coref, name='neuralcoref')

# You're done. You can now use NeuralCoref the same way you usually manipulate a SpaCy document and it's annotations.
doc = nlp(u'My sister has a dog. She loves him.')

doc._.has_coref
doc._.coref_clusters
# neuralcoref.add_to_pipe(nlp)
# 
#%%
# start from generating very simple questions from very simple sentences
# generate who and what question using the most naive method
sents = [u'Apple is red', 
        u'Harry and Larry Wilson will be making a car!!?', 
        u'He said that he likes going to class',
        u'Larry like to fly', 
        u'The most beautiful woman is Betty',
        u'Gary has a brown dog. It chases the cat every day.',
        u'It is the best day of my life today', 
        u'The man in the city goes to work every day', 
        u'The dog is chasing the cat', 
        u'Tommy is eating ice cream'
        ]
#%% testing
doc = nlp(sents[1])
s = 'abckdjf'
print ((s[:-1]))
for nc in doc.noun_chunks:
    print(nc.text, nc.root.dep_, nc.root.head.text, nc.root.text  )
    print(nc.text ,doc[nc.root.head.i : nc.root.head.right_edge.i + 1])
    print(nc.root.head.left_edge, nc.root.head.right_edge)
    print(nc.root.text)
    print('  ', nc.start, nc.end)
    print('  ', )
    
#%%
sent = u"Larry Wilson is going to the park by car."
doc = nlp(sent)
tokens = []
for t in doc:
    tokens.append(t.text)   
print ((nltk.pos_tag(tokens)))
text = nltk.wordpunct_tokenize(u" is going to the park by car.")


#%% 
# use syntactic structure to do parsing -> forget about all the modifier shit


def is_person(sent, nc):
    """Determine if the noun chunk from the sentence is a person. Return True if it is."""
    if nc.root.pos_ == 'PRON' and nc.root.lemma_ in ['he', 'she', 'they', 'i', 'you']:
        return True
    else:
        # the word means man, person, human ....
        if sent[nc.root.i].ent_type_ == 'PERSON':
            return True
        else:
            return False


def reformat_result(question_body):
    """
    Get rid of the space between question word and the tailing punctuation if there are any
    """
    if len(question_body) == 0:
        return ''
    if question_body[0] != "'":
        question_body = " " + question_body
    for i in range(len(question_body), 0, -1):
        if question_body[i - 1] in string.punctuation and not question_body[i-1] in ['"', "'", ')']:
            question_body = question_body[:i-1]
        return question_body
  
# TODO: get the coreference resolution working:(
def coref_resolution(sent, pron):
    """
    Find the noun that the pron refers to 
    """
    return ''

def generate_subj_question(sent, nc, Qword):
    """Generate a WH question that doesn't envolve auxiliary verb extraction and sequence reordering."""
    rest = sent[nc.root.right_edge.i + 1: nc.root.head.right_edge.i + 1]
    question_body = reformat_result(rest.text)
    return Qword + question_body + '?'


def generate_obj_question(sent, nc, Qword):
    """
    Generate a WH question from sent about noun chunk nc using Question work Qword.
    The question generated involves auxiliary ver extraction and 
    """
    # find out the subject noun chunk of the sentence
    main_verb = nc.root.head
    subj_root = [t for t in list(main_verb.lefts) if t.dep_ == 'nsubj']
    if len(subj_root) > 1:
        logging.warning("Length of subject > 1")
        logging.warning(sent.text)
        loggint.warning(subject.text)
    if len(subj_root) == 0:
        logging.warning(
            "main verb is not derectly linked to the subject in sentence: " + sent.text)
        return -1
    subj_root = subj_root[0]
    subject = sent[subj_root.left_edge.i:subj_root.right_edge.i + 1]
    if subj_root.pos_ == 'PRON':
        subject = coref_resolution(sent, subj_root)
        if subject == '':
            return -1
    else:
        subject = subject.text.strip()
        if subj_root.left_edge.i == 0 and subj_root.left_edge.tag_ != 'NNP' and subj_root.left_edge.text != 'I':
            subject = subject[0].lower() + subject[1:]

    # extract auxiliary verb based on the tense and case of the main verb
    # verb is like taking or taken -> must have auxiliary
    if main_verb.tag_ in ['VBG', 'VBN']:
        aux = [c for c in list(main_verb.lefts) if c.dep_ == 'aux']
        if len(aux) != 0:
            extracted_aux = aux.pop(0)
            if extracted_aux.tag_ in ['VBP', 'VBZ', 'VBD']:
                extracted_aux = extracted_aux._.inflect(extracted_aux.tag_)
            else:
                extracted_aux = extracted_aux.text
        else:
            logging.warning("Something's wrong with the parsing, main verb is defined as VBG or VBN without auxiliary")
            logging.warning("sentence is: ", sent) 
            logging.warning( main_verb.text)
            return -1
        aux = [a.text for a in aux]
        verb = ' '.join(aux) + ' ' + \
            main_verb.text if len(aux) > 0 else main_verb.text
    else:
        if main_verb.tag_ == 'VBD':
            extracted_aux = 'did'
            verb = main_verb.lemma_
        elif main_verb.tag_ == 'VBZ':
            extracted_aux = 'does'
            verb = main_verb.lemma_
        elif main_verb.tag_ == 'VBP' or main_verb.tag_ == 'VB':
            aux = [c for c in list(main_verb.lefts) if c.dep_ == 'aux']
            if len(aux) != 0:
                extracted_aux = aux[0].text
                if len(aux) > 1:

                    logging.warning(
                        "Two aux with a present original verb ...?")
                    logging.warning(aux)
            else:
                extracted_aux = 'does'
        else:
            logging.warning('main verb is not a verb')
            logging.warning(main_verb.text)
            return -1


        verb = main_verb.lemma_
        
    ## get the xcomp
    comp = ''
    for desc in main_verb.rights:
        if desc.dep_  == 'xcomp':
                comp = sent[desc.left_edge.i:desc.right_edge.i+1]
                comp = comp.text
    if comp != '':
        question_body = [extracted_aux, subject, verb, comp]
    else:
        question_body = [extracted_aux, subject, verb]
    # piece together the rest of the sentence
    question_body = reformat_result(" ".join(question_body))
    return Qword + question_body + '?'




# asking what and who question
_, parsed_data = pt.parse_text(
    '/home/flora/Github/question_answer/data/noun_counting_data/a1.txt')
for i in range(len(parsed_data)):
    doc = parsed_data[i]
    for sent in doc.sents:
        print sent
        for nc in sent.noun_chunks:
            # asking what who question
            if nc.root.dep_ == 'nsubj' or nc.root.dep_ == 'nsubjpass':
                Qword = u'Who' if is_person(doc, nc) else u'What'
                question = generate_subj_question(doc, nc, Qword)
                print question
            elif nc.root.dep_ == 'dobj':
                Qword = u'Who' if is_person(doc, nc) else u'What'
                question = generate_obj_question(doc, nc, Qword)
                print question

        print ' \n'



# nsubj
# # %% generate who question - Trial 1
# # start with the most preliminary version
# # can use nc.root.head -> to find out about RHS of the subtree and use that as the stuff added to who
# def generate_who_question(parsed_sent, start, end):
#     qn = 'Who ' + parsed_sent[end:].text + '?'
#     return qn


# def generate_what_question(parsed_sent, start, end):
#     qn = 'What ' + parsed_sent[end:].text + '?'
#     return qn


# %% what and

sent = sents[0]
for i in range(len(sents)):
    sent = sents[i]
    print(sent)
    parsed_sent = nlp(sent)
    for nc in parsed_sent.noun_chunks:
        if nc.root.dep_ == 'nsubj':
            if nc.root.pos_ == 'PRON':
                # try coreference resolution
                if str.lower(nc.root.text) in ['he', 'she', 'they', 'i', 'you']:
                    question = generate_who_question(
                        parsed_sent,  nc.start, nc.end)
                    print(question)
            for i in range(nc.start, nc.end):
                if parsed_sent[i].ent_type_ == 'PERSON':
                    question = generate_who_question(
                        parsed_sent, nc.start, nc.end)
                    print(question)
                else:
                    question = generate_what_question(
                        parsed_sent, nc.start, nc.end)
                    print(question)
# dependency tagging
# %%
# try NER


# %%
