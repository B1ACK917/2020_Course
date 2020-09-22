import os
import math
from abc import abstractmethod, ABCMeta


class BaseDecisionTree(metaclass=ABCMeta):
    class DecisionNode:
        def __init__(self, key):
            self.isLeafNode = None
            self.key = key
            self.value = None
            self.branch = {}

        def __str__(self):
            return self.value

    def __init__(self, root_path, train_file, valid_file, binary=False):
        self.root = None
        self.rootPath = root_path
        self.trainFile = os.path.join(root_path, train_file)
        self.validFile = os.path.join(root_path, valid_file)
        self.trainData = self.__load_data('train')
        self.validData = self.__load_data('valid')
        self.validDataFeature = [data[:-1] for data in self.validData]
        self.validDataLabel = [data[-1] for data in self.validData]
        self.predict = []
        self.useBinaryStructure = binary

    @abstractmethod
    def evaluate_function(self, _data, key):
        pass

    @abstractmethod
    def branch_function(self, _data):
        pass

    def __make_tree(self, _data):
        test = {}
        for data in _data:
            if data[-1] not in test:
                test.update({data[-1]: 1})
            else:
                test[data[-1]] += 1
        test_s = sorted(test.items(), key=lambda x: (x[1], x[0]), reverse=True)
        if len(test_s) == 1:
            node = self.DecisionNode(-1)
            node.isLeafNode = True
            node.value = test_s[0][0]
            return node
        value_dict = {}
        for i in range(len(_data[0]) - 1):
            self.evaluate_function = getattr(self, 'evaluate_function')
            value_dict.update({i: self.evaluate_function(_data, i)})
        value_dict = sorted(value_dict.items(), key=lambda x: (x[1], x[0]), reverse=True)
        key_feature = value_dict[0][0]
        kf_dict = {}
        for data in _data:
            if data[key_feature] not in kf_dict:
                kf_dict.update({data.pop(key_feature): [1, [data]]})
            else:
                kf_dict[data[key_feature]][1].append(data)
                kf_dict[data[key_feature]][1][-1].pop(key_feature)
        for k in kf_dict:
            kf_dict[k] = self.__make_tree(kf_dict[k][1])
        node = self.DecisionNode(key_feature)
        node.branch = kf_dict
        node.value = test_s[0][0]
        return node

    def __make_binary_tree(self, _data):
        test = {}
        for data in _data:
            if data[-1] not in test:
                test.update({data[-1]: 1})
            else:
                test[data[-1]] += 1
        test_s = sorted(test.items(), key=lambda x: (x[1], x[0]), reverse=True)
        if len(test_s) == 1 or len(_data[0]) == 1:
            node = self.DecisionNode(-1)
            node.isLeafNode = True
            node.value = test_s[0][0]
            return node
        value_dict = {}
        for i in range(len(_data[0]) - 1):
            self.evaluate_function = getattr(self, 'evaluate_function')
            value_dict.update({i: self.evaluate_function(_data, i)})
        value_dict = sorted(value_dict.items(), key=lambda x: (x[1], x[0]), reverse=True)
        key_feature = value_dict[0][0]
        kf_dict = {}
        for data in _data:
            if data[key_feature] not in kf_dict:
                kf_dict.update({data.pop(key_feature): [1, [data]]})
            else:
                kf_dict[data[key_feature]][1].append(data)
                kf_dict[data[key_feature]][1][-1].pop(key_feature)
        branch_func = getattr(self, 'branch_function')
        target_gini = branch_func([d[-1] for d in _data])
        branch_dict = {}
        for k in kf_dict:
            branch_dict.update({k: [0.0, [], [], []]})
        for k in kf_dict:
            branch_dict[k][1].extend([d[-1] for d in kf_dict[k][1]])
            for ok in kf_dict:
                if ok != k:
                    branch_dict[k][2].extend([d[-1] for d in kf_dict[ok][1]])
                    branch_dict[k][3].extend(kf_dict[ok][1])
            Tgini = branch_func(branch_dict[k][1])
            Fgini = branch_func(branch_dict[k][2])
            branch_dict[k][0] = target_gini - (len(branch_dict[k][1]) / len(_data)) * Tgini - (
                    len(branch_dict[k][2]) / len(_data)) * Fgini
        b_dict = sorted(branch_dict.items(), key=lambda x: (x[1], x[0]), reverse=True)
        key_branch = b_dict[0][0]
        temp_dict = {}
        for data in branch_dict[key_branch][1]:
            if data in temp_dict:
                temp_dict[data] += 1
            else:
                temp_dict.update({data: 1})
        temp_dict = sorted(temp_dict.items(), key=lambda x: (x[1], x[0]), reverse=True)
        node = self.DecisionNode(key_feature)
        node.value = test_s[0][0]
        newnode = self.DecisionNode(-1)
        newnode.isLeafNode = True
        newnode.value = temp_dict[0][0]
        node.branch.update({key_branch: newnode})
        node.branch.update({'others': self.__make_binary_tree(branch_dict[key_branch][3])})
        return node

    def __load_data(self, _type):
        data = None
        if _type == 'train':
            with open(self.trainFile) as file:
                data = [i.replace('\n', '').split(',') for i in file.readlines()][1:]
        if _type == 'valid':
            with open(self.validFile) as file:
                data = [i.replace('\n', '').split(',') for i in file.readlines()][1:]
        return data

    def __get_predict(self, data, node):
        if node.isLeafNode:
            return node.value
        feature = data.pop(node.key)
        try:
            return self.__get_predict(data, node.branch[feature])
        except KeyError:
            return node.value

    def __get_binary_predict(self, data, node):
        if node.isLeafNode:
            return node.value
        feature = data.pop(node.key)
        try:
            return self.__get_predict(data, node.branch[feature])
        except KeyError:
            return self.__get_predict(data, node.branch['other'])

    def _get_predict(self, data):
        if self.useBinaryStructure:
            return self.__get_binary_predict(data, self.root)
        return self.__get_predict(data, self.root)

    def get_accuracy(self):
        cnt = 0
        for i in range(len(self.predict)):
            if self.predict[i] == self.validDataLabel[i]:
                cnt += 1
        return cnt / len(self.predict)

    def __print(self, node, depth):
        if node.isLeafNode:
            return
        for i in range(depth):
            print('\t', end='')
        print(node.key)
        for br in node.branch:
            self.__print(node.branch[br], depth + 1)

    def __str__(self):
        self.__print(self.root, 0)
        return ''

    def run(self):
        if not self.useBinaryStructure:
            self.root = self.__make_tree(self.trainData)
        else:
            self.root = self.__make_binary_tree(self.trainData)

    def run_validation(self):
        dataset = self.validDataFeature
        self.predict.clear()
        for data in dataset:
            try:
                self.predict.append(self._get_predict(data))
            except KeyError:
                pass


