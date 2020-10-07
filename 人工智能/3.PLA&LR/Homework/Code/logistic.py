import random
import time
import threading
import math


class logistic:
    def __init__(self, root_path, train_file, valid_file, learning_rate=1, it=10000):
        self.root = None
        self.rootPath = root_path
        self.trainFile = root_path + train_file
        self.validFile = root_path + valid_file
        self.trainDataFeature, self.trainDataLabel = self.__load_data('train', ex=True)
        self.validDataFeature, self.validDataLabel = self.__load_data('valid', ex=True)
        self.predict = []
        self.accuracy = None
        self.learningRate = learning_rate
        self.max_iter = it
        self.it = 0
        self.__w = self.__ini_mat(len(self.trainDataFeature[0]), _func='0')
        self.__accList = []
        self.__argsList = []

    def __load_data(self, _type, ex=False):
        data = None
        if _type == 'train':
            with open(self.trainFile) as file:
                data = [i.replace('\n', '').split(',') for i in file.readlines()]
        elif _type == 'valid':
            with open(self.validFile) as file:
                data = [i.replace('\n', '').split(',') for i in file.readlines()]

        data = [[float(f) for f in d] for d in data]
        if ex:
            for i in data:
                i.insert(0, 1.0)
        return [i[:-1] for i in data], [i[-1] for i in data]

    @staticmethod
    def __ini_mat(l, _func='0'):
        if _func == '0':
            w = [0 for i in range(l)]
        elif _func == 'random':
            w = [random.uniform(0, 1) for i in range(l)]
        else:
            w = []
        return w

    @staticmethod
    def __mult(a, b):
        if len(a) != len(b):
            raise ValueError('length a != length b')
        res = sum([a[i] * b[i] for i in range(len(a))])
        return res

    def __pi(self, x):
        return 1 / (1 + math.exp(-self.__mult(self.__w, x)))

    def __run_1_epoch(self, _type):
        if _type == 'train':
            predict = [self.__pi(feature) for feature in self.trainDataFeature]
        else:
            predict = [1 if self.__pi(feature) >= 0.5 else 0 for feature in self.validDataFeature]
        return predict

    def __optimize(self, x, y):
        c = y - self.__pi(x)
        self.__w = [self.__w[i] + c * x[i] for i in range(len(self.__w))]

    def __show_progress(self):
        while self.it != self.max_iter - 1:
            print('\rRunning Epoch {}/{}'.format(self.it, self.max_iter), end='', flush=True)
            time.sleep(3)

    def test(self):
        t = threading.Thread(target=self.__show_progress)
        t.setDaemon(True)
        t.start()
        for self.it in range(1, self.max_iter + 1):
            if self.it % 100 == 0:
                self.valid()
                self.__accList.append(self.get_accuracy())
            for j in range(len(self.trainDataLabel)):
                self.__optimize(self.trainDataFeature[j], self.trainDataLabel[j])
        print('\rTraining Finished', flush=True)

    def train(self):
        t = threading.Thread(target=self.__show_progress)
        t.setDaemon(True)
        t.start()
        for self.it in range(1, self.max_iter + 1):
            self.valid()
            self.__accList.append(self.get_accuracy())
            self.__argsList.append(self.__w)
            for j in range(len(self.trainDataLabel)):
                self.__optimize(self.trainDataFeature[j], self.trainDataLabel[j])
        self.__w = self.__argsList[self.__accList.index(max(self.__accList))]
        print('\rTraining Finished', flush=True)

    def valid(self):
        self.predict = self.__run_1_epoch('valid')

    def get_accuracy(self):
        hit = sum([(1 if self.predict[i] == self.validDataLabel[i] else 0) for i in range(len(self.predict))])
        self.accuracy = hit / len(self.predict)
        return self.accuracy

    def get_w(self):
        return self.__w

    def get_accl(self):
        return self.__accList


def run_10_cross_validation():
    acc = []
    for i in range(10):
        print('Cross Validation {} Now Running'.format(i))
        model = logistic('./data/', 'train_{}.csv'.format(i), 'valid_{}.csv'.format(i), it=1000)
        model.train()
        model.valid()
        acc.append(model.get_accuracy())
    print(acc)
    print(sum(acc) / len(acc))


if __name__ == '__main__':
    # model = logistic('./data/', 'train.csv', 'valid_0.csv', it=1000)
    # model.train()
    # model.valid()
    # print(model.get_accuracy())
    # print(model.get_w())
    # print(model.get_accl())
    run_10_cross_validation()
# 20975
# 25975
