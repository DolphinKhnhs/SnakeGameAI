import time
from collections import deque
import itertools
import random


def _result(stats, duration, dirs, path):
    """Trả về kết quả."""
    return {
        "nodes_expanded": stats["nodes_expanded"],
        "max_frontier_size": stats["max_frontier_size"],
        "time": duration,
        "found_directions": dirs,
        "found_path": path,
        "expanded_nodes": stats["expanded_nodes"],
    }


def _empty_result(start_time):
    """Trả về kết quả rỗng khi không tìm được đường."""
    return {
        "nodes_expanded": 0,
        "max_frontier_size": 0,
        "time": time.time() - start_time,
        "found_directions": None,
        "found_path": None,
        "expanded_nodes": [],
    }


def path_to_dirs(path):
    """Chuyển danh sách tọa độ thành hướng di chuyển."""
    if len(path) < 2:
        return []
    return [(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
            for i in range(1, len(path))]


# =================== AND-OR TREE SEARCH ===================
def and_or_tree_search(snake, obstacles, food, rows, cols,
                       max_depth=20,
                       time_limit_ms=80):
    """
    AND-OR Tree Search cho Snake Game.
    - Tìm một vị trí mồi có thể đạt được
    - Sau đó dùng BFS để tìm đường tối ưu
    - Trả về hướng đi đầu tiên (hoặc toàn bộ đường)
    """
    start_time = time.time()
    deadline = start_time + (time_limit_ms / 1000.0)
    
    if not food:
        return _empty_result(start_time)
    
    # Chọn mồi gần nhất
    start = tuple(snake[0])
    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    target_food = min(food, key=lambda f: manhattan(start, tuple(f)))
    target_food = tuple(target_food)
    
    print(f"[DEBUG] AND-OR: Snake at {start}, Target food: {target_food}")
    
    # Chuẩn bị dữ liệu
    fixed_obs = set(map(tuple, snake[1:] + obstacles))
    all_food = [tuple(f) for f in food]
    
    stats = {
        "nodes_expanded": 0,
        "max_frontier_size": 0,
        "expanded_nodes": []
    }
    
    best_path = None
    best_dirs = None
    
    # Tìm đường đến tất cả thức ăn theo thứ tự tối ưu
    for food_order in itertools.permutations(all_food):
        if time.time() > deadline:
            break
            
        cur_path, cur_pos = [], start
        visited = fixed_obs.union(map(tuple, snake))  # Không đi qua cơ thể hiện tại
        
        is_valid = True
        for target in food_order:
            # Tìm đường BFS đến mồi này
            path = find_path_and_or(cur_pos, target, visited, rows, cols, stats, deadline)
            
            if not path:
                is_valid = False
                break
            
            # Thêm vào đường đi chung
            if cur_path:
                cur_path.extend(path[1:])
            else:
                cur_path.extend(path)
            
            cur_pos = target
            # Cập nhật visited - mồi đã ăn không block nữa
            visited.discard(target)
        
        # Nếu tìm được đường hợp lệ, lưu lại
        if is_valid:
            best_path = cur_path
            best_dirs = path_to_dirs(cur_path)
            break  # Lấy cái đầu tiên/tối ưu
    
    # Nếu không tìm được toàn bộ mồi, chỉ tìm đến 1 mồi gần nhất
    if not best_path:
        visited = fixed_obs.union(map(tuple, snake))
        best_path = find_path_and_or(start, target_food, visited, rows, cols, stats, deadline)
        
        if best_path:
            best_dirs = path_to_dirs(best_path)
        else:
            return _empty_result(start_time)
    
    # Lấy đường đi
    if not best_path:
        return _empty_result(start_time)
    
    duration = time.time() - start_time
    print(f"[DEBUG] AND-OR: Found path of length {len(best_path)}, time: {duration:.4f}s")
    
    return _result(stats, duration, best_dirs, best_path)


def find_path_and_or(start, goal, visited, rows, cols, stats, deadline):
    """
    Tìm đường từ start đến goal bằng BFS.
    - visited: tập hợp các ô không được đi (cơ thể rắn, tường, chướng ngại vật)
    - stats: thống kê nodes
    """
    if start == goal:
        return [start]
    
    frontier = deque([start])
    parent = {start: None}
    in_frontier = {start}
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    while frontier and time.time() < deadline:
        cur = frontier.popleft()
        in_frontier.discard(cur)
        stats["expanded_nodes"].append(cur)
        stats["nodes_expanded"] += 1
        
        # Kiểm tra điều kiện dừng
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return list(reversed(path))
        
        # Expand neighbors
        for dx, dy in dirs:
            nx, ny = cur[0] + dx, cur[1] + dy
            nxt = (nx, ny)
            
            # Kiểm tra hợp lệ
            if not (0 <= nx < rows and 0 <= ny < cols):
                continue
            if nxt in visited or nxt in in_frontier:
                continue
            
            # Thêm vào frontier
            parent[nxt] = cur
            frontier.append(nxt)
            in_frontier.add(nxt)
            visited.add(nxt)
            stats["max_frontier_size"] = max(stats["max_frontier_size"], len(frontier))
    
    return None


# =================== PARTIALLY OBSERVABLE SEARCH ===================
import time
import random
from collections import deque
import itertools

# =================== PARTIALLY OBSERVABLE SEARCH ===================
def partially_observable_search(snake, obstacles, food, rows, cols,
                                max_depth=30,  # độ sâu quyết định tầm nhìn
                                time_limit_ms=80,
                                vision_range=5,
                                random_tries=5):
    """
    Partially Observable Search (PO-Search).
    - Tìm mồi trong tầm nhìn trước (get_visible_food -> BFS đến mục tiêu)
    - Nếu không thấy mồi, khám phá theo heuristic (quadrant) bằng BFS
    - Nếu vẫn không, thử một vài random exploratory walks (ngắn)
    - Trả về kết quả theo _result/_empty_result
    """
    start_time = time.time()
    deadline = start_time + (time_limit_ms / 1000.0)

    if not food:
        return _empty_result(start_time)

    start = tuple(snake[0])
    fixed_obs = set(map(tuple, snake[1:] + obstacles))
    all_food = [tuple(f) for f in food]

    stats = {
        "nodes_expanded": 0,
        "max_frontier_size": 0,
        "expanded_nodes": []
    }

    # 1) Xem có mồi trong tầm nhìn từ start không
    visible = get_visible_food(start, all_food, vision_range)
    if visible:
        target = visible[0]
        visited = fixed_obs.union(set(map(tuple, snake)))
        visited_copy = visited.copy()
        path = find_path_and_or(start, target, visited_copy, rows, cols, stats, deadline)
        if path:
            dirs = path_to_dirs(path)
            duration = time.time() - start_time
            return _result(stats, duration, dirs, path)

    # 2) Heuristic exploration toward an unexplored quadrant
    visited = fixed_obs.union(set(map(tuple, snake)))
    path = heuristic_explore(start, all_food, visited, rows, cols,
                             max_depth, vision_range, stats, deadline)
    if path:
        dirs = path_to_dirs(path)
        duration = time.time() - start_time
        return _result(stats, duration, dirs, path)

    # 3) Random short exploratory attempts as fallback
    for _ in range(random_tries):
        if time.time() > deadline:
            break
        rpath = random_explore(start, fixed_obs.union(set(map(tuple, snake))), rows, cols,
                               max_steps= max(3, max_depth//2), stats=stats, deadline=deadline,
                               vision_range=vision_range, all_food=all_food)
        if rpath:
            dirs = path_to_dirs(rpath)
            duration = time.time() - start_time
            return _result(stats, duration, dirs, rpath)

    # Không tìm được đường
    return _empty_result(start_time)


def get_visible_food(pos, all_food, vision_range):
    """
    Trả về danh sách mồi nằm trong tầm nhìn (theo Manhattan),
    sắp xếp từ gần đến xa.
    """
    visible = []
    for f in all_food:
        dist = abs(pos[0] - f[0]) + abs(pos[1] - f[1])
        if dist <= vision_range:
            visible.append((f, dist))
    visible.sort(key=lambda x: x[1])
    return [v[0] for v in visible]


def heuristic_explore(start, all_food, visited, rows, cols,
                      max_depth, vision_range, stats, deadline):
    """
    Cải tiến: rắn sẽ khám phá dần theo BFS đa tầng, mỗi bước lại mở rộng tầm nhìn.
    Khi thấy mồi ở bất kỳ vị trí nào -> tìm đường đến đó.
    """
    from collections import deque
    queue = deque([(start, [start])])
    local_visited = set(visited)

    while queue and time.time() < deadline:
        pos, path = queue.popleft()

        # Kiểm tra tầm nhìn từ vị trí hiện tại
        visible = get_visible_food(pos, all_food, vision_range)
        if visible:
            # Tìm BFS đến mồi đầu tiên trong tầm nhìn
            food_target = visible[0]
            visited_for_food = visited.copy()
            food_path = find_path_and_or(start, food_target, visited_for_food, rows, cols, stats, deadline)
            if food_path:
                return food_path

        # Mở rộng tìm kiếm (exploration BFS)
        if len(path) >= max_depth:
            continue

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = pos[0] + dx, pos[1] + dy
            nxt = (nx, ny)
            if not (0 <= nx < rows and 0 <= ny < cols):
                continue
            if nxt in local_visited:
                continue
            local_visited.add(nxt)
            queue.append((nxt, path + [nxt]))
            stats["nodes_expanded"] += 1
            stats["expanded_nodes"].append(nxt)
            stats["max_frontier_size"] = max(stats["max_frontier_size"], len(queue))

    # Không tìm thấy mồi nhưng có thể trả về đường khám phá gần nhất
    if queue:
        # Chọn đường cuối cùng làm hướng khám phá
        return queue[-1][1]
    return None

def get_unexplored_quadrants(pos, rows, cols):
    """
    Trả về danh sách 4 điểm đại diện cho các quadrant, sắp xếp ưu tiên quadrant xa nhất.
    """
    quadrants = [
        (rows // 4, cols // 4),
        (rows // 4, 3 * cols // 4),
        (3 * rows // 4, cols // 4),
        (3 * rows // 4, 3 * cols // 4)
    ]
    quadrants.sort(key=lambda q: -(abs(pos[0] - q[0]) + abs(pos[1] - q[1])))
    return quadrants


def random_explore(start, visited, rows, cols, max_steps, stats, deadline, vision_range, all_food):
    """
    Thực hiện một random walk ngắn (max_steps) cố gắng không đi vào visited.
    Trả về đường đi từ start đến vị trí dừng (nếu tìm thấy food trong quá trình, trả về path đến food).
    """
    path = [start]
    cur = start
    local_visited = visited.copy()
    directions = [(1,0),(-1,0),(0,1),(0,-1)]

    for _ in range(max_steps):
        if time.time() > deadline:
            break
        # shuffle lựa chọn để random hóa
        random.shuffle(directions)
        moved = False
        for dx, dy in directions:
            nx, ny = cur[0] + dx, cur[1] + dy
            nxt = (nx, ny)
            if not (0 <= nx < rows and 0 <= ny < cols):
                continue
            if nxt in local_visited:
                continue
            # move
            path.append(nxt)
            local_visited.add(nxt)
            cur = nxt
            moved = True
            # kiểm tra visible food tại ô mới
            visible = get_visible_food(cur, all_food, vision_range)
            if visible:
                # tìm BFS trực tiếp từ start -> visible[0]
                visited_for_food = visited.copy()
                food_path = find_path_and_or(start, visible[0], visited_for_food, rows, cols, stats, deadline)
                if food_path:
                    return food_path
            break
        if not moved:
            # không thể đi tiếp (bị bế tắc)
            break

    if len(path) > 1:
        return path
    return None


def belief_state_search(snake, obstacles, food, rows, cols):
    start_time = time.time()
    obs = set(obstacles)
    snake_body = set(snake)
    start = tuple(snake[0])
    goal = tuple(food[0]) if isinstance(food, list) else tuple(food)

    def in_bounds(p):
        return 0 <= p[0] < rows and 0 <= p[1] < cols

    def neigh4(p):
        x, y = p
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            q = (x+dx, y+dy)
            if in_bounds(q):
                yield q, (dx,dy)

    def legal_step(nxt, snake_now):
        """Một bước là hợp lệ nếu không va vào thân hoặc obstacle"""
        if nxt in obs or nxt in snake_now:
            return False
        return True

    expanded_nodes = []
    nodes_expanded = 0
    max_frontier = 0

    # ========== BFS ĐẾN GẦN FOOD ==========
    q = deque([(start, [], list(snake))])  # (pos, path, body)
    visited = {start}
    found_path = None

    while q:
        pos, path, body_now = q.popleft()
        nodes_expanded += 1
        expanded_nodes.append(pos)

        if pos == goal or abs(pos[0]-goal[0]) + abs(pos[1]-goal[1]) == 1:
            found_path = path
            head = pos
            break

        for nxt, d in neigh4(pos):
            if not legal_step(nxt, body_now):
                continue
            if nxt in visited:
                continue

            visited.add(nxt)
            # Mô phỏng thân rắn di chuyển
            new_body = [nxt] + body_now[:-1]
            q.append((nxt, path + [d], new_body))

        max_frontier = max(max_frontier, len(q))

    # Không tìm thấy đường
    if not found_path:
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

    # ========== BELIEF: TỐI ƯU HƯỚNG ĂN ==========
    head = [start[0], start[1]]
    path = [list(start)]
    for d in found_path:
        head = [head[0] + d[0], head[1] + d[1]]
        path.append(list(head))

    # Nếu đã ở kề food thì chỉ chọn 1 bước hợp pháp tiến vào food
    if abs(head[0]-goal[0]) + abs(head[1]-goal[1]) == 1:
        candidates = []
        for nxt, d in neigh4(tuple(head)):
            if nxt == goal and legal_step(nxt, snake_body):
                candidates.append((nxt, d))
        if candidates:
            nxt, d = random.choice(candidates)
            path.append(list(nxt))
            found_path.append(d)

    # ========== TRẢ KẾT QUẢ ==========
    directions = found_path
    h_val = abs(head[0]-goal[0]) + abs(head[1]-goal[1])

    return {
        "found_path": path,
        "found_directions": directions,
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier,
        "heuristic_value": h_val,
        "distance_cost": len(path),
        "total_cost": h_val,
        "expanded_nodes": expanded_nodes,
        "time": time.time() - start_time
    }