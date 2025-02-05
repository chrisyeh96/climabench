from __future__ import annotations

import argparse
import copy
import itertools
import pickle

from dataloaders import CDPQA
import numpy as np
from sklearn.metrics import ndcg_score
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification

parser = argparse.ArgumentParser()

parser.add_argument("--task", default='CDPCitiesQA',
                    help="Tasks like CDPCitiesQA, CDPStatesQA")
parser.add_argument("--model", type=str, default='cross-encoder/ms-marco-MiniLM-L-12-v2',
                    help="huggingface model to test")
parser.add_argument("--tokenizer", type=str, default='cross-encoder/ms-marco-MiniLM-L-12-v2',
                    help="huggingface tokenizer to ttest")
parser.add_argument("--max-len", type=int, default=512,
                    help="huggingface model max length")
parser.add_argument("--bs", default=64, type=int,
                    help="batch size")
args = parser.parse_args()


def mrr_at_k(grouped_labels, grouped_scores, k):
    all_mrr_scores = []
    for labels, scores in zip(grouped_labels, grouped_scores):
        pred_scores_argsort = np.argsort(-np.array(scores))
        mrr_score = 0
        for rank, index in enumerate(pred_scores_argsort[0:k]):
            if labels[index]:
                mrr_score = 1 / (rank + 1)

        all_mrr_scores.append(mrr_score)

    mean_mrr = np.mean(all_mrr_scores)
    return mean_mrr


def create_batches(pairs, bs):
    all_questions = []
    all_answers = []
    all_selected_questions = []
    all_labels = []
    for i in range(0, len(pairs), bs):
        selected_questions, questions, answers, labels = list(zip(*pairs[i:i + bs]))
        all_questions.append(questions)
        all_answers.append(answers)
        all_selected_questions.append(selected_questions)
        all_labels.append(labels)
    batched_pairs = list(zip(all_selected_questions, all_questions, all_answers, all_labels))
    return batched_pairs


def get_loader(task):

    if task == 'CDPCitiesQA':
        folder = './CDP/Cities/Cities Responses/'
    elif task == 'CDPStatesQA':
        folder = './CDP/States/'
    elif task == 'CDPCorpsQA':
        folder = './CDP/Corporations/Corporations Responses/Climate Change/'

    data_class = CDPQA(folder)
    dataset = data_class.load_dataset()
    print(data_class.class_weights)
    if 'train' in dataset:
        train_df, val_df, test_df = dataset['train'].to_pandas(),\
                                    dataset['val'].to_pandas(),\
                                    dataset['test'].to_pandas()
    else:
        train_df, val_df, test_df = dataset[0].to_pandas(), dataset[1].to_pandas(), dataset[2].to_pandas()

    return train_df, val_df, test_df, data_class


model = AutoModelForSequenceClassification.from_pretrained(args.model)
tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

_, _, test_df, data_class = get_loader(args.task)

pairs = test_df[test_df['label'] == 1].groupby('answer').agg(list)[['question']].reset_index()
sampled_pairs = pairs.sample(frac=1.0, random_state=42)


all_questions = set(itertools.chain(*pairs['question'].values))


exploded_pairs = []
for idx, (ans, ques) in tqdm(sampled_pairs.iterrows()):
    questions_copy = copy.deepcopy(all_questions)
    i = 0
    selected_question = None
    for q in set(ques):
        selected_question = q
        exploded_pairs.append((selected_question, q, ans, 1))
        questions_copy.remove(q)
        i += 1
        break
    for q in questions_copy:
        i += 1
        exploded_pairs.append((selected_question, q, ans, 0))
    assert i == len(all_questions)

batched_pairs = create_batches(exploded_pairs, args.bs)
model.cuda()
model.eval()
scores = {}
with torch.no_grad():
    for selected_questions, questions, answers, labels in tqdm(batched_pairs):
        features = tokenizer(questions, answers, padding=True, truncation=True,
                             return_tensors="pt", max_length=args.max_len,
                             return_token_type_ids=True)
        features['input_ids'] = features['input_ids'].cuda()
        features['attention_mask'] = features['attention_mask'].cuda()
        features['token_type_ids'] = features['token_type_ids'].cuda()
        outputs = model(**features).logits.cpu().numpy()
        for idx, (sq, q, a, l) in enumerate(zip(selected_questions, questions, answers, labels)):
            if sq not in scores:
                scores[sq] = {}
            if a not in scores[sq]:
                scores[sq][a] = []
            scores[sq][a].append((l, outputs[idx][0]))

results = {}
for sq in scores:
    answers = scores[sq].keys()
    results[sq] = {}
    results[sq]['no. of samples'] = len(answers)
    grouped_labels = []
    grouped_scores = []
    for answer in answers:
        label_list, score_list = zip(*scores[sq][answer])
        grouped_labels.append(label_list)
        grouped_scores.append(score_list)

    results[sq][f'NDCG@{len(all_questions)}'] = ndcg_score(grouped_labels, grouped_scores, k=len(all_questions))
    results[sq][f'MRR@{len(all_questions)}'] = mrr_at_k(grouped_labels, grouped_scores, len(all_questions))


print(results)
with open(f'test_results/per_question_{args.task}_{args.model.replace("/","_")}.pickle', 'wb') as f:
    pickle.dump(results, f)
