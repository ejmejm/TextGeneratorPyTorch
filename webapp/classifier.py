import os

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import tensorflow as tf
import pickle
from keras.models import load_model
from nltk.tokenize import RegexpTokenizer
from keras.preprocessing import sequence

class Classifier():
    def __init__(self):
        with open('tokenizer', 'rb') as f:
            self.tokenizer = pickle.load(f)
        self.model = load_model('model.hdf5')
        self.graph = tf.get_default_graph()
        self.formatter = RegexpTokenizer(r'\w+')
        self.stop_words = set(['has', 'was', 'ain', 'she', 'did', 'any', 'should', 'those', 'again', 'from', 'at', 'in', 'yours', 'all', 'do', 'wasn', 'or', 'on', 'through', 'only', 'for', 'what', 'own', 'both', 'which', 'above', 'but', 'about', 'while', 'the', 'isn', 'into', 'haven', 'of', 'don', 'needn', 'most', 'been', 'him', 'over', 'if', 'aren', 'weren', 'hadn', 'against', 'off', 'am', 'between', 'nor', 'shan', 'i', 'being', 'with', 'm', 've', 'now', 'this', 'mightn', 'he', 'up', 'herself', 'doesn', 'as', 'whom', 'than', 'a', 'myself', 'how', 'll', 'yourselves', 'me', 'hasn', 'does', 'can', 'very', 'by', 'my', 'why', 'having', 'further', 'them', 'so', 'here', 'our', 'ma', 'when', 'themselves', 'be', 'under', 'didn', 'o', 'they', 'out', 't', 'we', 'such', 'where', 'is', 'won', 'who', 'same', 'not', 'few', 'will', 'no', 'and', 'below', 'you', 'more', 'couldn', 'after', 'that', 'their', 'theirs', 'hers', 'yourself', 'were', 'too', 're', 'then', 'once', 'ours', 'mustn', 'during', 'have', 'y', 'd', 'are', 'until', 'had', 'its', 'an', 'some', 'his', 'these', 'doing', 'other', 'shouldn', 's', 'it', 'himself', 'ourselves', 'down', 'her', 'just', 'itself', 'before', 'because', 'there', 'to', 'your', 'each', 'wouldn'])
        self.max_seq_len = 20

    def format_sent(self, sent):
        return ' '.join([word for word in self.formatter.tokenize(sent) 
                            if word not in self.stop_words])

    def preprocess_sent(self, sent):
        seq = self.tokenizer.texts_to_sequences([sent])
        padded_seq = sequence.pad_sequences(seq, maxlen=self.max_seq_len)
        return padded_seq

    def classify(self, x):
        with self.graph.as_default():
            return self.model.predict(x)[0]

    def prediction_to_str(self, pred):
        if pred[0] > pred[1]:
            return 'left'
        return 'right'

    def classify_sentence(self, sent, discrete=True):
        formatted_sent = self.format_sent(sent)
        preprocessed_sent = self.preprocess_sent(formatted_sent)
        pred = self.classify(preprocessed_sent)
        if discrete:
            final_class = self.prediction_to_str(pred)
        else:
            final_class = pred.tolist()
        return final_class
