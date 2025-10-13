import copy
import time
import random
import math
from collections import deque

# ======================
#   CLASS CSP SEARCH
# ======================
class CSP:
    def __init__(self, snake, obstacles, food, rows, cols):
        self.snake = snake
        self.obstacles = obstacles
        self.food = food
        self.rows = rows
        self.cols = cols
        self.nodes_expanded = 0
        self.max_frontier_size = 0
# -------------------------
# Backtracking Search
# -------------------------
    def backtracking(self, max_depth=50):
        start_time = time.time()
        self.nodes_expanded = 0
        self.max_frontier_size = 0

        def heuristic(pos):
            food_pos = self.food[0] if isinstance(self.food, list) else self.food
            return abs(pos[0] - food_pos[0]) + abs(pos[1] - food_pos[1])

        def is_valid_move(pos, path):
            """Kiểm tra bước đi hợp lệ (bao gồm thân rắn là vật cản)"""
            # Kiểm tra biên
            if not (0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols):
                return False
            # Va chướng ngại vật
            if tuple(pos) in set(tuple(obs) for obs in self.obstacles):
                return False
            #  Va thân rắn hiện tại
            if tuple(pos) in set(tuple(seg) for seg in self.snake):
                return False
            # Va vào đường đã đi trong quá trình tìm kiếm
            if tuple(pos) in [tuple(p) for p in path]:
                return False
            return True

        def is_safe_move(pos):
            """Đảm bảo từ ô này vẫn còn ít nhất 1 hướng thoát, tránh tự khóa đầu"""
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nxt = [pos[0] + dx, pos[1] + dy]
                if (0 <= nxt[0] < self.rows and 0 <= nxt[1] < self.cols
                    and tuple(nxt) not in set(tuple(obs) for obs in self.obstacles)
                    and tuple(nxt) not in set(tuple(seg) for seg in self.snake)):
                    return True
            return False

        def get_valid_moves(current_pos, path):
            moves = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_pos = [current_pos[0] + dx, current_pos[1] + dy]
                if is_valid_move(new_pos, path) and is_safe_move(new_pos):
                    moves.append(new_pos)
            return moves

        expanded_nodes = []

        def backtrack(current_path, depth):
            self.nodes_expanded += 1
            expanded_nodes.append(tuple(current_path[-1]))
            self.max_frontier_size = max(self.max_frontier_size, len(current_path))
            current_pos = current_path[-1]
            food_target = self.food[0] if isinstance(self.food, list) else self.food

            if current_pos == list(food_target):
                return current_path[:]
            if depth >= max_depth:
                return None

            valid_moves = get_valid_moves(current_pos, current_path)
            valid_moves.sort(key=heuristic)

            for next_pos in valid_moves:
                current_path.append(next_pos)
                result = backtrack(current_path, depth + 1)
                if result:
                    return result
                current_path.pop()
            return None

        start_pos = list(self.snake[0])
        solution_path = backtrack([start_pos], 0)

        found_directions = []
        if solution_path:
            for i in range(1, len(solution_path)):
                dx = solution_path[i][0] - solution_path[i - 1][0]
                dy = solution_path[i][1] - solution_path[i - 1][1]
                found_directions.append((dx, dy))

        elapsed = time.time() - start_time
        return {
            "nodes_expanded": self.nodes_expanded,
            "max_frontier_size": self.max_frontier_size,
            "time": elapsed,
            "found_directions": found_directions if solution_path else None,
            "found_path": solution_path,
            "expanded_nodes": expanded_nodes,
        }
#========================
# Forward Checking Search
#========================
    def forward_checking(self, max_depth=50):
        start_time = time.time()
        self.nodes_expanded = 0
        self.max_frontier_size = 0

        def heuristic(pos):
            """Ưu tiên ô gần thức ăn hơn"""
            food_pos = self.food[0] if isinstance(self.food, list) else self.food
            return abs(pos[0] - food_pos[0]) + abs(pos[1] - food_pos[1])

        def is_valid(pos, path):
            """Kiểm tra bước đi hợp lệ"""
            # Biên
            if not (0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols):
                return False
            # Va chướng ngại vật
            if tuple(pos) in set(tuple(obs) for obs in self.obstacles):
                return False
            # Va thân rắn hiện tại
            if tuple(pos) in set(tuple(seg) for seg in self.snake):
                return False
            # Va đường đã đi
            if tuple(pos) in [tuple(p) for p in path]:
                return False
            return True

        def is_safe_move(pos):
            """Kiểm tra xem từ vị trí mới có còn ít nhất 1 hướng thoát không"""
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nxt = [pos[0]+dx, pos[1]+dy]
                if (0 <= nxt[0] < self.rows and 0 <= nxt[1] < self.cols
                    and tuple(nxt) not in set(tuple(obs) for obs in self.obstacles)
                    #  Không đè thân rắn
                    and tuple(nxt) not in set(tuple(seg) for seg in self.snake)):
                    return True
            return False

        def forward_domain(current, path):
            """Trả về danh sách các ô khả thi kế tiếp"""
            domain = []
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nxt = [current[0] + dx, current[1] + dy]
                if is_valid(nxt, path) and is_safe_move(nxt):
                    domain.append(nxt)
            domain.sort(key=heuristic)
            return domain

        expanded_nodes = []

        def fc_backtrack(path, depth):
            self.nodes_expanded += 1
            expanded_nodes.append(tuple(path[-1]))
            self.max_frontier_size = max(self.max_frontier_size, len(path))
            if depth >= max_depth:
                return None

            current = path[-1]
            food_target = self.food[0] if isinstance(self.food, list) else self.food
            if current == list(food_target):
                return path

            domain = forward_domain(current, path)
            if not domain:
                return None

            for nxt in domain:
                if not is_valid(nxt, path):
                    continue
                result = fc_backtrack(path + [nxt], depth + 1)
                if result:
                    return result
            return None

        start = list(self.snake[0])
        solution_path = fc_backtrack([start], 0)

        found_directions = []
        if solution_path:
            for i in range(1, len(solution_path)):
                dx = solution_path[i][0] - solution_path[i - 1][0]
                dy = solution_path[i][1] - solution_path[i - 1][1]
                found_directions.append((dx, dy))

        elapsed = time.time() - start_time
        return {
            "nodes_expanded": self.nodes_expanded,
            "max_frontier_size": self.max_frontier_size,
            "time": elapsed,
            "found_directions": found_directions if solution_path else None,
            "found_path": solution_path,
            "expanded_nodes": expanded_nodes
        }

