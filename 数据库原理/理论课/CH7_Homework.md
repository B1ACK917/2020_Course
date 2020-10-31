# 数据库原理CH7作业

<p align="right"> 18340040 冯大纬</p>

## P353-7.2

**List all nontrivial functional dependencies satisfied by the relation of Figure 7.18.**

![image-20201012163749052](https://maho.kyoka.cloud/images/2020/10/17/Figure7.18.png)

Answer:

​	A->B, 因为$a_1$被唯一映射到$b_1$,$a_2$被唯一映射到$b_1$,且B不是A的子集

​	C->B, 因为$c_1$被唯一映射到$b_1$,$c_2$被唯一映射到$b_1$,$c_3$被唯一映射到$b_1$,且B不是C的子集

​	AC->B,  因为$a_1c_1$被唯一映射到$b_1$,$a_1c_2$被唯一映射到$b_1$,$a_2c_1$被唯一映射到$b_1$,$a_2c_3$被唯一映射到$b_1$,且B不是AC的子集

## P353-7.3

**Explain how functional dependencies can be used to indicate the following:**

- **A one-to-one relationship set exists between entity sets student and instructor.** 
- **A many-to-one relationship set exists between entity sets student and instructor.**

Answer:

​	假设K(x)表示关系x的主键

- ​	**A one-to-one relationship set exists between entity sets student and instructor.**

  若`K(student)->K(instructor)`且`K(instructor)->K(student)`，那么student的每一个主键唯一对应一个instructor的主键，且instructor的每一个主键唯一对应一个student的主键，所以student和instructor的主键一一对应，即one-to-one关系。

- ​	**A many-to-one relationship set exists between entity sets student and instructor.**

  若`K(student)->K(instructor)`，那么student的每一个主键唯一对应一个instructor的主键，且对instructor的主键对应关系没有约束，所以可以有多个student的主键对应一个instructor的主键，即many-to-one关系。

