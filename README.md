# Flow3r Particles Eye

[Flow3r app](https://docs.flow3r.garden/) with particle simulation, forming an evil'ish eye. Kind of inspired by both HAL 9000 and Sauron's Eye.

Based on an earlier implementation called "DeepFace": https://github.com/turiphro/deepFace/ (written in C++/OpenFrameworks).


## Usage
- by default will show the particle simulation
- tap the petals to attract particles towards your finger
- left app wheel to change the colour of the particles (random colour)


## Todo
- Optimise code; currently, it's pretty sluggish for >200 particles (the original ran >2000 particles on a raspberry pi 3B+). Likely in-place coordinate updates will help. Maybe the round_rectangle drawing is also slow.
- Ideas for more features:
    - react to sound (increase entropy)
    - API or MQTT listener to update colours/entropy based on external events (e.g., smart home events)
    - sound effects (e.g., on touch)
