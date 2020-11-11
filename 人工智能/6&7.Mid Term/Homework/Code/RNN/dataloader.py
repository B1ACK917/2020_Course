import random
import re
import xml.etree.ElementTree as ET

import numpy as np
import torch
import torch.utils.data as data


def show_process(func):
    def wrapper(self, *args, **kwargs):
        print('Running {} process'.format(func.__name__))
        return func(self, *args, **kwargs)

    return wrapper


class DataLoader:
    class SingleClass:
        S, B, I, E, O = 0, 0, 0, 0, 1

    class MultiClass:
        S = [1, 0, 0, 0, 0]
        B = [0, 1, 0, 0, 0]
        M = [0, 0, 1, 0, 0]
        E = [0, 0, 0, 1, 0]
        O = [0, 0, 0, 0, 1]

    def __init__(self):
        self.__dataPath = None
        self.__vecPath = None
        self.__originData = []
        self.__data = []
        self.__vec = {}
        self.__fillRule = None
        self.__feature = None
        self.__label = None

    @show_process
    def __load_vec(self):
        self.__vec = {}
        with open(self.__vecPath, encoding='UTF-8') as file:
            newline = file.readline()
            while newline:
                newline = newline.replace('\n', '').split(' ')
                self.__vec.update({newline[0].lower(): [float(_k) for _k in newline[1:]]})
                if '__0' not in self.__vec:
                    self.__vec.update({'__0': [0 for i in range(len(newline) - 1)]})
                if '__r' not in self.__vec:
                    self.__vec.update({'__random': [random.uniform(-1, 1) for i in range(len(newline) - 1)]})
                newline = file.readline()

    @show_process
    def __load_data(self):
        tree = ET.parse(self.__dataPath)
        root = tree.getroot()
        self.__data = []
        for sentence in root.findall('sentence'):
            _text = sentence.find('text').text.lower()
            aspectTerms = sentence.find('aspectTerms')
            try:
                _term_list = []
                for aspectTerm in aspectTerms.findall('aspectTerm'):
                    _term = aspectTerm.get('term')
                    _term_list.append(_term.lower())
                self.__data.append([_text, _term_list])
            except AttributeError:
                pass
                # self.__data.append([_text, []])
        self.__originData = self.__data.copy()

    @show_process
    def __generate_feature(self):
        self.__feature = []
        failed, succeed = 0, 0
        for i in range(len(self.__data)):
            sentence = self.__data[i][0]
            words = sentence.split(' ')
            word_vec = []
            for w in words:
                if w == '':
                    continue
                try:
                    word_vec.append(self.__vec[w])
                    succeed += 1
                except KeyError:
                    failed += 1
                    word_vec.append(self.__vec[self.__fillRule])
            # self.__feature.append(np.array(word_vec))
            self.__feature.append(torch.Tensor(word_vec))
        print('Coverage ratio: {}'.format(succeed / (succeed + failed)))

    def __get_class(self, word, term_list):
        classify = self.SingleClass
        for terms in term_list:
            term = terms.split(' ')
            if word in term:
                if len(term) == 1:
                    return classify.S
                elif word == term[0]:
                    return classify.B
                elif word == term[-1]:
                    return classify.E
                else:
                    return classify.I
        return classify.O

    @show_process
    def __generate_label(self):
        self.__label = []
        for i in range(len(self.__data)):
            label_vec = []
            sentence = self.__data[i][0]
            term = self.__data[i][1]
            words = sentence.split(' ')
            for w in words:
                if w == '':
                    continue
                label_vec.append(self.__get_class(w, term))
            # self.__label.append(np.array(label_vec))
            self.__label.append(torch.Tensor(label_vec))

    @show_process
    def __clean(self):
        pattern = '\'!,;:?.*\(\)-'
        for i in range(len(self.__data)):
            self.__data[i][0] = re.sub(r'[{}]'.format(pattern), lambda x: ' ' + x.group() + ' ', self.__data[i][0])

    def set(self, data_path: str, vec_path: str, fill_rule: str = 'random'):
        self.__dataPath = data_path
        self.__vecPath = vec_path
        self.__fillRule = '__' + fill_rule

    def load(self):
        self.__load_data()
        self.__load_vec()
        self.__clean()
        self.__generate_feature()
        self.__generate_label()
        train_ind = int(len(self.__feature) // 5) * 4
        return self.__feature[:train_ind], self.__label[:train_ind], \
               self.__feature[train_ind:], self.__label[train_ind:]


if __name__ == '__main__':
    a = DataLoader()
    a.set(data_path='dataset/Laptops_Train.xml', vec_path='wordvec/glove.6B/glove.6B.50d.txt', fill_rule='random')
    # a.set(data_path='dataset/Laptops_Train.xml', vec_path='wordvec/glove.twitter.27B/glove.twitter.27B.25d.txt',
    #       fill_rule='random')
    b = a.load()
    for i in b:
        print(i)
    # print(b.shape)
