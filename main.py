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
    """
    Object of game field piece
    Can either be an empty (no mines among 8 neighbours)
        or having some mines as one of 8 neighbours (number in the cell tells how many)
        or be a mine
    Extends tk class Button and fill some style config
    """
    def __init__(self, master, row, col, order_number=0, *args, **kwargs) -> None:
        super(Cell, self).__init__(
            master, *args, 
            width=5, height=2, font="Calibri 15 bold", **kwargs
        )
        # position on main screen grid
        self.row = row
        self.col = col
        
        # for placing mines to define a cell by 1 number
        self.order_number = order_number

        self.is_mine = False
        self.bombs_around = 0  # mines among 8 neighbours (0 <= bombs_around <= 8)

        self.is_clicked = False  # was clicked by player or recursively opened in chain as a result of some click

        self.has_flag = False  # flag was set on the cell


    def __str__(self) -> str:
        return f"Button {self.order_number} ({self.row}, {self.col})"


class MineSweeper:
    """
    Main class, responsible for: 
    - creating the game field
    - placing mines
    - processing clicks, opening map
    """

    # default game settings
    ROWS, COLS, MINES = 10, 10, 10
    FIRST_OPENED = True  # indicates, that the game is first opened

    def __init__(self):
        # when opened first time - initialize the main game window and prompting the settings to configure game parameters
        if MineSweeper.FIRST_OPENED:
            self.window = tk.Tk()
            self.window.title('Mine Sweeper')
            self.window.resizable(False, False)
            self.window.geometry('+450+50')

            self.create_settings_win()
            MineSweeper.FIRST_OPENED = False

        # creating field cells
        self.buttons = []
        # add border elements to simplify neighbours check logic (each game cell has 8 neighbours, some may be virtual)
        for row in range(MineSweeper.ROWS + 2):
            buttons_row = []
            for col in range(MineSweeper.COLS + 2):
                cell = Cell(self.window, row, col)
                cell.config(command=lambda btn = cell: self.click_cell(btn))  # callback on click
                buttons_row.append(cell)

                cell.bind('<Button-3>', self.set_flag)  # callback on right click (setting a red flag)

            self.buttons.append(buttons_row)
        
        self.IS_GAMEOVER = False
        self.IS_FIRST_CLICK = True

        self.markers_left = self.MINES  # how many flags are left to place onto the field
        self.real_mines_marked = 0  # secret param, indicates how many actual mines the player has found
    
    def set_flag(self, event):
        """
        Callback of clicking right mouse on a cell
        """
        if self.IS_GAMEOVER:
            return

        button_clicked = event.widget

        if button_clicked.has_flag:
            button_clicked.config(state=tk.NORMAL, text='')
            button_clicked.has_flag = False

            # update stat data in the bottom row
            self.markers_left += 1
            self.label_mines_unmarked['text'] = f'Мины: {self.markers_left}'
            if button_clicked.is_mine:
                self.real_mines_marked -= 1
        
        elif button_clicked['state'] == tk.NORMAL and self.markers_left > 0:
            button_clicked.config(state=tk.DISABLED, text='🚩',
                                  disabledforeground='red')
            button_clicked.has_flag = True

            # update stat data in the bottom row
            self.markers_left -= 1
            self.label_mines_unmarked['text'] = f'Мины: {self.markers_left}'

            if button_clicked.is_mine:
                self.real_mines_marked += 1
        
        # win msg
        self._check_game_is_won()
        

    def _check_game_is_won(self):
        """
        When no more flaga are left check if it's a win and all mines were found and all cells were open
        """
        if self.real_mines_marked == self.MINES and\
                all([(self.buttons[row][col].is_clicked or self.buttons[row][col].is_mine) for row in range(1, self.ROWS+1) for col in range(1, self.COLS+1)]):
            self.IS_GAMEOVER = True
            
            game_time = self.label_time["text"][7:]
            self._hide_bottom_panel()
            messagebox.showinfo('Finish', f'You won in {game_time} seconds!')

    def _hide_bottom_panel(self):
        """
        When a round is finished, close labels with time and mines left
        """
        self.label_time.destroy()
        self.label_mines_unmarked.destroy()

    def create_field(self):
        """
        - create top cascade menu with settings, restart and quit options
        - placing buttons (game fields) on the main field
        - displaying timer and number of mines left in the bottom
        """
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
        
        # Need to fix a floating bug with too little window after applying settings
        for row in range(1, MineSweeper.ROWS+2):
            tk.Grid.rowconfigure(self.window, row, weight=1)
        for col in range(1, MineSweeper.COLS+2):
            tk.Grid.columnconfigure(self.window, col, weight=1)

        # Create bottom labels with stat data
        self.label_mines_unmarked = tk.Label(self.window, text=f'Мины: {self.markers_left}', font='Times 15 bold')
        self.label_mines_unmarked.grid(row=self.ROWS+2, 
                                    column=self.COLS // 2 + 1,
                                    columnspan=self.COLS // 2)

        self.label_time = tk.Label(self.window, font='Times 15 bold')
        self.label_time.grid(row=self.ROWS+2, column=self.COLS // 2 - 1, columnspan=self.COLS // 2)
        self._set_up_timer(self.label_time)

    @staticmethod
    def _set_up_timer(label_time):
        """
        Helper to get a timer inside Label
        """
        counter = 0 
        def counter_label(label):
            def count():
                nonlocal counter
                counter += 1
                label.config(text=f'Время: {counter}')
                label.after(1000, count)
            count()

        counter_label(label_time)

    def _show_bombs(self):
        """
        Revealing bombs position on game over when a mine was clicked and disabling all buttons
        """
        for btn_row in self.buttons:
            for btn in btn_row:
                kwargs = {}
                if btn.is_mine:
                    btn.config(text='*')
                    kwargs = {'disabledforeground': 'black'}
                btn.config(state=tk.DISABLED, relief=tk.SUNKEN, **kwargs)
    
    def print_field_schema(self):
        """
        Debug feature to print out bombs map in the console
        """
        for row in range(1, MineSweeper.ROWS+1):
            for col in range(1, MineSweeper.COLS+1):
                btn = self.buttons[row][col]
                if btn.is_mine:
                    print('*', end='')
                else:
                    print(btn.bombs_around, end='')
            print()

    def start(self):
        """
        Main initial
        """
        self.create_field()

        self.window.mainloop()

    def reload(self):
        """
        Re-create game field
        """
        # Очищаем клетки
        for child in self.window.winfo_children():
            child.destroy()

        MineSweeper.__init__(self)
        self.create_field()

        self.IS_FIRST_CLICK = True
        self.IS_GAMEOVER = False
    
    def create_settings_win(self):
        """
        Callback on click on settings options in the top menu
        """
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
        settings_win.lift(self.window)
        settings_win.geometry('+500+250')

    def change_settings(self, settings_win, rows_entry, cols_entry, mines_entry):
        """
        Set up and validate input in game settings window
        """
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
        """
        Helper to get some random order_number's for setting up mines
        The cell which is opened first is out of consideration
        """
        cell_numbers = [i for i in range(1, MineSweeper.ROWS * MineSweeper.COLS + 1)]
        cell_numbers.remove(exclude_cell_number)
        shuffle(cell_numbers)
        return cell_numbers[:MineSweeper.MINES]
    
    def insert_mines(self, exclude_cell_number: int):
        """
        Set is_mine attr for some random cells on the field
        """
        mines_numbers = MineSweeper._get_mines_places(exclude_cell_number)

        for row in range(1, self.ROWS + 1):
            for col in range(1, self.COLS + 1):
                btn = self.buttons[row][col]
                if btn.order_number in mines_numbers:
                    btn.is_mine = True
    
    def count_mines_for_cell(self):
        """
        Check for initial field for each cell how many mines it has near it (8 at the most)
        If any - set up cell's attr bombs_around
        """
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
        """
        Callback on left click
        - if first click - fill the field with mines
        - if a mine was clicked - gameover
        - elif an empty field was clicked - bredth search of an area restricted by "numbered" cells (which have mines among neighbours)
        - elif a "numbered" cell was clicked - only it is gonna be open 
        """
        def _is_in_range(row, col):
            """
            Check whether (row, col) belongs to real field (with regard to virtual cells)
            """
            return 1 <= row < self.ROWS + 1 and 1 <= col <= self.COLS + 1
        
        cell_clicked.is_clicked = True

        # this is when we place our mines - user never hit one when click first
        if self.IS_FIRST_CLICK:
            self.insert_mines(cell_clicked.order_number)
            self.count_mines_for_cell()

            # DEBUG
            # self.print_field_schema()

            self.IS_FIRST_CLICK = False
        
        if cell_clicked.is_mine:
            cell_clicked.config(text='*', background='red')

            self.label_time.destroy()
            self.label_mines_unmarked.destroy()

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

                # disabling and restylingthe cell being opened if it is not a flag
                if not cell.has_flag:    
                    cell.config(state=tk.DISABLED, 
                                background='#b5b3b3', disabledforeground=COLORS.get(cell.bombs_around) or 'black', 
                                relief=tk.SUNKEN)
                
        # win msg
        self._check_game_is_won()
            

game = MineSweeper()
game.start()
