import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog

# Опции
root_size = "325x100", # Размер начального окна
color_var = "black",  # Обычный цвет кисти
cell_size = 20,  # Размер одной клетки, обычный размер 20
lang = "en"  # Начальный язык интерфейса

# Для переводов
lang_dict = {
    'en': {
        'guide_label': 'Left-click to draw\nRight-click to erase',
        'width_label': 'Width:',
        'height_label': 'Height:',
        'create_button': 'Create canvas',
        'canvas_title': 'Canvas',
        'color_button': 'Choose color',
        'copy_button': 'Copy to clipboard',
        'line_button': 'Draw line',
        'stop_line': 'Stop Drawing',
        'clear_button': 'Clear canvas'
    },
    'ru': {
        'guide_label': 'ЛКМ - Рисовать\nПКМ - Стирать',
        'width_label': 'Ширина:',
        'height_label': 'Высота:',
        'create_button': 'Создать холст',
        'canvas_title': 'Холст',
        'color_button': 'Выбрать цвет',
        'copy_button': 'Копировать в буфер',
        'line_button': 'Провести линию',
        'stop_line': 'Перестать чертить',
        'clear_button': 'Очистить холст'
    }
}

# Для функций
drawing_mode = True
line_mode = False
line_start_x = None
line_start_y = None
canvases = []

# Создаём холст для рисования
def create_canvas():
    global color_button, copy_button, line_button, clear_button
    width = int(width_entry.get())
    height = int(height_entry.get())

    new_window = tk.Toplevel(root)
    new_window.title(lang_dict[lang_var.get()]['canvas_title'])

    # Подгоняем размер клеток
    if width <= 16 and height <= 16:
        cell_size = 30
    elif width <= 32 and height <= 32:
        cell_size = 20
    elif width <= 64 and height <= 64:
        cell_size = 10
    else:
        cell_size = 5
    canvas = tk.Canvas(new_window, width=width*cell_size, height=height*cell_size)
    canvas.pack(fill="both", expand=True)
    pixels = [["white" for _ in range(width)] for _ in range(height)]
    for i in range(width):
        for j in range(height):
            canvas.create_rectangle(i*cell_size, j*cell_size, (i+1)*cell_size, (j+1)*cell_size, fill="white")

    # Биндим функции
    canvas.bind("<B1-Motion>", lambda event: draw_pixel(event, canvas, width, height, cell_size, pixels))
    canvas.bind("<B3-Motion>", lambda event: erase_pixel(event, canvas, width, height, cell_size, pixels))
    canvas.bind("<Button-1>", lambda event: start_line(event, canvas, width, height, cell_size, pixels))
    canvas.bind("<ButtonRelease-1>", lambda event: draw_line(event, canvas, width, height, cell_size, pixels))

    # Создаём кнопки
    color_button = tk.Button(new_window, text=lang_dict[lang_var.get()]['color_button'], command=lambda: choose_color(new_window, canvas, width, height, cell_size))
    color_button.pack()
    copy_button = tk.Button(new_window, text=lang_dict[lang_var.get()]['copy_button'], command=lambda: copy_to_clipboard(canvas, width, height, pixels))
    copy_button.pack()
    line_button = tk.Button(new_window, text=lang_dict[lang_var.get()]['line_button'], command=lambda: toggle_line_mode(line_button))
    line_button.pack()
    clear_button = tk.Button(new_window, text=lang_dict[lang_var.get()]['clear_button'], command=lambda: clear_canvas(canvas, width, height, cell_size, pixels))
    clear_button.pack()

    # Заносим в список
    canvases.append((canvas, new_window, color_button, copy_button, line_button, clear_button))

# Рисовка на ЛКМ
def draw_pixel(event, canvas, width, height, cell_size, pixels):
    if drawing_mode:
        x = event.x // cell_size
        y = event.y // cell_size
        if 0 <= x < width and 0 <= y < height:
            canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, outline="black", fill=color_var)
            pixels[y][x] = color_var

# Стёрка на ПКМ
def erase_pixel(event, canvas, width, height, cell_size, pixels):
    x = event.x // cell_size
    y = event.y // cell_size
    if 0 <= x < width and 0 <= y < height:
        canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, outline="black", fill="white")
        pixels[y][x] = "white"

