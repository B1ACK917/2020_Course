import numpy
import torch


class replay_buffer:
    def __init__(self, capacity, N_state, gamma, embedding_dim):
        self.__capacity = capacity
        self.gamma = gamma
        self.__states = numpy.zeros((capacity, N_state), dtype=numpy.int)
        self.__actions = numpy.zeros((capacity, 1), dtype=numpy.long)
        self.__rewards = numpy.zeros((capacity, 1), dtype=numpy.float32)
        self.__done = numpy.zeros((capacity, 1), dtype=numpy.bool)
        self.__next_states = numpy.zeros((capacity, N_state), dtype=numpy.int)
        self.__embedding = torch.zeros((capacity, embedding_dim), dtype=torch.float32)
        self.__id = 0
        self.__cnt = 0
        self.__T_limit = 30

    def push(self, state, action, done, reward, next_state, embedding=None):
        if self.__cnt < self.__capacity:
            self.__cnt += 1
        self.__states[self.__id] = state
        self.__actions[self.__id] = action
        self.__rewards[self.__id] = reward
        self.__done[self.__id] = done
        self.__next_states[self.__id] = next_state
        if embedding != None:
            self.__embedding[self.__id] = embedding
        self.__id += 1
        if self.__id == self.__capacity:
            self.__id = 0

    def random_get(self):  # N-step # state, action, reward_t, next_state_t, gamma_t
        id = numpy.random.randint(self.__cnt)
        _id = id
        for i in range(self.__T_limit):
            if self.__done[_id]:
                return self.__states[id], self.__actions[id], self.__rewards[_id] * self.gamma ** i, self.__states[
                    _id], 0
            _id += 1
            if _id == self.__capacity:
                _id = 0
        return self.__states[id], self.__actions[id], numpy.zeros((1), dtype=numpy.float32), self.__next_states[
            _id], self.gamma ** self.__T_limit

    def get_sample(self, batch_size):
        state = []
        action = []
        reward_t = []
        next_state_t = []
        gamma_t = []
        for i in range(batch_size):
            _state, _action, _reward_t, _next_state_t, _gamma_t = self.random_get()
            state.append(_state)
            action.append(_action)
            reward_t.append(_reward_t)
            next_state_t.append(_next_state_t)
            gamma_t.append(_gamma_t)
        return state, action, reward_t, next_state_t, gamma_t
