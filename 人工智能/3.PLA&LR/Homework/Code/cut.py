import random


def cut(path, _file):
    with open(path + _file) as file:
        data = file.readlines()
        data[-1] += '\n'
        random.shuffle(data)
        data_group = []
        for i in range(9):
            data_group.append(data[len(data) // 10 * i:len(data) // 10 * (i + 1)])
        data_group.append(data[len(data) // 10 * 9:])
        for i in range(10):
            with open(path + '/train_{}.csv'.format(i), 'w') as troutput:
                with open(path + '/valid_{}.csv'.format(i), 'w') as vaoutput:
                    for j in range(10):
                        if i == j:
                            for d in data_group[j]:
                                vaoutput.write(d)
                        else:
                            for d in data_group[j]:
                                troutput.write(d)


if __name__ == '__main__':
    cut(r'./data/', 'train.csv')
