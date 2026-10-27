# 실습 과제 진행
import os
from pico2d import *

image_path = os.path.join(os.path.dirname(__file__), 'character.png')

open_canvas(800, 600)
character = load_image(image_path)

theta = math.radians(30)
x = 400 + 200 * math.cos(theta)
y = 300 + 200 * math.sin(theta)



def draw_character(x, y):
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.01)


def move_circle():
   for degree in range(360):
        theta = math.radians(degree)
        x = 400 + 200 * math.cos(theta)
        y = 300 + 200 * math.sin(theta)

        draw_character(x, y)




def draw_top():
        for x in range(750, 50, -5):
              draw_character(x, 550)

def draw_left():    
        for y in range(550, 50, -5):
            draw_character(50, y)

def draw_bottom():
        for x in range(50, 750, 5):
            draw_character(x, 50)

def draw_right():
        for y in range(50, 550, 5):
            draw_character(750, y)



def move_rectangle():
    # print("rectangle")
    draw_top()
    draw_left()
    draw_bottom()
    draw_right()


point_a = (400, 500)
point_b = (700, 100)
point_c = (100, 100)


def draw_triangle_ab():
    for step in range(101):
        t = step / 100
        x = point_a[0] + (point_b[0] - point_a[0]) * t
        y = point_a[1] + (point_b[1] - point_a[1]) * t
        draw_character(x, y)


def draw_triangle_bc():
    for step in range(101):
        t = step / 100
        x = point_b[0] + (point_c[0] - point_b[0]) * t
        y = point_b[1] + (point_c[1] - point_b[1]) * t
        draw_character(x, y)


def draw_triangle_ca():
    for step in range(101):
        t = step / 100
        x = point_c[0] + (point_a[0] - point_c[0]) * t
        y = point_c[1] + (point_a[1] - point_c[1]) * t
        draw_character(x, y)


def move_triangle():
    draw_triangle_ab()
    draw_triangle_ca()
    draw_triangle_bc()



while True:
    move_circle()
    move_rectangle()
    move_triangle()


close_canvas()