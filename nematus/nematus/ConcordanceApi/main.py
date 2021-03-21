from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask import jsonify

import nltk
from nltk import word_tokenize
from nltk.tokenize import TreebankWordTokenizer
import os

app = Flask(__name__)
api = Api(app)

post_args = reqparse.RequestParser()
post_args.add_argument("word", type=str, help="concordance keyword")
post_args.add_argument("dataset", type=str, help="concordance dataset")

base_dir = os.path.dirname(os.path.realpath(__file__))
dataset_path = os.path.join(base_dir, "Datasets")

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



api.add_resource(concordance_txt, "/concordance")
api.add_resource(concordance_txt_dataset, "/concordance/dataset")
api.add_resource(concordance_txt_files, "/concordance/allfiles")

if __name__ == "__main__":
    app.run(debug=True)