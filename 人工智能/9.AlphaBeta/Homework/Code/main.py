import pygame
from renju import Renju
import sys
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ai_first', '-a', action='store_true', default=False, help='load model')
args = parser.parse_args()

class AI:
    class conv:
        live_3 = np.array([5, 8, 5])
        live_4 = np.array([10, 15, 15, 10])
        live_2 = np.array([1, 1])
        win = np.array([1, 1, 1, 1])
        n_win = np.array([1, 1, 1])

    def __init__(self, maxX, maxY, ai_first, depth):
        self.maxX, self.maxY = maxX, maxY
        self.baseScore = np.zeros((maxX, maxY))
        self.aiFirst = 0 if ai_first else 1
        self.depth = depth
        self.searchSeq = []
        for _i in range(maxX):
            for _j in range(maxY):
                dist = min(_i, self.maxX - _i - 1, _j, self.maxY - _j - 1)
                sc = dist * 3.0
                self.baseScore[_i, _j] = sc
                self.searchSeq.append((_i, _j, sc))
        self.searchSeq.sort(key=lambda x: x[2], reverse=True)
        self.padMap = None
        self.padMapNeg = None

    def is_legal(self, x, y):
        return -1 < x < self.maxX and -1 < y < self.maxY

    def __score(self, _map, x, y, _type):
        if _type == 1:
            line = np.zeros((4, 9))
            x += 4
            y += 4
            line[0] = self.padMap[x - 4:x + 5, y]
            line[1] = self.padMap[x, y - 4:y + 5]
            line[2] = [self.padMap[x + k, y + k] for k in range(-4, 5)]
            line[3] = [self.padMap[x + k, y - k] for k in range(-4, 5)]
            line_mat = line
            sc = 0.0
            for line in line_mat:
                for c in [self.conv.live_3, self.conv.live_4]:
                    sc += np.sum(np.convolve(line, c, 'valid'))
                if 4 in np.convolve(line, self.conv.win, 'valid'):
                    sc += 1000000
                if 3 in np.convolve(line, self.conv.n_win, 'valid'):
                    sc += 500000
            sc += self.baseScore[x - 4, y - 4]
        else:
            line = np.zeros((4, 9))
            x += 4
            y += 4
            line[0] = self.padMapNeg[x - 4:x + 5, y]
            line[1] = self.padMapNeg[x, y - 4:y + 5]
            line[2] = [self.padMapNeg[x + k, y + k] for k in range(-4, 5)]
            line[3] = [self.padMapNeg[x + k, y - k] for k in range(-4, 5)]
            line_mat = line
            sc = 0.0
            for line in line_mat:
                for c in [self.conv.live_3, self.conv.live_4]:
                    sc += np.sum(np.convolve(line, c, 'valid'))
                if -4 in np.convolve(line, self.conv.win, 'valid'):
                    sc -= 1000000
                if -3 in np.convolve(line, self.conv.n_win, 'valid'):
                    sc -= 500000
            sc -= self.baseScore[x - 4, y - 4]
        return sc

    # def min_max(self, _map, _x, _y, _type, d):
    #     if d == self.depth:
    #         return self.__score(_map, _x, _y, -_type)
    #     if _type == -1:
    #         ch, x, y = float('inf'), -1, -1
    #         _map[_x, _y] = 1
    #         self.padMapNeg[_x + 4, _y + 4] = 1
    #         for _i in range(_map.shape[0]):
    #             for _j in range(_map.shape[1]):
    #                 if int(_map[_i, _j]) == 0:
    #                     sc = self.min_max(_map.copy(), _i, _j, _type=1, d=d + 1)
    #                     if sc < ch:
    #                         ch, x, y = sc, _i, _j
    #                         # print(sc, _i, _j)
    #         self.padMapNeg[_x + 4, _y + 4] = 0
    #         return ch
    #     elif _type == 1:
    #         ch, x, y = float('-inf'), -1, -1
    #         _map[_x, _y] = -1
    #         self.padMap[_x + 4, _y + 4] = -1
    #         for _i in range(_map.shape[0]):
    #             for _j in range(_map.shape[1]):
    #                 if int(_map[_i, _j]) == 0:
    #                     sc = self.min_max(_map.copy(), _i, _j, _type=-1, d=d + 1)
    #                     if sc > ch:
    #                         ch, x, y = sc, _i, _j
    #         self.padMap[_x + 4, _y + 4] = 0
    #         return ch

    def alpha_beta(self, _map, _x, _y, _type, d, alpha, beta):
        if d == self.depth:
            return self.__score(_map, _x, _y, -_type)
        if _type == -1:
            _map[_x, _y] = 1
            self.padMapNeg[_x + 4, _y + 4] = 1
            for (_i, _j, _) in self.searchSeq:
                if int(_map[_i, _j]) == 0:
                    beta = min(beta, self.alpha_beta(_map.copy(), _i, _j, _type=1, d=d + 1, alpha=alpha, beta=beta))
                    if beta <= alpha:
                        self.padMapNeg[_x + 4, _y + 4] = 0
                        return beta
            self.padMapNeg[_x + 4, _y + 4] = 0
            return beta
        elif _type == 1:
            _map[_x, _y] = -1
            self.padMap[_x + 4, _y + 4] = -1
            for (_i, _j, _) in self.searchSeq:
                if int(_map[_i, _j]) == 0:
                    alpha = max(alpha,
                                self.alpha_beta(_map.copy(), _i, _j, _type=-1, d=d + 1, alpha=alpha, beta=beta))
                    if alpha >= beta:
                        self.padMap[_x + 4, _y + 4] = 0
                        return alpha
            self.padMap[_x + 4, _y + 4] = 0
            return alpha

    def AI_search(self, _map):
        alpha, beta, x, y = float('-inf'), float('inf'), -1, -1
        for (_i, _j, _) in self.searchSeq:
            if int(_map[_i, _j]) == 0:
                ch = self.alpha_beta(_map.copy(), _i, _j, _type=-1, d=1, alpha=alpha, beta=beta)
                print(ch, _i, _j)
                if ch > alpha:
                    alpha, x, y = ch, _i, _j
        return y, x

    # def AI_search(self, _map, _type, d=0):
    #     if d==self.depth:
    #         return
    #     ch, x, y = -10000, -1, -1
    #     for _i in range(_map.shape[0]):
    #         for _j in range(_map.shape[1]):
    #             if int(_map[_i, _j]) == 0:
    #                 sc = self.__score(_map, _i, _j)
    #                 if sc > ch:
    #                     ch, x, y = sc, _i, _j
    #     return y, x

    def go(self, cur):
        _map = np.zeros((self.maxX, self.maxY))
        for step in cur:
            i, j = step['coord'].y, step['coord'].x
            _map[i, j] = 1 if self.aiFirst == step['type'] else -1
        self.padMap = np.pad(_map, ((4, 4), (4, 4)), 'constant', constant_values=(-1, -1))
        self.padMapNeg = np.pad(_map, ((4, 4), (4, 4)), 'constant', constant_values=(1, 1))
        bestPos = self.AI_search(_map)
        return bestPos
        # return random.randint(0, self.maxX - 1), random.randint(0, self.maxY - 1)


