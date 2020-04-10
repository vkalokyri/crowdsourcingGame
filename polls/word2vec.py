from gensim.models import KeyedVectors
import operator
from nltk.corpus import stopwords

 

def load_model():
    return KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin', binary=True)  

def check_similarity(sentence, model, infile='sentencesDoctor.txt'):
    stops = set(stopwords.words("english"))
    check_sentence = [w for w in sentence.lower().split() if not w in stops]
    doc = open(infile,"r") 
    scores = dict()
    for line in doc:
        line = line[0:len(line)-1]#I think this is needed for escaping '\n'
        words = [w for w in line.lower().split() if not w in stops]
        scores[line] = model.n_similarity(words, check_sentence)
    return scores

model = load_model()
sentences = ['explain my symptoms'] 
for sentence in sentences:
    print(sentence)
    scores = check_similarity(sentence, model)
    print(sorted(scores.items(), key=operator.itemgetter(1)))



#from sklearn.cluster import DBSCAN
#print(model.get_vector(sentence))
#dbscan = DBSCAN(metric='cosine', eps=0.07, min_samples=3) # you can change these parameters, given just for example 
#cluster_labels = dbscan.fit_predict(scores)





