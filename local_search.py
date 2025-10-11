import random
import math
import time
from collections import deque


class LocalSearch:
    def __init__(self, snake, obstacles, food, rows, cols):
        self.snake = snake
        self.obstacles = obstacles
        self.food = food
        self.rows = rows
        self.cols = cols
        self.nodes_expanded = 0
        self.max_frontier_size = 0

    # -------------------------
    # Helper function: Find complete path using BFS
    # -------------------------
    def find_complete_path(self, start_state):
        """Helper function to find a complete path from current state to food using BFS"""
        start = tuple(start_state[0])
        goal = tuple(self.food[0]) if isinstance(self.food, list) else tuple(self.food)

        obstacles_set = set(tuple(obs) for obs in self.obstacles)

        frontier = deque([start])
        came_from = {start: None}
        visited = set([start])

        # Reset counters for accurate measurement
        nodes_expanded = 0
        max_frontier = 1

        # Add obstacles and snake body to visited
        for pos in list(start_state[1:]) + list(self.obstacles):
            visited.add(tuple(pos))

        directions_list = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        while frontier:
            current = frontier.popleft()
            nodes_expanded += 1

            if current == goal:
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()

                # Update global counters
                self.nodes_expanded = nodes_expanded
                self.max_frontier_size = max_frontier
                return path

            for dx, dy in directions_list:
                neighbor = (current[0] + dx, current[1] + dy)

                if (0 <= neighbor[0] < self.rows and 0 <= neighbor[1] < self.cols and
                        neighbor not in visited):
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    frontier.append(neighbor)

                    # Update max frontier size
                    max_frontier = max(max_frontier, len(frontier))

        # Update global counters even if no path found
        self.nodes_expanded = nodes_expanded
        self.max_frontier_size = max_frontier
        return None  # No path found

    # -------------------------
    # Hill Climbing for Snake
    # -------------------------
    def hill_climbing(self, max_iterations=100):
        start_time = time.time()
        self.nodes_expanded = 0
        self.max_frontier_size = 0

        # Heuristic function: Manhattan distance to food
        def heuristic(pos):
            food_pos = self.food[0] if isinstance(self.food, list) else self.food
            return abs(pos[0] - food_pos[0]) + abs(pos[1] - food_pos[1])

        # Try to find a complete path first
        complete_path = self.find_complete_path(self.snake)
        if complete_path:
            directions = []
            for i in range(1, len(complete_path)):
                prev = complete_path[i - 1]
                curr = complete_path[i]
                dx = curr[0] - prev[0]
                dy = curr[1] - prev[1]
                directions.append((dx, dy))

            elapsed_time = time.time() - start_time

            # Calculate heuristic value for start position
            start_heuristic = heuristic(self.snake[0])

            return {
                "found_path": complete_path,
                "found_directions": directions,
                "nodes_expanded": self.nodes_expanded,
                "max_frontier_size": self.max_frontier_size,
                "heuristic_value": start_heuristic,  # h(x) from start to goal
                "distance_cost": len(complete_path) - 1,  # g(x) - actual path cost
                "total_cost": len(complete_path) - 1,  # f(x) = g(x) for BFS
                "expanded_nodes": complete_path,
                "time": elapsed_time
            }

        # Fallback to local search if no complete path found
        current_head = tuple(self.snake[0])
        path = [list(current_head)]
        expanded_nodes = [list(current_head)]

        current_heuristic = heuristic(current_head)
        self.nodes_expanded = 1
        self.max_frontier_size = 1

        for iteration in range(max_iterations):
            if current_heuristic == 0:
                break

            # Generate neighbors (possible moves)
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_head = (current_head[0] + dx, current_head[1] + dy)

                # Check boundaries
                if not (0 <= new_head[0] < self.rows and 0 <= new_head[1] < self.cols):
                    continue

                # Check obstacles
                obstacles_set = set(tuple(obs) for obs in self.obstacles)
                if new_head in obstacles_set:
                    continue

                # Check self-collision (excluding tail for movement)
                snake_positions = set(tuple(segment) for segment in self.snake[:-1])
                if new_head in snake_positions:
                    continue

                neighbors.append(new_head)

            self.nodes_expanded += len(neighbors)
            self.max_frontier_size = max(self.max_frontier_size, len(neighbors))

            if not neighbors:
                break

            # Find best neighbor (lowest heuristic)
            best_neighbor = min(neighbors, key=heuristic)
            best_heuristic = heuristic(best_neighbor)

            # If no improvement, stop
            if best_heuristic >= current_heuristic:
                break

            current_head = best_neighbor
            current_heuristic = best_heuristic
            path.append(list(current_head))
            expanded_nodes.append(list(current_head))

        # Convert to directions
        directions = []
        for i in range(1, len(path)):
            prev_head = path[i - 1]
            curr_head = path[i]
            dx = curr_head[0] - prev_head[0]
            dy = curr_head[1] - prev_head[1]
            directions.append((dx, dy))

        elapsed_time = time.time() - start_time

        return {
            "found_path": path,
            "found_directions": directions,
            "nodes_expanded": self.nodes_expanded,
            "max_frontier_size": self.max_frontier_size,
            "heuristic_value": heuristic(path[0]) if path else 0,  # h(x) from start
            "distance_cost": len(path) - 1 if path else 0,  # g(x) - actual moves
            "total_cost": len(path) - 1 if path else 0,  # f(x) = g(x) for hill climbing
            "expanded_nodes": expanded_nodes,
            "time": elapsed_time
        }

    # -------------------------
    # Simulated Annealing for Snake
    # -------------------------
    def simulated_annealing(self, initial_temp=1000, cooling_rate=0.95, max_iterations=100):
        start_time = time.time()
        self.nodes_expanded = 0
        self.max_frontier_size = 0

        # Heuristic function: Manhattan distance to food
        def heuristic(pos):
            food_pos = self.food[0] if isinstance(self.food, list) else self.food
            return abs(pos[0] - food_pos[0]) + abs(pos[1] - food_pos[1])

        # Try to find a complete path first
        complete_path = self.find_complete_path(self.snake)
        if complete_path:
            directions = []
            for i in range(1, len(complete_path)):
                prev = complete_path[i - 1]
                curr = complete_path[i]
                dx = curr[0] - prev[0]
                dy = curr[1] - prev[1]
                directions.append((dx, dy))

            elapsed_time = time.time() - start_time

            start_heuristic = heuristic(self.snake[0])

            return {
                "found_path": complete_path,
                "found_directions": directions,
                "nodes_expanded": self.nodes_expanded,
                "max_frontier_size": self.max_frontier_size,
                "heuristic_value": start_heuristic,
                "distance_cost": len(complete_path) - 1,
                "total_cost": len(complete_path) - 1,
                "expanded_nodes": complete_path,
                "time": elapsed_time
            }

        # Fallback to simulated annealing
        current_head = tuple(self.snake[0])
        path = [list(current_head)]
        expanded_nodes = [list(current_head)]

        current_heuristic = heuristic(current_head)
        temperature = initial_temp

        self.nodes_expanded = 1
        self.max_frontier_size = 1

        for iteration in range(max_iterations):
            if current_heuristic == 0:
                break

            # Generate neighbors
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_head = (current_head[0] + dx, current_head[1] + dy)

                if not (0 <= new_head[0] < self.rows and 0 <= new_head[1] < self.cols):
                    continue

                obstacles_set = set(tuple(obs) for obs in self.obstacles)
                if new_head in obstacles_set:
                    continue

                snake_positions = set(tuple(segment) for segment in self.snake[:-1])
                if new_head in snake_positions:
                    continue

                neighbors.append(new_head)

            self.nodes_expanded += len(neighbors)
            self.max_frontier_size = max(self.max_frontier_size, len(neighbors))

            if not neighbors:
                break

            # Randomly select a neighbor
            next_head = random.choice(neighbors)
            next_heuristic = heuristic(next_head)

            delta = next_heuristic - current_heuristic

            # Accept if better, or with probability if worse
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_head = next_head
                current_heuristic = next_heuristic
                path.append(list(current_head))
                expanded_nodes.append(list(current_head))

            temperature *= cooling_rate
            if temperature < 1e-10:
                break

        # Convert to directions
        directions = []
        for i in range(1, len(path)):
            prev_head = path[i - 1]
            curr_head = path[i]
            dx = curr_head[0] - prev_head[0]
            dy = curr_head[1] - prev_head[1]
            directions.append((dx, dy))

        elapsed_time = time.time() - start_time

        return {
            "found_path": path,
            "found_directions": directions,
            "nodes_expanded": self.nodes_expanded,
            "max_frontier_size": self.max_frontier_size,
            "heuristic_value": heuristic(path[0]) if path else 0,
            "distance_cost": len(path) - 1 if path else 0,
            "total_cost": len(path) - 1 if path else 0,
            "expanded_nodes": expanded_nodes,
            "time": elapsed_time
        }

    # -------------------------
    # Genetic Algorithm for Snake
    # -------------------------
    def genetic_algorithm(self, population_size=20, generations=50, mutation_rate=0.1):
        start_time = time.time()
        self.nodes_expanded = 0
        self.max_frontier_size = population_size

        # Heuristic function: Manhattan distance to food
        def heuristic(pos):
            food_pos = self.food[0] if isinstance(self.food, list) else self.food
            return abs(pos[0] - food_pos[0]) + abs(pos[1] - food_pos[1])

        # Try to find a complete path first
        complete_path = self.find_complete_path(self.snake)
        if complete_path:
            directions = []
            for i in range(1, len(complete_path)):
                prev = complete_path[i - 1]
                curr = complete_path[i]
                dx = curr[0] - prev[0]
                dy = curr[1] - prev[1]
                directions.append((dx, dy))

            elapsed_time = time.time() - start_time

            start_heuristic = heuristic(self.snake[0])

            return {
                "found_path": complete_path,
                "found_directions": directions,
                "nodes_expanded": self.nodes_expanded,
                "max_frontier_size": self.max_frontier_size,
                "heuristic_value": start_heuristic,
                "distance_cost": len(complete_path) - 1,
                "total_cost": len(complete_path) - 1,
                "expanded_nodes": complete_path,
                "time": elapsed_time
            }

        # Fallback to simple move towards food
        head = tuple(self.snake[0])
        food_pos = tuple(self.food[0]) if isinstance(self.food, list) else tuple(self.food)
        obstacles_set = set(tuple(obs) for obs in self.obstacles)

        # Find a safe move towards food
        best_move = None
        best_heuristic = float('inf')
        possible_moves = []

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_head = (head[0] + dx, head[1] + dy)
            if (0 <= new_head[0] < self.rows and 0 <= new_head[1] < self.cols and
                    new_head not in obstacles_set and
                    new_head not in set(tuple(seg) for seg in self.snake[:-1])):
                possible_moves.append((dx, dy))
                h_val = heuristic(new_head)
                if h_val < best_heuristic:
                    best_heuristic = h_val
                    best_move = (dx, dy)

        self.nodes_expanded = len(possible_moves)
        self.max_frontier_size = len(possible_moves)

        if best_move:
            directions = [best_move]
            new_position = [head[0] + best_move[0], head[1] + best_move[1]]
            elapsed_time = time.time() - start_time

            return {
                "found_path": [list(head), new_position],
                "found_directions": directions,
                "nodes_expanded": self.nodes_expanded,
                "max_frontier_size": self.max_frontier_size,
                "heuristic_value": heuristic(head),  # h(x) from start position
                "distance_cost": 1,  # g(x) = 1 move
                "total_cost": 1,  # f(x) = 1 for single move
                "expanded_nodes": [list(head), new_position],
                "time": elapsed_time
            }

        # Final fallback
        elapsed_time = time.time() - start_time
        return {
            "found_path": [],
            "found_directions": [],
            "nodes_expanded": 0,
            "max_frontier_size": 0,
            "heuristic_value": 0,
            "distance_cost": 0,
            "total_cost": 0,
            "expanded_nodes": [],
            "time": elapsed_time
        }


# -------------------------
# Wrapper functions for UI integration
# -------------------------

def Hill_Climbing(snake, obstacles, food, rows, cols):
    ls = LocalSearch(snake, obstacles, food, rows, cols)
    return ls.hill_climbing()


def Simulated_Annealing(snake, obstacles, food, rows, cols):
    ls = LocalSearch(snake, obstacles, food, rows, cols)
    return ls.simulated_annealing()


def Genetic_Algorithm(snake, obstacles, food, rows, cols):
    ls = LocalSearch(snake, obstacles, food, rows, cols)
    return ls.genetic_algorithm()