# Files

## DickyTwister.py

主代码，DickyTwister类

启动参数如下

| 参数             | 作用                           |
| ---------------- | ------------------------------ |
| --train    -t    | 训练模型                       |
| --ai_first    -a | AI先手（默认人类先手）         |
| --play    -p     | Play模式（使用EVA+DQN模型）    |
| --cheat    -c    | Cheat模式（使用AlphaZero模型） |
| --help    -h     | 输出帮助信息                   |

## model.py

Q网络模型

## DQN.py

包含DQN及EVA改进部分的代码

## ReplayBuffer.py

经验池

## Othello.py

训练时使用的黑白棋Backend

## az/*.py

AlphaZero相关代码（Cheat Mode调用）