# -------------------------
# AC3 Search
# -------------------------
    def ac3(self, max_depth=30):
        start_time = time.time()
        self.nodes_expanded = 0
        self.max_frontier_size = 0

        start = tuple(self.snake[0])
        goal = tuple(self.food[0]) if isinstance(self.food, list) else tuple(self.food)

        obs = set(tuple(o) for o in self.obstacles)
        body = set(tuple(b) for b in self.snake)
        blocked = obs | body

        def in_bounds(p):
            return 0 <= p[0] < self.rows and 0 <= p[1] < self.cols

        def free(p):
            return in_bounds(p) and p not in blocked

        def neigh4(p):
            x, y = p
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                q = (x + dx, y + dy)
                if free(q):
                    yield q, (dx, dy)

        def manhattan(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        expanded_nodes = []
        nodes_expanded = 0
        max_frontier = 0

        def backtrack(cur, path, visited):
            nonlocal nodes_expanded, max_frontier
            nodes_expanded += 1
            expanded_nodes.append(cur)
            max_frontier = max(max_frontier, len(path))
            if manhattan(cur, goal) <= 2:
                return path
            if len(path) > max_depth:
                return None

            neighbors = list(neigh4(cur))
            neighbors.sort(key=lambda t: manhattan(t[0], goal))
            for nxt, d in neighbors:
                if nxt not in visited:
                    visited.add(nxt)
                    result = backtrack(nxt, path + [nxt], visited)
                    if result:
                        return result
                    visited.remove(nxt)
            return None

        partial_path = backtrack(start, [start], {start})
        if not partial_path:
            return {
                "nodes_expanded": nodes_expanded,
                "max_frontier_size": max_frontier,
                "time": time.time() - start_time,
                "found_directions": None,
                "found_path": None,
                "expanded_nodes": expanded_nodes
            }

        head_near = partial_path[-1]

        # AC3
        radius = 3
        local_cells = set()
        for i in range(goal[0] - radius, goal[0] + radius + 1):
            for j in range(goal[1] - radius, goal[1] + radius + 1):
                p = (i, j)
                if free(p):
                    local_cells.add(p)

        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        domains = {p: list(moves) for p in local_cells}

        from collections import deque as dq
        def local_neighbors(p):
            return [q for q, _ in neigh4(p) if q in local_cells]

        def revise(xi, xj):
            revised = False
            keep = []
            for vi in domains[xi]:
                xi_next = (xi[0] + vi[0], xi[1] + vi[1])
                if xi_next not in local_cells:
                    revised = True
                    continue
                ok = any(
                    abs((xj[0] + vj[0]) - xi_next[0]) + abs((xj[1] + vj[1]) - xi_next[1]) == 1
                    for vj in domains[xj]
                )
                if ok:
                    keep.append(vi)
                else:
                    revised = True
            domains[xi] = keep
            return revised

        Q = dq()
        for x in local_cells:
            for y in local_neighbors(x):
                Q.append((x, y))

        while Q:
            xi, xj = Q.popleft()
            if revise(xi, xj):
                if not domains[xi]:
                    break
                for xk in local_neighbors(xi):
                    if xk != xj:
                        Q.append((xk, xi))

        
        def bfs_local(src, dst):
            qq = dq([src])
            came = {src: None}
            while qq:
                u = qq.popleft()
                if u == dst:
                    path = []
                    while u is not None:
                        path.append(u)
                        u = came[u]
                    return path[::-1]
                for v, _ in neigh4(u):
                    if v in local_cells and v not in came:
                        came[v] = u
                        qq.append(v)
            return None

        local_path = bfs_local(head_near, goal)
        if local_path:
            full_path = partial_path + local_path[1:]
        else:
            full_path = partial_path

        directions = []
        for i in range(1, len(full_path)):
            dx = full_path[i][0] - full_path[i - 1][0]
            dy = full_path[i][1] - full_path[i - 1][1]
            directions.append((dx, dy))

        elapsed = time.time() - start_time
        return {
            "nodes_expanded": nodes_expanded,
            "max_frontier_size": max_frontier,
            "time": elapsed,
            "found_directions": directions if full_path else None,
            "found_path": full_path,
            "expanded_nodes": expanded_nodes
        }

# -----------------------------------------------------------------
# UI SnakeGame
# -----------------------------------------------------------------
def AC3(snake, obstacles, food, rows, cols):
    csp = CSP(snake, obstacles, food, rows, cols)
    return csp.ac3()   

def Backtracking(snake, obstacles, food, rows, cols):
    csp = CSP(snake, obstacles, food, rows, cols)
    return csp.backtracking()  

def Forward_Checking(snake, obstacles, food, rows, cols):
    csp = CSP(snake, obstacles, food, rows, cols)
    return csp.forward_checking()