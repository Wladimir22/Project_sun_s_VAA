import tkinter as tk
import math
import json

ORBIT_EARTH_SPEED = math.pi / 20
orbit_time = 0.0
def load_image(name):
    """Загрузить изображение в память из папки img (png или gif)"""
    try:
        image = tk.PhotoImage(file = "img/%s" % name)
        return image
    except Exception as e:
        print('Ошибка загрузки изображения {0}:\n{1}'.format(name, e))
        exit(-1)
#Размеры экрана
ROOT_W = 800
ROOT_H = 600

INFO_TEXT_PLANET = """\
{name} ({type})

Эксцентристет орбиты: {orbit_excenter}
Время оборота: {orbit_year}
Орбитальная скорость: {orbit_speed} км/с
Ср. растояние до Солнца: {orbit_size} а.е.

Масса: {mass_mantissa} · 10{mass_exp} кг
Радиус: {radius} км
Объём: {volume_mantissa} · 10{volume_exp} кг
Ср. плотность: {density} г/см³
Наклон оси: {tilt} градусов
Ускорение свободного падения: {gravity} м/с²
Площадь поверхности: {area_mantissa} · 10{area_exp} м²
Период вращения: {sidereal_period}
Температура: от {temp[0]} К до {temp[2]} К
Средняя температура: {temp[1]} К

Космические скорости:
Первая — {space_speed_1} км/с
Вторая — {space_speed_2} км/с

Состав атмосферы:
"""

INFO_TEXT_STAR = """\
{name} ({type})

Масса: {mass_mantissa} · 10{mass_exp} кг
Радиус: {radius} км
Объём: {volume_mantissa} · 10{volume_exp} кг
Ср. плотность: {density} г/см³
Сидерический период: {sidereal_period}
Ускорение свободного падения: {gravity} м/с²
Температура кроны: {temp[0]} К
Температура ядра: {temp[1]} К

Состав фотосферы:
"""

class Orbit():
    """Класс для орбиты планет"""
    def __init__(self, hw, e, x, y, td, speed):
        self.hw = hw #Полуширина орбиты
        self.e = e #Эксцентристет орбиты
        self.hh = math.sqrt(hw * hw * (1 - e * e)) #Полувысота орбиты
        #Центр орбиты
        self.x = x
        self.y = y
        self.td = td #Начальное отклонение
        self.speed = speed #Коэффициент скорости
    
    def get_current_position(self):
        """Получить текущую позицию на орбите"""
        t = self.td + orbit_time * ORBIT_EARTH_SPEED / self.speed
        x = self.x + self.hw * math.cos(t)
        y = self.y + self.hh * math.sin(t)
        return x, y
    
    def get_oval_params(self):
        """Получить параметры для рисования овала орбиты в Tkinter"""
        return self.x - self.hw, self.y - self.hh, self.x + self.hw, self.y + self.hh

class ImageObject():
    """Класс для отображемых объектов"""
    def __init__(self, img_name, x = 0, y = 0, anchor = tk.NW):
        self.image = load_image(img_name)
        self.x, self.y = x, y
        self.anchor = anchor
    
    def draw_on_canvas(self, canvas):
        self.canvas_image = canvas.create_image(self.x, self.y, anchor = self.anchor, image = self.image)

class InfoObject(ImageObject):
    """Класс для кликабельных объектов Солнечной системы информации о них"""
    def __init__(self, info):
        self.info = info #Информация об объекте
        self.name = info['name']
        self.info['type'] = "неизвестно"
        self.image = load_image(info['image'])
        self.image_big = load_image(info['image_big'])
        self.x, self.y = 0, 0
        self.anchor = tk.CENTER
        self.canvas = None
        self.radius = self.image.width() / 2
        self.convert_exps()
    
    def convert_exps(self):
        for key in self.info:
            if key[-4:] == "_exp":
                s = ""
                n = self.info[key]
                while n > 0:
                    d = n % 10
                    if d == 1:
                        s += '\u00B9'
                    elif d == 2 or d == 3:
                        s += chr(0xB0 + d)
                    else:
                        s += chr(0x2070 + d)
                    n //= 10
                self.info[key] = s
    
    def if_clicked(self, event):
        mx, my = event.x, event.y #Позиция мыши
        rel_mx, rel_my = mx - self.x, my - self.y
        return (rel_mx * rel_mx + rel_my * rel_my <= self.radius * self.radius)

    def draw_on_canvas(self, canvas):
        self.canvas_image = canvas.create_image(self.x, self.y, anchor = self.anchor, image = self.image)
        self.canvas = canvas

