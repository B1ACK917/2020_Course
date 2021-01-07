import torch
import torch.nn as nn
from Othello import *
from model import QNet
from replaybuffer import replay_buffer

BOARD_SIZE = 8
N_STATE = BOARD_SIZE ** 2
N_ACTION = N_STATE + 1

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


class DQN:
    def __init__(self, buffer_size=10000, gamma=0.99, embedding_dim=512, Lambda=0.4):
        self.Q, self.Q_ = QNet(embedding_dim).to(device), QNet(embedding_dim).to(device)
        self.learningRate = 1e-3
        self.batchSize = 32
        self.gamma = gamma
        self.Lambda = Lambda
        self.buffer = replay_buffer(buffer_size, N_STATE, gamma, embedding_dim)
        # self.transitionsStorage = 200
        self.updateTime = 10
        # self.transitions = np.zeros((self.transitionsStorage, 2 * N_STATE + 2))
        # self.transitions_index = 0
        self.learn_iter = 0

        self.optimizer = torch.optim.Adam(self.Q.parameters(), lr=self.learningRate)
        self.criteria = nn.MSELoss()
        self.lossLog = []

    def eps_greedy(self, x, game_state, color, Epsilon=0.1):
        if color == 1:
            available_pos = game_state.Get_Valid_Pos(game_state.black_chess, game_state.white_chess)
        else:
            available_pos = game_state.Get_Valid_Pos(game_state.white_chess, game_state.black_chess)

        available_pos = list(map(lambda a: game_state.board_size * a[0] + a[1], available_pos))
        if not available_pos:
            return 64

        if np.random.uniform() < Epsilon:
            action = np.random.choice(available_pos, 1)[0]
        else:
            x = torch.tensor(x, dtype=torch.float)
            x = x.view(1, -1).to(device)
            net_output = self.Q(x)
            actions_values = net_output[0]

            ava_actions = torch.tensor(
                actions_values.index_select(0, torch.tensor(available_pos, dtype=torch.long).to(device)))

            _, action_ind = torch.max(ava_actions, 0)
            action = available_pos[action_ind]
        return action

    def Store_transition(self, s, a, done, r, s_):
        self.buffer.push(s, a, done, r, s_)

    def learn(self):
        for step in range(100):
            if self.learn_iter % self.updateTime == 0:
                self.Q_.load_state_dict(self.Q.state_dict())
            self.learn_iter += 1

            batch_state, batch_action, batch_reward_t, batch_next_state_t, batch_gamma_t = self.buffer.get_sample(
                self.batchSize)

            batch_state = torch.tensor(batch_state, dtype=torch.float).to(device)
            batch_action = torch.tensor(batch_action, dtype=int).to(device)

            batch_reward_t = torch.tensor(batch_reward_t, dtype=torch.float).to(device)
            batch_next_state_t = torch.tensor(batch_next_state_t, dtype=torch.float).to(device)
            batch_gamma_t = torch.tensor(batch_gamma_t, dtype=torch.float).to(device)

            batch_Qa = self.Q(batch_state).gather(1, batch_action)
            batch_Qexp = self.Lambda * batch_Qa + (1 - self.Lambda) * (
                        batch_reward_t.view(-1, 1) + torch.mul(batch_gamma_t.view(-1, 1),
                                                               torch.max(self.Q(batch_next_state_t), 1)[0].view(-1, 1)))

            loss = self.criteria(batch_Qa, batch_Qexp)
            self.optimizer.zero_grad()
            self.lossLog.append(loss.item())
            loss.backward()
            self.optimizer.step()

    def load(self, saved_path):
        map_location = None if torch.cuda.is_available() else 'cpu'
        checkpoint = torch.load(saved_path, map_location=map_location)
        self.Q.load_state_dict(checkpoint['state_dict'])
