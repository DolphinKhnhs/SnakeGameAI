import time, heapq
from collections import deque


# Bản chất: sử dụng Queue (FIFO)
def BFS(snake, obstacles, food, row, col):
    start_time = time.time()

    start = tuple(snake[0])
    goals = [tuple(f) for f in food]  # Sửa: food là list nên cần chuyển đổi

    frontier = deque([start])  # đúng bản chất!
    parent = {start: None}
    visited = set([start])

    # Thêm snake và obstacles vào visited
    for pos in list(snake[1:]) + list(obstacles):
        visited.add(tuple(pos))

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    nodes_expanded = 0
    max_frontier_size = 1
    found_path, found_directions = None, None
    expanded_nodes = []  # THÊM: để lưu các node đã mở rộng cho visualization

    while frontier:
        x, y = frontier.popleft()
        expanded_nodes.append((x, y))  # THÊM: ghi nhận node đã mở rộng

        # nếu tìm thấy food (kiểm tra tất cả food)
        if (x, y) in goals:
            found_path = []
            cur = (x, y)
            while cur is not None:
                found_path.append(list(cur))
                cur = parent[cur]
            found_path.reverse()

            # lấy hướng đi
            found_directions = []
            for i in range(1, len(found_path)):
                prev_x, prev_y = found_path[i - 1]
                curr_x, curr_y = found_path[i]
                dx, dy = curr_x - prev_x, curr_y - prev_y
                found_directions.append((dx, dy))
            break

        # mở rộng nút
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # kiểm tra biên đúng thứ tự (x ~ row, y ~ col)
            if 0 <= nx < row and 0 <= ny < col:
                new_pos = (nx, ny)
                if new_pos not in visited:
                    visited.add(new_pos)
                    parent[new_pos] = (x, y)
                    frontier.append(new_pos)
                    nodes_expanded += 1
                    max_frontier_size = max(max_frontier_size, len(frontier))

    end_time = time.time()
    stats = {
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier_size,
        "time": end_time - start_time,
        "found_directions": found_directions,
        "found_path": found_path,
        "expanded_nodes": expanded_nodes  # THÊM: trả về expanded_nodes
    }

    return stats


# Bản chất: sử dụng Priority Queue (ưu tiên đỉnh có chi phí thấp nhất)
def UCS(snake, obstacles, food, row, col):
    start_time = time.time()
    start = tuple(snake[0])
    goals = [tuple(f) for f in food]  # Sửa: food là list

    pq = [(0, start)]  # Hàng đợi ưu tiên (cost, (x, y))
    visited = set()
    parent = {start: None}
    cost_so_far = {start: 0}

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    nodes_expanded = 0
    max_frontier_size = 1
    found_path, found_directions = None, None
    expanded_nodes = []  # THÊM: để lưu các node đã mở rộng

    while pq:
        current_cost, (x, y) = heapq.heappop(pq)

        if (x, y) in visited:
            continue

        expanded_nodes.append((x, y))  # THÊM: ghi nhận node đã mở rộng
        visited.add((x, y))
        nodes_expanded += 1

        # Kiểm tra nếu tìm thấy food
        if (x, y) in goals:
            # reconstruct path
            found_path = []
            cur = (x, y)
            while cur is not None:
                found_path.append(list(cur))
                cur = parent[cur]
            found_path.reverse()

            # lấy hướng đi
            found_directions = []
            for i in range(1, len(found_path)):
                prev_x, prev_y = found_path[i - 1]
                curr_x, curr_y = found_path[i]
                dx, dy = curr_x - prev_x, curr_y - prev_y
                found_directions.append((dx, dy))
            break

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < row and 0 <= ny < col and
                    (nx, ny) not in [tuple(s) for s in snake] and  # Sửa: chuyển sang tuple để so sánh
                    (nx, ny) not in obstacles):

                new_pos = (nx, ny)
                new_cost = current_cost + 1
                if new_pos not in cost_so_far or new_cost < cost_so_far[new_pos]:
                    cost_so_far[new_pos] = new_cost
                    parent[new_pos] = (x, y)
                    heapq.heappush(pq, (new_cost, new_pos))
                    max_frontier_size = max(max_frontier_size, len(pq))

    end_time = time.time()
    stats = {
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier_size,
        "time": end_time - start_time,
        "found_directions": found_directions,
        "found_path": found_path,
        "expanded_nodes": expanded_nodes  # THÊM: trả về expanded_nodes
    }
    return stats


