#%%
import os, sys
import spacy

from src.util.parse_text import parse_text
#%%
dataDir = '/home/flora/Github/question_answer/data/noun_counting_data/a2.txt'
data, parsed_data = parse_text(dataDir)
#%% start from noun chunk
doc = parsed_data[1]
sent = list(doc.sents)[0]
for nc in doc.noun_chunks:
    print(nc)
    print('  ' + nc.root.text)
    print('  ' + nc.root.dep_)
    print('  ' + nc.root.head.text)
#%% try coef resolution to see 

#%%
# try PoS tagging




#%%
# dependency tagging
#%%
# try NER



#%%
