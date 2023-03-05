import re
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords as stopwords_scratch
import nltk


def hapus_kata(text):
    text = re.sub('USER',' ', str(text))
    text = re.sub(r'\\n+',' ', str(text))
    text = re.sub(r'https\S+',' ', str(text))
    text = re.sub(r'\\x[a-zA-Z0-9./]+',' ', str(text))
    text = re.sub('#[A-Za-z0-9./]+',' ', str(text))
    text = re.sub(' +',' ', str(text))
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9]',' ', str(text))
    return text

#kamus alay
alay_dict = pd.read_csv('new_kamusalay.csv', encoding='latin-1',header=None)
alay_dict = alay_dict.rename(columns={0: 'original', 1:'arti'})
def normalize_alay(text):
    alay_dict_map = dict(zip(alay_dict['original'], alay_dict['arti']))
    return ' '.join([alay_dict_map[word] if word in alay_dict_map else word for word in text.split(' ')])

#stem kata
stem = StemmerFactory()
stemmer = stem.create_stemmer()
def stemming(text):
    return stemmer.stem(text)

#Stopword
nltk.download('stopwords')
list_stopwords= stopwords_scratch.words('indonesian')
list_stopwords.extend(['sih','nya','iya','nih','biar','tau','kayak','banget','ya','gue','rt','RT','seperti','wkwk','haha',])
stopwords = list_stopwords

def remove_stopword(text):
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
    tweet_tokens = tokenizer.tokenize(text)

    tweet_clean = []
    for word in tweet_tokens:
        if(word not in stopwords):
            stem_word = stemmer.stem(word)
            tweet_clean.append(stem_word)
    return " ".join(tweet_clean)

def cleansing(text):
    text = hapus_kata(text)
    text = normalize_alay(text)
    text = stemming(text)
    text = remove_stopword(text)
    return text