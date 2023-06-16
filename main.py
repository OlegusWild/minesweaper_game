import tkinter as tk
from tkinter import messagebox

from random import shuffle

COLORS = {
    1: '#0f67d9',
    2: '#07f007',
    3: '#0b4507',
    4: '#0f07f0',
    5: '#810fd9',
    6: '#a602cf',
    7: '#cf0246',
    8: '#cf0217',

}


class Cell(tk.Button):
    def __init__(self, master, row, col, order_number=0, *args, **kwargs) -> None:
        super(Cell, self).__init__(
            master, *args, 
            width=5, height=2, font="Calibri 15 bold", **kwargs
        )
        self.row = row
        self.col = col

        self.order_number = order_number

        self.is_mine = False
        self.bombs_around = 0

        self.is_clicked = False


    def __str__(self) -> str:
        return f"Button {self.order_number} ({self.row}, {self.col})"


class MineSweeper:
    # game settings
    ROWS, COLS = 10, 7
    MINES = 69

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
        
        self.IS_GAMEOVER = False
        self.IS_FIRST_CLICK = True

    def create_field(self):
        counter = 1
        for row in range(1, MineSweeper.ROWS+1):
            for col in range(1, MineSweeper.COLS+1):
                btn = self.buttons[row][col]
                btn.order_number = counter
                btn.grid(row=row-1, column=col-1)

                counter += 1

    def _show_bombs(self):
        for btn_row in self.buttons:
            for btn in btn_row:
                kwargs = {}
                if btn.is_mine:
                    btn.config(text='*')
                    kwargs = {'disabledforeground': 'black'}
                btn.config(state=tk.DISABLED, relief=tk.SUNKEN, **kwargs)
    
    def print_field_schema(self):
        for row in range(1, MineSweeper.ROWS+1):
            for col in range(1, MineSweeper.COLS+1):
                btn = self.buttons[row][col]
                if btn.is_mine:
                    print('*', end='')
                else:
                    print(btn.bombs_around, end='')
            print()

    def start(self):
        self.create_field()

        MineSweeper.window.mainloop()
    
    @staticmethod
    def _get_mines_places(exclude_cell_number: int):
        cell_numbers = [i for i in range(1, MineSweeper.ROWS * MineSweeper.COLS + 1)]
        cell_numbers.remove(exclude_cell_number)
        shuffle(cell_numbers)
        return cell_numbers[:MineSweeper.MINES]
    
    def insert_mines(self, exclude_cell_number: int):
        mines_numbers = MineSweeper._get_mines_places(exclude_cell_number)

        for row in range(1, self.ROWS + 1):
            for col in range(1, self.COLS + 1):
                btn = self.buttons[row][col]
                if btn.order_number in mines_numbers:
                    btn.is_mine = True
    
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
        def _is_in_range(row, col):
            return 1 <= row < self.ROWS + 1 and 1 <= col <= self.COLS + 1
        
        # this is when we place our mines - user never hit one when click first
        if self.IS_FIRST_CLICK:
            self.insert_mines(cell_clicked.order_number)
            self.count_mines_for_cell()

            # DEBUG
            self.print_field_schema()

            self.IS_FIRST_CLICK = False
        
        if cell_clicked.is_mine:
            cell_clicked.config(text='*', background='red')
            messagebox.showinfo('Game Over', 'You are banged!')
            self.IS_GAMEOVER = True
            self._show_bombs()
        else:
            cells_to_open = [cell_clicked]
            while cells_to_open:
                cell = cells_to_open.pop()
                if cell.bombs_around:
                    cell.config(text=str(cell.bombs_around))
                else:
                    # left
                    if _is_in_range(cell.row, cell.col-1):
                        btn = self.buttons[cell.row][cell.col-1]
                        if btn.is_mine is False and btn.is_clicked is False:
                            cells_to_open.append(btn)
                    # right
                    if _is_in_range(cell.row, cell.col+1):
                        btn = self.buttons[cell.row][cell.col+1]
                        if btn.is_mine is False and btn.is_clicked is False:
                            cells_to_open.append(btn)
                    # down
                    if _is_in_range(cell.row+1, cell.col):
                        btn = self.buttons[cell.row+1][cell.col]
                        if btn.is_mine is False and btn.is_clicked is False:
                            cells_to_open.append(btn)
                    # up
                    if _is_in_range(cell.row-1, cell.col):
                        btn = self.buttons[cell.row-1][cell.col]
                        if btn.is_mine is False and btn.is_clicked is False:
                            cells_to_open.append(btn)
                    
                    cell.is_clicked = True
                        
                cell.config(state=tk.DISABLED, background='#b5b3b3', disabledforeground=COLORS.get(cell.bombs_around) or 'black', relief=tk.SUNKEN)

        
game = MineSweeper()
game.start()
