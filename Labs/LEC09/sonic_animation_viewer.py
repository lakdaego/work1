"""Play every animation in the Sonic sprite sheet with pico2d."""

from dataclasses import dataclass
from math import isfinite, pi, sin
from pathlib import Path
from time import perf_counter

CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800
SPRITE_WIDTH = 399
SPRITE_HEIGHT = 525
SPRITE_SCALE = 4
FRAME_DURATION = 0.1
FRAME_TIME_EPSILON = 1e-9
REPEAT_COUNT = 5
REST_DURATION = 1.0
GROUND_Y = 140
RUN_SPEED = 260
ROLL_SPEED = 180
EXPECTED_FRAME_COUNTS = (11, 12, 6, 9, 6, 6, 6, 8, 8, 4)


@dataclass(frozen=True)
class Frame:
    left: int
    top: int
    width: int
    height: int


@dataclass(frozen=True)
class Animation:
    name: str
    movement: str
    frames: tuple


def _frames_from_bounds(bounds):
    frames = []
    for left, top, right, bottom in bounds:
        crop_left = max(0, left - 1)
        crop_top = max(0, top - 1)
        crop_right = min(SPRITE_WIDTH, right + 2)
        crop_bottom = min(SPRITE_HEIGHT, bottom + 2)
        frames.append(
            Frame(
                crop_left,
                crop_top,
                crop_right - crop_left,
                crop_bottom - crop_top,
            )
        )
    return tuple(frames)


_ANIMATION_DATA = [
    (
        "대기 자세",
        "still",
        [
            (1, 39, 29, 77),
            (31, 40, 56, 77),
            (58, 39, 85, 77),
            (86, 40, 115, 77),
            (118, 40, 147, 77),
            (150, 40, 179, 77),
            (182, 40, 210, 77),
            (211, 39, 239, 76),
            (240, 39, 268, 76),
            (270, 45, 293, 76),
            (302, 51, 330, 76),
        ],
    ),
    (
        "달리기",
        "run",
        [
            (8, 80, 33, 116),
            (37, 80, 63, 116),
            (65, 80, 95, 117),
            (97, 80, 133, 116),
            (135, 80, 166, 114),
            (170, 79, 201, 116),
            (206, 79, 231, 116),
            (238, 80, 261, 116),
            (263, 80, 292, 116),
            (295, 80, 330, 116),
            (334, 80, 365, 115),
            (370, 79, 398, 116),
        ],
    ),
    (
        "질주",
        "run",
        [
            (1, 124, 33, 163),
            (39, 124, 73, 162),
            (89, 125, 123, 162),
            (130, 121, 163, 162),
            (181, 122, 214, 162),
            (228, 122, 260, 161),
        ],
    ),
    (
        "회전 준비",
        "still",
        [
            (1, 169, 29, 198),
            (35, 167, 63, 197),
            (67, 169, 96, 197),
            (98, 169, 128, 197),
            (131, 168, 159, 197),
            (162, 168, 190, 198),
            (193, 170, 222, 198),
            (230, 170, 260, 198),
            (268, 170, 297, 199),
        ],
    ),
    (
        "구르기",
        "roll",
        [
            (1, 206, 30, 232),
            (36, 206, 64, 232),
            (70, 206, 98, 232),
            (105, 206, 133, 232),
            (139, 206, 167, 232),
            (174, 206, 202, 232),
        ],
    ),
    (
        "회전 구르기",
        "roll",
        [
            (1, 239, 29, 273),
            (36, 239, 65, 273),
            (74, 239, 104, 273),
            (111, 238, 141, 273),
            (149, 239, 178, 273),
            (186, 238, 216, 273),
        ],
    ),
    (
        "공격",
        "run",
        [
            (1, 283, 29, 317),
            (36, 283, 65, 317),
            (72, 286, 110, 316),
            (123, 285, 161, 316),
            (172, 286, 210, 316),
            (218, 285, 255, 316),
        ],
    ),
    (
        "공중 동작",
        "jump",
        [
            (1, 326, 24, 370),
            (31, 327, 59, 370),
            (65, 327, 84, 370),
            (90, 327, 114, 369),
            (119, 327, 143, 369),
            (149, 327, 168, 370),
            (184, 341, 223, 368),
            (232, 341, 270, 367),
        ],
    ),
    (
        "달리기 변형",
        "run",
        [
            (1, 379, 27, 416),
            (31, 379, 61, 414),
            (64, 379, 94, 414),
            (99, 377, 131, 414),
            (136, 379, 167, 414),
            (176, 379, 208, 414),
            (217, 379, 249, 414),
            (254, 378, 286, 413),
        ],
    ),
    (
        "점프",
        "jump",
        [
            (6, 429, 39, 468),
            (49, 426, 82, 468),
            (96, 427, 118, 465),
            (125, 427, 147, 465),
        ],
    ),
]
ANIMATIONS = tuple(
    Animation(name, movement, _frames_from_bounds(bounds))
    for name, movement, bounds in _ANIMATION_DATA
)


