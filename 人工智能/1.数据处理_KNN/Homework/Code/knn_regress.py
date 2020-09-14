# coding=utf-8
import math
import time


class KNN:
    def __init__(self, train_path, valid_path, test_path, K, distance_rule, vote_rule, run_mode='train'):
        """
        构造函数
        :param train_path:  The Path Where you stored the Training Data
        :param valid_path: The Path Where you stored the Validation Data
        :param test_path: The Path Where you stored the Testing Data
        :param K: Param K for KNN Algorithm,
        :param distance_rule: 'Lp' or 'Cos'
        :param vote_rule: Whether to Vote Using Distance, Chosen from True or False
        :param run_mode: Chosen from ['train','predict']
        """
        self.TrainDataPath = train_path
        self.ValidationDataPath = valid_path
        self.TestDataPath = test_path
        self.WordDict = None
        self.WordList = None
        self.x_Train = None
        self.y_Train = None
        self.x_Valid = None
        self.y_Valid = None
        self.x_Test = None
        self.y_Test = None
        self.y_Predict = None
        if K == 'Dynamic':
            self.__K = None
        else:
            self.__K = K
        self.Accuracy = None
        if distance_rule[0] == 'L':
            self.ArgP = int(distance_rule[1:])
            self.DistanceMode = 'Lp-Norm'
        elif distance_rule == 'Cos':
            self.DistanceMode = 'Cos-Distance'
        else:
            raise NameError('Not a Legal Distance Algorithm')
        if vote_rule is None:
            self.VoteWithWeight = False
        else:
            self.VoteWithWeight = True
            self.VoteRule = vote_rule
        self.mode = run_mode

    @staticmethod
    def mult(a, b):
        """
        向量点乘
        :param a: 一个列表，表示向量a
        :param b: 一个列表，表示向量b
        :return: 向量a点乘b的结果
        """
        c = [0 for i in range(len(a))]
        for i in range(len(a)):
            c[i] = a[i] * b[i]
        return c

    @classmethod
    def make_tfidf_mat(cls, data, WordDict, WordList):
        """
        生成TF-IDF矩阵
        :param data: 一个列表，每一行是一个句子
        :param WordDict: 词表
        :param WordList: 词位置
        :return: TF-IDF矩阵
        """
        if WordDict is None or WordList is None:
            WordDict, WordList = {}, []
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
                IDF_MAT[WordList.index(key)] = math.log10(len(data) / (WordDict[key] + 1))
            TF_IDF_MAT = [[] for i in range(len(data))]
            for i in range(len(TF_IDF_MAT)):
                TF_IDF_MAT[i] = cls.mult(IDF_MAT, TF_MAT[i])
        else:
            NewDict = WordDict.copy()
            for key in NewDict.keys():
                NewDict[key] = 0
            for Target in data:
                for word in Target:
                    if word in WordDict:
                        NewDict[word] += 1
            IDF_MAT = [0.0 for i in range(len(NewDict))]
            TF_MAT = [[0.0 for i in range(len(NewDict))] for i in range(len(data))]
            for i in range(len(data)):
                Target = data[i]
                LocalDict, TotalCount = {}, 0
                for word in Target:
                    if word in NewDict:
                        TotalCount += 1
                        if word not in LocalDict:
                            LocalDict.update({word: 1})
                        else:
                            LocalDict[word] += 1
                for key, value in LocalDict.items():
                    TF_MAT[i][WordList.index(key)] = value / TotalCount
            for key in NewDict.keys():
                IDF_MAT[WordList.index(key)] = math.log10(len(data) / (NewDict[key] + 1))
            TF_IDF_MAT = [[] for i in range(len(data))]
            for i in range(len(TF_IDF_MAT)):
                TF_IDF_MAT[i] = cls.mult(IDF_MAT, TF_MAT[i])
        return TF_IDF_MAT, WordDict, WordList

    @staticmethod
    def Lp_Norm(x_vec, y_vec, p):
        """
        Lp范数求取函数
        :param x_vec: 特征向量x
        :param y_vec: 特征向量y
        :param p: 要求取的范数p值
        :return: x_vec-y_vec的Lp范数
        """
        VecLen = len(x_vec)
        Result, Inner = 0, 0
        for i in range(VecLen):
            Inner += math.fabs(x_vec[i] - y_vec[i]) ** p
        Result = Inner ** (1 / p)
        return Result

    @staticmethod
    def Cos_Distance(x_vec, y_vec):
        """
        余弦距离求取函数
        :param x_vec: 特征向量x
        :param y_vec: 特征向量y
        :return: x_vec和y_vec的余弦距离
        """
        VecLen = len(x_vec)
        Result, DivA, VecDisA, VecDisB = 0, 0, 0, 0
        for i in range(VecLen):
            DivA += x_vec[i] * y_vec[i]
            VecDisA += x_vec[i] ** 2
            VecDisB += y_vec[i] ** 2
        DivB = (VecDisA * VecDisB) ** 0.5
        Result = 1 - (DivA / DivB) if DivB != 0 else 1
        return Result

    def Smooth_Method(self, x):
        """
        激活函数
        :param x: 原数据x
        :return: 激活后的x
        """
        if self.VoteRule == 'log':
            return math.log(x)
        elif self.VoteRule == 'square':
            return max([0, (1 - (2 * math.fabs(x) / 10)) ** 2])
        elif self.VoteRule == 'sigmoid':
            return 1 / (1 + (math.e ** (-x)))
        elif self.VoteRule == 'tan':
            return math.atan(x) * 2 / math.pi

    @staticmethod
    def calculate_COR(y_predict, y_label):
        """
        计算相关系数
        :param y_predict: KNN给出的预测结果
        :param y_label: 真实标签
        :return: 预测结果和标签间的相关系数
        """
        VecLen = len(y_predict)
        Result, DivA, VecDisA, VecDisB = 0, 0, 0, 0
        y_predictBar = sum(y_predict) / VecLen
        y_labelBar = sum(y_label) / VecLen
        for i in range(VecLen):
            DivA += (y_predict[i] - y_predictBar) * (y_label[i] - y_labelBar)
            VecDisA += (y_predict[i] - y_predictBar) ** 2
            VecDisB += (y_label[i] - y_labelBar) ** 2
        DivB = (VecDisA * VecDisB) ** 0.5
        Result = DivA / DivB
        return Result

    def load_train(self):
        """
        读取训练集
        """
        self.y_Train, x_pre = [], []
        with open(r'./lab1_data/regression_dataset/{}'.format(self.TrainDataPath), 'r') as file:
            file.readline()
            text = file.readlines()
            for line in text:
                target = line.replace('\n', '').split(',')
                self.y_Train.append([float(item) for item in target[1:]])
                x_pre.append(target[0].split(' '))
        self.x_Train, self.WordDict, self.WordList = self.make_tfidf_mat(x_pre, None, None)
        if self.__K is None:
            self.__K = int(math.sqrt(len(self.x_Train)))

    def load_validation(self):
        """
        读取验证集
        """
        self.y_Valid, x_pre = [], []
        with open(r'./lab1_data/regression_dataset/{}'.format(self.ValidationDataPath), 'r') as file:
            file.readline()
            text = file.readlines()
            for line in text:
                target = line.replace('\n', '').split(',')
                self.y_Valid.append([float(item) for item in target[1:]])
                x_pre.append(target[0].split(' '))
        self.x_Valid, _, __ = self.make_tfidf_mat(x_pre, self.WordDict, self.WordList)

    def load_test(self):
        """
        读取测试集
        """
        self.y_Test, x_pre = [], []
        with open(r'./lab1_data/regression_dataset/{}'.format(self.TestDataPath), 'r') as file:
            file.readline()
            text = file.readlines()
            for line in text:
                target = line.replace('\n', '').split(',')
                x_pre.append(target[1].split(' '))
        self.x_Test, _, __ = self.make_tfidf_mat(x_pre, self.WordDict, self.WordList)

    def get_k_nearest(self, x):
        """
        获取和x最近的K个邻居
        :param x: 特征向量x
        :return: 一个列表，列表元素为元组，元组包含两个值：距离、该邻居在训练集中的索引
        """
        DistanceQueue = []
        if self.DistanceMode == 'Lp-Norm':
            for i in range(len(self.x_Train)):
                DistanceQueue.append((self.Lp_Norm(self.x_Train[i], x, self.ArgP), i))
        elif self.DistanceMode == 'Cos-Distance':
            for i in range(len(self.x_Train)):
                DistanceQueue.append((self.Cos_Distance(self.x_Train[i], x), i))
        DistanceQueue = sorted(DistanceQueue, key=lambda arg: arg[0])
        return DistanceQueue[:self.__K]

    def show_args(self):
        """
        显示模型参数
        """
        print(len(self.x_Train), len(self.x_Train[0]))
        print(len(self.x_Valid), len(self.x_Valid[0]))
        print(len(self.x_Test), len(self.x_Test[0]))
        print(self.y_Train)
        print(self.y_Valid)
        print(self.__K)

    def get_accuracy(self):
        """
        获取预测准确度
        :return: 一个在0-1之间的浮点数，表示准确度
        """
        if self.Accuracy is None:
            self.Accuracy = 0
            for i in range(len(self.y_Predict[0])):
                x, y = [key[i] for key in self.y_Predict], [key[i] for key in self.y_Valid]
                self.Accuracy += self.calculate_COR(x, y)
            self.Accuracy /= len(self.y_Predict[0])
        return self.Accuracy

    def get_predict(self):
        """
        获取预测结果
        :return: 一个二维列表，包含预测结果
        """
        return self.y_Predict

    def run(self):
        """
        使用给定参数运行
        :return: None
        """
        self.load_train()
        self.load_validation()
        self.load_test()
        # self.show_args()
        self.y_Predict = [[0.0 for i in range(6)] for i in
                          range(len(self.y_Valid if self.mode == 'train' else self.x_Test))]
        for i in range(len(self.x_Valid if self.mode == 'train' else self.x_Test)):
            VoteList = []
            KNeighbour = self.get_k_nearest(self.x_Valid[i] if self.mode == 'train' else self.x_Test[i])
            for neighbour in KNeighbour:
                Vote = self.y_Train[neighbour[1]]
                VoteList.append(
                    (Vote, (1 / neighbour[0]) if not self.VoteWithWeight else self.Smooth_Method(1 / neighbour[0])))
            Result = [0 for item in range(len(VoteList[0][0]))]
            for Voter in VoteList:
                for j in range(len(Voter[0])):
                    Result[j] += Voter[0][j] * Voter[1]
            Sum = sum(Result)
            Result = [(item / Sum) if Sum != 0 else 0 for item in Result]
            self.y_Predict[i] = Result


