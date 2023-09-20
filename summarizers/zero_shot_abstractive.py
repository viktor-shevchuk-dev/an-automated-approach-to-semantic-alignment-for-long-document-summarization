import math
import numpy as np
import os
from nltk.tokenize import sent_tokenize, word_tokenize
from transformers import pipeline, AutoTokenizer, set_seed

from helpers import *


# set_seed(1)
# gpt2_model_name = "gpt2-xl"
# summarizer = pipeline("text-generation", model=gpt2_model_name, max_new_tokens=64)
# gpt2_query = "summarize:\n"+ sample_text
# pipe_out = summarizer(gpt2_query, clean_up_tokenization_spaces=True)
# test3 = sent_tokenize(pipe_out[0]["generated_text"][len(gpt2_query) :])
# test3


def summarize_para(para, summarizer):
    try:
        if summarizer.task == 'text-generation':
            gpt2_query = "summarize:\n" + para
            summarized_para = summarizer(
                gpt2_query, clean_up_tokenization_spaces=True)[0]['generated_text'][len(gpt2_query):]
        else:
            summarized_para = summarizer(para, max_length=256)[
                0]["summary_text"]

        return summarized_para
    except:
        print("An error occurred, chunk text trying to summarize: ", para)
        return ""


def summarize_long_para(para, para_length, tokenizer, summarizer, max_token_number):
    para_list = para.split(" ")
    chunks_number = math.ceil(para_length / max_token_number)
    chunkified = np.array_split(para_list, chunks_number)
    summarized_chunk_list = []
    print("mega long sentence, chunks_number is: ", chunks_number)

    if chunks_number == 1:
        print(para_list)

    for chunk in chunkified:
        chunk_text = ' '.join(chunk)
        summarized_chunk = summarize_para(chunk_text, summarizer)
        summarized_chunk_list.append(summarized_chunk)

    summarized_long_para = ' '.join(summarized_chunk_list)
    summarized_para_length = len(tokenizer.tokenize(summarized_long_para))

    if summarized_para_length > max_token_number:
        return summarize_long_para(summarized_long_para, summarized_para_length, tokenizer, summarizer, max_token_number)

    return summarized_long_para


def summarize_abstractively(tokenizer, summarizer, max_token_number, para_list):
    chunk = []
    summarized = []

    for para in para_list:
        chunk_length = len(tokenizer.tokenize(' '.join(chunk)))
        para_length = len(tokenizer.tokenize(para))
        chunk_and_para_length = chunk_length + para_length

        if para_length > max_token_number:
            para = summarize_long_para(
                para, para_length, tokenizer, summarizer, max_token_number)
            summarized_long_para_length = len(tokenizer.tokenize(para))
            chunk_and_para_length = chunk_length + summarized_long_para_length

        if chunk_and_para_length > max_token_number:
            summarized_chunk_text = summarize_para(' '.join(chunk), summarizer)
            summarized.append(summarized_chunk_text)
            print(chunk_length)
            chunk.clear()

        chunk.append(para)

    if chunk:
        chunk_text = ' '.join(chunk)
        chunk_length = len(tokenizer.tokenize(chunk_text))
        summarized_remaining_chunk_text = summarize_para(
            chunk_text, summarizer)
        summarized.append(summarized_remaining_chunk_text)

        print("summarized remaining chunk with length: ", chunk_length)
        chunk.clear()

    summarized_law_text = ' '.join(summarized)

    return summarized_law_text


def save_abstractive_summaries(model_name, max_token_number, max_new_tokens):
    path = os.path
    storage_directory = path.join(path.curdir, "english_laws_with_abstracts")

    method_folder = path.join(
        storage_directory, "summarized", "zero_shot_abstractive")

    create_folder_if_not_exists(method_folder)

    model_folder_mame = model_name.replace('/', '_').replace('-', '_')
    summarized_method_folder = path.join(method_folder, model_folder_mame)

    create_folder_if_not_exists(summarized_method_folder)

    laws_folder = path.join(storage_directory, "laws")
    laws_listed = os.listdir(laws_folder)

    if model_name == 'gpt2-xl':
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        summarizer = pipeline("text-generation", model=model_name,
                              max_new_tokens=max_new_tokens, tokenizer=tokenizer)
    else:
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, model_max_length=max_token_number)
        summarizer = pipeline(
            "summarization", model=model_name, tokenizer=tokenizer)

    for index, _ in enumerate(laws_listed):
        start_index = get_next_index(
            summarized_method_folder, split_by_dot=True)

        if int(start_index) > index:
            continue

        law_folder = path.join(laws_folder, str(index))
        paras_listed = os.listdir(law_folder)
        para_list = []

        summarized_law_file = path.join(
            summarized_method_folder, f"{start_index}.txt")

        for index, _ in enumerate(paras_listed):
            para_file = path.join(law_folder, f"{index}.txt")

            with open(para_file, 'r') as file:
                para_text = file.read()
                para_list.append(para_text)

        summarized_text = summarize_abstractively(
            tokenizer, summarizer, max_token_number - 2, para_list)

        with open(summarized_law_file, 'w') as f:
            f.write(summarized_text)
