# Import package
import pandas as pd
import sqlite3
import os

from flask import Flask, jsonify, render_template, send_from_directory, make_response, request
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from
from fileinput import filename
from Script import cleansing
from werkzeug.utils import secure_filename

#Pendefinisian app
app = Flask(__name__)

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'API Dcoumentation for Data Processing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host)
)

#Flask swagger config
swagger_config = {
    "headers": [],
    "specs": [ 
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,config=swagger_config)

#DATABASE
data_connect = sqlite3.connect('data.db', check_same_thread=False)
connect = data_connect.cursor()
data_connect.execute('''CREATE TABLE IF NOT EXISTS data(text varchar(255), text_clean varchar(255));''')

#HOMEPAGE
@app.route('/', methods =['GET'])
def main():
    return 'Welcome to My API'

#HELLO WORD
@swag_from("docs/hello_world.yml",methods=['GET'])
@app.route('/hello_world',methods =['GET'])
def hello_world():
    json_response = {
        'status_code': 200,
        'description' : "Menyapa Hello World",
        'data' : "Hello World",
    }

    response_data = jsonify(json_response)
    return response_data

#TEXT
@swag_from('docs/text.yml',methods =['GET'])
@app.route('/text',methods =['GET'])
def text():
    json_response = {
        'status_code' : 200,
        'description' : "Original Teks",
        'data' : "Hola! Apa kabar? Selamat Datang",
    }

    response_data = jsonify(json_response)
    return response_data

#TEXT CLEAN
@swag_from('docs/text_clean.yml',methods =['GET'])
@app.route('/text_clean',methods =['GET'])
def text_clean():
    json_response = {
        'status_code' : 200,
        'description' : "Original Teks",
        'data' : cleansing("Hola! Apa kabar? Selamat Datang"),
    }

    response_data = jsonify(json_response)
    return response_data

#INPUTAN TEKS
@swag_from("docs/text_processing.yml", methods = ['POST'])
@app.route('/text_processing', methods=['POST'])
def text_processing():
    text = request.form.get('text')
    text_clean = cleansing(text)

    with data_connect:
        connect.execute('''INSERT INTO data(text, text_clean) VALUES (? , ?);''', (text, text_clean))
        data_connect.commit()

    json_response = {
        'status_code' : 200,
        'description' : "Teks yang sudah diproses",
        'data' : text_clean,
    }

    response_data = jsonify(json_response)
    return response_data

#Ekstensi file yang dapat diproses
extention_file = set(['csv','xlsx'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in extention_file

#INPUTAN FILE
@swag_from("docs/file_Upload.yml", methods = ['POST'])
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files['file']

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)

        new_filename = f'{filename.split(".")[0]}.csv'

        save_location = os.path.join('gold', new_filename)
        file.save(save_location)

        filepath = 'gold/' + str(new_filename)

        data = pd.read_csv(filepath, encoding='latin-1')
        first_column_pre_process = data.iloc[:, 0]

        cleaned_word = []

        for text in first_column_pre_process:
            file_clean = cleansing(text)

            with data_connect:
                connect.execute('''INSERT INTO data(text, text_clean) VALUES (? , ?);''',(text, file_clean))
                data_connect.commit()

            cleaned_word.append(file_clean)
        
        new_data_frame = pd.DataFrame(cleaned_word, columns= ['Tweet Bersih'])
        outputfilepath = f'output_file/{new_filename}'
        new_data_frame.to_csv(outputfilepath)

    json_response = {
        'status_code' : 200,
        'description' : "File yang sudah diproses",
        'data' : "Selamat, file kamu sudah tercleansing",
    }

    response_data = jsonify(json_response)
    return response_data

#OUTPUT CLEANSING
@swag_from("docs/output_cleansing.yml", methods = ['GET'])
@app.route("/output_cleansing", methods=["GET"])
def output():
    row = connect.execute('''Select * from data''')
    my_list = []
    for text in row:
        my_list.append(text)

        json_response = {
        'status_code' : 200,
        'description' : "Hasil Cleansing",
        'data' : my_list,
    }

    response_data = jsonify(json_response)
    return response_data

#DOWNLOAD HASIL FILE
@app.route('/download')
def download():
    return render_template('download.html', files=os.listdir('output_file'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('output_file', filename)

## App Runner
if __name__ == '__main__':
    app.run(debug=True)