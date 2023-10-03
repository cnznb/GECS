# -*- encoding = utf-8 -*-
"""
@description: Using CodeGPT to generate text vectors for each field in dataset
@date: 2022/9/4
@File : CodeGPT.py
@Software : PyCharm
"""
import csv
import os
import sys
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn import preprocessing

model_path = 'D:\\workspace\\EC\\CodeGPT-small-java'  # sys.argv[1]  # CodeGPT预训练模型目录

# 预训练
np.set_printoptions(suppress=True)
ss = preprocessing.StandardScaler()
print('Start To Load Pretrain Model ... ...')
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModel.from_pretrained(model_path)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print('Finish Loading Pretrain Model ! !')


def get_embedding(text):
    code_tokens = tokenizer.tokenize(text)
    tokens = [tokenizer.bos_token] + code_tokens + [tokenizer.eos_token]
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens)
    embedding = []
    index = 0
    while (index + 512) < len(tokens_ids):
        tk = torch.tensor(tokens_ids[index:(index + 512)]).to(device)
        embedding.extend(model(tk[None, :]).last_hidden_state[0].detach().cpu().numpy().tolist())
        index += 512
    if index < len(tokens_ids):
        tk = torch.tensor(tokens_ids[index:len(tokens_ids)]).to(device)
        embedding.extend(model(tk[None, :]).last_hidden_state[0].detach().cpu().numpy().tolist())
    embedding = np.array(embedding).reshape((-1, 768)).mean(axis=0).tolist()
    return embedding


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        return content

def solve(path):
    java_file = read_file(path + '\\old.java')
    code = java_file.split('\n')
    codes = [''] + code
    with open(path + '\\field_range.csv', 'r') as fp:
        lines = fp.read().split('\n')
        if not os.path.exists(path + '\\codeEmbedding'):
            os.mkdir(path + '\\codeEmbedding')
        for line in lines:
            if line == '':
                break
            code_line = ''
            ranges = [int(x) for x in line.split(',')[-2:]]
            for i in range(ranges[0], ranges[1] + 1):
                code_line += codes[i].strip()
            vec = get_embedding(code_line)
            with open(path+'\\codeEmbedding\\codeGPT.csv', 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                datas = [float(x) for x in vec]
                writer.writerow(datas)


def scan_dir(path):
    print(path)
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)

        if os.path.isdir(file_path):
            if file_name.startswith('1'):
                solve(file_path)
            else:
                scan_dir(file_path)


if __name__ == '__main__':
    scan_dir('E:/datasets')