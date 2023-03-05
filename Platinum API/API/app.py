#import pakages for flask
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
import json
import uuid

#import library for flask
import pickle, re 
import sqlite3
import pandas as pd
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from clean_text import cleansing
from sklearn.feature_extraction.text import TfidfVectorizer

from werkzeug.utils import secure_filename
from datetime import datetime
import os

#Defining app
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing and Modeling')
        },
    host = LazyString(lambda:request.host)
)

#Swager configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path":  "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,config=swagger_config)

#database connection
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()
print('Opened database successfully')

c.execute('''CREATE TABLE IF NOT EXISTS data (uuid text, file text, download_path text, text text, model text, feature_extraction text, sentiment text);''')
print('Table created successfully')

#Feature Extraction & Load Model LSTM
file = open('recources_of_lstm/x_pad_sequences.pickle','rb')
feature_lstm = pickle.load(file)
file.close()

model_lstm = load_model('model_of_lstm/model.h5')

max_features=100000
tokenizer=Tokenizer(num_words=max_features,split=' ',lower=True)

#Feature Extraction & Load Model NN
#Import model
file = open('resources_of_nn/feature_xnn_tfidf1.pickle','rb')
X_tfid = pickle.load(file)
file.close()

file = open("model_of_nn/model_nn_hyperparam1.pickle",'rb')
model_nn = pickle.load(file)
file.close()

#definisi ramalan sentimen lstm
def getsentimentLSTM(input_text: str):
    sentiment=['negative','neutral','positive']
    text_cleansing = [cleansing(input_text)]
    feature = tokenizer.texts_to_sequences(text_cleansing)
    guess = pad_sequences(feature, maxlen=feature_lstm.shape[1])
    prediction = model_lstm.predict(guess)
    get_sentiment=np.argmax(prediction[0])
    hasil_sentiment = sentiment[get_sentiment]
    return hasil_sentiment

#definisi ramalan sentiment nn
def getsentimentNN(text: str):
    text_cleanse = cleansing(text)
    text_transform = X_tfid.transform([text_cleanse])
    result = model_nn.predict(text_transform)[0]
    return result



@swag_from("docs/text_lstm.yml", methods=['POST'])
@app.route('/text-processing-lstm', methods=['POST'])
def text_lstm():

    text = request.form.get('text')
    sentiment = getsentimentLSTM(text)

    #with conn:
    #   c.execute('''INSERT INTO data(text, text_clean) VALUES (? , ?);''', (text, text_clean))
    #   conn.commit()

    json_response = {
        'status_code': 200,
        'description': "Original Teks",
        'data': text,
        'sentiment' : sentiment
    }
    
    response_data = jsonify(json_response)
    '''c.execute("INSERT INTO data (uuid, text, model, sentiment) values(?,?,?,?)",(str(uuid.uuid4()), text, 'LSTM', sentiment)) 
    conn.commit()'''
    return response_data

@swag_from("docs/text_nn.yml", methods=['POST'])
@app.route('/text-processing-nn', methods=['POST'])
def neural_network_text():

    text = request.form.get('text')
    sentiment = getsentimentNN(text)
    
    json_response = {
        'status_code': 200,
        'description': "Result of Sentiment Analysis using NN",
        'data': {
            'text': text,
            'sentiment': sentiment
        },
    }
    response_data = jsonify(json_response)
    '''c.execute("INSERT INTO data (uuid, text, model, sentiment) values(?,?,?,?)",(str(uuid.uuid4()), text, 'Neural Network', sentiment)) 
    conn.commit() 
    conn.commit()'''
    return response_data

@swag_from("docs/file_lstm.yml", methods = ['POST'])
@app.route("/file_lstm", methods=["POST"])
def file_lstm():
    file = request.files['file']
    print("request file")
    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        time_stamp = (datetime.now().strftime('%d-%m-%Y_%H%M%S'))

        new_filename = f'{filename.split(".")[0]}_{time_stamp}.csv'
        
        
        save_location = os.path.join('input', new_filename)
        file.save(save_location)


        filepath = 'input/' + str(new_filename)

        data = pd.read_csv(filepath, encoding='latin-1')
        data = data.dropna()
        print(data)
        first_column_pre_process = data.iloc[:, 0]
        print(first_column_pre_process)

        sentiment_result = []

        for text in first_column_pre_process:
            #Cleaning inputted text
            file_clean = cleansing(text)
            print('ini teksnya : ', file_clean)

            get_sentiment = getsentimentLSTM(file_clean)
            print('ini sentimennya : ', get_sentiment)

            sentiment_result.append(get_sentiment)
    

        new_data_frame = pd.DataFrame(
                {'text': first_column_pre_process,
                'Sentiment': sentiment_result,
                })

        outputfilepath = f'output/{new_filename}'
        new_data_frame.to_csv(outputfilepath)

        result = new_data_frame.to_json(orient="index")
        parsed = json.loads(result)
        json.dumps(parsed) 

        

    json_response = {
        'status_code' : 200,
        'description' : "File sudah diproses",
        'result' : parsed
    }

    response_data = jsonify(json_response)
    '''c.execute('BEGIN TRANSACTION')
    c.execute("INSERT OR IGNORE INTO data (uuid, file, download_path, model) values(?,?,?,?)",(file_id, url_path, download_path, 'LSTM')) 
    c.execute('COMMIT')'''
    return response_data   

@swag_from("docs/file_nn.yml", methods = ['POST'])
@app.route("/file_nn", methods=["POST"])
def file_nn():
    file = request.files['file']
    print("request file")
    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        time_stamp = (datetime.now().strftime('%d-%m-%Y_%H%M%S'))

        new_filename = f'{filename.split(".")[0]}_{time_stamp}.csv'
        
        
        save_location = os.path.join('input', new_filename)
        file.save(save_location)


        filepath = 'input/' + str(new_filename)

        data = pd.read_csv(filepath, encoding='latin-1')
        data = data.dropna()
        print(data)
        first_column_pre_process = data.iloc[:, 0]

        sentiment_result = []

        for text in first_column_pre_process:
            #Cleaning inputted text
            file_clean = cleansing(text)
            print('ini teksnya : ', file_clean)

            get_sentiment = getsentimentNN(file_clean)
            print('ini sentimennya : ', get_sentiment)

            sentiment_result.append(get_sentiment)
    

        new_data_frame = pd.DataFrame(
                {'text': first_column_pre_process,
                'Sentiment': sentiment_result,
                })

        outputfilepath = f'output/{new_filename}'
        new_data_frame.to_csv(outputfilepath)

        result = new_data_frame.to_json(orient="index")
        parsed = json.loads(result)
        json.dumps(parsed) 

        

    json_response = {
        'status_code' : 200,
        'description' : "File sudah diproses",
        'result' : parsed
    }

    response_data = jsonify(json_response)
    '''c.execute('BEGIN TRANSACTION')
    c.execute("INSERT OR IGNORE INTO data (uuid, file, download_path, model) values(?,?,?,?)",(file_id, url_path, download_path, 'Neural Network')) 
    c.execute('COMMIT')'''
    return response_data  


#Defining allowed extensions
allowed_extensions = set(['csv'])
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route("/")
def hello_world():
    return "<p>Welcome to my API!</p>"

if __name__ == '__main__':
    app.run(debug=True)