import os

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import tensorflow as tf
import pickle
from keras.models import load_model
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from keras.preprocessing import sequence

class Classifier():
    def __init__(self):
        with open('tokenizer', 'rb') as f:
            self.tokenizer = pickle.load(f)
        self.model = load_model('model.hdf5')
        self.graph = tf.get_default_graph()
        self.formatter = RegexpTokenizer(r'\w+')
        self.stop_words = set(stopwords.words('english'))
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

    def classify_sentence(self, sent):
        formatted_sent = self.format_sent(sent)
        preprocessed_sent = self.preprocess_sent(formatted_sent)
        pred = self.classify(preprocessed_sent)
        final_class = self.prediction_to_str(pred)
        return final_class