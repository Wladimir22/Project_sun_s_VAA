import tkinter as tk
import math

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
        self.x, self.y = 0, 0
        self.anchor = tk.CENTER
        self.canvas = None
        self.radius = self.image.width() / 2
    
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
        #Загрузка изображения планеты
        self.x, self.y = self.orbit.get_current_position()
    
    def move(self):
        old_x, old_y = self.x, self.y
        self.x, self.y = self.orbit.get_current_position()
        dx, dy = self.x - old_x, self.y - old_y
        self.canvas.move(self.canvas_image, dx, dy)
        return 
    

planets = [
    {"name": 'Земля', "image": 'earth.png', "orbit": Orbit(200, 0.017, 350, 300, 0, 1),
    "orbit_excenter": 0.017, "orbit_year": "1 год", "orbit_speed": 29.783, "orbit_perihelion": 0.98329134, "orbit_aphelion": 1.01671388,
    "mass_mantissa": 5.9726, "mass_exp": 24, "volume_mantissa": 10.8321, "volume_exp": 11, "radius": 6371, "area": "5,10072⋅10^8",
    "tilt": 23.44, "space_speed": (7.91, 11.186), "sidereal_period": (23, 56, 4), "temp": (184, 287.2, 329.9),
    "atmo": {"Азот": 78.08, "Кислород": 20.95, "Водяной пар": 1, "Аргон": 0.93, "Углекислый газ": 0.04}
    }
]

def update_info_frame():
    pass #TODO

def update_selection(event):
    global planets, selected_planet
    for p in planets:
        if p.if_clicked(event):
            selected_planet = p
            return
    selected_planet = None

def update():
    global root, planets, orbit_time, selected_planet_halo
    orbit_time += 1 / 60
    for p in planets:
        p.move()
    if selected_planet is not None:
        r = selected_planet.radius
        x, y = selected_planet.x, selected_planet.y
        if selected_planet_halo is not None:
            canvas.delete(selected_planet_halo)
        selected_planet_halo = canvas.create_oval(x - r, y - r, x + r, y + r, outline = "white", width = 2)
    else:
        if selected_planet_halo:
            canvas.delete(selected_planet_halo)
            selected_planet_halo = None
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
    canvas_frame.pack(side = 'left')
    #Создаём сам Canvas
    canvas = tk.Canvas(canvas_frame, width = ROOT_W - 200, height = ROOT_H)
    canvas.bind('<Button-1>', update_selection)
    canvas.pack(side = 'left')
    #Рисуем фон
    bg = ImageObject('bg.png')
    bg.draw_on_canvas(canvas)
    #Конвертируем и расставляем планеты
    planets = [Planet(p) for p in planets]
    selected_planet = None
    selected_planet_halo = None
    for p in planets:
        p.draw_on_canvas(canvas)
        print(p.x, p.y)
    root.after(int(1000/60), update)
    root.mainloop()