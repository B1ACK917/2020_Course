# a = [0.231, 124124, 0.213]
# b = [0.231, 124124, 0.23]
# with open('a.txt', 'w') as file:
#     file.write(str(a) + '\n')
#     file.write(str(b))
# with open('a.txt', 'r') as file:
#     a = file.readline().replace('[', '').replace(']', '').split(', ')
#     a = [float(item) for item in a]
#     print(a)
#     a = file.readline().replace('[', '').replace(']', '').split(', ')
#     a = [float(item) for item in a]
#     print(a)

KBegin, KEnd = 1,2
for Vote in [True]:
    for Algo in ['L1']:
        x, y = [], []
        begin = time.perf_counter()
        print(
            'Training Now Running, With Arg K in Range[{},{}), Distance Algorithm is {}, Voting With Weight is {}'.format(
                KBegin, KEnd, Algo, 'Used' if Vote else 'Not Used'))
        for i in range(KBegin, KEnd):
            Model = KNN('train_set.csv', 'validation_set.csv', 'test_set.csv', K=i, distance_rule=Algo,
                        vote_rule=Vote)
            Model.run()
            x.append(i)
            y.append(Model.get_accuracy())
        print('Training Completed, Average Time: {} s'.format(time.perf_counter() - begin / len(x)))
        with open(r'result/result_{}_Vote-{}.txt'.format(Algo, Vote), 'w') as file:
            file.write(str(x) + '\n')
            file.write(str(y))