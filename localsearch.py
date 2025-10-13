import time, random, heapq, math
from collections import deque
from uninformedsearch import BFS

# -----------------------------------------------------------------
# Hill Climbing
# -----------------------------------------------------------------
def hill_climbing(snake, obstacles, food, rows, cols):
    start_time = time.time()

    # ======= Chuẩn hóa dữ liệu =======
    start = tuple(snake[0])
    if isinstance(food, list) and len(food) > 0:
        goal = tuple(food[0])
    else:
        goal = tuple(food)

    # Thân rắn + vật cản = blocked
    blocked = set(obstacles) | set(snake)

    # ======= Heuristic =======
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # ======= Sinh hàng xóm =======
    def neighbors(pos):
        x, y = pos
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                yield (nx, ny), (dx, dy)

    # ======= Kiểm tra an toàn =======
    def is_safe(pos):
        return (0 <= pos[0] < rows and 0 <= pos[1] < cols and pos not in blocked)

    # ======= BFS kiểm tra có đường an toàn đến food =======
    def path_exists_bfs(start_pos, end_pos):
        q = deque([start_pos])
        visited = {start_pos}
        while q:
            x, y = q.popleft()
            if (x, y) == end_pos:
                return True
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nxt = (x + dx, y + dy)
                if is_safe(nxt) and nxt not in visited:
                    visited.add(nxt)
                    q.append(nxt)
        return False

    # ======= Đánh giá khoảng trống =======
    def open_space_score(pos):
        q = deque([pos])
        visited = {pos}
        free = 0
        while q:
            x, y = q.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nxt = (x + dx, y + dy)
                if (
                    0 <= nxt[0] < rows
                    and 0 <= nxt[1] < cols
                    and nxt not in blocked
                    and nxt not in visited
                ):
                    visited.add(nxt)
                    q.append(nxt)
                    free += 1
                    if free > 50:
                        return 50
        return free

    # ======= Hàm đánh giá =======
    def evaluate(pos):
        if pos in blocked:
            return -float("inf")
        dist_score = -heuristic(pos, goal)
        space_score = 0.3 * open_space_score(pos)
        return dist_score + space_score

    # ======= Hill Climbing core =======
    def climb(start_point):
        current = start_point
        current_eval = evaluate(current)
        path = [current]
        visited = {current}
        local_expanded = []

        for _ in range(rows * cols*2):
            candidates = []
            for nxt, direction in neighbors(current):
                if nxt not in visited and is_safe(nxt):
                    score = evaluate(nxt)
                    candidates.append((score, nxt))
                    local_expanded.append(nxt)

            if not candidates:
                break

            best_score, best_pos = max(candidates, key=lambda x: x[0])

            if best_score > current_eval:
                path.append(best_pos)
                visited.add(best_pos)
                current, current_eval = best_pos, best_score
            else:
                # === Khi kẹt, thử 1 hướng ngẫu nhiên hợp lệ (có BFS an toàn) ===
                random.shuffle(candidates)
                safe_found = False
                for _, nxt in candidates:
                    if is_safe(nxt) and path_exists_bfs(nxt, goal):
                        path.append(nxt)
                        current, current_eval = nxt, evaluate(nxt)
                        safe_found = True
                        break
                if not safe_found:
                    break

            if current == goal:
                break

        return path, local_expanded, current, current_eval

    # ======= Chạy duy nhất 1 lần =======
    path, all_expanded, last_pos, best_eval = climb(start)

    # ======= Kết quả =======
    directions = []
    for i in range(len(path) - 1):
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        directions.append((dx, dy))

    heuristic_value = heuristic(path[-1], goal) if path else 0
    g_cost = len(path) - 1
    f_cost = heuristic_value

    end_time = time.time()

    return {
        "found_path": path,
        "found_directions": directions,
        "nodes_expanded": len(all_expanded),
        "max_frontier_size": len(path),
        "heuristic_value": heuristic_value,
        "distance_cost": g_cost,
        "total_cost": f_cost,
        "expanded_nodes": all_expanded,
        "time": end_time - start_time
    }