class ID3(BaseDecisionTree):
    def __init__(self, root_path, train_file, valid_file):
        super().__init__(root_path, train_file, valid_file)

    @staticmethod
    def calculate_entropy(_data):
        d_dict = {}
        for data in _data:
            if data in d_dict:
                d_dict[data] += 1
            else:
                d_dict.update({data: 1})
        total = sum([value for value in d_dict.values()])
        entropy = -sum([value / total * math.log2(value / total) for value in d_dict.values()])
        return entropy

    def evaluate_function(self, _data, key):
        d_entropy = self.calculate_entropy([s[-1] for s in _data])
        key_feature = [[s[key], s[-1]] for s in _data]
        feature_dict, feature_list, i = {}, [], 0
        for feature in key_feature:
            if feature[0] in feature_dict:
                feature_dict[feature[0]][0] += 1
                feature_list[feature_dict[feature[0]][1]].append(feature[1])
            else:
                feature_dict.update({feature[0]: [1, i]})
                feature_list.append([feature[1]])
                i += 1
        entropy = 0.0
        total = sum([s[0] for s in feature_dict.values()])
        for key in feature_dict:
            entropy += feature_dict[key][0] / total * self.calculate_entropy(feature_list[feature_dict[key][1]])
        return d_entropy - entropy


class C45(BaseDecisionTree):
    def __init__(self, root_path, train_file, valid_file):
        super().__init__(root_path, train_file, valid_file)

    @staticmethod
    def calculate_entropy(_data):
        d_dict = {}
        for data in _data:
            if data in d_dict:
                d_dict[data] += 1
            else:
                d_dict.update({data: 1})
        total = sum([value for value in d_dict.values()])
        entropy = -sum([value / total * math.log2(value / total) for value in d_dict.values()])
        return entropy

    def evaluate_function(self, _data, key):
        d_entropy = self.calculate_entropy([s[-1] for s in _data])
        key_feature = [[s[key], s[-1]] for s in _data]
        feature_dict, feature_list, i = {}, [], 0
        for feature in key_feature:
            if feature[0] in feature_dict:
                feature_dict[feature[0]][0] += 1
                feature_list[feature_dict[feature[0]][1]].append(feature[1])
            else:
                feature_dict.update({feature[0]: [1, i]})
                feature_list.append([feature[1]])
                i += 1
        entropy = 0.0
        total = sum([s[0] for s in feature_dict.values()])
        for key in feature_dict:
            entropy += feature_dict[key][0] / total * self.calculate_entropy(feature_list[feature_dict[key][1]])
        splitInfo = self.calculate_entropy([s[0] for s in key_feature])
        return (d_entropy - entropy) / splitInfo


class CART(BaseDecisionTree):
    def __init__(self, root_path, train_file, valid_file, use_binary):
        super().__init__(root_path, train_file, valid_file, use_binary)

    @staticmethod
    def branch_function(_data):
        class_dict, gini = {}, 1.0
        for data in _data:
            if data in class_dict:
                class_dict[data] += 1
            else:
                class_dict.update({data: 1})
        for key in class_dict:
            gini -= (class_dict[key] / len(_data)) ** 2
        return gini

    def evaluate_function(self, _data, key):
        key_feature = [[s[key], s[-1]] for s in _data]
        feature_dict = {}
        gini_d_k = 0.0
        for feature in key_feature:
            if feature[0] in feature_dict:
                feature_dict[feature[0]][0] += 1
                feature_dict[feature[0]][1].append(feature[-1])
            else:
                feature_dict.update({feature[0]: [1, [feature[-1]]]})
        for feature in feature_dict:
            gini = self.branch_function(feature_dict[feature][1])
            gini_d_k += feature_dict[feature][0] / len(key_feature) * gini
        return -gini_d_k


if __name__ == '__main__':
    tree = CART(r'./lab2_dataset_2020AIlab/lab2_dataset', 'train_0.csv', 'valid_0.csv', False)
    tree.run()
    tree.run_validation()
    print(tree.get_accuracy())

