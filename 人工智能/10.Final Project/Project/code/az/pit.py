import Arena
from MCTS import MCTS
from othello.OthelloGame import OthelloGame
from othello.OthelloPlayers import *
from othello.pytorch.NNet import NNetWrapper as NNet
import argparse
import numpy as np
from utils import *

parser = argparse.ArgumentParser()
parser.add_argument('--ai_first', '-a', action='store_true', default=False, help='Whether AI plays first')
args = parser.parse_args()

g = OthelloGame(8)

human_vs_cpu = True

# all players
rp = RandomPlayer(g).play
gp = GreedyOthelloPlayer(g).play
hp = HumanOthelloPlayer(g).play

# nnet players
n1 = NNet(g)
n1.load_checkpoint('./pretrained_models/', '8x8_100checkpoints_best.pth.tar')
args1 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
mcts1 = MCTS(g, n1, args1)
n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

if human_vs_cpu:
    player2 = hp
else:
    n2 = NNet(g)
    n2.load_checkpoint('./pretrained_models/', '8x8_100checkpoints_best.pth.tar')
    args2 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
    mcts2 = MCTS(g, n2, args2)
    n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))

    player2 = n2p

print(args.ai_first)
if args.ai_first:
    arena = Arena.Arena(n1p, player2, g, display=OthelloGame.display)
else:
    arena = Arena.Arena(player2, n1p, g, display=OthelloGame.display)

print(arena.playGames(2, verbose=True))
