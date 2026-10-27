import time
from math import pi

from pico2d import (
    SDLK_a, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDL_KEYDOWN, SDL_KEYUP,
    load_image,
)
from transitions import Machine

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.direction_keys = set()
        self.idle_since = time.monotonic()
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'SLEEP', 'AUTORUN'],
            initial='IDLE',
            auto_transitions=False,
        )
        self.machine.add_transition('run', ['IDLE', 'SLEEP'], 'RUN')
        self.machine.add_transition('autorun', 'IDLE', 'AUTORUN')
        self.machine.add_transition('stop_running', 'RUN', 'IDLE')
        self.machine.add_transition('sleep', 'IDLE', 'SLEEP')
        self.machine.add_transition('wake', 'SLEEP', 'IDLE')

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
            if time.monotonic() - self.idle_since >= 5:
                self.sleep()
        elif self.state == 'RUN':
            self.x = max(50, min(750, self.x + self.face_dir * 5))
            self.frame = (self.frame + 1) % 8
        elif self.state == 'AUTORUN':
            next_x = self.x + self.face_dir * 5
            if next_x <= 50:
                self.x = 50
                self.face_dir = 1
            elif next_x >= 750:
                self.x = 750
                self.face_dir = -1
            else:
                self.x = next_x
            self.frame = (self.frame + 1) % 8

    def handle_event(self, event):
        if self.state == 'AUTORUN':
            return

        if (
            self.state == 'IDLE'
            and event.type == SDL_KEYDOWN
            and event.key == SDLK_a
        ):
            self.autorun()
            return

        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.direction_keys.add(event.key)
            self.face_dir = -1 if event.key == SDLK_LEFT else 1
            if self.state in ('IDLE', 'SLEEP'):
                self.run()
            return

        if event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.direction_keys.discard(event.key)
            if self.state == 'RUN':
                if self.direction_keys:
                    self.face_dir = (
                        -1 if SDLK_LEFT in self.direction_keys else 1
                    )
                else:
                    self.stop_running()
                    self.idle_since = time.monotonic()
            return

        if (
            self.state == 'SLEEP'
            and event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
        ):
            self.wake()
            self.idle_since = time.monotonic()

    def draw(self):
        if self.state == 'SLEEP':
            source_y = 300 if self.face_dir == 1 else 200
            self.image.clip_composite_draw(
                self.frame * 100, source_y, 100, 100,
                pi / 2, '', self.x, self.y - 25, 100, 100,
            )
            return

        if self.state in ('RUN', 'AUTORUN'):
            source_y = 100 if self.face_dir == 1 else 0
        else:
            source_y = 300 if self.face_dir == 1 else 200
        self.image.clip_draw(
            self.frame * 100, source_y, 100, 100, self.x, self.y
        )
