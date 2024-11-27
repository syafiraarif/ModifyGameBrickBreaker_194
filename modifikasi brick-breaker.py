import tkinter as tk

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        # mengubah ukuran bola dmenjadai lebih kecil daei 10 menjadi 8
        self.radius = 8
        self.direction = [1, -1]
        # mengubah kecepatan pada bola dari 7 menjadi 10
        self.speed = 10
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='red')       # mengubah warna bola dari putih menjadi red
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFFFFF')  
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#ADD8E6', 2: '#F08080', 3: '#E0FFFF', 4: '#FF6347'}  # mengubah warna bata dan jumlahnya ditambahkan menjadi 4

    def __init__(self, canvas, x, y, hits, game):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.game = game
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.game.add_score(self.hits) 
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        # mengubah game manjadi memiliki 5 nyawa
        self.lives = 5
        # menambahkan skor pada permainan ketika setiap bola memecahkan bata
        self.score = 0  
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        # Membuat latar belakang sesuai bendera Palestina
        self.canvas.create_rectangle(0, 0, self.width, self.height / 3, fill='black', outline="")
        self.canvas.create_rectangle(0, self.height / 3, self.width, 2 * self.height / 3, fill='white', outline="")
        self.canvas.create_rectangle(0, 2 * self.height / 3, self.width, self.height, fill='green', outline="")
        self.canvas.create_polygon(0, 0, 200, self.height / 2, 0, self.height, fill='red', outline="")

        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        # untuk menambahkan bata menjaadi 4 lapis
        self.add_bricks()
    #membuat bata menjadi 4 lapis
    def add_bricks(self):
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 4)
            self.add_brick(x + 37.5, 70, 3)
            self.add_brick(x + 37.5, 90, 2)
            self.add_brick(x + 37.5, 110, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.update_score_text() 
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits, self)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40', color='black'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font, fill=color)

    def update_lives_text(self):
        text = f'Lives: {self.lives}'
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15, color='green')
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def update_score_text(self):
        if hasattr(self, 'score_text'):
            self.canvas.itemconfig(self.score_text, text=f'Score: {self.score}')
        else:
            self.score_text = self.draw_text(500, 20, f'Score: {self.score}', 15, color='green')

    def add_score(self, points):
        self.score += points
        self.update_score_text()

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(300, 200, 'You win! You the Breaker of Bricks.')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'You Lose! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()
