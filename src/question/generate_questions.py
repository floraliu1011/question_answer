#%%
import os, sys
import spacy
# from pattern.en import conjugate
import logging
import neuralcoref
# nltk.download('averaged_perceptron_tagger')
sys.path.append('/home/flora/Github/question_answer')


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
        if sent[nc.root.i].ent_type_ == 'PERSON': # the word means man, person, human ....
            return True
        else:
            return False

def generate_subj_question(sent, nc, Qword):
    """Generate a WH question that doesn't envolve auxiliary verb extraction and sequence reordering."""
    rest = sent[nc.root.right_edge.i + 1 : nc.root.head.right_edge.i + 1]
    if rest[-1].pos_ == 'PUNCT':
        i = -1
        while rest[i].pos_ == 'PUNCT':
            i = i -1
        rest = rest[:i+1]
    return Qword + ' ' + rest.text + '?'
    
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
        logging.warning(sent)
        loggint.warning(subject)
    subj_root = subj_root[0]
    subject = sent[subj_root.left_edge.i:subj_root.right_edge.i + 1].text
    if subj_root.left_edge.i == 0 and subj_root.left_edge.tag_ != 'NNP':
        subject = subject[0].lower() + subject[1:]
    
    # extract auxiliary verb based on the tense and case of the main verb
    if main_verb.tag_ in ['VBG', 'VBN']: # verb is like taking or taken -> must have auxiliary
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
        verb = ' '.join(aux) + ' ' + main_verb.text if len(aux) > 0 else main_verb.text
    else:
        if main_verb.tag_ == 'VBD':
            extracted_aux = 'did'
            verb = main_verb.lemma_
        elif main_verb.tag_ == 'VBZ':
            extracted_aux = 'does'
            verb = main_verb.lemma_
        elif main_verb.tag_ == 'VBP':
            aux = [c for c in list(main_verb.lefts) if c.dep_ == 'aux']
            if len(aux) != 0:
                extracted_aux = aux[0].text
                if len(aux) > 1:
                    print ("Two aux with a present original verb ...?")
                    print(sent)
                    print(aux)
            else:
                extracted_aux = 'does'
        verb = main_verb.lemma_
    # piece together the rest of the sentence
    return ' '.join([Qword, extracted_aux, subject,verb]) + '?'



# asking what and who question
for i in range(len(sents)):
    sent = nlp(sents[i])
    print(sent)
    for nc in sent.noun_chunks:
        # asking what who question
        if nc.root.dep_ == 'nsubj' or nc.root.dep_ == 'nsubjpass':
            Qword = u'Who' if is_person(sent, nc) else u'What'
            question = generate_subj_question(sent, nc, Qword)
            print(question)
        elif nc.root.dep_ == 'dobj':
            Qword = u'Who' if is_person(sent, nc) else u'What'
            question = generate_obj_question(sent, nc, Qword)
            print(question)
    print(' \n')


# nsubj 
#%% generate who question
# start with the most preliminary version
# can use nc.root.head -> to find out about RHS of the subtree and use that as the stuff added to who
def generate_who_question(parsed_sent, start, end):
    qn = 'Who ' + parsed_sent[end:].text + '?' 
    return qn

def generate_what_question(parsed_sent, start, end):
    qn = 'What ' + parsed_sent[end:].text + '?'
    return qn



#%% what and 
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
                    question = generate_who_question(parsed_sent,  nc.start, nc.end )
                    print(question)
            for i in range(nc.start, nc.end):
                if parsed_sent[i].ent_type_ == 'PERSON':
                    question = generate_who_question(parsed_sent, nc.start, nc.end)
                    print(question)
                else:
                    question = generate_what_question(parsed_sent, nc.start, nc.end)
                    print(question)
# dependency tagging
#%%
# try NER



#%%
