from pico2d import *


open_canvas()
grass = load_image('grass.png')
character = load_image('animation_sheet.png')


def handle_events():
    global running, dir

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif (event.type == SDL_KEYDOWN and 
            event.key == SDLK_RIGHT):
            dir = 1
        elif (event.type == SDL_KEYDOWN and 
            event.key == SDLK_LEFT):
            dir = -1
        elif (event.type == SDL_KEYDOWN and 
                    event.key == SDLK_ESCAPE):
                    running = False
        elif (event.type == SDL_KEYUP and 
            (event.key == SDLK_RIGHT or event.key == SDLK_LEFT)):
            dir = 0
        


    events = get_events()



running = True
x = 800 // 2
frame = 0
dir = 0

# fill here


close_canvas()

