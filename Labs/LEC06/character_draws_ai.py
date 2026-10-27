import math
import os
from pico2d import *


image_path = os.path.join(os.path.dirname(__file__), "character.png")

open_canvas(800, 600)
character = load_image(image_path)


def draw_character(x, y):
	clear_canvas()
	character.draw(x, y)
	update_canvas()
	delay(0.01)


def move_circle():
	for degree in range(361):
		theta = math.radians(degree)
		x = 400 + 200 * math.cos(theta)
		y = 300 + 200 * math.sin(theta)
		draw_character(x, y)


def draw_rectangle_top():
	for x in range(750, 49, -5):
		draw_character(x, 550)


def draw_rectangle_right():
	for y in range(50, 551, 5):
		draw_character(750, y)


def draw_rectangle_bottom():
	for x in range(50, 751, 5):
		draw_character(x, 50)


def draw_rectangle_left():
	for y in range(550, 49, -5):
		draw_character(50, y)


def move_rectangle():
	draw_rectangle_left()
	draw_rectangle_bottom()
	draw_rectangle_right()
	draw_rectangle_top()


point_a = (400, 500)
point_b = (700, 100)
point_c = (100, 100)


def draw_triangle_ac():
	for step in range(101):
		t = step / 100
		x = point_a[0] + (point_c[0] - point_a[0]) * t
		y = point_a[1] + (point_c[1] - point_a[1]) * t
		draw_character(x, y)


def draw_triangle_cb():
	for step in range(101):
		t = step / 100
		x = point_c[0] + (point_b[0] - point_c[0]) * t
		y = point_c[1] + (point_b[1] - point_c[1]) * t
		draw_character(x, y)


def draw_triangle_ba():
	for step in range(101):
		t = step / 100
		x = point_b[0] + (point_a[0] - point_b[0]) * t
		y = point_b[1] + (point_a[1] - point_b[1]) * t
		draw_character(x, y)


def move_triangle():
	draw_triangle_ac()
	draw_triangle_cb()
	draw_triangle_ba()


while True:
	move_circle()
	move_rectangle()
	move_triangle()


close_canvas()
