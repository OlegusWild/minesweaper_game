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
    MINES = 5

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
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)

        cascade_menu = tk.Menu(menubar, 
                               tearoff=0)  # disables tearing off the menu to a separate window
        cascade_menu.add_command(label='Перезапустить игру', command=self.reload)
        cascade_menu.add_command(label='Настройки', command=self.create_settings_win)
        cascade_menu.add_command(label='Выход', command=self.window.destroy)

        menubar.add_cascade(menu=cascade_menu, label='Меню')

        counter = 1
        for row in range(1, MineSweeper.ROWS+1):
            for col in range(1, MineSweeper.COLS+1):
                btn = self.buttons[row][col]
                btn.order_number = counter
                btn.grid(row=row, column=col, stick='wesn')

                counter += 1
        
        for row in range(1, MineSweeper.ROWS+1):
            tk.Grid.rowconfigure(self.window, row, weight=1)
        for col in range(1, MineSweeper.COLS+1):
            tk.Grid.columnconfigure(self.window, col, weight=1)

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

    def reload(self):
        # Очищаем клетки
        for child in self.window.winfo_children():
            child.destroy()

        MineSweeper.__init__(self)
        self.create_field()

        self.IS_FIRST_CLICK = True
        self.IS_GAMEOVER = False
    
    def create_settings_win(self):
        settings_win = tk.Toplevel(self.window)
        settings_win.wm_title('Настройки')

        tk.Label(settings_win, text='Количество строк: ').grid(row=0, column=0)
        tk.Label(settings_win, text='Количество столбцов: ').grid(row=1, column=0)
        tk.Label(settings_win, text='Количество мин: ').grid(row=2, column=0)

        rows_entry = tk.Entry(settings_win)
        rows_entry.grid(row=0, column=1, padx=20, pady=20)
        rows_entry.insert(0, MineSweeper.ROWS)

        cols_entry = tk.Entry(settings_win)
        cols_entry.grid(row=1, column=1, padx=20, pady=20)
        cols_entry.insert(0, MineSweeper.COLS)

        mines_entry = tk.Entry(settings_win)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)
        mines_entry.insert(0, MineSweeper.MINES)

        tk.Button(settings_win, 
                  text='Сохранить', 
                  command=lambda: self.change_settings(settings_win, rows_entry, cols_entry, mines_entry)).grid(row=3, 
                                                                                                                column=0, 
                                                                                                                columnspan=2,
                                                                                                                pady=5)

    def change_settings(self, settings_win, rows_entry, cols_entry, mines_entry):
        try:
            rows, cols, mines = int(rows_entry.get()), int(cols_entry.get()), int(mines_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Допустимы только целые числа!")
            return
        
        if not float(rows).is_integer() or not float(cols).is_integer() or not float(mines).is_integer():
            messagebox.showerror("Ошибка ввода", "Допустимы только целые числа!")
            return
        
        if cols <= 0 or rows <= 0 or mines <= 0:
            messagebox.showerror("Ошибка ввода", 
                                 f"Количество мин, строк и столбцов не могут равняться нулю или быть отрицательными!\n\
                                 Вы ввели: мин={mines}, строк={rows}, столбцов={cols}")
            return

        if mines >= rows * cols:
            messagebox.showerror("Ошибка ввода", 
                                 f"Количество мин должно быть меньше количества клеток на поле!\n\
                                 Вы ввели: мин={mines} >= кол-во клеток={cols * rows}")
            return

        MineSweeper.ROWS = rows
        MineSweeper.COLS = cols
        MineSweeper.MINES = mines

        settings_win.destroy()

        self.reload()

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
                        
                cell.config(state=tk.DISABLED, 
                            background='#b5b3b3', disabledforeground=COLORS.get(cell.bombs_around) or 'black', 
                            relief=tk.SUNKEN)

        
game = MineSweeper()
game.start()
