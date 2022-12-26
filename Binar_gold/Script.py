import re
import pandas as pd
import seaborn as sns
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords 

factory = StemmerFactory()
stemmer = factory.create_stemmer()

kamus_stopword = stopwords.words('indonesian')

def lowercase(teks):
    teks_baru = teks.lower()
    return teks_baru

def stemming(teks):
    return stemmer.stem(teks)

def replacement_alay(teks):
    df_kamusalay = pd.read_csv('gold/new_kamusalay.csv',encoding = 'latin-1')
    kamusalay_map = dict(zip(df_kamusalay['Teks'], df_kamusalay['Arti']))
    for word in kamusalay_map:
        return ' '.join([kamusalay_map[word] if word in kamusalay_map else word for word in teks.split(' ')])

def remove_stopword(teks):
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
    tweet_tokens = tokenizer.tokenize(teks)
 
    tweets_clean = []    
    for word in tweet_tokens:
        if (word not in kamus_stopword): # remove punctuation
            stem_word = stemmer.stem(word) # stemming word
            tweets_clean.append(stem_word)
    return " ".join(tweets_clean)

def remove_worduncess(teks):
    teks = re.sub(r':',' ', teks) #Menghilangkan tanda baca :
    teks = re.sub('[0-9]+',' ', teks) #Menghilangkan angka-angka
    teks = re.sub('\n',' ',teks) #Menghilangkan tab
    teks = re.sub('  +',' ',teks) #Menghilangkan ekstra spasi
    teks = re.sub(r'#', '', teks) #Menghilangkan hashtag
    teks = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',teks) #Menghilangkan link/web
    return teks
                        
def remove_punctuation(teks):
    teks = re.sub(r'[^\w\s]',' ',teks) #Menghilangkan tanda baca
    teks = re.sub(' +',' ',teks)
    return teks

def remove_rt(teks):
    teks = re.sub('rt',' ',teks) #Menghilangkan kata rt
    teks = re.sub('  +',' ',teks) #Menghilangkan ekstra spasi
    return teks

def remove_user(teks):
    teks = re.sub('user',' ',teks) #Menghilangkan kata user
    teks = re.sub('  +',' ',teks) #Menghilangkan ekstra spasi
    return teks

def remove_emoticon(teks):
    teks = teks.replace(' \ ', ' ')
    teks = re.sub('x..', ' ', teks)
    teks = re.sub(' \n', ' ', teks)
    teks = re.sub('\+', ' ', teks)
    teks = re.sub(' +',' ', teks)
    teks = re.sub(r'\$\w*',' ',teks)
    return teks

def cleansing(teks):
    teks = lowercase(teks)
    teks = stemming(teks)
    teks = remove_rt(teks)
    teks = remove_user(teks)
    teks = remove_emoticon(teks)
    teks = remove_worduncess(teks)
    teks = remove_punctuation(teks)
    teks = replacement_alay(teks)
    teks = remove_stopword(teks)
    return teks