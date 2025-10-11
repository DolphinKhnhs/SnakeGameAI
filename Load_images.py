import os
from PIL import Image, ImageTk


class SpriteManager:
    def __init__(self, sprite_folder=None, cell_size=20):
        if sprite_folder is None:
            # sprite folder nằm cùng cấp với file gui.py
            self.sprite_folder = os.path.join(os.path.dirname(__file__), "sprite")
        else:
            self.sprite_folder = sprite_folder

        self.cell_size = cell_size
        self.sprites = {}
        self.load_all_sprites()

    def load_all_sprites(self):
        """Load tất cả sprite từ thư mục"""
        if not os.path.exists(self.sprite_folder):
            print(f"⚠️ Warning: sprite folder not found: {self.sprite_folder}")
            return

        for filename in os.listdir(self.sprite_folder):
            if filename.endswith(".png"):
                sprite_name = os.path.splitext(filename)[0]  # bỏ .png
                filepath = os.path.join(self.sprite_folder, filename)
                try:
                    image = Image.open(filepath)
                    image = image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
                    self.sprites[sprite_name] = ImageTk.PhotoImage(image)
                except Exception as e:
                    self.create_default_sprite(sprite_name)

    def create_default_sprite(self, sprite_name):
        """Tạo sprite mặc định với màu sắc"""
        from PIL import Image
        colors = {
            'block': 'brown',
            'body': 'green',
            'food': 'red',
            'head': 'lime',
            'tail': 'darkgreen'
        }
        color = colors.get(sprite_name.split("_")[0], 'gray')
        image = Image.new('RGB', (self.cell_size, self.cell_size), color)
        self.sprites[sprite_name] = ImageTk.PhotoImage(image)

    def get_sprite(self, sprite_name):
        """Lấy sprite theo tên"""
        return self.sprites.get(sprite_name, self.sprites.get('body'))

    def get_head_sprite(self, direction):
        """Lấy sprite đầu rắn theo hướng"""
        direction_map = {
            (1, 0): 'head_down',
            (-1, 0): 'head_up',
            (0, 1): 'head_right',
            (0, -1): 'head_left'
        }
        return self.get_sprite(direction_map.get(direction, 'head'))

    def get_tail_sprite(self, direction):
        """Lấy sprite đuôi rắn theo hướng"""
        direction_map = {
            (1, 0): 'tail_down',
            (-1, 0): 'tail_up',
            (0, 1): 'tail_right',
            (0, -1): 'tail_left'
        }
        return self.get_sprite(direction_map.get(direction, 'tail'))

    def get_body_sprite(self, prev_segment, current_segment, next_segment):
        """Xác định sprite thân rắn dựa trên vị trí các segment"""
        if not prev_segment or not next_segment:
            return self.get_sprite('body')

        px, py = prev_segment
        cx, cy = current_segment
        nx, ny = next_segment

        # Tính hướng đi vào và đi ra từ current segment
        in_dir = (cx - px, cy - py)  # Hướng từ prev đến current
        out_dir = (nx - cx, ny - cy)  # Hướng từ current đến next

        # Nếu đi thẳng
        if in_dir == out_dir:
            if in_dir[0] != 0:  # Di chuyển dọc
                return self.get_sprite('body_vertical')
            else:  # Di chuyển ngang
                return self.get_sprite('body_horizontal')

        # Xác định góc rẽ
        # Kết hợp hướng vào và hướng ra
        combo = (in_dir, out_dir)

        corner_map = {
            # Góc từ trên xuống, rẽ phải: (0,-1) -> (1,0)
            ((0, -1), (1, 0)): 'body_bottomright',
            # Góc từ trên xuống, rẽ trái: (0,-1) -> (-1,0)
            ((0, -1), (-1, 0)): 'body_topright',
            # Góc từ dưới lên, rẽ phải: (0,1) -> (1,0)
            ((0, 1), (1, 0)): 'body_bottomleft',
            # Góc từ dưới lên, rẽ trái: (0,1) -> (-1,0)
            ((0, 1), (-1, 0)): 'body_topleft',
            # Góc từ trái sang, rẽ lên: (1,0) -> (0,-1)
            ((1, 0), (0, -1)): 'body_topleft',  # same as above
            # Góc từ trái sang, rẽ xuống: (1,0) -> (0,1)
            ((1, 0), (0, 1)): 'body_topright',  # same as above
            # Góc từ phải sang, rẽ lên: (-1,0) -> (0,-1)
            ((-1, 0), (0, -1)): 'body_bottomleft',  # same as above
            # Góc từ phải sang, rẽ xuống: (-1,0) -> (0,1)
            ((-1, 0), (0, 1)): 'body_bottomright',  # same as above
        }

        return self.get_sprite(corner_map.get(combo, 'body'))