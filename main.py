import tkinter as tk


class Cell(tk.Button):
    def __init__(self, master, x, y, *args, **kwargs) -> None:
        super(Cell, self).__init__(
            master, *args, 
            width=5, height=2, font="Calibri 15 bold", **kwargs
        )
        self.x = x
        self.y = y
        self.is_mine = False

    def __repr__(self) -> str:
        return f"Button {self.x}, {self.y}"


class MineSweeper:
    # game settings
    ROWS, COLS = 10, 7

    window = tk.Tk()

    def __init__(self):
        self.buttons = []
        # place table of buttons on the screen
        for row in range(MineSweeper.ROWS):
            buttons_row = []
            for col in range(MineSweeper.COLS):
                buttons_row.append(Cell(MineSweeper.window, row, col))
            self.buttons.append(buttons_row)

    def create_field(self):
        for row in range(MineSweeper.ROWS):
            for col in range(MineSweeper.COLS):
                self.buttons[row][col].grid(row=row, column=col)

    def start(self):
        self.create_field()
        MineSweeper.window.mainloop()


game = MineSweeper()
game.start()
