# 数据库原理CH7作业

<p align="right"> 18340040 冯大纬 </p>

## P357-7.30

![image-20201017173239926](https://maho.kyoka.cloud/images/2020/10/17/image-20201017173239926.png)

![image-20201017173328990](https://maho.kyoka.cloud/images/2020/10/17/image-20201017173328990.png)

Answer:

a.
$$
B\to BD (B\to D)\\
BD\to ABD(D\to A)\\
ABD\to ABCD(A\to BCD)\\
ABCD\to ABCDE(BC\to DE)\\
所以B^+=ABCDE
$$
b.
$$
A\to BCD\\
A\to ABCD\\
BC\to DE\\
ABCD\to ABCDE\\
A\to ABCDE\\
AG\to ABCDEG
$$
c.
$$
A\to BCD和BC\to DE说明D为第一个依赖的无关项，所以化简为\\
A\to BC\\
BC\to DE\\
B\to D\\
D\to A\\
由BC\to DE和B\to D说明D是无关项，化简为\\
A\to BC\\
BC\to E\\
B\to D\\
D\to A\\
因为B^+=ABCDE\\
所以B\to C，故BC\to E可化简为B\to E，和B\to D结合为\\
A\to BC\\
B\to DE\\
D\to A\\
$$
d.
$$
由c题知函数的正则依赖为：\\
A\to BC\\
B\to DE\\
D\to A\\
所以3NF分解为\{ABC\},\{BDE\},\{DA\}，\{AG\}
$$
e.
$$
由A\to BCD，分解为\{ABCD\},\{AEG\}\\
因为前两个函数依赖能够推出A\to E\\
所以将\{AEG\}分解为\{AE\},\{AG\}\\
故BCNF分解为\{ABCD\},\{AE\},\{AG\}
$$

## P360-7.40

![image-20201017190037444](https://maho.kyoka.cloud/images/2020/10/17/image-20201017190037444.png)

Answer:

考虑下面这个表，符合$A\to \to BC$

| A    | B    | C    | D    |
| ---- | ---- | ---- | ---- |
| a1   | b1   | c1   | d2   |
| a1   | b2   | c2   | d1   |
| a1   | b1   | c1   | d1   |
| a1   | b2   | c2   | d2   |

很明显，为了满足$A\to\to B$的条件$t_1[B]=t_3[B]$，则只有如下四种可能的情况：

1. $t_1=r_1,t_3=r_3$

   那么$t_3[CD]=c_1d_1$

   当$t_2=r_2时，t_2[CD]=c_2d_1$,不满足$t_3[CD]=t_2[CD]$

   当$t_2=r_4时，t_2[CD]=c_2d_2$,不满足$t_3[CD]=t_2[CD]$

2. $t_1=r_3,t_3=r_1$

   那么$t_3[CD]=c_1d_2$

   当$t_2=r_2时，t_2[CD]=c_2d_1$,不满足$t_3[CD]=t_2[CD]$

   当$t_2=r_4时，t_2[CD]=c_2d_2$,不满足$t_3[CD]=t_2[CD]$

3. $t_1=r_2,t_3=r_4$

   那么$t_3[CD]=c_2d_2$

   当$t_2=r_1时，t_2[CD]=c_1d_2$,不满足$t_3[CD]=t_2[CD]$

   当$t_2=r_3时，t_2[CD]=c_1d_1$,不满足$t_3[CD]=t_2[CD]$

4. $t_1=r_4,t_3=r_2$

   那么$t_3[CD]=c_2d_1$

   当$t_2=r_1时，t_2[CD]=c_1d_2$,不满足$t_3[CD]=t_2[CD]$

   当$t_2=r_3时，t_2[CD]=c_1d_1$,不满足$t_3[CD]=t_2[CD]$

所以$A\to\to B$不成立