if __name__ == '__main__':
    pygame.init()  # pygame初始化
    size = width, height = 460, 460
    screen = pygame.display.set_mode(size, 0, 32)
    pygame.display.set_caption('五子棋')
    font = pygame.font.Font('simhei.ttf', 48)
    clock = pygame.time.Clock()  # 设置时钟
    game_over = False
    renju = Renju()  # Renju是核心类，实现落子及输赢判断等
    renju.init()  # 初始化
    AI_CUR = args.ai_first
    ai = AI(renju.edge, renju.edge, AI_CUR, 4)
    renju.drop_at(5, 5)
    renju.drop_at(4, 5)
    renju.drop_at(6, 5)
    renju.drop_at(5, 6)

    while True:
        clock.tick(20)  # 设置帧率
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if AI_CUR and (not game_over):
                i, j = ai.go(renju.ball_coord)
                print(i, j)
                if renju.check_at(i, j):  # 检查(i,j)位置能否被占用，如未被占用返回True
                    renju.drop_at(i, j)  # 在(i,j)位置落子，该函数将黑子或者白子画在棋盘上
                    if renju.check_over():  # 检查是否存在五子连线，如存在则返回True
                        if renju.black_turn:  # check_at会切换落子的顺序，所以轮到黑方落子，意味着最后落子方是白方，所以白方顺利
                            text = '白方获胜，游戏结束！'
                        else:
                            text = '黑方获胜，游戏结束！'
                        gameover_text = font.render(text, True, (255, 0, 0))
                        renju.chessboard().blit(gameover_text, (round(width / 2 - gameover_text.get_width() / 2),
                                                                round(height / 2 - gameover_text.get_height() / 2)))
                        game_over = True
                    AI_CUR = not AI_CUR
            if event.type == pygame.MOUSEBUTTONDOWN and (not game_over):
                if event.button == 1:  # 按下的是鼠标左键
                    i, j = renju.get_coord(event.pos)  # 将物理坐标转换成矩阵的逻辑坐标
                    if renju.check_at(i, j):  # 检查(i,j)位置能否被占用，如未被占用返回True
                        renju.drop_at(i, j)  # 在(i,j)位置落子，该函数将黑子或者白子画在棋盘上
                        if renju.check_over():  # 检查是否存在五子连线，如存在则返回True
                            if renju.black_turn:  # check_at会切换落子的顺序，所以轮到黑方落子，意味着最后落子方是白方，所以白方顺利
                                text = '白方获胜，游戏结束！'
                            else:
                                text = '黑方获胜，游戏结束！'
                            gameover_text = font.render(text, True, (255, 0, 0))
                            renju.chessboard().blit(gameover_text, (round(width / 2 - gameover_text.get_width() / 2),
                                                                    round(height / 2 - gameover_text.get_height() / 2)))
                            game_over = True
                    AI_CUR = not AI_CUR
                else:
                    print('此位置已占用，不能在此落子')

        screen.blit(renju.chessboard(), (0, 0))
        pygame.display.update()
