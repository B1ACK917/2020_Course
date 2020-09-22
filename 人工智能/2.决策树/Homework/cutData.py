def cut(path, _file):
    with open(path + _file) as file:
        data = file.readlines()
        with open(path + '/train_0.csv', 'w') as output:
            output.write(data[0])
            for i in range(1, len(data) // 10 * 9):
                output.write(data[i])
        with open(path + '/valid_0.csv', 'w') as output:
            output.write(data[0])
            for i in range(len(data) // 10 * 9, len(data)):
                output.write(data[i])


if __name__ == '__main__':
    cut(r'./lab2_dataset_2020AIlab/lab2_dataset', '/car_train.csv')
