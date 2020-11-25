import time


class Solution:
    def __init__(self, maze):
        self.__maze = maze
        flag = 0
        for i in range(len(maze)):
            j = maze[i].find('S')
            k = maze[i].find('E')
            if j != -1:
                self.__startX, self.__startY = i, j
                self.__maze[i] = self.__maze[i].replace('S', '0')
                flag += 1
            if k != -1:
                self.__endX, self.__endY = i, k
                self.__maze[i] = self.__maze[i].replace('E', '0')
                flag += 1
            if flag == 2:
                break
        self.maxX, self.maxY = len(maze), len(maze[0])

    def test(self):
        print(self.__maze)
        print(self.__startX, self.__startY, self.__endX, self.__endY)

    @staticmethod
    def __get_dist(x0, y0, x1, y1, func='norm'):
        if func == 'norm':
            return ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5
        elif func == 'man':
            return abs(x0 - x1) + abs(y0 - y1)
        else:
            return 0

    def __is_legal(self, x, y):
        return 0 <= x < self.maxX and 0 <= y < self.maxY and self.__maze[x][y] == '0'

    def __is_success(self, x, y):
        return (x, y) == (self.__endX, self.__endY)

    def __draw(self, path):
        for i in range(self.maxX):
            for j in range(self.maxY):
                if (i, j) == (self.__startX, self.__startY):
                    print('\033[44;1m S \033[0m', end='')
                elif (i, j) == (self.__endX, self.__endY):
                    print('\033[44;1m E \033[0m', end='')
                elif (i, j) in path:
                    print('\033[42;1m   \033[0m', end='')
                elif self.__maze[i][j] == '0':
                    print('\033[47;1m   \033[0m', end='')
                else:
                    print('\033[41;1m   \033[0m', end='')
            print('')
        print('')

    def __swap(self):
        self.__startX, self.__startY, self.__endX, self.__endY = self.__endX, self.__endY, self.__startX, self.__startY

    def __dls(self, x, y, path=None, depth=None, max_depth=None, need_init=False):
        if need_init:
            path = []
        if self.__is_success(x, y):
            path.append((x, y))
            return True, path
        if depth == max_depth:
            return False, path
        path.append((x, y))
        p_queue = []
        for i in [-1, 1]:
            nextX, nextY = x + i, y
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                p_queue.append((self.__get_dist(nextX, nextY, x, y), (nextX, nextY)))
            nextX, nextY = x, y + i
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                p_queue.append((self.__get_dist(nextX, nextY, x, y), (nextX, nextY)))
        p_queue.sort(key=lambda k: k[0])
        for d, (nx, ny) in p_queue:
            suc, res = self.__dls(nx, ny, path[:], depth + 1, max_depth)
            if suc:
                return suc, res
        return False, path

    def __f_dls(self, x, y, path=None, depth=None, max_depth=None, need_init=False):
        if need_init:
            path = []
        if depth == max_depth:
            return {(x, y): path}
        path.append((x, y))
        p_queue = []
        for i in [-1, 1]:
            nextX, nextY = x + i, y
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                p_queue.append((self.__get_dist(nextX, nextY, x, y), (nextX, nextY)))
            nextX, nextY = x, y + i
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                p_queue.append((self.__get_dist(nextX, nextY, x, y), (nextX, nextY)))
        p_queue.sort(key=lambda k: k[0])
        reached = {}
        for d, (nx, ny) in p_queue:
            res = self.__f_dls(nx, ny, path[:], depth + 1, max_depth)
            reached.update(res)
        return reached

    def __b_dls(self, x, y, path=None, depth=None, max_depth=None, need_init=False):
        if need_init:
            path = []
        if depth == max_depth:
            return {(x, y): path}
        path.append((x, y))
        p_queue = []
        for i in [-1, 1]:
            nextX, nextY = x + i, y
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                p_queue.append((self.__get_dist(nextX, nextY, x, y), (nextX, nextY)))
            nextX, nextY = x, y + i
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                p_queue.append((self.__get_dist(nextX, nextY, x, y), (nextX, nextY)))
        p_queue.sort(key=lambda k: k[0])
        reached = {}
        for d, (nx, ny) in p_queue:
            res = self.__f_dls(nx, ny, path[:], depth + 1, max_depth)
            reached.update(res)
        return reached

    def __ids_s(self, x, y, g, bound, path=None, need_init=False):
        if need_init:
            path = []
        if self.__is_success(x, y):
            path.append((x, y))
            return True, path
        path.append((x, y))
        p_queue = []
        for i in [-1, 1]:
            nextX, nextY = x + i, y
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                hx = self.__get_dist(nextX, nextY, self.__endX, self.__endY, func='man')
                gx = self.__get_dist(nextX, nextY, x, y) + g
                fx = gx + hx
                p_queue.append((fx, gx, (nextX, nextY)))
            nextX, nextY = x, y + i
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                hx = self.__get_dist(nextX, nextY, self.__endX, self.__endY, func='man')
                gx = self.__get_dist(nextX, nextY, x, y) + g
                fx = gx + hx
                p_queue.append((fx, gx, (nextX, nextY)))
        p_queue.sort(key=lambda k: k[0])
        for d, g, (nx, ny) in p_queue:
            if d > bound:
                return False, path
            suc, res = self.__ids_s(nx, ny, g, bound, path[:])
            if suc:
                return suc, res
        return False, path

    def ucs(self, x, y, pre_c=None, p_queue=None, path=None, need_init=False):
        if need_init:
            path, p_queue, pre_c = [], [], 0  # 初始化路径
        if self.__is_success(x, y):
            path.append((x, y))  # 加入结束点
            return True, [(x, y)]
        path.append((x, y))  # 加入当前点
        for i in [-1, 1]:  # 遍历上下左右
            nextX, nextY = x + i, y
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                p_queue.append((self.__get_dist(nextX, nextY, x, y) + pre_c, (nextX, nextY), (x, y)))  # 计算代价，加入队列
            nextX, nextY = x, y + i
            if self.__is_legal(nextX, nextY) and (nextX, nextY) not in path:
                p_queue.append((self.__get_dist(nextX, nextY, x, y) + pre_c, (nextX, nextY), (x, y)))
        p_queue.sort(key=lambda k: k[0])  # 按代价排序
        suc, res = self.ucs(p_queue[0][1][0], p_queue[0][1][1], p_queue[0][0], p_queue[1:], path[:])  # 递归
        if suc:
            for item in p_queue:
                if item[1] == res[-1]:
                    res.append(item[2])
            return suc, res
        return False, path

    def ids(self, x, y, path=None, depth=None, max_depth=None, need_init=False):
        if need_init:
            path, depth, max_depth = [], 0, self.maxX * self.maxY  # 初始化做大深度为长乘宽，因为最大步数不会大于这个值
        if self.__is_success(x, y):
            path.append((x, y))  # 如果到达终点，将终点加入路径
            return True, path
        for i in range(max_depth):
            suc, res = self.__dls(x, y, path[:], depth, i)  # 迭代加深搜索
            if suc:
                return suc, res
        return False, path

    def bids(self, x, y, path=None, depth=None, max_depth=None, need_init=False):
        if need_init:
            path, depth, max_depth = [], 0, self.maxX * self.maxY  # 初始化最大深度
        if self.__is_success(x, y):
            path.append((x, y))  # 成功，返回路径
            return True, path
        for i in range(max_depth):
            f_res = self.__f_dls(self.__startX, self.__startY, path[:], depth, i)  # 前向搜索
            self.__swap()  # 交换起点终点
            b_res = self.__b_dls(self.__startX, self.__startY, path[:], depth, i)  # 反向搜索
            self.__swap()
            for pt in f_res:
                if pt in b_res:  # 如果存在信息交叉
                    path = f_res[pt].copy()
                    path.append(pt)
                    path.extend(list(reversed(b_res[pt].copy())))
                    return True, path
        return False, 0

    def ida_star(self, x, y, need_init=False):
        cur_bound = int(self.__get_dist(self.__startX, self.__startY, self.__endX, self.__endY))
        max_bound = cur_bound * 2
        for i in range(cur_bound, max_bound):
            suc, res = self.__ids_s(x, y, 0, i, need_init=True)
            if suc:
                return suc, res
        return False, 0

    def run(self, search_func):
        try:
            func = getattr(self, search_func)
        except AttributeError:
            print('No such search function as {}'.format(search_func))
            return None
        begin = time.perf_counter()
        for i in range(100):
            is_success, path = func(self.__startX, self.__startY, need_init=True)
        cost = (time.perf_counter() - begin) / 100
        if is_success:
            print('Found path using "{}" method, total {} steps, elapsed time: {}'.format(search_func, len(path), cost))
            self.__draw(path)
        else:
            print('No path Found')


if __name__ == '__main__':
    with open('./maze/MazeData.txt') as m_file:
        maze = [i.strip() for i in m_file.readlines()]
    sol = Solution(maze)
    for func in ['ucs', 'ids', 'bids', 'ida_star']:
        sol.run(search_func=func)
