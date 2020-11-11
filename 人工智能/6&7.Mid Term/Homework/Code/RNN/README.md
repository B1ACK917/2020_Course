# 文件说明

## dataloader.py

loader，会从当前目录下的`dataset`文件夹中寻找`Laptops_Train.xml`并读取数据，从`wordvec`中寻找词向量来生成数据集

## utils.py

封装Focal Loss，CRF以及计算precision、recall、accuracy、F1 Score的函数

## train.py

训练过程，具有以下参数

| 参数           | 简化参数 | 说明                             |
| -------------- | -------- | -------------------------------- |
| --load         | -l       | 是否使用硬盘中存在的模型继续训练 |
| --learningrate | -lr      | 学习率                           |
| --iteration    | -i       | 迭代次数上限                     |
| --save_ite     | -s       | 多少轮保存一次模型结构           |