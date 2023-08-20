from .particles_eye import ParticlesEye

import st3m.run
from st3m.application import ApplicationContext


st3m.run.run_view(ParticlesEye(ApplicationContext))
