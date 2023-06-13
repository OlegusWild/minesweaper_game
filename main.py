import tkinter as tk

from random import shuffle


class Cell(tk.Button):
    def __init__(self, master, x, y, order_number, *args, **kwargs) -> None:
        super(Cell, self).__init__(
            master, *args, 
            width=5, height=2, font="Calibri 15 bold", **kwargs
        )
        self.x = x
        self.y = y
        self.order_number = order_number
        self.is_mine = False

    def __str__(self) -> str:
        return f"Button {self.order_number} ({self.x}, {self.y})"


class MineSweeper:
    # game settings
    ROWS, COLS = 10, 7
    MINES = 15

    window = tk.Tk()

    def __init__(self):
        self.buttons = []

        counter = 1
        for row in range(MineSweeper.ROWS):
            buttons_row = []
            for col in range(MineSweeper.COLS):
                buttons_row.append(Cell(MineSweeper.window, row, col, counter))
                counter += 1
            self.buttons.append(buttons_row)

    def create_field(self):
        for row in range(MineSweeper.ROWS):
            for col in range(MineSweeper.COLS):
                self.buttons[row][col].grid(row=row, column=col)

    def start(self):
        self.create_field()
        self.insert_mines()

        for row in self.buttons:
            for btn in row:
                if btn.is_mine:
                    print(btn)

        MineSweeper.window.mainloop()
    
    @staticmethod
    def _get_mines_places():
        cell_numbers = [i for i in range(1, MineSweeper.ROWS * MineSweeper.COLS + 1)]
        shuffle(cell_numbers)
        return cell_numbers[:MineSweeper.MINES]
    
    def insert_mines(self):
        mines_numbers = MineSweeper._get_mines_places()
        for row in self.buttons:
            for btn in row:
                if btn.order_number in mines_numbers:
                    btn.is_mine = True


game = MineSweeper()
game.start()
