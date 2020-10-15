class dataLoader:
    def __init__(self, data_path, skip_head=True, crop_instant=True):
        self.__originData = None
        self.__data = None
        self.__dataNum = None
        self.__dataPath = data_path
        self.__skipHead = skip_head
        self.__cropInstant = crop_instant

    def __load(self):
        with open(self.__dataPath) as file:
            if self.__skipHead:
                file.readline()
            if self.__cropInstant:
                self.__originData = [i.replace('\n', '').split(',')[1:] for i in file.readlines()]
            else:
                self.__originData = [i.replace('\n', '').split(',') for i in file.readlines()]
            self.__dataNum = len(self.__originData)

    @staticmethod
    def __one_hot(features, __sort=True):
        unique_f = list(set(features))
        std_vec = [0 for i in range(len(unique_f))]
        one_hot_code = []
        if __sort:
            unique_f.sort()
        for feature in features:
            vec = std_vec[:]
            vec[unique_f.index(feature)] = 1
            one_hot_code.append(vec)
        return one_hot_code

    def __clean(self):
        tmp_data = [data[1:] for data in self.__originData]
        self.__data = [[] for i in range(self.__dataNum)]
        for i in range(8):
            oh_code = self.__one_hot([data[i] for data in tmp_data])
            for j in range(self.__dataNum):
                self.__data[j].extend(oh_code[j])
        for i in range(8, len(tmp_data[0])):
            for j in range(self.__dataNum):
                self.__data[j].append(float(tmp_data[j][i]))
        # label = [float(data[-1]) for data in tmp_data]
        # max_lb = max(label)
        # label = [d / max_lb for d in label]
        # for j in range(self.__dataNum):
        #     self.__data[j].append(label[j])

    def load(self):
        self.__load()
        self.__clean()
        return self.__data


if __name__ == '__main__':
    d = dataLoader('data/train.csv')
    # d.test()
    print(d.load()[:10])