class Planet(InfoObject):
    """Класс для планет и информации о них"""
    def __init__(self, info):
        super().__init__(info)
        self.orbit = info['orbit']
        self.info['type'] = "планета"
        self.x, self.y = self.orbit.get_current_position()
    
    def move(self):
        old_x, old_y = self.x, self.y
        self.x, self.y = self.orbit.get_current_position()
        dx, dy = self.x - old_x, self.y - old_y
        self.canvas.move(self.canvas_image, dx, dy)
        return

class Star(InfoObject):
    """Класс для Солнца"""
    def __init__(self, info, x, y):
        super().__init__(info)
        self.info['type'] = "звезда"
        self.x, self.y = x, y

#Парсим информцию о планетах
def parse_json(name):
    with open("info/%s.json" % name, "r", encoding = 'utf-8') as read_file:
        return json.load(read_file)

planets = [parse_json("earth")]

def update_info_frame(reset = False):
    global info_frame, selected_planet, info_image, info_text
    if reset:
        if info_image is not None:
            info_image.destroy()
        if info_text is not None:
            info_text.destroy()
        info_image = tk.Label(info_frame, text = "Нажмите на планету, чтобы узнать о ней побольше", 
            width = 200, wraplength = 194, bg = 'white')
        info_image.pack(side = "top", fill = "both")
    else:
        info_image.destroy()
        if info_text is not None:
            info_text.destroy()
        info_image = tk.Label(info_frame, image = selected_planet.image_big,
            width = 200, height = 160, bg = 'white')
        if type(selected_planet) == Planet:
            info_text = INFO_TEXT_PLANET.format(**selected_planet.info)
        else:
            info_text = INFO_TEXT_STAR.format(**selected_planet.info)
        for comp in selected_planet.info['atmo']:
            info_text += '%s: %s%%\n' % (comp, selected_planet.info['atmo'][comp])
        info_text = tk.Label(info_frame, text = info_text, wraplength = 194, bg = 'white')
        info_image.pack(side = "top", fill = "both")
        info_text.pack(side = "top", fill = "both")


def update_selection(event):
    global planets, selected_planet
    for p in planets:
        if p.if_clicked(event):
            selected_planet = p
            update_info_frame()
            return
    update_info_frame(True)
    selected_planet = None

def update():
    global root, planets, orbit_time
    orbit_time += 1 / 60
    for p in planets[1:]:
        p.move()
    if selected_planet is not None:
        r = selected_planet.radius
        x, y = selected_planet.x, selected_planet.y
    else:
        pass
    root.after(int(1000/60), update)

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("%dx%d+%d+%d" % (ROOT_W, ROOT_H, 100, 100))
    #Создаём панель с информацией и панель для canvas
    canvas_frame = tk.Frame(root, borderwidth=1)
    canvas_frame.pack(fill="both", expand=True)
    canvas_frame.pack(side = 'right')
    info_frame = tk.Frame(root, borderwidth=1, bg = "white", width = 200)
    info_frame.pack(fill="both", expand=True)
    info_image, info_text = None, None
    update_info_frame(True)
    canvas_frame.pack(side = 'left')
    #Создаём сам Canvas
    canvas = tk.Canvas(canvas_frame, width = ROOT_W - 200, height = ROOT_H)
    canvas.bind('<Button-1>', update_selection)
    canvas.pack(side = 'left')
    #Рисуем фон
    bg = ImageObject('bg.png')
    bg.draw_on_canvas(canvas)
    #Конвертируем и расставляем планеты
    planets_done = []
    for p in planets:
        p['orbit'] = Orbit(*p['orbit'])
        planets_done.append(Planet(p))
    planets = planets_done
    planets_done.insert(0, Star(parse_json("sun"), 300, 300))
    selected_planet = None
    for p in planets:
        p.draw_on_canvas(canvas)
        print(p.x, p.y)
    root.after(int(1000/60), update)
    root.mainloop()