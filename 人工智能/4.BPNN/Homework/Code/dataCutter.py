import random
import os


class dataCutter:
    def __init__(self, data, mode, train_percent=None):
        self.__data = data
        self.__mode = mode
        self.__num = len(self.__data)
        self.__trainPercent = train_percent

    def run(self):
        cut_data = []
        random.shuffle(self.__data)
        random.shuffle(self.__data)
        if self.__mode[-5:] == 'cross':
            num = int(self.__mode[:-6])
            data_group = []
            for i in range(num - 1):
                data_group.append(self.__data[self.__num // num * i:self.__num // num * (i + 1)])
            data_group.append(self.__data[self.__num // num * (num - 1):])
            for i in range(num):
                train, valid = [], None
                for j in range(num):
                    if i == j:
                        valid = data_group[j]
                    else:
                        train.extend(data_group[j])
                cut_data.append((train, valid))
        elif self.__trainPercent:
            cut_data.append((self.__data[:int(self.__trainPercent * self.__num)],
                             self.__data[int(self.__trainPercent * self.__num):]))
        else:
            raise TypeError('unknown mode as {}'.format(self.__mode))
        return cut_data


if __name__ == '__main__':
    a = [1, 1, 2, 4, 66, 1, 34, 5, 6, 1, 1]
    cutter = dataCutter(a, mode='10 cross')
    cutter.run()
