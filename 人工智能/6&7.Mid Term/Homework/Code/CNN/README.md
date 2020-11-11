# 文件说明

## loader.py

读入cifar数据集，如果当前目录内不存在`cifar-10-batches-py`，则会从https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz下载数据集

## model.py

构建模型，根据`FLOW_PATH`及`NUM_LAYERS`自动构建网络

## model_shape.py

记录模型结构，会通过反射机制被`model.py`引用

## cf10.py

训练过程，具有以下参数

| 参数            | 简化参数 | 说明                                                     |
| --------------- | -------- | -------------------------------------------------------- |
| --model         | -m       | 使用哪一种model，model结构必须在model_shape.py中存在定义 |
| --load          | -l       | 是否使用硬盘中存在的模型继续训练                         |
| --learningrate  | -lr      | 学习率                                                   |
| --iteration     | -i       | 迭代次数上限                                             |
| --save_ite      | -s       | 多少轮保存一次模型结构                                   |
| --normalization | -n       | 是否使用归一化                                           |

使用示例

```
python ./cf10.py -m AlexNet -lr 1e-4 -i 1000 -s 100 -n
# 使用AlexNet模型，学习率1e-4，训练1000轮，每100轮保存一次模型，使用归一化
```

