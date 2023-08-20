from st3m.reactor import Responder
import st3m.run
from st3m.application import Application, ApplicationContext

import random
import math


SCREEN_SIZE = [240, 240]
TOPLEFT = [-dim // 2 for dim in SCREEN_SIZE]
CENTER = [0, 0]
CIRCLE_CENTER_R = 25
CIRCLE_RING_R = 90
CIRCLE_RING_WIDTH = 6
TOUCH_DISTANCE = SCREEN_SIZE[0] / 2

PARTICLE_SIZE = 4
NUM_PARTICLES_INNER = 50
NUM_PARTICLES_OUTER = 150
DAMPING = 0.8
ENTROPY_BASE = 5
ENTROPY_TOUCH = 10


class Vector:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, other: Vector):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector):
        return self + (other * -1)

    def __mul__(self, other: Union[Vector, float, int]):
        if isinstance(other, (int, float)):
            return Vector(other * self.x, other * self.y)
        elif isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y)

    def __rmul__(self, other: Union[Vector, float, int]):
        return self * other

    def __truediv__(self, other: Union[Vector, float, int]):
        if isinstance(other, (int, float)):
            return Vector(self.x / other, self.y / other)
        elif isinstance(other, Vector):
            return Vector(self.x / other.x, self.y / other.y)

    def distance_to(self, other: Vector):
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5

    def __str__(self):
        return f"({self.x}, {self.y})"


center = Vector(*CENTER)
screen_size = Vector(*SCREEN_SIZE)


def force_to_pupil(position: Vector) -> Vector:
    """Move towards a filled circle (no force when within)"""
    difference = center - position
    distance = center.distance_to(position)
    
    if distance > CIRCLE_CENTER_R:
        return difference * (distance - CIRCLE_CENTER_R) / screen_size
    else:
        return center


def force_to_outline(position: Vector) -> Vector:
    """Move towards the contour of a circle"""
    difference = center - position
    distance = center.distance_to(position)
    
    if distance > CIRCLE_RING_R + CIRCLE_RING_WIDTH:  # move inwards
        return difference * (distance - CIRCLE_RING_R - CIRCLE_RING_WIDTH) / screen_size
    elif distance < CIRCLE_RING_R - CIRCLE_RING_WIDTH:  # move outwards
        return difference * (distance - CIRCLE_RING_R + CIRCLE_RING_WIDTH) / screen_size
    else:
        return center


def force_to_mass(mass: Vector):
    """Gravity-like force (stronger if closer) towards a mass"""
    def force_fn(position: Vector) -> Vector:
        difference = mass - position
        distance = mass.distance_to(position)
        force = difference / (distance) * screen_size * 0.1
        return force

    return force_fn


class Particle:
    def __init__(self, force_fn):
        self.position = Vector(
            float(random.randint(TOPLEFT[0], TOPLEFT[0] + SCREEN_SIZE[0])),
            float(random.randint(TOPLEFT[1], TOPLEFT[0] + SCREEN_SIZE[1]))
        )
        self.colour = [255, 0, 0]
        self.entropy = ENTROPY_BASE
        self.speed = Vector(0, 0)
        self.force_fn = force_fn

    def draw(self, ctx: Context) -> None:
        ctx.rgb(*self.colour).round_rectangle(
            self.position.x - PARTICLE_SIZE / 2,
            self.position.y - PARTICLE_SIZE / 2,
            PARTICLE_SIZE,
            PARTICLE_SIZE,
            PARTICLE_SIZE // 2
        ).fill()

    def move(self, delta_ms: int, additional_forces: None) -> None:
        force = self.force_fn(self.position)
        if additional_forces:
            for add_force_fn in additional_forces:
                force += add_force_fn(self.position)
        wiggle = Vector(random.uniform(-1, 1), random.uniform(-1, 1))
        self.speed = self.speed * DAMPING + (force + self.entropy * wiggle) * (1 - DAMPING)

        self.position += self.speed



class ParticlesEye(Application):
    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)

        self.particles = []
        for _ in range(NUM_PARTICLES_INNER):
            self.particles.append(Particle(force_fn=force_to_pupil))
        for _ in range(NUM_PARTICLES_OUTER):
            self.particles.append(Particle(force_fn=force_to_outline))

    def draw(self, ctx: Context) -> None:
        # Paint the background black
        ctx.rgb(0, 0, 0).rectangle(TOPLEFT[0], TOPLEFT[1], SCREEN_SIZE[0], SCREEN_SIZE[1]).fill()

        # paint particles
        for particle in self.particles:
            particle.draw(ctx)

    def think(self, ins: InputState, delta_ms: int) -> None:
        super().think(ins, delta_ms)

        additional_forces = []
        for index, petal in enumerate(self.input.captouch.petals):
            if petal.whole.pressed or petal.whole.repeated:
                angle = 2 * math.pi * index / 10 - math.pi / 2
                additional_forces.append(force_to_mass(Vector(
                    TOUCH_DISTANCE * math.cos(angle),
                    TOUCH_DISTANCE * math.sin(angle),
                )))

        for particle in self.particles:
            particle.entropy = ENTROPY_TOUCH if additional_forces else ENTROPY_BASE
            particle.move(delta_ms, additional_forces)


# development purposes (mpremote run)
if __name__ == '__main__':
    st3m.run.run_view(ParticlesEye(ApplicationContext()))

