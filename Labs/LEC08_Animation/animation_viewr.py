from pico2d import *

open_canvas()

grass = load_image('grass.png')
character = load_image('SamuraiSheet.png')

while True:
	for source_y in (1024, 896):
		for _ in range(5):
			for frame in range(8):
				clear_canvas()
				grass.draw(400, 30)
				character.clip_draw(frame * 128, source_y, 128, 128, 400, 300)
				update_canvas()
				delay(0.05)
		delay(1)

	for _ in range(5):
		for frame in range(6):
			clear_canvas()
			grass.draw(400, 30)
			character.clip_draw(frame * 128, 640, 128, 128, 400, 300, 154, 154)
			update_canvas()
			delay(0.05)
	delay(1)

	for _ in range(5):
		for death_frame in range(3):
			clear_canvas()
			grass.draw(400, 30)
			death_size = 154 if death_frame == 2 else 128
			character.clip_draw(death_frame * 128, 0, 128, 128, 400, 300, death_size, death_size)
			update_canvas()
			delay(0.2)
	delay(1)





