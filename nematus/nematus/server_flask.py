# from flask import Flask, request, jsonify
#!/usr/bin/env python3

"""
Runs Nematus as a Web Server.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import json
import pkg_resources
import logging

# from bottle import Bottle, request, response
# from bottle_log import LoggingPlugin

# from server.response import TranslationResponse
# from server.api.provider import request_provider, response_provider

from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask import jsonify

import nltk
from nltk import word_tokenize
from nltk.tokenize import TreebankWordTokenizer
import os

from settings import ServerSettings
from server_translator import Translator
from settings import TranslationSettings

class Param:
    def __init__(self):
        self.style = "Nematus"
        self.host = "0.0.0.0"
        self.port = 5000
        self.threads = 4
        self.verbose = False
        self.models = ["../../model/model"]
        self.num_processes = 1
        self.minibatch_size = 80

class NematusServer(object):
    """
    Keeps a Nematus model in memory to answer http translation requests.
    """

    STATUS_LOADING = 'loading'
    STATUS_OK = 'ok'

    def __init__(self, server_settings):
        """
        Loads a translation model and initialises the webserver.

        @param server_settings: see `settings.py`
        """
        self._style = server_settings.style
        self._host = server_settings.host
        self._port = server_settings.port
        self._threads = server_settings.threads
        self._debug = server_settings.verbose
        self._models = server_settings.models
        self._num_processes = server_settings.num_processes
        self._status = self.STATUS_LOADING
        # start webserver
        # self._server = Bottle()
        # self._server.config['logging.level'] = 'DEBUG' if server_settings.verbose else 'WARNING'
        # self._server.config['logging.format'] = '%(levelname)s: %(message)s'
        # self._server.install(LoggingPlugin(self._server.config))
        # logging.info("Starting Nematus Server")
        # start translation workers
        logging.info("Loading translation models")
        self._translator = Translator(server_settings)
        print("Server")
        self._status = self.STATUS_OK

    def status(self):
        """
        Reports on the status of this translation server.
        """
        response_data = {
            'status': self._status,
            'models': self._models,
            'service': 'nematus',
        }
        response.content_type = "application/json"
        return json.dumps(response_data)

    def translate(self,segment):
        """
        Processes a translation request.
        """

        translations= self._translator.translate_string(
            segment,
            TranslationSettings()
        )

        result = " ".join(translations[0].target_words)
        return result

    def start(self):
        """
        Starts the webserver.
        """
        self._route()
        self._server.run(host=self._host, port=self._port, debug=self._debug, server='tornado', threads=self._threads)
        self._cleanup()

    def _cleanup(self):
        """
        Graceful exit for components.
        """
        self._translator.shutdown()

    def _route(self):
        """
        Routes webserver paths to functions.
        """
        self._server.route('/status', method="GET", callback=self.status)
        self._server.route('/translate', method="POST", callback=self.translate)



app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def predict():

        
    try:
        json_ = request.json
        # print(json_)
        return jsonify({'translation':server.translate(json_['segments'])})

    except:
        # print(json_)
        return jsonify({'trace': "error"})



server_settings = Param()
server = NematusServer(server_settings)


###concordance
post_args = reqparse.RequestParser()
post_args.add_argument("word", type=str, help="concordance keyword")
post_args.add_argument("dataset", type=str, help="concordance dataset")

base_dir = os.path.dirname(os.path.realpath(__file__))
dataset_path = os.path.join(base_dir, "ConcordanceApi/Datasets")

class concordance_txt_files(Resource):
    def get(self):
        args = post_args.parse_args()
        word = args.word
        res = []

        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                fileName = str(file)
                res.append(fileName)
                

        return jsonify(res)

class concordance_txt(Resource):
    def n_concordance_tokenised(self, text,phrase,left_margin=10,right_margin=10):

        phraseList=phrase.split(' ')

        c = nltk.ConcordanceIndex(text.tokens, key = lambda s: s.lower())

        #Find the offset for each token in the phrase
        offsets=[c.offsets(x) for x in phraseList]
        offsets_norm=[]
        #For each token in the phraselist, find the offsets and rebase them to the start of the phrase
        for i in range(len(phraseList)):
            offsets_norm.append([x-i for x in offsets[i]])
        intersects=set(offsets_norm[0]).intersection(*offsets_norm[1:])

        concordance_txt = ([text.tokens[list(map(lambda x: x-left_margin if (x-left_margin)>0 else 0,[offset]))[0]:offset+len(phraseList)+right_margin] for offset in intersects])

        outputs=[''.join([x+' ' for x in con_sub]) for con_sub in concordance_txt]
        return outputs

    def n_concordance(self, txt,phrase,left_margin=10,right_margin=10):
        tokens = nltk.word_tokenize(txt)
        text = nltk.Text(tokens)

        return self.n_concordance_tokenised(text,phrase,left_margin=left_margin,right_margin=right_margin)

    #n_concordance_tokenised(text,phrase,left_margin=left_margin,right_margin=right_margin)

    def post(self):
        args = post_args.parse_args()
        word = args.word
        res = []

        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                filePath = root+"/"+str(file)
                fileOpen = open(filePath, "r", encoding="utf8")
                tokenizer = TreebankWordTokenizer()
                text = nltk.Text( tokenizer.tokenize( fileOpen.read( ) ) )
                r = fileOpen.read()
                texted = nltk.Text(text)
                ttokens = self.n_concordance_tokenised(text = texted, phrase = word)
                for t in ttokens:
                    ans = t.partition(word)
                    res.append(ans)
                

        return jsonify(res)

class concordance_txt_dataset(Resource):
    def n_concordance_tokenised(self, text,phrase,left_margin=5,right_margin=5):

        phraseList=phrase.split(' ')

        c = nltk.ConcordanceIndex(text.tokens, key = lambda s: s.lower())

        #Find the offset for each token in the phrase
        offsets=[c.offsets(x) for x in phraseList]
        offsets_norm=[]
        #For each token in the phraselist, find the offsets and rebase them to the start of the phrase
        for i in range(len(phraseList)):
            offsets_norm.append([x-i for x in offsets[i]])
        intersects=set(offsets_norm[0]).intersection(*offsets_norm[1:])

        concordance_txt = ([text.tokens[list(map(lambda x: x-left_margin if (x-left_margin)>0 else 0,[offset]))[0]:offset+len(phraseList)+right_margin] for offset in intersects])

        outputs=[''.join([x+' ' for x in con_sub]) for con_sub in concordance_txt]
        return outputs

    def n_concordance(self, txt,phrase,left_margin=5,right_margin=5):
        tokens = nltk.word_tokenize(txt)
        text = nltk.Text(tokens)

        return self.n_concordance_tokenised(text,phrase,left_margin=left_margin,right_margin=right_margin)

    #n_concordance_tokenised(text,phrase,left_margin=left_margin,right_margin=right_margin)

    def post(self):
        args = post_args.parse_args()
        word = args.word
        dataset = args.dataset
        res = []

        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                if (str(file) == dataset):
                    filePath = root+"/"+str(file)
                    fileOpen = open(filePath, "r", encoding="utf8")
                    tokenizer = TreebankWordTokenizer()
                    text = nltk.Text( tokenizer.tokenize( fileOpen.read( ) ) )
                    r = fileOpen.read()
                    texted = nltk.Text(text)
                    ttokens = self.n_concordance_tokenised(text = texted, phrase = word)
                    for t in ttokens:
                        ans = t.partition(word)
                        res.append(ans)
                

        return jsonify(res)


api = Api(app)
api.add_resource(concordance_txt, "/concordance")
api.add_resource(concordance_txt_dataset, "/concordance/dataset")
api.add_resource(concordance_txt_files, "/concordance/allfiles")


if __name__ == '__main__':

    port = 5000 # If you don't provide any port the port will be set to 1234
    app.run(host="localhost", port=port, debug=True)