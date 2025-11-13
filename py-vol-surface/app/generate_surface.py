import numpy as np

def generate_demo_surface():
    # Simple synthetic surface:
    # vol = base + 0.1 * exp(-((k - 1)^2 + (t - 1)^2))
    strikes = np.linspace(0.5, 1.5, 20)
    tenors = np.linspace(0.1, 2.0, 20)
    base_vol = 0.2

    surface = []
    for t in tenors:
        row = []
        for k in strikes:
            vol = base_vol + 0.1 * np.exp(-((k - 1)**2 + (t - 1)**2))
            row.append(float(vol))
        surface.append(row)

    return surface