def validate_animations():
    if len(ANIMATIONS) != 10:
        raise ValueError("The sprite sheet must define exactly 10 animations.")

    actual_frame_counts = tuple(len(animation.frames) for animation in ANIMATIONS)
    if actual_frame_counts != EXPECTED_FRAME_COUNTS:
        raise ValueError("The sprite sheet must define exactly 76 frames.")

    names = set()
    for animation in ANIMATIONS:
        if not animation.name.strip():
            raise ValueError("Animation names cannot be empty.")
        if animation.name in names:
            raise ValueError("Animation names must be unique: " + animation.name)
        names.add(animation.name)

        if animation.movement not in {"still", "run", "roll", "jump"}:
            raise ValueError("Unsupported movement type: " + animation.movement)
        if not animation.frames:
            raise ValueError("Animation has no frames: " + animation.name)

        for frame in animation.frames:
            if (
                frame.left < 0
                or frame.top < 0
                or frame.width <= 0
                or frame.height <= 0
                or frame.left + frame.width > SPRITE_WIDTH
                or frame.top + frame.height > SPRITE_HEIGHT
            ):
                raise ValueError("Frame lies outside the sprite sheet: " + animation.name)


class AnimationViewer:
    def __init__(self, sprite):
        self.sprite = sprite
        self.animation_index = 0
        self.animation_elapsed = 0.0
        self.rest_elapsed = 0.0
        self.resting = False
        self.x = CANVAS_WIDTH / 2
        self.direction = 1
        self._reset_position()

    @property
    def animation(self):
        return ANIMATIONS[self.animation_index]

    @property
    def frame_index(self):
        if self.resting:
            return len(self.animation.frames) - 1
        cycle_duration = len(self.animation.frames) * FRAME_DURATION
        return min(
            int(
                (self.animation_elapsed % cycle_duration + FRAME_TIME_EPSILON)
                / FRAME_DURATION
            ),
            len(self.animation.frames) - 1,
        )

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def _reset_position(self):
        self.direction = 1
        if self.animation.movement in {"run", "roll"}:
            widest_frame = max(frame.width for frame in self.animation.frames)
            self.x = widest_frame * SPRITE_SCALE / 2 + 8
        else:
            self.x = CANVAS_WIDTH / 2

    def update(self, delta_time):
        if not isfinite(delta_time) or delta_time < 0:
            raise ValueError("Elapsed time must be finite and non-negative.")

        remaining = delta_time
        while remaining > 0:
            if self.resting:
                until_next_animation = REST_DURATION - self.rest_elapsed
                step = min(remaining, until_next_animation)
                self.rest_elapsed += step
                remaining -= step
                if self.rest_elapsed >= REST_DURATION:
                    self._advance_animation()
                continue

            animation_duration = (
                len(self.animation.frames) * FRAME_DURATION * REPEAT_COUNT
            )
            until_rest = animation_duration - self.animation_elapsed
            step = min(remaining, until_rest)
            self._move(step)
            self.animation_elapsed += step
            remaining -= step
            if self.animation_elapsed >= animation_duration:
                self.resting = True
                self.rest_elapsed = 0.0

    def _move(self, delta_time):
        if self.animation.movement in {"run", "roll"}:
            widest_frame = max(frame.width for frame in self.animation.frames)
            left_edge = widest_frame * SPRITE_SCALE / 2 + 8
            right_edge = CANVAS_WIDTH - left_edge
            span = right_edge - left_edge
            distance = self.x - left_edge
            if self.direction < 0:
                distance = 2 * span - distance
            speed = RUN_SPEED if self.animation.movement == "run" else ROLL_SPEED
            phase = (distance + speed * delta_time) % (2 * span)
            if phase <= span:
                self.x = left_edge + phase
                self.direction = 1
            else:
                self.x = right_edge - (phase - span)
                self.direction = -1

    def draw(self):
        frame = self.frame
        draw_width = frame.width * SPRITE_SCALE
        draw_height = frame.height * SPRITE_SCALE
        draw_y = GROUND_Y + draw_height / 2
        if self.animation.movement == "jump":
            last_frame = len(self.animation.frames) - 1
            phase = self.frame_index / last_frame if last_frame else 0
            draw_y += 150 * sin(pi * phase)

        source_bottom = SPRITE_HEIGHT - frame.top - frame.height
        if self.direction < 0 and self.animation.movement in {"run", "roll"}:
            self.sprite.clip_composite_draw(
                frame.left,
                source_bottom,
                frame.width,
                frame.height,
                0,
                "h",
                self.x,
                draw_y,
                draw_width,
                draw_height,
            )
        else:
            self.sprite.clip_draw(
                frame.left,
                source_bottom,
                frame.width,
                frame.height,
                self.x,
                draw_y,
                draw_width,
                draw_height,
            )

    def _advance_animation(self):
        self.animation_index = (self.animation_index + 1) % len(ANIMATIONS)
        self.animation_elapsed = 0.0
        self.rest_elapsed = 0.0
        self.resting = False
        self._reset_position()


def main():
    from pico2d import (
        SDL_QUIT,
        clear_canvas,
        close_canvas,
        delay,
        get_events,
        load_image,
        open_canvas,
        update_canvas,
    )

    validate_animations()
    sprite_path = Path(__file__).resolve().parent / "sonic-sprite.png"
    if not sprite_path.is_file():
        raise FileNotFoundError("Required sprite image not found: " + str(sprite_path))

    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        sprite = load_image(str(sprite_path))
        viewer = AnimationViewer(sprite)
        running = True
        previous_time = perf_counter()

        while running:
            for event in get_events():
                if event.type == SDL_QUIT:
                    running = False

            if not running:
                break

            current_time = perf_counter()
            viewer.update(current_time - previous_time)
            previous_time = current_time

            clear_canvas()
            viewer.draw()
            update_canvas()
            delay(0.01)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
