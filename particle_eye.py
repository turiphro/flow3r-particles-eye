from st3m.reactor import Responder
import st3m.run

import random
import math


SCREEN_SIZE = [240, 240]
TOPLEFT = [-dim // 2 for dim in SCREEN_SIZE]
CENTER = [0, 0]
CIRCLE_CENTER_R = 25
CIRCLE_RING_R = 90
CIRCLE_RING_WIDTH = 6

PARTICLE_SIZE = 2
NUM_PARTICLES_INNER = 100
NUM_PARTICLES_OUTER = 150
DAMPING = 0.9


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
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

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


class Particle:
    def __init__(self, force_fn):
        self.position = Vector(
            float(random.randint(TOPLEFT[0], TOPLEFT[0] + SCREEN_SIZE[0])),
            float(random.randint(TOPLEFT[1], TOPLEFT[0] + SCREEN_SIZE[1]))
        )
        self.colour = [255, 0, 0]
        self.entropy = 5
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

    def move(self, delta_ms: int) -> None:
        force = self.force_fn(self.position)
        wiggle = Vector(random.uniform(-1, 1), random.uniform(-1, 1))
        self.speed = self.speed * DAMPING + (force + self.entropy * wiggle) * (1 - DAMPING)

        self.position += self.speed



class ParticleEye(Responder):
    def __init__(self) -> None:
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
        for particle in self.particles:
            particle.move(delta_ms)


if __name__ == '__main__':  # debugging purposes
    st3m.run.run_responder(ParticleEye())

