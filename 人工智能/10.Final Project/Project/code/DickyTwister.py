from DQN import *
import tqdm
import pygame
import time
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ai_first', '-a', action='store_true', default=False, help='Whether AI plays first')
parser.add_argument('--train', '-t', action='store_true', default=False, help='Train Mode')
parser.add_argument('--play', '-p', action='store_true', default=False, help='Play Mode (use normal DQN)')
parser.add_argument('--cheat', '-c', action='store_true', default=False, help='Cheat Mode (use Alpha Zero)')
args = parser.parse_args()


class DickyTwister:
    def __init__(self):
        self.maxIter = 50000
        self.saveIter = 500
        self.Oth_N = None
        self.background = None
        self.gameWidth = None
        self.box = None
        self.screen = None
        self.savePath = 'model'
        self.agentSavePath = os.path.join(self.savePath, 'agent.pth')
        self.lossLogSavePath = os.path.join(self.savePath, 'loss.txt')

    def train(self):
        agent = DQN()

        for ite in tqdm.tqdm(range(self.maxIter), ncols=100):
            game_state = Game()
            round_ = 0

            a_zip = b_zip = None
            a_zip_list = b_zip_list = []

            while True:
                round_ += 1
                s = game_state.Get_State()
                a = agent.eps_greedy(s, game_state, 1)
                game_state.Add(1, a)
                done, score = game_state.Gameover()
                r = score
                s_ = game_state.Get_State()

                a_zip = [s, a, r]

                if b_zip != None:
                    s, a, r_lst = b_zip
                    a_zip_list.append([s, a, done, r_lst - r, s_])

                if done:
                    break

                s = game_state.Get_State()
                a = agent.eps_greedy(s, game_state, -1)
                game_state.Add(-1, a)
                done, score = game_state.Gameover()
                r = -score
                s_ = game_state.Get_State()

                b_zip = [s, a, r]

                if a_zip != None:
                    s, a, r_lst = a_zip
                    b_zip_list.append([s, a, done, r_lst - r, s_])

                if done:
                    break

            for s, a, done, r, s_ in a_zip_list:
                agent.Store_transition(s, a, done, r, s_)
            for s, a, done, r, s_ in b_zip_list:
                agent.Store_transition(s, a, done, r, s_)

            agent.learn()

            if not os.path.exists(self.savePath):
                os.mkdir(self.savePath)
            if (ite + 1) % self.saveIter == 0:
                torch.save(agent.Q.state_dict(), os.path.join(self.savePath, '{}'.format(ite), 'agent.pth'))
        with open(self.lossLogSavePath, 'w') as file:
            file.write(str(agent.lossLog) + '\n')

    def init_pygame(self):
        self.Oth_N = 8
        self.background = pygame.image.load('board.jpg')
        self.gameWidth = 400
        self.box = self.gameWidth / (8 + 2)
        self.screen = pygame.display.set_mode((self.gameWidth, self.gameWidth))
        pygame.display.set_caption('DickyTwister')

    def show_board(self, board, last_pos=0, valid=None):
        surf = self.screen
        surf.blit(self.background, (0, 0))

        BOUNDS = [((self.box, self.box), (self.box, self.gameWidth - self.box)),
                  ((self.gameWidth - self.box, self.box), (self.box, self.box)),
                  ((self.gameWidth - self.box, self.gameWidth - self.box), (self.gameWidth - self.box, self.box)),
                  ((self.gameWidth - self.box, self.gameWidth - self.box), (self.box, self.gameWidth - self.box))]
        for line in BOUNDS:
            pygame.draw.line(surf, (0, 0, 0), line[0], line[1], 1)
        for i in range(self.Oth_N - 1):
            pygame.draw.line(surf, (0, 0, 0),
                             (self.box * (2 + i), self.box),
                             (self.box * (2 + i), self.gameWidth - self.box))
            pygame.draw.line(surf, (0, 0, 0),
                             (self.box, self.box * (2 + i)),
                             (self.gameWidth - self.box, self.box * (2 + i)))

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 1:
                    t = (int((j + 1.5) * self.box), int((i + 1.5) * self.box))
                    pygame.draw.circle(surf, (0, 0, 0), t, int(self.box / 3))
                if board[i][j] == -1:
                    t = (int((j + 1.5) * self.box), int((i + 1.5) * self.box))
                    pygame.draw.circle(surf, (255, 255, 255), t, int(self.box / 3))

        for (x, y) in valid:
            t = (int((y + 1.5) * self.box), int((x + 1.5) * self.box))
            pygame.draw.circle(surf, (0, 255, 0), t, int(self.box / 3))

        if isinstance(last_pos, tuple):
            (x, y) = last_pos
            t = (int((y + 1.5) * self.box), int((x + 1.5) * self.box))
            pygame.draw.circle(surf, (255, 0, 0), t, int(self.box / 8))

        pygame.display.flip()

    def play(self):
        self.init_pygame()
        human_first = 1
        ai = DQN()
        ai.load('model/agent50000.pth')
        game = Game()
        running = True

        if human_first:
            step = 1
            ai_color = 1
            human_color = -1

        else:
            step = 0
            ai_color = -1
            human_color = 1

        grid = 0
        while running:
            if human_color == 1:
                valid_pos = game.Get_Valid_Pos(game.black_chess, game.white_chess)
            else:
                valid_pos = game.Get_Valid_Pos(game.white_chess, game.black_chess)

            self.show_board(game.board, grid, valid_pos)

            while step % 2 == 0:
                if len(valid_pos) == 0:
                    time.sleep(1)
                    step += 1
                    break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        step += 1
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        grid = (int(event.pos[1] / (self.box + .0) - 1), int(event.pos[0] / (self.box + .0) - 1))
                        if 0 <= grid[0] < 8 and 0 <= grid[1] < 8:
                            if grid in valid_pos:
                                a = self.Oth_N * grid[0] + grid[1]
                                game.Add(human_color, a)
                                self.show_board(game.board, grid)
                                time.sleep(1)
                                step += 1
                                break

            # 电脑走
            begin_time = time.time()

            s = game.Get_State()
            a = ai.eps_greedy(s, game, ai_color, 0)
            game.Add(ai_color, a)
            grid = (a // self.Oth_N, a % self.Oth_N)
            self.show_board(game.board, grid)
            print('AI step: {}'.format(grid))
            step += 1

            end_time = time.time()
            cal_time = end_time - begin_time
            print('calculating time: %.4f' % cal_time)

    @staticmethod
    def cheat(ai_first):
        from az import Arena
        from az.MCTS import MCTS
        from az.othello.OthelloGame import OthelloGame
        from az.othello.pytorch.NNet import NNetWrapper as NNet
        from az.othello.OthelloPlayers import HumanOthelloPlayer
        from az.utils import dotdict
        import numpy as np

        g = OthelloGame(8)

        human_vs_cpu = True
        hp = HumanOthelloPlayer(g).play

        # nnet players
        n1 = NNet(g)
        n1.load_checkpoint('./az/pretrained_models/', '8x8_100checkpoints_best.pth.tar')
        args1 = dotdict({'numMCTSSims': 150, 'cpuct': 1.0})
        mcts1 = MCTS(g, n1, args1)
        n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

        if human_vs_cpu:
            player2 = hp
        else:
            n2 = NNet(g)
            n2.load_checkpoint('./az/pretrained_models/', '8x8_100checkpoints_best.pth.tar')
            args2 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
            mcts2 = MCTS(g, n2, args2)
            n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))

            player2 = n2p

        if not ai_first:
            arena = Arena.Arena(n1p, player2, g, display=OthelloGame.display)
        else:
            arena = Arena.Arena(player2, n1p, g, display=OthelloGame.display)

        os.system('')
        win = arena.playGame(-1 if ai_first else 1, verbose=True)
        if win == -1:
            print('{} won'.format('AI' if ai_first else 'Human'))
        elif win == 1:
            print('{} won'.format('Human' if ai_first else 'AI'))
        else:
            print('Draw')


if __name__ == '__main__':
    dt = DickyTwister()
    if args.train:
        dt.train()
    if args.play:
        dt.play(args.ai_first)
    if args.cheat:
        dt.cheat(args.ai_first)
    else:
        parser.print_help()
