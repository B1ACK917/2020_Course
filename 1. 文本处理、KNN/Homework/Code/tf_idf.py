import math


def mult(a, b):
    c = [0 for i in range(len(a))]
    for i in range(len(a)):
        c[i] = a[i] * b[i]
    return c


def make_tfidf_mat(data):
    WordDict = {}
    WordList = []
    for Target in data:
        for word in Target:
            if word not in WordDict:
                WordDict.update({word: 1})
            else:
                WordDict[word] += 1
    for word in WordDict.keys():
        WordList.append(word)
    WordList = sorted(WordList)
    IDF_MAT = [0.0 for i in range(len(WordDict))]
    TF_MAT = [[0.0 for i in range(len(WordDict))] for i in range(len(data))]
    for i in range(len(data)):
        Target = data[i]
        LocalDict = {}
        for word in Target:
            if word not in LocalDict:
                LocalDict.update({word: 1})
            else:
                LocalDict[word] += 1
        for key, value in LocalDict.items():
            TF_MAT[i][WordList.index(key)] = value / len(Target)
    for key in WordDict.keys():
        IDF_MAT[WordList.index(key)] = math.log2(len(data) / WordDict[key])
    TF_IDF_MAT = [[] for i in range(len(data))]
    for i in range(len(TF_IDF_MAT)):
        TF_IDF_MAT[i] = mult(IDF_MAT, TF_MAT[i])
    return TF_IDF_MAT


if __name__ == '__main__':
    data = []
    with open(r'./lab1_data/semeval.txt', 'r') as file:
        text = file.readlines()
        for line in text:
            data.append(line.replace('\n', '').split('\t')[2].split(' '))
    TF_IDF_MAT = make_tfidf_mat(data)
    with open(r'./result/result1_1.txt', 'w') as file_2:
        for i in range(len(TF_IDF_MAT)):
            file_2.write(str(TF_IDF_MAT[i]))
