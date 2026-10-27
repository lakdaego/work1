import time
from math import pi

from pico2d import (
    SDLK_a, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDL_KEYDOWN, SDL_KEYUP,
    load_image,
)
from transitions import Machine


class AutoRunState:
    def __init__(self):
        self.started_at = time.monotonic()

    def start(self):
        self.started_at = time.monotonic()

    def handle_event(self, boy, event):
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            boy.direction_keys.add(event.key)
            boy.face_dir = -1 if event.key == SDLK_LEFT else 1
            boy.cancel_autorun()

    def update(self, boy):
        if time.monotonic() - self.started_at >= 5:
            boy.finish_autorun()
            boy.idle_since = time.monotonic()
            return

        next_x = boy.x + boy.face_dir * 10
        if next_x <= 100:
            boy.x = 100
            boy.face_dir = 1
        elif next_x >= 700:
            boy.x = 700
            boy.face_dir = -1
        else:
            boy.x = next_x
        boy.frame = (boy.frame + 1) % 8

    def draw(self, boy):
        source_y = 100 if boy.face_dir == 1 else 0
        boy.image.clip_draw(
            boy.frame * 100, source_y, 100, 100,
            boy.x, boy.y, 200, 200,
        )


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.direction_keys = set()
        self.autorun_state = AutoRunState()
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
        self.machine.add_transition('cancel_autorun', 'AUTORUN', 'RUN')
        self.machine.add_transition('finish_autorun', 'AUTORUN', 'IDLE')
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
            self.autorun_state.update(self)

    def handle_event(self, event):
        if self.state == 'AUTORUN':
            self.autorun_state.handle_event(self, event)
            return

        if (
            self.state == 'IDLE'
            and event.type == SDL_KEYDOWN
            and event.key == SDLK_a
        ):
            self.autorun()
            self.autorun_state.start()
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

        if self.state == 'AUTORUN':
            self.autorun_state.draw(self)
            return

        if self.state == 'RUN':
            source_y = 100 if self.face_dir == 1 else 0
        else:
            source_y = 300 if self.face_dir == 1 else 200
        self.image.clip_draw(
            self.frame * 100, source_y, 100, 100, self.x, self.y
        )
