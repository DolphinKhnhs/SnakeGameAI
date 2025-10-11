import time, heapq
from collections import deque


# A* Nó kết hợp sức mạnh của:
# UCS (Uniform Cost Search) — luôn chọn đường có chi phí g(x) nhỏ nhất
# Greedy Best-First Search — luôn chọn node "gần đích nhất" qua heuristic h(x)
# Tổng chi phí f(x) = g(x) + h(x)

def A_star(snake, obstacles, food, rows, cols):
    start_time = time.time()

    # ---- Xử lý input ----
    start = tuple(snake[0])
    if isinstance(food, list) and len(food) > 0:
        goal = tuple(food[0])
    else:
        goal = tuple(food)

    # ---- Heuristic ----
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    # ---- Neighbor generator ----
    def neighbors(pos):
        x, y = pos
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in obstacles and (nx, ny) not in snake:
                yield (nx, ny)

    # ---- Khởi tạo ----
    open_set = []
    came_from = {start: None}
    g = {start: 0}  # g(x) - chi phí thực tế từ start đến current node
    f = {start: heuristic(start, goal)}

    heapq.heappush(open_set, (f[start], start))

    expanded_nodes = []
    nodes_expanded = 0
    max_frontier = 1

    # ---- Vòng lặp chính ----
    while open_set:
        current_f, current = heapq.heappop(open_set)
        nodes_expanded += 1
        expanded_nodes.append(current)

        # Nếu đến đích
        if current == goal:
            path = []
            while current is not None:
                path.append(list(current))
                current = came_from[current]
            path.reverse()

            directions = [
                (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
                for i in range(len(path) - 1)
            ]

            h_value = heuristic(start, goal)  # h(x): ước lượng ban đầu
            g_cost = len(path) - 1  # g(x): tổng chi phí thật (số bước) - MỖI Ô +1
            f_cost = g_cost + h_value  # f(x): tổng chi phí dự đoán

            return {
                "found_path": path,
                "found_directions": directions,
                "nodes_expanded": nodes_expanded,
                "max_frontier_size": max_frontier,
                "heuristic_value": h_value,
                "distance_cost": g_cost,  # CHI PHÍ THỰC TẾ - MỖI Ô +1
                "total_cost": f_cost,
                "expanded_nodes": expanded_nodes,
                "time": time.time() - start_time
            }

        # Duyệt hàng xóm
        for nxt in neighbors(current):
            tentative_g = g[current] + 1  # MỖI BƯỚC +1 CHI PHÍ
            tentative_f = tentative_g + heuristic(nxt, goal)
            if nxt not in g or tentative_g < g[nxt]:
                came_from[nxt] = current
                g[nxt] = tentative_g
                f[nxt] = tentative_f
                heapq.heappush(open_set, (tentative_f, nxt))
                max_frontier = max(max_frontier, len(open_set))

    # ---- Nếu không tìm thấy đường ----
    return {
        "found_path": [],
        "found_directions": [],
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier,
        "heuristic_value": 0,
        "distance_cost": 0,
        "total_cost": 0,
        "expanded_nodes": expanded_nodes,
        "time": time.time() - start_time
    }


def greedy_search(snake, obstacles, food, rows, cols):
    start_time = time.time()

    # ======= Xử lý input =======
    start = tuple(snake[0])
    if isinstance(food, list) and len(food) > 0:
        goal = tuple(food[0])
    else:
        goal = tuple(food)
    blocked = set(obstacles) | set(snake)

    # ======= Heuristic (Manhattan) =======
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # ======= Lân cận =======
    def neighbors(pos):
        x, y = pos
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in blocked:
                yield (nx, ny)

    # ======= Kiểm tra đường đi an toàn (chống kẹt) =======
    def safe_path_exists(head_pos, body_cells):
        q = deque([head_pos])
        visited = {head_pos}
        free = 0
        while q:
            x, y = q.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (
                        0 <= nx < rows and 0 <= ny < cols and
                        (nx, ny) not in body_cells and (nx, ny) not in visited
                ):
                    visited.add((nx, ny))
                    q.append((nx, ny))
                    free += 1
                    if free > 30:
                        return True
        return free > 5

    # ======= Greedy search chính =======
    frontier = []
    heapq.heappush(frontier, (heuristic(start, goal), start))
    came_from = {start: None}
    visited = {start}
    expanded_nodes = []
    nodes_expanded = 0
    max_frontier = 1

    # THÊM: Theo dõi chi phí thực tế g(x)
    g_cost_tracker = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)
        nodes_expanded += 1
        expanded_nodes.append(current)

        # Nếu đến goal
        if current == goal:
            path = []
            while current is not None:
                path.append(list(current))
                current = came_from[current]
            path.reverse()

            directions = [
                (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
                for i in range(len(path) - 1)
            ]

            h_value = heuristic(start, goal)
            g_cost = len(path) - 1  # CHI PHÍ THỰC TẾ - MỖI Ô +1
            f_cost = h_value  # f(x) = h(x) trong greedy

            return {
                "found_path": path,
                "found_directions": directions,
                "nodes_expanded": nodes_expanded,
                "max_frontier_size": max_frontier,
                "heuristic_value": h_value,
                "distance_cost": g_cost,  # CHI PHÍ THỰC TẾ
                "total_cost": f_cost,
                "expanded_nodes": expanded_nodes,
                "time": time.time() - start_time,
            }

        # Mở rộng node lân cận
        for nxt in neighbors(current):
            if nxt not in visited:
                visited.add(nxt)
                came_from[nxt] = current
                g_cost_tracker[nxt] = g_cost_tracker[current] + 1  # THEO DÕI CHI PHÍ THỰC
                h_val = heuristic(nxt, goal)
                heapq.heappush(frontier, (h_val, nxt))
        max_frontier = max(max_frontier, len(frontier))

    # ======= Fallback an toàn nếu không tìm thấy đường =======
    best_move, best_score = None, float("inf")
    head = start
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = head[0] + dx, head[1] + dy
        if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in blocked:
            h = heuristic((nx, ny), goal)
            if safe_path_exists((nx, ny), blocked) and h < best_score:
                best_score = h
                best_move = (dx, dy)

    if best_move:
        # Chi phí thực tế cho 1 bước di chuyển
        g_cost_fallback = 1

        return {
            "found_path": [list(head), [head[0] + best_move[0], head[1] + best_move[1]]],
            "found_directions": [best_move],
            "nodes_expanded": nodes_expanded,
            "max_frontier_size": max_frontier,
            "heuristic_value": best_score,
            "distance_cost": g_cost_fallback,  # CHI PHÍ THỰC TẾ = 1
            "total_cost": best_score,
            "expanded_nodes": expanded_nodes,
            "time": time.time() - start_time,
        }

    # ======= Không tìm thấy gì =======
    return {
        "found_path": [],
        "found_directions": [],
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier,
        "heuristic_value": 0,
        "distance_cost": 0,
        "total_cost": 0,
        "expanded_nodes": expanded_nodes,
        "time": time.time() - start_time,
    }