# 文本数据集的简单处理与K最近邻算法的实现

<p align="right"> 18340040 冯大纬

## 1.实验任务：文本处理与TF-IDF

- ### 实验内容

  ​	将数据集“semeval.txt”的数据表示成TF-IDF矩阵

- ### 实验原理

  ![image-20200911172731567](./ScreenShots/2.png)

  ![image-20200911172652968](./ScreenShots/1.png)

  ![image-20200911172749048](./ScreenShots/3.png)

- ### 伪代码流程图

  ```c
  func Generate_TF_TDF(Sentence:An array with all sentences):
  	Word_Dict:
  ```

  

- ### 关键代码

  ```python
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
          IDF_MAT[WordList.index(key)] = math.log10(len(data) / WordDict[key])
      TF_IDF_MAT = [[] for i in range(len(data))]
      for i in range(len(TF_IDF_MAT)):
          TF_IDF_MAT[i] = mult(IDF_MAT, TF_MAT[i])
  ```

  ​	这部分代码是从词表字典中构建TF矩阵，IDF矩阵的过程，最后将TF矩阵的每一行和IDF矩阵点乘获得TF-IDF矩阵

## 2.实验任务：KNN分类

- ### 实验内容

  ​	使用KNN进行分类任务。数据文件为classification_dataset，其中train_set用于 训练。validation_set是验证集，通过调节K值、不同距离度量等参数来筛选准确 率最好的一组参数。在测试集test上应用该参数做预测，输出结果保存为“学号_ 姓名拼音_KNN_classification.csv”

- ### 实验原理

- ### 伪代码流程图

- ### 关键代码

- ### 实验结果分析

## 3.实验任务：KNN回归

- ### 实验内容

  ​	使用KNN进行回归任务。数据文件为regression_dataset，其中train_set用于训 练。validation_set是验证集，通过调节K值、不同距离度量等参数来筛选相关系 数最好的一组参数。在测试集test上应用该参数做预测，输出结果保存为“学号_ 姓名拼音_KNN_regression.csv”

- ### 实验原理

- ### 伪代码流程图

- ### 关键代码

- ### 实验结果分析