import tkinter as tk
from tkinter import ttk
import random
from Load_images import SpriteManager
from uninformedsearch import BFS, DFS, UCS, IDS
from informed_search import A_star, greedy_search
from  local_search import LocalSearch

cell_size = 20
col, row = 42, 19
width, height = cell_size * col, cell_size * row
game_speed = 200


class SnakeGame:
    def __init__(self, window):
        self.window = window
        window.title("Snake Game With AI")
        window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}")
        window.resizable(True, True)

        # ------------------ GRID CONFIG ------------------
        for i in range(4):
            self.window.grid_columnconfigure(i, weight=1)
            self.window.grid_rowconfigure(i, weight=1)

        # ------------------ VARIABLES --------------------
        self.sprite_manager = SpriteManager(cell_size=cell_size)
        self.algo_variable = tk.StringVar(value="BFS")
        self.difficulty_var = tk.StringVar(value="Hard")
        self.obstacles = []
        self.food = []
        self.snake = []

        # Game state variables
        self.game_over = False
        self.paused = False
        self.after_id = None
        self.direction = (0, 1)  # Initial direction: right
        self.next_direction = (0, 1)
        self.score = 0
        self.status = tk.StringVar(value="Ready")
        self.death_reason = ""
        self.game_over_text = None

        # variable for update
        # Algorithm info
        self.algorithm = self.algo_variable.get()
        self.node_expanded = 0
        self.max_frontier = 0
        self.path_length = 0
        self.execution_time = 0
        self.path = []
        self.total_cost = 0
        self.distance_cost = 0
        self.heuristic_value = 0
        # Game info
        self.snake_length = 0
        self.food_pos = (0, 0)
        self.snake_head = (0, 0)
        self.score_ = 0
        self.current_move = ""
        # statistics
        self.total_move = 0
        self.food_eaten = 0
        self.best_score = 0
        self.avg_solve_time = 0
        self.space_efficiency = 0
        self.movement_efficiency = 0
        self.solve_times = []

        # Biến cho search visualization
        self.search_visualization_done = False
        self.expanded_nodes = []
        self.final_path = []
        self.visualization_step = 0
        self.visualization_speed = 100

        # Biến kiểm soát visualization
        self.visualization_in_progress = False
        self.visualization_complete = False

        # Biến để kiểm soát việc chờ đường đi
        self.waiting_for_path = False
        self.path_found = False
        self.just_ate_food = False

        # THÊM BIẾN MỚI: Để theo dõi đường đi hiện tại
        self.current_path = []
        self.current_path_index = 0
        self.following_path = False

        # THÊM BIẾN: Để theo dõi số food ban đầu
        self.initial_food_count = 0
        self.food_remaining = 0

        # -------------------OBSTACLES----------------------
        self.obstacles_easy = [
            (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 16), (2, 23), (3, 7), (3, 14), (3, 23),
            (4, 4), (4, 7), (4, 20), (4, 21), (4, 22), (4, 23), (4, 24), (4, 34), (4, 35), (5, 4), (5, 5),
            (5, 7), (5, 10), (5, 23), (6, 7), (6, 23), (7, 7), (7, 37), (7, 38), (10, 10), (10, 13), (10, 24),
            (10, 36), (10, 37), (11, 5), (11, 6), (11, 10), (11, 11), (11, 12), (11, 13), (11, 24), (11, 36),
            (11, 37), (12, 3), (12, 24), (12, 25), (12, 26), (12, 27), (12, 28), (12, 29), (13, 3), (13, 16),
            (13, 24), (14, 3), (14, 16), (14, 24), (14, 36), (15, 3), (15, 4), (15, 5), (15, 6), (15, 8),
            (15, 16), (15, 36), (16, 8), (16, 39)
        ]
        self.obstacles_medium = [
            (0, 13), (1, 0), (1, 1), (1, 11), (1, 12), (1, 13), (1, 15), (1, 29), (1, 36), (2, 13), (2, 15), (2, 36),
            (3, 1), (3, 13), (3, 15), (3, 20), (3, 26), (3, 33), (3, 34), (3, 35), (3, 36), (3, 37), (3, 38), (3, 39),
            (4, 1), (4, 3), (4, 4), (4, 19), (4, 20), (4, 21), (4, 26), (4, 36), (5, 1), (5, 4), (5, 26), (5, 36),
            (6, 1), (6, 4), (6, 7), (6, 8), (6, 9), (6, 10), (6, 26), (7, 1), (7, 2), (7, 10), (7, 26), (8, 2),
            (8, 10), (8, 20), (8, 36), (8, 37), (8, 40), (9, 0), (9, 2), (9, 10), (9, 14), (9, 19), (9, 20), (9, 21),
            (10, 0), (10, 2), (10, 3), (10, 4), (10, 10), (10, 29), (10, 30), (10, 31), (10, 32), (10, 33), (10, 34),
            (10, 38), (10, 39), (11, 19), (11, 21), (11, 29), (12, 14), (12, 15), (12, 20), (12, 29), (13, 7),
            (13, 8), (13, 9), (13, 15), (13, 20), (13, 29), (14, 2), (14, 3), (14, 20), (15, 2), (15, 3), (15, 27),
            (15, 28), (15, 29), (15, 30), (15, 35), (15, 39), (16, 12), (16, 17), (16, 29), (16, 35), (16, 39),
            (17, 1), (17, 17), (17, 22), (17, 29)
        ]
        self.obstacle_hard = [
            (0, 5), (0, 33), (1, 1), (1, 2), (1, 4), (1, 23), (1, 26), (1, 30), (1, 36), (1, 37), (2, 1), (2, 23),
            (2, 26), (2, 30),
            (2, 33), (2, 37), (2, 38), (3, 1), (3, 3), (3, 4), (3, 6), (3, 11), (3, 13), (3, 14), (3, 15), (3, 16),
            (3, 17), (3, 18),
            (3, 23), (3, 26), (3, 27), (3, 28), (3, 33), (3, 38), (3, 39), (4, 1), (4, 3), (4, 7), (4, 11), (4, 23),
            (4, 33), (4, 39),
            (5, 1), (5, 3), (5, 11), (5, 13), (5, 16), (5, 20), (5, 23), (5, 28), (5, 31), (5, 33), (5, 35), (5, 36),
            (5, 37), (5, 39),
            (6, 3), (6, 4), (6, 5), (6, 6), (6, 11), (6, 13), (6, 16), (6, 20), (6, 23), (6, 33), (6, 41), (7, 0),
            (7, 1),
            (7, 3), (7, 11), (7, 13), (7, 14), (7, 16), (7, 20), (7, 21), (7, 22), (7, 23), (7, 24), (7, 25), (7, 26),
            (7, 27), (7, 28),
            (7, 33), (7, 34), (7, 35), (7, 36), (7, 37), (7, 38), (7, 40), (7, 41), (8, 1), (8, 3), (8, 6), (8, 8),
            (8, 11), (8, 14),
            (8, 16), (8, 19), (8, 23), (8, 31), (8, 35), (9, 11), (9, 12), (9, 14), (9, 16), (9, 37), (9, 41), (10, 3),
            (10, 4), (10, 5),
            (10, 8), (10, 12), (10, 14), (10, 16), (10, 17), (10, 18), (10, 37), (11, 0), (11, 1), (11, 3), (11, 4),
            (11, 5), (11, 6),
            (11, 7), (11, 8), (11, 12), (11, 14), (11, 24), (11, 37), (11, 40), (12, 3), (12, 12), (12, 17), (12, 18),
            (12, 21), (12, 24),
            (12, 31), (12, 32), (12, 33), (12, 34), (12, 35), (12, 37), (12, 40), (13, 1), (13, 2), (13, 3), (13, 12),
            (13, 14), (13, 17),
            (13, 21), (13, 24), (13, 35), (13, 37), (13, 40), (14, 12), (14, 14), (14, 17), (14, 21), (14, 24),
            (14, 25), (14, 26),
            (14, 27), (14, 28), (14, 31), (14, 32), (14, 33), (14, 35), (14, 37), (14, 40), (15, 2), (15, 6), (15, 7),
            (15, 8), (15, 9),
            (15, 12), (15, 17), (15, 18), (15, 20), (15, 31), (15, 35), (15, 37), (15, 40), (16, 2), (16, 3), (16, 4),
            (16, 5), (16, 10),
            (16, 17), (16, 33), (16, 37), (16, 39), (16, 40), (17, 2), (17, 20), (17, 22), (17, 24), (17, 25), (17, 27),
            (17, 28), (17, 30), (17, 33), (17, 35), (17, 36), (17, 37), (18, 5), (18, 8), (18, 22), (18, 33)
        ]

        # ------------------ FRAMES -----------------------
        self.frame_algorithminfo = tk.LabelFrame(self.window, text="Algorithm Information", font=("Arial", 8, "bold"))
        self.frame_algorithminfo.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.frame_gameinfo = tk.LabelFrame(self.window, text="Game Information", font=("Arial", 8, "bold"))
        self.frame_gameinfo.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.frame_statistics = tk.LabelFrame(self.window, text="Statistics", font=("Arial", 8, "bold"))
        self.frame_statistics.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.frame_snake = tk.LabelFrame(self.window, text="Snake", font=("Arial", 8, "bold"))
        self.frame_snake.grid(row=0, column=1, columnspan=3, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.frame_search = tk.LabelFrame(self.window, text="Search Visualization", font=("Arial", 8, "bold"))
        self.frame_search.grid(row=2, column=1, columnspan=3, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.frame_algorithm = tk.LabelFrame(self.window, text="Algorithm", font=("Arial", 8, "bold"))
        self.frame_algorithm.grid(row=0, column=4, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.frame_controls = tk.LabelFrame(self.window, text="Control", font=("Arial", 8, "bold"))
        self.frame_controls.grid(row=2, column=4, padx=5, pady=5, sticky="nsew")

        # ------------------ CANVAS -----------------------
        self.canvas_snake = tk.Canvas(self.frame_snake, height=height)
        self.canvas_snake.pack(fill="both", expand=True, padx=5)
        self.canvas_search = tk.Canvas(self.frame_search, height=height)
        self.canvas_search.pack(fill="both", expand=True, padx=5)

        # ------------------ INITIALIZE UI ----------------
        self.init_ui()

        # ------------------ BIND EVENTS ------------------
        self.window.bind('<space>', self.toggle_pause)
        self.window.bind('<Escape>', self.quit_game)
        self.window.bind('<r>', self.restart_game)
        self.window.focus_set()

    def init_ui(self):
        self.draw_background(self.canvas_snake)
        self.draw_background(self.canvas_search)
        self.create_algo_widgets()
        self.create_gameinfo_frame()
        self.create_statistics_frame()
        self.create_algorithminfo_frame()
        self.add_control_buttons()

    def create_algo_widgets(self):
        for i in range(2):
            self.frame_algorithm.grid_columnconfigure(i, weight=0)
        for i in range(3):
            self.frame_algorithm.grid_rowconfigure(i, weight=0)

        algo_groups = {
            "Uninformed search": ["BFS", "DFS", "UCS", "IDS"],  # THÊM IDS VÀO DANH SÁCH
            "Informed search": ["A*", "Greedy"],
            "Local search": ["Hill Climbing", "Simulated Annealing"],
            "Complex Environment": ["AND-OR Tree Search", "Partially Observable Search"],
            "CSP Search": ["Backtracking", "Forward Checking"]
        }
        positions = {
            "Uninformed search": (0, 0),
            "Informed search": (1, 0),
            "Local search": (2, 0),
            "Complex Environment": (0, 1),
            "CSP Search": (1, 1)
        }
        for group_name, algos in algo_groups.items():
            r, c = positions[group_name]
            frame = tk.LabelFrame(self.frame_algorithm, text=group_name, font=("Arial", 8, "bold"))
            frame.grid(row=r, column=c, padx=5, pady=2, sticky="nsew")
            for algo in algos:
                tk.Radiobutton(frame, text=algo, variable=self.algo_variable, value=algo,
                               command=self.on_algorithm_change).pack(anchor="w")

    def on_algorithm_change(self):
        if not self.paused and not self.game_over and hasattr(self, 'snake') and len(self.snake) > 0:
            # Khi đổi thuật toán, dừng đường đi hiện tại và chạy lại
            self.following_path = False
            self.current_path = []
            self.run_algorithm()

    def create_algorithminfo_frame(self):
        columns = ("Information", "Value")
        self.table_algoinfo = ttk.Treeview(
            self.frame_algorithminfo, columns=columns, show="headings", height=6
        )
        self.table_algoinfo.heading("Information", text="Information")
        self.table_algoinfo.heading("Value", text="Value")
        self.table_algoinfo.column("Information", width=50, anchor="w")
        self.table_algoinfo.column("Value", width=80, anchor="w")

        self.algoinfo_items = {
            "algorithm": self.table_algoinfo.insert("", "end", iid="algorithm", values=("Algorithm", "None")),
            "nodes": self.table_algoinfo.insert("", "end", iid="nodes", values=("Nodes Expanded", "0")),
            "frontier": self.table_algoinfo.insert("", "end", iid="frontier", values=("Max Frontier Size", "0")),
            "pathlen": self.table_algoinfo.insert("", "end", iid="pathlen", values=("Path Length", "0")),
            "time": self.table_algoinfo.insert("", "end", iid="time", values=("Execution Time", "0.0000 s")),
            "path": self.table_algoinfo.insert("", "end", iid="path", values=("Path", "")),
            "heuristic": self.table_algoinfo.insert("", "end", iid="heuristic", values=("h(x)", "0")),
            "distance_cost": self.table_algoinfo.insert("", "end", iid="distance_cost", values=("g(x)", "0")),
            "total_cost": self.table_algoinfo.insert("", "end", iid="total_cost", values=("f(x)", "0")),
        }

        scrollbar = tk.Scrollbar(self.frame_algorithminfo, orient="vertical", command=self.table_algoinfo.yview)
        self.table_algoinfo.configure(yscrollcommand=scrollbar.set)
        self.frame_algorithminfo.grid_rowconfigure(0, weight=1)
        self.frame_algorithminfo.grid_columnconfigure(0, weight=1)
        self.table_algoinfo.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def create_gameinfo_frame(self):
        columns = ("Information", "Value")
        self.table_gameinfo = ttk.Treeview(
            self.frame_gameinfo, columns=columns, show="headings", height=4
        )
        self.table_gameinfo.heading("Information", text="Information")
        self.table_gameinfo.heading("Value", text="Value")
        self.table_gameinfo.column("Information", width=50, anchor="w")
        self.table_gameinfo.column("Value", width=80, anchor="center")
        self.gameinfo_items = {
            "length": self.table_gameinfo.insert("", "end", iid="length", values=("Snake length", "0")),
            "food": self.table_gameinfo.insert("", "end", iid="food", values=("Food position", "None")),
            "head": self.table_gameinfo.insert("", "end", iid="head", values=("Snake head", "(0,0)")),
            "score": self.table_gameinfo.insert("", "end", iid="score", values=("Score", "0")),
            "current_move": self.table_gameinfo.insert("", "end", iid="current_move", values=("Current move", "")),
            "status": self.table_gameinfo.insert("", "end", iid="status", values=("Status", "")),
        }
        scrollbar = tk.Scrollbar(self.frame_gameinfo, orient="vertical", command=self.table_gameinfo.yview)
        self.table_gameinfo.configure(yscrollcommand=scrollbar.set)
        self.frame_gameinfo.grid_rowconfigure(0, weight=1)
        self.frame_gameinfo.grid_columnconfigure(0, weight=1)
        self.table_gameinfo.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def create_statistics_frame(self):
        columns = ("Information", "Value")
        self.detailed_stats_table = ttk.Treeview(
            self.frame_statistics, columns=columns, show="headings", height=6
        )
        self.detailed_stats_table.heading("Information", text="Information")
        self.detailed_stats_table.heading("Value", text="Value")
        self.detailed_stats_table.column("Information", width=50, anchor="w")
        self.detailed_stats_table.column("Value", width=80, anchor="w")

        self.detailed_stats_items = {
            "total_moves": self.detailed_stats_table.insert("", "end", values=("Total Moves", "0")),
            "food_eaten": self.detailed_stats_table.insert("", "end", values=("Food Eaten", "0")),
            "best_score": self.detailed_stats_table.insert("", "end", values=("Best Score", "0")),
            "avg_solve_time": self.detailed_stats_table.insert("", "end", values=("Avg Solve Time", "0.0000s")),
            "space_efficiency": self.detailed_stats_table.insert("", "end", values=("Space efficiency", "0%")),
            "movement_efficiency": self.detailed_stats_table.insert("", "end", values=("Movement efficiency", "0%")),
        }
        scrollbar = tk.Scrollbar(self.frame_statistics, orient="vertical", command=self.detailed_stats_table.yview)
        self.detailed_stats_table.configure(yscrollcommand=scrollbar.set)
        self.frame_statistics.grid_rowconfigure(0, weight=1)
        self.frame_statistics.grid_columnconfigure(0, weight=1)
        self.detailed_stats_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def add_control_buttons(self):
        difficulty_label = tk.Label(self.frame_controls, text="Difficulty", font=("Arial", 10, "bold"))
        difficulty_label.grid(row=0, column=0, columnspan=3, pady=(5, 0))

        frame_difficulty = tk.Frame(self.frame_controls)
        frame_difficulty.grid(row=1, column=0, columnspan=3, pady=5)

        difficulties = [("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")]
        for i, (label, value) in enumerate(difficulties):
            tk.Radiobutton(
                frame_difficulty,
                text=label,
                variable=self.difficulty_var,
                value=value,
                font=("Arial", 9),
                anchor="w",
                command=self.on_difficulty_change
            ).grid(row=0, column=i, padx=10)

        self.speed_scale = tk.Scale(
            self.frame_controls,
            from_=10, to=500,
            orient="horizontal",
            label="Speed",
            length=200,
            resolution=10,
            font=("Arial", 9, "bold"),
            command=self.update_speed
        )
        self.speed_scale.set(game_speed)
        self.speed_scale.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.vis_speed_scale = tk.Scale(
            self.frame_controls,
            from_=10, to=500,
            orient="horizontal",
            label="Visualization Speed",
            length=200,
            resolution=10,
            font=("Arial", 9, "bold"),
            command=self.set_visualization_speed
        )
        self.vis_speed_scale.set(self.visualization_speed)
        self.vis_speed_scale.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        btn_pause = tk.Button(self.frame_controls, text="⏸ Pause/Resume", bg="#4CAF50", fg="white",
                              font=("Arial", 10, "bold"), command=self.toggle_pause)
        btn_restart = tk.Button(self.frame_controls, text="🔄 Restart", bg="#2196F3", fg="white",
                                font=("Arial", 10, "bold"), command=self.restart_game)
        btn_quit = tk.Button(self.frame_controls, text="❌ Quit", bg="#f44336", fg="white",
                             font=("Arial", 10, "bold"), command=self.quit_game)
        btn_run = tk.Button(self.frame_controls, text="🚀 Run", bg="#FF9800", fg="white",
                            font=("Arial", 10, "bold"), command=self.start_game)
        btn_stats = tk.Button(self.frame_controls, text="📊 Statistics", bg="#9C27B0", fg="white",
                              font=("Arial", 10, "bold"))

        for i in range(3):
            self.frame_controls.grid_columnconfigure(i, weight=1)
        for i in range(10):
            self.frame_controls.grid_rowconfigure(i, weight=1)

        btn_pause.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        btn_restart.grid(row=4, column=1, padx=10, pady=5, sticky="nsew")
        btn_quit.grid(row=4, column=2, padx=10, pady=5, sticky="nsew")

        btn_run.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
        btn_stats.grid(row=5, column=1, padx=10, pady=5, sticky="nsew")

    def set_visualization_speed(self, speed):
        self.visualization_speed = int(speed)

    def on_difficulty_change(self):
        if not self.paused and not self.game_over and hasattr(self, 'snake') and len(self.snake) > 0:
            self.generate_obstacles()
            self.generate_food()
            self.following_path = False  # Dừng đường đi hiện tại
            self.current_path = []
            self.run_algorithm()

    def update_gameinfo(self, length=None, food=None, head=None, score=None, current_move=None, status=None):
        params = {"length": length, "food": food, "head": head, "score": score, "current_move": current_move,
                  "status": status}
        for key, value in params.items():
            if value is not None:
                display_key = {
                    "length": "Snake length",
                    "food": "Food position",
                    "head": "Snake head",
                    "score": "Score",
                    "current_move": "Current move",
                    "status": "Status"
                }.get(key, key.replace("_", " ").title())

                # Xử lý đặc biệt cho food position - hiển thị tất cả thức ăn
                if key == "food":
                    if value == "None" or not value:  # Không có thức ăn
                        food_text = "None"
                    elif isinstance(value, list) and len(value) > 0:  # Có nhiều thức ăn
                        food_text = ", ".join(str(pos) for pos in value)
                    else:  # Có 1 thức ăn
                        food_text = str(value)
                    self.table_gameinfo.item(self.gameinfo_items[key], values=(display_key, food_text))
                else:
                    self.table_gameinfo.item(self.gameinfo_items[key], values=(display_key, str(value)))

    def update_algoinfo(self, algorithm=None, nodes=None, frontier=None, pathlen=None, time=None, path=None,
                        heuristic=None, distance_cost=None, total_cost=None):
        params = {
            "algorithm": algorithm,
            "nodes": nodes,
            "frontier": frontier,
            "pathlen": pathlen,
            "time": f"{time:.4f} s" if time is not None else None,
            "path": " -> ".join(str(p) for p in path) if isinstance(path, (list, tuple)) and len(
                path) > 0 else "No path found",
            "heuristic": heuristic,
            "distance_cost": distance_cost,
            "total_cost": total_cost
        }
        for key, value in params.items():
            if value is not None:
                label = {"heuristic": "h(x)", "distance_cost": "g(x)", "total_cost": "f(x)"}.get(key, key.replace("_",
                                                                                                                  " ").title())
                self.table_algoinfo.item(self.algoinfo_items[key], values=(label, str(value)))

    def update_detailed_stats(self, total_moves=None, food_eaten=None, best_score=None,
                              avg_solve_time=None, space_efficiency=None, movement_efficiency=None):
        params = {
            "total_moves": total_moves,
            "food_eaten": food_eaten,
            "best_score": best_score,
            "avg_solve_time": f"{avg_solve_time:.5f}s" if avg_solve_time is not None else None,
            "space_efficiency": f"{space_efficiency:.1f}%" if space_efficiency is not None else None,
            "movement_efficiency": f"{movement_efficiency:.1f}%" if movement_efficiency is not None else None
        }
        for key, value in params.items():
            if value is not None:
                label = {"avg_solve_time": "Avg Solve Time", "space_efficiency": "Space Efficiency",
                         "movement_efficiency": "Movement Efficiency"}.get(key, key.replace("_", " ").title())
                self.detailed_stats_table.item(self.detailed_stats_items[key], values=(label, str(value)))

    # -------------------- ALGORITHM EXECUTION ---------------------------
    def run_algorithm(self):
        """Chạy thuật toán và bắt đầu visualization"""
        algorithm_name = self.algo_variable.get()

        result = self.run_real_algorithm(algorithm_name)

        if result:
            # self.update_algoinfo(
            #     algorithm=algorithm_name,
            #     nodes=result["nodes_expanded"],
            #     frontier=result["max_frontier_size"],
            #     pathlen=len(result["found_path"]) if result["found_path"] else 0,
            #     time=result["time"],
            #     path=result["found_path"],
            #     heuristic=0,
            #     distance_cost=len(result["found_path"]) if result["found_path"] else 0,
            #     total_cost=len(result["found_path"]) if result["found_path"] else 0
            # )
            self.update_algoinfo(
                algorithm=algorithm_name,
                nodes=result["nodes_expanded"],
                frontier=result["max_frontier_size"],
                pathlen=len(result["found_path"]) if result["found_path"] else 0,
                time=result["time"],
                path=result["found_path"],
                heuristic=result.get("heuristic_value", 0),  # NEW ĐỂ HIỂN THỊ H(X) CỦA A*
                distance_cost=result.get("distance_cost", 0),
                total_cost=result.get("total_cost", 0)
            )

            self.expanded_nodes = result["expanded_nodes"]
            self.final_path = result["found_path"] if result["found_path"] else []

            if result["found_directions"] and len(result["found_directions"]) > 0:
                # Lưu toàn bộ đường đi để snake có thể đi theo
                self.current_path = result["found_directions"]
                self.current_path_index = 0
                self.path_found = True
                self.following_path = True  # Bắt đầu theo đường đi
            else:
                self.path_found = False
                self.following_path = False
                self.end_game("No path found to food")

        # Bắt đầu visualization
        self.perform_search_visualization()

    def run_real_algorithm(self, algorithm_name):
        try:
            if algorithm_name == "BFS":
                return BFS(self.snake, self.obstacles, self.food, row, col)
            elif algorithm_name == "DFS":
                return DFS(self.snake, self.obstacles, self.food, row, col)
            elif algorithm_name == "UCS":
                return UCS(self.snake, self.obstacles, self.food, row, col)
            elif algorithm_name == "IDS":  # THÊM XỬ LÝ CHO IDS
                return IDS(self.snake, self.obstacles, self.food, row, col)
            elif algorithm_name == "A*":
                return A_star(self.snake, self.obstacles, self.food, row, col)
            elif algorithm_name == "Greedy":
                return greedy_search(self.snake, self.obstacles, self.food, row, col)
            elif algorithm_name == "Hill Climbing":
                ls = LocalSearch(self.snake, self.obstacles, self.food, row, col)
                return ls.hill_climbing()
            elif algorithm_name == "Simulated Annealing":
                ls = LocalSearch(self.snake, self.obstacles, self.food, row, col)
                return ls.simulated_annealing()
            elif algorithm_name == "Genetic Algorithm":
                ls = LocalSearch(self.snake, self.obstacles, self.food, row, col)
                return ls.genetic_algorithm()
            else:
                return BFS(self.snake, self.obstacles, self.food, row, col)
        except Exception as e:
            print(f"Error running algorithm {algorithm_name}: {e}")
            return {
                "nodes_expanded": 0,
                "max_frontier_size": 0,
                "time": 0,
                "found_directions": None,
                "found_path": None,
                "expanded_nodes": []
            }

    # -------------------- SEARCH VISUALIZATION ---------------------------
    def perform_search_visualization(self):
        """Thực hiện visualization"""
        self.search_visualization_done = False
        self.visualization_step = 0
        self.visualization_in_progress = True
        self.visualization_complete = False

        self.clear_search_visualization()
        self.visualize_search_step()

    def visualize_search_step(self):
        """Visualization từng bước"""
        if self.visualization_step < len(self.expanded_nodes):
            node = self.expanded_nodes[self.visualization_step]
            self.draw_search_node(node, "expanded")
            self.visualization_step += 1
            self.after_id = self.window.after(self.visualization_speed, self.visualize_search_step)
        else:
            self.visualize_final_path()

    def visualize_final_path(self):
        """Visualization đường đi cuối cùng"""
        if not self.final_path:
            self.finish_visualization()
            return

        def draw_path_step(step=0):
            if step < len(self.final_path):
                node = self.final_path[step]
                self.draw_search_node(node, "path")
                self.window.after(self.visualization_speed, lambda: draw_path_step(step + 1))
            else:
                self.finish_visualization()

        draw_path_step()

    def finish_visualization(self):
        """Kết thúc visualization và tiếp tục game"""
        self.visualization_in_progress = False
        self.visualization_complete = True
        self.search_visualization_done = True

        # Tiếp tục game loop ngay lập tức
        self.after_id = self.window.after(game_speed, self.update)

    def draw_search_node(self, node, node_type):
        x, y = node
        colors = {
            "expanded": "#FFD700",
            "path": "#FF4500"
        }
        outline_colors = {
            "expanded": "#FF8C00",
            "path": "#B22222"
        }

        if node_type in colors:
            self.canvas_search.create_rectangle(
                y * cell_size, x * cell_size,
                (y + 1) * cell_size, (x + 1) * cell_size,
                fill=colors[node_type],
                outline=outline_colors[node_type],
                width=2,
                tags=f"search_{node_type}"
            )

    def clear_search_visualization(self):
        self.canvas_search.delete("search_expanded")
        self.canvas_search.delete("search_path")
        self.search_visualization_done = False
        self.visualization_step = 0

    # --------------------SNAKE GAME LOGIC--------------------------
    def draw_background(self, canvas):
        canvas.delete("board")
        for i in range(row):
            for j in range(col):
                color = "#bcd6c3" if (i + j) % 2 == 0 else "#7fba8e"
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tags="board")

    def generate_obstacles(self):
        diff = self.difficulty_var.get()
        if diff == "Easy":
            self.obstacles = self.obstacles_easy
        elif diff == "Medium":
            self.obstacles = self.obstacles_medium
        elif diff == "Hard":
            self.obstacles = self.obstacle_hard
        else:
            self.obstacles = []
        self.canvas_snake.delete("obstacle")
        for x, y in self.obstacles:
            self.canvas_snake.create_rectangle(
                y * cell_size, x * cell_size,
                (y + 1) * cell_size, (x + 1) * cell_size,
                fill="#f04305",
                outline="",
                tags="obstacle"
            )

    def generate_food(self):
        """Chỉ sinh 1 food cho tất cả độ khó"""
        # Luôn chỉ tạo 1 food duy nhất
        self.food = []

        while True:
            x = random.randrange(row)
            y = random.randrange(col)
            if (x, y) not in self.snake and (x, y) not in self.obstacles:
                self.food.append((x, y))
                break

        # Lưu số lượng food ban đầu
        self.initial_food_count = len(self.food)
        self.food_remaining = self.initial_food_count

        self.canvas_snake.delete("food")
        food_sprite = self.sprite_manager.get_sprite('food')
        for x, y in self.food:
            self.canvas_snake.create_image(
                y * cell_size + cell_size // 2,
                x * cell_size + cell_size // 2,
                image=food_sprite,
                tags="food"
            )

    def start_game(self):
        if getattr(self, "after_id", None):
            try:
                self.window.after_cancel(self.after_id)
            except Exception:
                pass

        # Reset các biến
        self.clear_search_visualization()
        self.visualization_in_progress = False
        self.visualization_complete = False
        self.waiting_for_path = True
        self.path_found = False
        self.following_path = False
        self.current_path = []
        self.current_path_index = 0

        self.canvas_snake.delete("all")
        self.canvas_snake.delete("game_over")
        self.draw_background(self.canvas_snake)

        # Khởi tạo rắn
        mid_x = row // 2
        mid_y = col // 2
        self.snake = [(mid_x, mid_y)]
        self.direction = (0, 1)
        self.next_direction = (0, 1)
        self.score = 0
        self.total_move = 0
        self.food_eaten = 0
        self.game_over = False
        self.paused = False
        self.waiting_for_path = True
        self.path_found = False
        self.just_ate_food = False
        self.status.set("Running")
        self.death_reason = ""

        self.generate_obstacles()
        self.generate_food()
        self.draw_snake()

        self.update_gameinfo(
            length=len(self.snake),
            food=self.food,  # Truyền toàn bộ danh sách thức ăn
            head=self.snake[0],
            score=self.score,
            status="Running"
        )

        # Bắt đầu game loop
        self.after_id = self.window.after(game_speed, self.update)

    def draw_snake(self):
        self.canvas_snake.delete("snake")

        if len(self.snake) == 0:
            return

        # Vẽ đầu rắn
        head_x, head_y = self.snake[0]
        head_sprite = self.sprite_manager.get_head_sprite(self.direction)
        self.canvas_snake.create_image(
            head_y * cell_size + cell_size // 2,
            head_x * cell_size + cell_size // 2,
            image=head_sprite, tags="snake"
        )

        # Vẽ đuôi rắn
        if len(self.snake) > 1:
            tail_x, tail_y = self.snake[-1]
            if len(self.snake) > 1:
                prev_tail_x, prev_tail_y = self.snake[-2]
                tail_dir = (tail_x - prev_tail_x, tail_y - prev_tail_y)
            else:
                tail_dir = self.direction
            tail_sprite = self.sprite_manager.get_tail_sprite(tail_dir)
            self.canvas_snake.create_image(
                tail_y * cell_size + cell_size // 2,
                tail_x * cell_size + cell_size // 2,
                image=tail_sprite, tags="snake"
            )

        # Vẽ thân rắn
        for i in range(1, len(self.snake) - 1):
            current = self.snake[i]
            prev = self.snake[i - 1]
            next_seg = self.snake[i + 1]

            body_sprite = self.sprite_manager.get_body_sprite(prev, current, next_seg)
            self.canvas_snake.create_image(
                current[1] * cell_size + cell_size // 2,
                current[0] * cell_size + cell_size // 2,
                image=body_sprite, tags="snake"
            )

    def update(self):
        if self.game_over or self.paused:
            return

        # Nếu đang trong quá trình visualization, tiếp tục chờ
        if self.visualization_in_progress:
            self.after_id = self.window.after(game_speed, self.update)
            return

        # Nếu đang theo đường đi, tiếp tục di chuyển theo đường đi
        if self.following_path and self.current_path_index < len(self.current_path):
            self.follow_path()
        elif self.visualization_complete and self.path_found:
            # Nếu visualization xong và có đường đi, bắt đầu theo đường đi
            self.following_path = True
            self.current_path_index = 0
            self.follow_path()
        else:
            # Nếu chưa có đường đi, chạy thuật toán
            self.run_algorithm()

    def follow_path(self):
        """Di chuyển snake theo đường đi đã tìm được"""
        if self.current_path_index >= len(self.current_path):
            # Đã đi hết đường đi, chạy thuật toán mới
            self.following_path = False
            self.run_algorithm()
            return

        # Lấy hướng đi tiếp theo từ đường đi
        self.next_direction = self.current_path[self.current_path_index]
        self.current_path_index += 1

        # Thực hiện di chuyển
        self.direction = self.next_direction
        dx, dy = self.direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)
        self.total_move += 1

        if self.check_collision(new_head):
            self.end_game("Collision detected")
            return

        self.snake.insert(0, new_head)

        # Xử lý ăn thức ăn
        ate_food = False
        if new_head in self.food:
            self.eat_food(new_head)
            ate_food = True

            # THÊM DELAY NHỎ ĐỂ ĐẢM BẢO ĐẦU RẮN ĐƯỢC VẼ ĐÚNG
            self.draw_snake()
            self.canvas_snake.update()

            # QUAN TRỌNG: Nếu ăn hết tất cả food, tạo food mới NGAY LẬP TỨC
            if not self.food:
                self.generate_food()  # Tạo food mới
                self.following_path = False  # Dừng đường đi cũ
                self.current_path = []
                self.run_algorithm()  # Chạy thuật toán tìm đường đến food mới
                return  # Dừng hàm ngay để tránh xung đột

        # Chỉ pop đuôi nếu KHÔNG ăn food
        if not ate_food:
            self.snake.pop()

        self.draw_snake()
        self.update_info()

        # Tiếp tục game loop
        self.after_id = self.window.after(game_speed, self.update)

    def check_collision(self, pos):
        x, y = pos
        if x < 0 or x >= row or y < 0 or y >= col:
            self.death_reason = "Hit the wall"
            return True
        if pos in self.obstacles:
            self.death_reason = "Hit an obstacle"
            return True
        if pos in self.snake:
            self.death_reason = "Hit itself"
            return True
        return False

    def eat_food(self, new_head):
        if new_head in self.food:
            self.score += 10
            self.food_eaten += 1
            self.food.remove(new_head)
            self.canvas_snake.delete("food")

            # Vẽ lại các food còn lại
            food_sprite = self.sprite_manager.get_sprite('food')
            for x, y in self.food:
                self.canvas_snake.create_image(
                    y * cell_size + cell_size // 2,
                    x * cell_size + cell_size // 2,
                    image=food_sprite,
                    tags="food"
                )

            self.just_ate_food = True
            # Cập nhật thông tin thức ăn sau khi ăn
            self.update_info()

    def update_info(self):
        self.update_gameinfo(
            length=len(self.snake),
            food=self.food,  # Truyền toàn bộ danh sách thức ăn
            head=self.snake[0],
            score=self.score,
            current_move=self.direction_to_text(self.direction),
            status=self.status.get()
        )

        self.update_detailed_stats(
            total_moves=self.total_move,
            food_eaten=self.food_eaten,
            best_score=max(self.best_score, self.score),
            avg_solve_time=self.calculate_avg_solve_time(0.001),
            space_efficiency=self.calculate_space_efficiency(),
            movement_efficiency=self.calculate_movement_efficiency()
        )

    def direction_to_text(self, direction):
        mapping = {
            (0, 1): "Right",
            (0, -1): "Left",
            (1, 0): "Down",
            (-1, 0): "Up"
        }
        return mapping.get(direction, str(direction))

    def calculate_space_efficiency(self):
        if self.total_move > 0:
            return min(100, (self.food_eaten / self.total_move) * 100)
        return 0

    def calculate_movement_efficiency(self):
        if self.total_move > 0:
            return min(100, (self.food_eaten / self.total_move) * 100)
        return 0

    def calculate_avg_solve_time(self, current_time):
        self.solve_times.append(current_time)
        if self.solve_times:
            return sum(self.solve_times) / len(self.solve_times)
        return 0

    # ------------------ CONTROL FUNCTIONS ------------------
    def toggle_pause(self, event=None):
        if self.game_over:
            return

        self.paused = not self.paused
        if self.paused:
            self.status.set("Paused")
            if self.after_id:
                self.window.after_cancel(self.after_id)
                self.after_id = None
        else:
            self.status.set("Running")
            if not self.game_over:
                self.after_id = self.window.after(game_speed, self.update)

        self.update_gameinfo(status=self.status.get())

    def restart_game(self, event=None):
        if self.after_id:
            try:
                self.window.after_cancel(self.after_id)
            except Exception:
                pass
        self.start_game()

    def quit_game(self, event=None):
        if self.after_id:
            try:
                self.window.after_cancel(self.after_id)
            except Exception:
                pass
        self.window.quit()

    def update_speed(self, val):
        global game_speed
        game_speed = int(val)
        if self.after_id and not self.game_over and not self.paused:
            try:
                self.window.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = self.window.after(game_speed, self.update)

    def end_game(self, reason=""):
        self.game_over = True
        self.status.set("Game Over")
        self.death_reason = reason

        self.show_game_over()

        if self.after_id:
            try:
                self.window.after_cancel(self.after_id)
            except Exception:
                pass

    def show_game_over(self):
        if self.game_over_text:
            self.canvas_snake.delete(self.game_over_text)

        canvas_width = self.canvas_snake.winfo_width()
        canvas_height = self.canvas_snake.winfo_height()

        self.canvas_snake.create_rectangle(
            0, 0, canvas_width, canvas_height,
            fill="black", stipple="gray50", tags="game_over"
        )

        text = f"GAME OVER\n{self.death_reason}\nScore: {self.score}\nPress R to restart"
        self.game_over_text = self.canvas_snake.create_text(
            canvas_width // 2,
            canvas_height // 2,
            text=text,
            fill="red",
            font=("Arial", 20, "bold"),
            justify="center",
            tags="game_over"
        )


# ------------------ MAIN ------------------------------
if __name__ == "__main__":
    window = tk.Tk()
    game = SnakeGame(window)
    window.mainloop()