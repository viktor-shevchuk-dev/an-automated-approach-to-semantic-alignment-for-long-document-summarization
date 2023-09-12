import os
import numpy as np
import pandas as pd
import rouge
import evaluate

from helpers import *


rouge = evaluate.load('rouge')
bertscore = evaluate.load("bertscore")


def insert_row_at_index(df, specific_df, row_index):
    if row_index is None:
        return pd.concat([df, specific_df])

    for col in specific_df.columns:
        df.at[row_index, col] = specific_df[col].values[0]

    return df


def update_common_df(evaluation_directory, specific_df, approach_name, method_name):
    common_df_path = os.path.join(evaluation_directory, "common.csv")

    if os.path.exists(common_df_path):
        common_df = pd.read_csv(common_df_path)
        query_string = f"Approach == '{approach_name}' and Method == '{method_name}'"
        matching_row = common_df.query(query_string)
        row_index = matching_row.index[0] if not matching_row.empty else None
        common_df = common_df.drop(matching_row.index)
        common_df = insert_row_at_index(common_df, specific_df, row_index)
        common_df = common_df.sort_index()
    else:
        common_df = specific_df

    common_df.to_csv(common_df_path, index=False)


def save_evaluation_to_df(rouge_score, bert_score, approach_name, model_name):
    specific_df = pd.DataFrame([{
        'Approach': approach_name,
        'Method': model_name,
        **rouge_score,
        **bert_score
    }])

    evaluation_directory = os.path.join(
        os.path.curdir, "evaluators", "evaluated")
    method_folder = os.path.join(evaluation_directory, approach_name)
    create_folder_if_not_exists(method_folder)
    evaluation_row_file_name = os.path.join(method_folder, f"{model_name}.csv")
    specific_df.to_csv(evaluation_row_file_name, index=False)
    update_common_df(evaluation_directory, specific_df,
                     approach_name, model_name)


def rouge_evaluate(references, predictions):
    rouge_types = ['rouge1', 'rouge2', 'rougeL']
    results = rouge.compute(predictions=predictions,
                            references=references, rouge_types=rouge_types)
    rouge_1 = round(results['rouge1'], 2)
    rouge_2 = round(results['rouge2'], 2)
    rouge_L = round(results['rougeL'], 2)

    avg_rouge = round(np.mean([rouge_1, rouge_2, rouge_L]), 2)

    return {"rouge_1": rouge_1, "rouge_2": rouge_2, "rouge_L": rouge_L, "avg_rouge": avg_rouge}


def bertscore_evaluate(references, predictions):
    results = bertscore.compute(
        predictions=predictions, references=references, lang="en")
    precision = results["precision"]
    recall = results["recall"]
    f1 = results["f1"]

    avg_precision = round(np.mean(precision), 2)
    avg_recall = round(np.mean(recall), 2)
    avg_f1 = round(np.mean(f1), 2)

    return {"precision": avg_precision, "recall": avg_recall, "f1": avg_f1}


def evaluate_models(summarized_directory, summarization_method_name, single_model, references):
    summarization_method_directory = os.path.join(
        summarized_directory, summarization_method_name)
    models = os.listdir(summarization_method_directory)

    for _, model_name in enumerate(models):
        if single_model != "all" and model_name != single_model:
            continue

        model_folder = os.path.join(summarization_method_directory, model_name)
        summaries = os.listdir(model_folder)
        predictions = []

        for summary_index, _ in enumerate(summaries):
            summary_file = os.path.join(model_folder, f"{summary_index}.txt")

            with open(summary_file, 'r') as file:
                generated_summary_text = file.read()
                predictions.append(generated_summary_text)

        bert_score = bertscore_evaluate(references, predictions)
        rouge_score = rouge_evaluate(references, predictions)
        save_evaluation_to_df(rouge_score, bert_score,
                              summarization_method_name, model_name)


def evaluate_generated_summaries(single_approach="all", single_model="all"):
    storage_directory = os.path.join(
        os.path.curdir, "english_laws_with_abstracts")
    summarized_directory = os.path.join(storage_directory, "summarized")
    summarized_methods_listed = os.listdir(summarized_directory)
    references = get_references(storage_directory)

    for _, summarization_method_name in enumerate(summarized_methods_listed):
        if single_approach != "all" and summarization_method_name != single_approach:
            continue

        evaluate_models(summarized_directory,
                        summarization_method_name, single_model, references)