# Bản chất: sử dụng Stack (LIFO)
def DFS(snake, obstacles, food, row, col):
    start_time = time.time()

    start = tuple(snake[0])
    goals = [tuple(f) for f in food]  # Sửa: food là list

    stack = [start]  # đúng bản chất!
    parent = {start: None}
    visited = set([start])

    for pos in list(snake[1:]) + list(obstacles):
        visited.add(tuple(pos))

    base_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    nodes_expanded = 0
    max_frontier_size = 1
    found_path, found_directions = None, None
    expanded_nodes = []  # THÊM: để lưu các node đã mở rộng

    while stack:
        x, y = stack.pop()
        expanded_nodes.append((x, y))  # THÊM: ghi nhận node đã mở rộng

        # Kiểm tra nếu tìm thấy food
        if (x, y) in goals:
            # reconstruct path
            found_path = []
            cur = (x, y)
            while cur is not None:
                found_path.append(list(cur))
                cur = parent[cur]
            found_path.reverse()

            # lấy hướng đi
            found_directions = []
            for i in range(1, len(found_path)):
                prev_x, prev_y = found_path[i - 1]
                curr_x, curr_y = found_path[i]
                dx, dy = curr_x - prev_x, curr_y - prev_y
                found_directions.append((dx, dy))
            break

        # cải tiến (cô chấp nhận) - mở rộng nút → ưu tiên gần food hơn
        # Sửa: sử dụng goal đầu tiên để sắp xếp
        if goals:
            goal = goals[0]
            dirs_sorted = sorted(
                base_directions,
                key=lambda d: abs((x + d[0]) - goal[0]) + abs((y + d[1]) - goal[1]),
                reverse=True
            )
        else:
            dirs_sorted = base_directions

        for dx, dy in dirs_sorted:
            nx, ny = x + dx, y + dy
            if 0 <= nx < row and 0 <= ny < col:
                new_pos = (nx, ny)
                if new_pos not in visited:
                    visited.add(new_pos)
                    parent[new_pos] = (x, y)
                    stack.append(new_pos)
                    nodes_expanded += 1
                    max_frontier_size = max(max_frontier_size, len(stack))

    end_time = time.time()
    stats = {
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier_size,
        "time": end_time - start_time,
        "found_directions": found_directions,
        "found_path": found_path,
        "expanded_nodes": expanded_nodes  # THÊM: trả về expanded_nodes
    }
    return stats

# Bản chất: Kết hợp BFS và DFS - tìm kiếm theo chiều sâu lặp lại
def IDS(snake, obstacles, food, row, col):
    start_time = time.time()

    start = tuple(snake[0])
    goals = [tuple(f) for f in food]

    # Hàm DFS giới hạn độ sâu
    def depth_limited_search(current, goal, depth_limit):
        stack = [(current, 0, [current])]
        visited_at_depth = set([current])

        while stack:
            (x, y), depth, path = stack.pop()

            # Nếu tìm thấy goal
            if (x, y) == goal:
                return path

            # Nếu chưa đạt độ sâu tối đa, tiếp tục mở rộng
            if depth < depth_limit:
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < row and 0 <= ny < col:
                        new_pos = (nx, ny)
                        # Kiểm tra không phải thân rắn hoặc vật cản
                        if (new_pos not in [tuple(s) for s in snake[1:]] and
                                new_pos not in obstacles and
                                new_pos not in visited_at_depth):
                            visited_at_depth.add(new_pos)
                            new_path = path + [new_pos]
                            stack.append((new_pos, depth + 1, new_path))
                            expanded_nodes.append(new_pos)  # Ghi nhận node mở rộng
        return None

    expanded_nodes = []  # Lưu tất cả các node đã mở rộng
    nodes_expanded = 0
    max_frontier_size = 1
    found_path = None
    found_directions = None

    # Thử từng độ sâu cho đến khi tìm thấy đường đi hoặc vượt quá giới hạn
    max_depth = row * col  # Giới hạn tối đa để tránh vòng lặp vô hạn

    for depth_limit in range(1, max_depth + 1):
        # Thử với mỗi food (ưu tiên food gần nhất)
        for goal in goals:
            expanded_nodes.append(start)  # Thêm start node
            path = depth_limited_search(start, goal, depth_limit)

            if path:
                found_path = [list(pos) for pos in path]

                # Lấy hướng đi
                found_directions = []
                for i in range(1, len(found_path)):
                    prev_x, prev_y = found_path[i - 1]
                    curr_x, curr_y = found_path[i]
                    dx, dy = curr_x - prev_x, curr_y - prev_y
                    found_directions.append((dx, dy))

                nodes_expanded = len(set(expanded_nodes))  # Số node duy nhất đã mở rộng
                break

        if found_path:
            break

    end_time = time.time()

    stats = {
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier_size,
        "time": end_time - start_time,
        "found_directions": found_directions,
        "found_path": found_path,
        "expanded_nodes": expanded_nodes
    }

    return stats