# -----------------------------------------------------------------
# Genetic Algorithm
# -----------------------------------------------------------------
def genetic_algorithm(snake, obstacles, food, rows, cols):
    start_time = time.time()
    MOVES = [(-1,0),(1,0),(0,-1),(0,1)]
    head = snake[0]
    obs = set(obstacles)
    food = tuple(food[0]) if isinstance(food, list) and len(food) > 0 else tuple(food)

    # ===== Helper =====
    def in_bounds(p): return 0 <= p[0] < rows and 0 <= p[1] < cols
    def manhattan(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def legal(nxt, s): return in_bounds(nxt) and nxt not in obs and nxt not in s

    # --- A* fallback tìm đường thật ---
    def astar_path(start, goal, snake_body):
        open_set = []
        heapq.heappush(open_set, (0 + manhattan(start, goal), 0, start, [start]))
        closed = set()
        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            if current == goal:
                return path
            if current in closed:
                continue
            closed.add(current)
            for dx, dy in MOVES:
                nx, ny = current[0] + dx, current[1] + dy
                nxt = (nx, ny)
                if not in_bounds(nxt) or nxt in obs or nxt in snake_body:
                    continue
                heapq.heappush(open_set, (g + 1 + manhattan(nxt, goal), g + 1, nxt, path + [nxt]))
        return None

    # ===== Fitness =====
    def simulate(s, genes):
        body = list(s)
        for mv in genes:
            nxt = (body[0][0] + mv[0], body[0][1] + mv[1])
            if not legal(nxt, body):
                return body, False, False
            body.insert(0, nxt)
            if nxt == food:
                return body, True, True
            body.pop()
        return body, True, False

    def fitness(genes):
        s2, alive, ate = simulate(snake, genes)
        if not alive:
            return -1000
        dist = manhattan(s2[0], food)
        score = 500 - dist * 10
        if ate: score += 10000
        return score

    # ===== GA Core =====
    POP, GEN, GENE_LEN = 40, 10, 8
    MUT_RATE = 0.25

    def greedy_dir():
        fx, fy = food
        hx, hy = head
        dx, dy = fx - hx, fy - hy
        if abs(dx) > abs(dy):
            return (1, 0) if dx > 0 else (-1, 0)
        else:
            return (0, 1) if dy > 0 else (0, -1)

    population = [
        [(greedy_dir() if random.random() < 0.7 else random.choice(MOVES)) for _ in range(GENE_LEN)]
        for __ in range(POP)
    ]

    for _ in range(GEN):
        scored = [(fitness(ind), ind) for ind in population]
        scored.sort(reverse=True)
        elites = [ind for _, ind in scored[:POP // 3]]
        children = []
        while len(children) + len(elites) < POP:
            p1, p2 = random.sample(elites, 2)
            cut = random.randint(1, GENE_LEN - 2)
            child = p1[:cut] + p2[cut:]
            if random.random() < MUT_RATE:
                child[random.randint(0, GENE_LEN - 1)] = random.choice(MOVES)
            children.append(child)
        population = elites + children

    best_score, best_gene = max([(fitness(ind), ind) for ind in population], key=lambda x: x[0])
    s2, alive, ate = simulate(snake, best_gene)

    # --- Nếu GA ăn được food => thành công ---
    if ate:
        path = [head]
        for mv in best_gene:
            path.append((path[-1][0] + mv[0], path[-1][1] + mv[1]))
            if path[-1] == food:
                break
        found_dirs = [(path[i+1][0]-path[i][0], path[i+1][1]-path[i][1]) for i in range(len(path)-1)]
    else:
        # --- fallback: dùng A* tìm đường chuẩn ---
        path = astar_path(head, food, snake)
        if path is None:
            return {
                "found_path": None,
                "found_directions": None,
                "nodes_expanded": POP * GEN,
                "max_frontier_size": POP,
                "heuristic_value": manhattan(head, food),
                "distance_cost": 0,
                "total_cost": 0,
                "expanded_nodes": [],
                "time": time.time() - start_time,
                "next_snake": snake
            }
        found_dirs = [(path[i+1][0]-path[i][0], path[i+1][1]-path[i][1]) for i in range(len(path)-1)]

    next_snake = [path[1]] + (snake[:] if path[1] == food else snake[:-1])

    return {
        "found_path": path,
        "found_directions": found_dirs,
        "nodes_expanded": POP * GEN,
        "max_frontier_size": POP,
        "heuristic_value": manhattan(head, food),
        "distance_cost": len(path) - 1,
        "total_cost": len(path),
        "expanded_nodes": path[:-1],
        "time": time.time() - start_time,
        "next_snake": next_snake
    }

# -----------------------------------------------------------------
# Simulated Annealing
# -----------------------------------------------------------------
def simulated_annealing(snake, obstacles, food, rows, cols):
    """
    Mô phỏng quá trình làm mát dần (Simulated Annealing)
    Áp dụng khi rắn đã gần food (dựa vào đường BFS cơ sở)
    """
    start_time = time.time()
    obs = set(obstacles)
    expanded_nodes = []

    # --- Chuẩn hóa food ---
    if isinstance(food, list):
        if len(food) > 0 and isinstance(food[0], (tuple, list)):
            food = tuple(food[0])
        else:
            food = tuple(food)
    else:
        food = tuple(food)

    def in_bounds(p): return 0 <= p[0] < rows and 0 <= p[1] < cols
    def manhattan(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neigh4(p):
        x, y = p
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            q = (x+dx, y+dy)
            if in_bounds(q):
                yield q, (dx, dy)

    # ======================
    # Giai đoạn 1: BFS tìm đường sơ bộ
    # ======================
    result_bfs = BFS(snake, obstacles, [food], rows, cols)
    if not result_bfs or not result_bfs["found_path"]:
        return {
            "found_path": [],
            "found_directions": [],
            "nodes_expanded": 0,
            "max_frontier_size": 0,
            "heuristic_value": 0,
            "distance_cost": 0,
            "total_cost": 0,
            "expanded_nodes": [],
            "time": time.time() - start_time
        }

    path = result_bfs["found_path"]
    directions = result_bfs["found_directions"]
    expanded_nodes.extend(result_bfs.get("expanded_nodes", []))

    head = path[-2] if len(path) >= 2 else snake[0]

    # ======================
    # Giai đoạn 2: Simulated Annealing local optimization
    # ======================
    nodes_expanded = 0
    temperature_trace = []

    if manhattan(head, food) <= 2:
        T = 6.0        # nhiệt độ khởi tạo
        end_T = 0.4
        cooling = 0.9

        def energy(pos):
            """Hàm năng lượng — càng gần food, năng lượng càng thấp"""
            if pos in obs or not in_bounds(pos):
                return 1e9
            return manhattan(pos, food)

        # Lấy tất cả ứng viên từ head
        scored = [(energy(q), q, d) for q, d in neigh4(head)]
        scored = [item for item in scored if item[0] < 1e9]
        if not scored:
            return result_bfs

        # chọn vị trí tốt nhất ban đầu
        best_E, best_pos, best_dir = min(scored, key=lambda x: x[0])
        expanded_nodes.extend([q for _, q, _ in scored])

        # Làm mát dần
        while T > end_T:
            cand_E, cand_pos, cand_dir = random.choice(scored)
            nodes_expanded += 1
            deltaE = cand_E - best_E
            if deltaE < 0 or random.random() < math.exp(-float(deltaE) / float(T)):
                best_E, best_pos, best_dir = cand_E, cand_pos, cand_dir
            T *= cooling
            temperature_trace.append(round(T, 2))

        move = (best_pos[0] - head[0], best_pos[1] - head[1])
        directions.append(move)
        path.append(best_pos)

        final_T = round(temperature_trace[-1], 2) if temperature_trace else round(T, 2)
    else:
        final_T = manhattan(head, food)

    # ======================
    # Giai đoạn 3: Kết quả
    # ======================
    return {
        "found_path": path,
        "found_directions": directions,
        "nodes_expanded": result_bfs["nodes_expanded"] + nodes_expanded,
        "max_frontier_size": result_bfs["max_frontier_size"],
        "heuristic_value": final_T,             # h(x): nhiệt độ cuối hoặc khoảng cách
        "distance_cost": len(path),             # g(x): số bước đã đi
        "total_cost": len(path),                # f(x) = g(x) + h(x)
        "expanded_nodes": expanded_nodes,
        "temperature_trace": temperature_trace,
        "time": time.time() - start_time
    }


def beam_search(snake, obstacles, food, rows, cols, beam_width=10):
    start_time = time.time()

    # --- Chuẩn hóa input ---
    head = tuple(snake[0])
    if isinstance(food, list) and len(food) > 0:
        food = tuple(food[0])
    else:
        food = tuple(food)

    obs = set(obstacles)
    MOVES = [(-1,0), (1,0), (0,-1), (0,1)]  # U, D, L, R

    def in_bounds(p):
        return 0 <= p[0] < rows and 0 <= p[1] < cols

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # --- Khởi tạo ---
    start = (head, list(snake), [])
    frontier = [(manhattan(head, food), start)]
    visited = {tuple(snake)}

    nodes_expanded = 0
    max_frontier_size = 1
    expanded_nodes = []

    # --- Vòng lặp Beam Search ---
    while frontier:
        next_frontier = []
        frontier.sort(key=lambda x: x[0])
        frontier = frontier[:beam_width]

        for _, (head, body, path) in frontier:
            nodes_expanded += 1
            expanded_nodes.append(head)

            # --- Nếu ăn được mồi ---
            if head == food:
                # Dựng đường đi từ path
                found_path = [snake[0]]
                cur = snake[0]
                directions = []
                for mv in path:
                    cur = (cur[0] + mv[0], cur[1] + mv[1])
                    found_path.append(cur)
                    directions.append(mv)

                heuristic_value = manhattan(head, food)
                g_cost = len(path)
                f_cost = g_cost + heuristic_value

                return {
                    "found_path": found_path,
                    "found_directions": directions,
                    "nodes_expanded": nodes_expanded,
                    "max_frontier_size": max_frontier_size,
                    "heuristic_value": heuristic_value,
                    "distance_cost": g_cost,
                    "total_cost": f_cost,
                    "expanded_nodes": expanded_nodes,
                    "time": time.time() - start_time
                }

            # --- Sinh node con ---
            for mv in MOVES:
                nx, ny = head[0] + mv[0], head[1] + mv[1]
                nxt = (nx, ny)
                if not in_bounds(nxt) or nxt in obs or nxt in body:
                    continue

                new_body = [nxt] + (body[:] if nxt == food else body[:-1])
                state_key = tuple(new_body)
                if state_key in visited:
                    continue
                visited.add(state_key)

                new_path = path + [mv]
                h = manhattan(nxt, food)
                next_frontier.append((h, (nxt, new_body, new_path)))

        frontier = next_frontier
        max_frontier_size = max(max_frontier_size, len(frontier))

    # --- Không tìm thấy đường ---
    return {
        "found_path": [],
        "found_directions": [],
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier_size,
        "heuristic_value": manhattan(snake[0], food),
        "distance_cost": 0,
        "total_cost": 0,
        "expanded_nodes": expanded_nodes,
        "time": time.time() - start_time
    }