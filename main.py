import tkinter as tk

from random import shuffle


class Cell(tk.Button):
    def __init__(self, master, x, y, order_number=0, *args, **kwargs) -> None:
        super(Cell, self).__init__(
            master, *args, 
            width=5, height=2, font="Calibri 15 bold", **kwargs
        )
        self.x = x
        self.y = y
        self.order_number = order_number
        self.is_mine = False
        self.bombs_around = 0

    def __str__(self) -> str:
        return f"Button {self.order_number} ({self.x}, {self.y})"


class MineSweeper:
    # game settings
    ROWS, COLS = 10, 7
    MINES = 15

    window = tk.Tk()

    def __init__(self):
        self.buttons = []

        # add border elements to simplify neighbours check logic (each game cell has 8 neighboutrs, some may be virtual)
        for row in range(MineSweeper.ROWS + 2):
            buttons_row = []
            for col in range(MineSweeper.COLS + 2):
                cell = Cell(MineSweeper.window, row, col)
                cell.config(command=lambda btn = cell: self.click_cell(btn))
                buttons_row.append(cell)
            self.buttons.append(buttons_row)

    def create_field(self):
        for row in range(1, MineSweeper.ROWS+1):
            for col in range(1, MineSweeper.COLS+1):
                self.buttons[row][col].grid(row=row-1, column=col-1)

    def show_field(self):
        for btn_row in self.buttons:
            for btn in btn_row:
                if btn.is_mine:
                    btn.config(text='*', background='red')
                else:
                    btn.config(text=str(btn.bombs_around))
                btn.config(state=tk.DISABLED, disabledforeground='black')

    def start(self):
        self.create_field()
        self.insert_mines()
        self.count_mines_for_cell()

        self.show_field()

        MineSweeper.window.mainloop()
    
    @staticmethod
    def _get_mines_places():
        cell_numbers = [i for i in range(1, MineSweeper.ROWS * MineSweeper.COLS + 1)]
        shuffle(cell_numbers)
        return cell_numbers[:MineSweeper.MINES]
    
    def insert_mines(self):
        mines_numbers = MineSweeper._get_mines_places()

        counter = 1
        for row in range(1, self.ROWS + 1):
            for col in range(1, self.COLS + 1):
                btn = self.buttons[row][col]
                if counter in mines_numbers:
                    btn.is_mine = True
                else:
                    btn.order_number = counter
                counter += 1
    
    def count_mines_for_cell(self):
        for row in range(1, self.ROWS + 1):
            for col in range(1, self.COLS + 1):
                btn = self.buttons[row][col]
                if not btn.is_mine:
                    bombs_count = 0
                    for row_dx in (-1, 0, 1):
                        for col_dx in (-1, 0, 1):
                            neighbour = self.buttons[row + row_dx][col + col_dx]
                            if neighbour.is_mine:
                                bombs_count += 1
                    btn.bombs_around = bombs_count

    
    def click_cell(self, cell_clicked: Cell):
        if cell_clicked.is_mine:
            cell_clicked.config(text='*', background='red')
        else:
            cell_clicked.config(text=str(cell_clicked.bombs_around))
        cell_clicked.config(state=tk.DISABLED, disabledforeground='black')
        

game = MineSweeper()
game.start()
