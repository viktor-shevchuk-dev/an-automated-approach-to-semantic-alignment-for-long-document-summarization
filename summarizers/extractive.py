import os
import sumy
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.kl import KLSummarizer
from sumy.summarizers.reduction import ReductionSummarizer
from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy.summarizers.random import RandomSummarizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
from sumy.utils import get_stop_words
from sumy.nlp.stemmers import Stemmer

from helpers import *

LANGUAGE = "english"
stemmer = Stemmer(LANGUAGE)
SENTENCES_COUNT = 7


def summarize_extractively(summarizer):
    summarizer_name = summarizer.__class__.__name__
    summarized_method_directory = './english_laws_with_abstracts/summarized/extractive/' + summarizer_name

    create_folder_if_not_exists(summarized_method_directory)

    summarizer.stop_words = get_stop_words(LANGUAGE)

    laws_folder = os.listdir("./english_laws_with_abstracts/laws")

    for index, _ in enumerate(laws_folder):
        start_index = get_next_index(
            summarized_method_directory, split_by_dot=True)

        if int(start_index) > index:
            continue

        law_folder = "./english_laws_with_abstracts/laws/" + str(index)
        paras_folder = os.listdir(law_folder)
        para_list = []

        summarized_law_path = summarized_method_directory + "/" + start_index + ".txt"

        for index, _ in enumerate(paras_folder):
            para_file = law_folder + "/" + str(index) + ".txt"

            with open(para_file, 'r') as file:
                para_text = file.read()
                para_list.append(para_text)

        law_text = " ".join(para_list)
        parser = PlaintextParser.from_string(law_text, Tokenizer(LANGUAGE))
        summarized = []

        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            summarized.append(sentence)

        summarized_text = ' '.join(str(v) for v in summarized)

        with open(summarized_law_path, 'w') as f:
            f.write(summarized_text)


def summarize_with_extractive_methods():
    summarize_extractively(LuhnSummarizer(stemmer))
    summarize_extractively(SumBasicSummarizer())
    summarize_extractively(RandomSummarizer(stemmer))

    summarizer = EdmundsonSummarizer(stemmer)
    summarizer.bonus_words = ('foo')
    summarizer.stigma_words = ('foo')
    summarizer.null_words = ('foo')
    summarize_extractively(summarizer)

    summarize_extractively(ReductionSummarizer(stemmer))
    summarize_extractively(ReductionSummarizer(stemmer))
    summarize_extractively(KLSummarizer(stemmer))
    summarize_extractively(LexRankSummarizer(stemmer))
    summarize_extractively(TextRankSummarizer(stemmer))
    summarize_extractively(LsaSummarizer(stemmer))