def Search():
    """
    搜索最优参数
    :return: None
    """
    KBegin, KEnd = 1, 31
    for Weight in [None, 'log', 'square', 'sigmoid', 'tan']:
        for Algo in ['L1', 'L2', 'L3', 'Cos']:
            x, y = [], []
            begin = time.perf_counter()
            print(
                'Regress Training Now Running, With Arg K in Range[{},{}), Distance Algorithm is {}, Voting Weight is '
                '{}'.format(
                    KBegin, KEnd, Algo, Weight))
            for i in range(KBegin, KEnd):
                Model = KNN('train_set.csv', 'validation_set.csv', 'test_set.csv', K=i, distance_rule=Algo,
                            vote_rule=Weight)
                Model.run()
                x.append(i)
                y.append(Model.get_accuracy())
            print('Training Completed, Average Time: {} s'.format(time.perf_counter() - begin / len(x)))
            with open(r'result/regress_result_{}_Weight-{}.txt'.format(Algo, Weight), 'w') as file:
                file.write(str(x) + '\n')
                file.write(str(y))


def Run(K, Weight, Algo):
    """
    使用给定参数进行预测
    :param K: KNN模型的K值
    :param Weight: 激活函数
    :param Algo: 距离函数
    :return: None
    """
    begin = time.perf_counter()
    print(
        'Running KNN-Regress Model With Arg K = {}, Distance Algorithm is {}, Voting Weight is {}'.format(
            K, Algo, Weight))
    Model = KNN('train_set.csv', 'validation_set.csv', 'test_set.csv', K=K, distance_rule=Algo,
                vote_rule=Weight, run_mode='predict')
    Model.run()
    Predict = Model.get_predict()
    # print(Predict)
    print('Training Completed, Time: {} s'.format(time.perf_counter() - begin))
    with open(r'result/Data/KNN_Regress/18340040_FengDawei_KNN_regression.csv', 'w') as file:
        file.write('textid,anger,disgust,fear,joy,sad,surprise\n')
        for i in range(len(Predict)):
            file.write(
                '{},{},{},{},{},{},{}\n'.format(i + 1, Predict[i][0], Predict[i][1], Predict[i][2], Predict[i][3],
                                                Predict[i][4], Predict[i][5]))


if __name__ == '__main__':
    Search()
    # Run(9, False, 'Cos')
