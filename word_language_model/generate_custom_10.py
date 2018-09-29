###############################################################################
# Language Modeling on Penn Tree Bank
#
# This file generates new sentences sampled from the language model
#
###############################################################################

import argparse

import torch
from torch.autograd import Variable
import os
import math

import data

parser = argparse.ArgumentParser(description='PyTorch Wikitext-2 Language Model')

# Model parameters.
parser.add_argument('--data', type=str, default='./data/wikitext-2',
                    help='location of the data corpus')
parser.add_argument('--checkpoint', type=str, default='./model.pt',
                    help='model checkpoint to use')
parser.add_argument('--outf', type=str, default='generated.txt',
                    help='output file for generated text')
parser.add_argument('--sentences', type=int, default='10',
                    help='number of words to generate')
parser.add_argument('--seed', type=int, default=1111,
                    help='random seed')
parser.add_argument('--cuda', action='store_true',
                    help='use CUDA')
parser.add_argument('--temperature', type=float, default=1.0,
                    help='temperature - higher will increase diversity')
parser.add_argument('--log-interval', type=int, default=100,
                    help='reporting interval')
args = parser.parse_args()

# Set the random seed manually for reproducibility.
torch.manual_seed(args.seed)
if torch.cuda.is_available():
    if not args.cuda:
        print("WARNING: You have a CUDA device, so you should probably run with --cuda")

device = torch.device("cuda" if args.cuda else "cpu")

if args.temperature < 1e-3:
    parser.error("--temperature has to be greater or equal 1e-3")

with open(args.checkpoint, 'rb') as f:
    model = torch.load(f).to(device)
model.eval()

corpus = data.Corpus(args.data)
ntokens = len(corpus.dictionary)

try:
    start_word = input('Choose a starting word\n')
    start_word_idx = corpus.dictionary.word2idx[start_word]
except KeyError:
    while True:
        try:
            start_word = input('That word is not in the corpus, please try another word\n')
            start_word_idx = corpus.dictionary.word2idx[start_word]
            break
        except KeyError:
            continue

curr_text = ''

with open(args.outf, 'w') as outf:
    outf.write(start_word + ' ')
    with torch.no_grad():  # no tracking history
        for j in range(args.sentences):
            print(j)
            hidden = model.init_hidden(1)
            m_input = torch.randint(ntokens, (1, 1), dtype=torch.long).to(device)
            model(m_input, hidden)
            m_input.fill_(start_word_idx)
            curr_text += start_word + ' '
            outf.write(curr_text)
            for i in range(10):
                output, hidden = model(m_input, hidden)
                word_weights = output.squeeze().div(args.temperature).exp().cpu()
                word_idx = torch.multinomial(word_weights, 1)[0]

                word = corpus.dictionary.idx2word[word_idx]

                m_input.fill_(word_idx)

                outf.write(word + ' ')
                curr_text += word + ' '

                # if i % args.log_interval == 0:
                #     print('| Generated {}/{} words'.format(i, args.words))
            outf.write('\n')
            curr_text += '\n'
        print(curr_text)