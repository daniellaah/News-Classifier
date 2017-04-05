import os
import time
import random
import re
import jieba
import numpy as np
import matplotlib.pyplot as plt
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib

def get_stopwords(stopwords_file):
    """返回所有停止词
    Args:
        stopwords_file: 停止词文件路径
    """
    stopwords_set = set()
    with open(stopwords_file, 'r') as f:
        for line in f.readlines():
            stopwords_set.add(line.strip())
    return stopwords_set

def words_extract(news_folder, stopwords_file="stopwords.txt"):
    """从所有文件内容提取词
    Args:
        news_data_folder:
            train/
                财经/
                体育/
                娱乐/
        stopwords_file: 停止词文件路径
    """
    subfolder_list = [subfolder for subfolder in os.listdir(news_folder) \
                        if os.path.isdir(os.path.join(news_folder, subfolder))]
    data_list = [] # element: ([word1, word2, ...], "财经")

    jieba.enable_parallel(8)
    # 遍历每个类别下的新闻
    for subfolder in subfolder_list:
        news_class = subfolder
        subfolder = os.path.join(news_folder, subfolder)
        news_list = [os.path.join(subfolder, news) for news in os.listdir(subfolder) \
                        if os.path.isfile(os.path.join(subfolder, news))]
        for news in news_list:
            with open(news, 'r') as f:
               content = f.read()
            word_list = jieba.lcut(content)
            data_list.append((word_list,news_class)) # element: ([word1, word2, ...], "财经")
    jieba.disable_parallel()
    return data_list

def get_feature_words(train_data_list, stopwords_file="stopwords.txt"):
    stopwords = get_stopwords(stopwords_file)
    feature_words_dict = {}
    for element in train_data_list:
        for word in element[0]:
            if not re.match("[a-z0-9A-Z]", word) and len(word) > 1 and word not in stopwords:
                if word in feature_words_dict:
                    feature_words_dict[word] += 1
                else:
                    feature_words_dict[word] = 1
    feature_words_tuple = sorted(feature_words_dict.items(), key=lambda x:x[1], reverse=True)
    feature_words = list(list(zip(*feature_words_tuple))[0])
    return feature_words

def train_test_extract(train_data, test_data, feature_words):
    X_train = [[1 if word in element[0] else 0 for word in feature_words] for element in train_data]
    y_train = [element[1] for element in train_data]
    X_test = [[1 if word in element[0] else 0 for word in feature_words] for element in test_data]
    y_test = [element[1] for element in test_data]
    return X_train, y_train, X_test, y_test

def predictWithFile(classifier, news_file, feature_words):
    with open(news_file) as f:
        news = f.read().strip()
    word_list = jieba.lcut(news)
    x = [1 if word in word_list else 0 for word in feature_words]
    return classifier.predict(x)

def predictWithContent(classifier, news_content, feature_words):
    word_list = jieba.lcut(news_content)
    x = [1 if word in word_list else 0 for word in feature_words]
    return classifier.predict(x)

if __name__ == '__main__':
    start_time = time.time()
    train_data = words_extract('train_test_data/train')
    test_data = words_extract('train_test_data/test')
    feature_words = get_feature_words(train_data, stopwords_file="stopwords.txt")
    X_train, y_train, X_test, y_test = train_test_extract(train_data, test_data, feature_words[:1000])
    clf = MultinomialNB().fit(X_train, y_train)
    test_accuracy = clf.score(X_test, y_test)
    print("用时%ss" % str(time.time()-start_time))
    print(test_accuracy)

    joblib.dump(clf, 'news_clf_model.pkl')
    with open("news_clf_feature_words.txt", 'w') as f:
        for word in feature_words:
            f.write(word + '\n')
