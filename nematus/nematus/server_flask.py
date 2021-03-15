from flask import Flask, request, jsonify
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


# if __name__ == "__main__":
#     # parse console arguments
#     server_settings = Param()
#     server = NematusServer(server_settings)
#     server.start()


# Your API definition
app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def predict():

        
    try:
        json_ = request.json
        # print(json_)
        return jsonify({'translation':server.translate(json_['segments'])})

    except Exception as e:
        # print(json_)
        return jsonify({'trace': e})



server_settings = Param()
server = NematusServer(server_settings)
if __name__ == '__main__':

    port = 5000 # If you don't provide any port the port will be set to 1234
    app.run(host="0.0.0.0", port=port, debug=True)