# Берём 1 позицию и 2 позицию для рисовки линии
def start_line(event, canvas, width, height, cell_size, pixels):
    global line_start_x, line_start_y
    if line_mode:
        line_start_x = event.x // cell_size
        line_start_y = event.y // cell_size
        if 0 <= line_start_x < width and 0 <= line_start_y < height:
            line_start_x = event.x // cell_size
            line_start_y = event.y // cell_size

# Рисовка линии
def draw_line(event, canvas, width, height, cell_size, pixels):
    global line_mode
    if line_mode:
        x1 = line_start_x
        y1 = line_start_y
        x2 = event.x // cell_size
        y2 = event.y // cell_size

        # Проверяет что координаты в границах холста
        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width - 1))
        y2 = max(0, min(y2, height - 1))

        # Рисует линию
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
            canvas.create_rectangle(x1*cell_size, y1*cell_size, (x1+1)*cell_size, (y1+1)*cell_size, outline="black", fill=color_var)
            pixels[y1][x1] = color_var

# Включает режим рисовки линии
def toggle_line_mode(line_button):
    global line_mode
    global drawing_mode
    if line_mode:
        line_mode = False
        drawing_mode = True
        line_button.config(text=lang_dict[lang_var.get()]['line_button'])
    else:
        line_mode = True
        drawing_mode = False
        line_button.config(text=lang_dict[lang_var.get()]['stop_line'])

# Меню выбора цвета
def choose_color(new_window, canvas, width, height, cell_size):
    color = colorchooser.askcolor()[1]
    global color_var
    color_var = color

# Копирование в буфер
def copy_to_clipboard(canvas, width, height, pixels):
    text = convert_to_text(pixels)
    root.clipboard_clear()
    root.clipboard_append(text)

# Соединяем все пиксели похожие по цвету в одну линию
def convert_to_text(pixels):
    text = ""
    for y in range(len(pixels)):
        current_color = None
        count = 0
        for x in range(len(pixels[y])):
            if pixels[y][x] == current_color:
                count += 1
            else:
                if current_color is not None:
                    text += f"[color={current_color}]{'█'*count}"
                current_color = pixels[y][x]
                count = 1
        if current_color is not None:
            text += f"[color={current_color}]{'█'*count}"
        text += "\n"
    return text

# Очистка холста
def clear_canvas(canvas, width, height, cell_size, pixels):
    canvas.delete("all")
    for i in range(width):
        for j in range(height):
            canvas.create_rectangle(i*cell_size, j*cell_size, (i+1)*cell_size, (j+1)*cell_size, fill="white")
    for i in range(height):
        for j in range(width):
            pixels[i][j] = "white"

# Изменение языка
def change_language(lang):
    lang_var.set(lang)
    guide_label.config(text=lang_dict[lang]['guide_label'])
    width_label.config(text=lang_dict[lang]['width_label'])
    height_label.config(text=lang_dict[lang]['height_label'])
    create_button.config(text=lang_dict[lang]['create_button'])

    # Есть ли холсты
    if any(canvases):
        for canvas, window, color_button, copy_button, line_button, clear_button in canvases:
            color_button.config(text=lang_dict[lang]['color_button'])
            copy_button.config(text=lang_dict[lang]['copy_button'])
            line_button.config(text=lang_dict[lang]['line_button'])
            clear_button.config(text=lang_dict[lang]['clear_button'])
            for _, window, _, _, _, _ in canvases:
                window.title(lang_dict[lang]['canvas_title'])
    else:
        print("Canvases not found")

# Основа программы
root = tk.Tk()
root.title("Image Painter")
root.geometry(root_size)

# Маленькая инструкция
guide_label = tk.Label(root, text=lang_dict[lang]['guide_label'])
guide_label.pack(side=tk.BOTTOM)

# Параметры ширины и высоты
width_label = tk.Label(root, text=lang_dict[lang]['width_label'])
width_label.pack(side=tk.LEFT)
width_entry = tk.Entry(root, width=5)
width_entry.pack(side=tk.LEFT)

height_label = tk.Label(root, text=lang_dict[lang]['height_label'])
height_label.pack(side=tk.LEFT)
height_entry = tk.Entry(root, width=5)
height_entry.pack(side=tk.LEFT)

# Кнопка создания нового холста
create_button = tk.Button(root, text=lang_dict[lang]['create_button'], command=create_canvas)
create_button.pack(side=tk.LEFT)

# Меню смены языков
lang_var = tk.StringVar()
lang_var.set(lang)
lang_menu = tk.OptionMenu(root, lang_var, 'en', 'ru', command=change_language)
lang_menu.pack(side=tk.LEFT)

root.mainloop()