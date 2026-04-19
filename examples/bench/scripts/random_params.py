import sys, json, random

params = {
    "heating_setpoints": [random.uniform(10, 35), random.uniform(10, 35)],
    "vent_openings": [random.uniform(0, 1), random.uniform(0, 1)],
    "shading": random.uniform(0, 1),
    "co2_injection": random.uniform(0, 15),
    "light_intensity": random.uniform(50, 800),
    "irrigation": random.uniform(0.1, 2.5),
    "sim_steps": random.randint(20, 150),
}
print(json.dumps(params))
