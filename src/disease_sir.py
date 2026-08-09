import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Button

# CONSTANTS & SETTINGS
GW, GH = 160, 100
DP = {
    'beta': 0.3,
    'sigma': 0.12,
    'gamma': 0.05,
    'mu': 0.018,
    'wane': 0.015
}

COLORS = ['#0e0500', '#00c8ff', '#c86eff', '#ff3232', '#20dc82', '#50505a', '#28f0d2']
LABELS = ['Empty', 'Healthy', 'Exposed', 'Infected', 'Recovered', 'Dead', 'Immune']
cmap = ListedColormap(COLORS)

# Pre-allocated tuples for faster 5x5 neighborhood math
DELTAS24 = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if not (dx == 0 and dy == 0)]

# STATE MATRICES
grid = np.zeros((GH, GW), dtype=np.uint8)
nrg = np.zeros((GH, GW), dtype=np.float32)
age = np.zeros((GH, GW), dtype=np.uint16)
gen_n = 0
is_paused = True
speed_label = "Paused"

def apply_random_distribution():
    global grid, nrg, age, gen_n
    grid.fill(0)
    nrg.fill(0)
    age.fill(0)
    gen_n = 0
    
    # Match initial exact randomizer distribution
    for i in range(GW * GH):
        y, x = divmod(i, GW)
        r = np.random.rand()
        if r < 0.68:
            grid[y, x] = 1
            nrg[y, x] = 100
        elif r < 0.73:
            grid[y, x] = 3
            nrg[y, x] = 80
        elif r < 0.75:
            grid[y, x] = 6
            nrg[y, x] = 100

apply_random_distribution()

# THE UI SETUP
fig = plt.figure(figsize=(13, 7.5))
fig.canvas.manager.set_window_title('Cellular Architect - Epidemic Spread')
fig.patch.set_facecolor('#04080f')

ax = fig.add_axes([0.05, 0.15, 0.7, 0.8])
ax.set_axis_off()
im = ax.imshow(grid, cmap=cmap, vmin=0, vmax=len(COLORS)-1, animated=True)

# CUSTOM STATS & LEGEND PANEL
stats_ax = fig.add_axes([0.78, 0.15, 0.2, 0.8])
stats_ax.set_axis_off()

speed_text = stats_ax.text(0, 0.95, f"SPEED: {speed_label}", color='#00d2ff', fontfamily='monospace', fontsize=12, fontweight='bold')
gen_text = stats_ax.text(0, 0.88, f"GEN: {gen_n}", color='#e0f2fe', fontfamily='monospace', fontsize=11)
pop_text = stats_ax.text(0, 0.83, f"POP: {0}", color='#e0f2fe', fontfamily='monospace', fontsize=11)

stats_texts = {}
y_start = 0.73
y_step = 0.08

for i in range(1, len(LABELS)):
    y_pos = y_start - (i-1) * y_step
    rect = plt.Rectangle((0, y_pos - 0.015), 0.06, 0.035, color=COLORS[i], transform=stats_ax.transAxes)
    stats_ax.add_patch(rect)
    txt = stats_ax.text(0.10, y_pos, f"{LABELS[i]}: 0", color='#e0f2fe', fontfamily='monospace', fontsize=11, va='center')
    stats_texts[i] = txt

def update_stats():
    pop = np.count_nonzero(grid)
    counts = [np.count_nonzero(grid == i) for i in range(len(LABELS))]
    
    speed_text.set_text(f"SPEED: {speed_label}")
    gen_text.set_text(f"GEN: {gen_n}")
    pop_text.set_text(f"POP: {pop}")
    
    for i in range(1, len(LABELS)):
        stats_texts[i].set_text(f"{LABELS[i]}: {counts[i]}")

# CORE SIMULATION LOGIC
def step_sim():
    global grid, nrg, age, gen_n
    
    next_grid = grid.copy()
    next_nrg = nrg.copy()
    
    infect_rate = DP['beta'] * 2.5
    
    # Engine Optimization: Only iterate mathematically active cells
    active_indices = np.flatnonzero(grid)
    
    for i in active_indices:
        y, x = divmod(i, GW)
        t = grid[y, x]
        e = nrg[y, x]
            
        if age[y, x] < 65535:
            age[y, x] += 1
            
        if t == 1: # Susceptible (Healthy)
            ic = 0.0
            for dx, dy in DELTAS24:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GW and 0 <= ny < GH:
                    nt = grid[ny, nx]
                    if nt == 3: 
                        ic += 1.0
                    elif nt == 2: 
                        ic += 0.5
            
            if ic > 0 and np.random.rand() < (infect_rate * ic / 24.0):
                next_grid[y, x] = 2
                next_nrg[y, x] = 100
                
        elif t == 2: # Exposed
            e -= 1.5
            if e <= 0 or np.random.rand() < DP['sigma']:
                next_grid[y, x] = 3
                next_nrg[y, x] = 100
            else:
                next_nrg[y, x] = e
                
        elif t == 3: # Infected
            e -= 2.5
            if e <= 0:
                if np.random.rand() < DP['mu']:
                    next_grid[y, x] = 5 # Dead
                else:
                    next_grid[y, x] = 4 # Recovered
                    next_nrg[y, x] = 100
            else:
                next_nrg[y, x] = e
                
        elif t == 4: # Recovered
            if np.random.rand() < DP['wane']:
                next_grid[y, x] = 1
                
    grid = next_grid
    nrg = next_nrg
    gen_n += 1

def update(frame):
    if not is_paused:
        step_sim()

    im.set_array(grid)
    update_stats()
    return [im, speed_text, gen_text, pop_text] + list(stats_texts.values())

# PLAYBACK CONTROLS 
btn_labels = ['Pause', 'Play', 'Step', 'Randomize']
btn_axs = [fig.add_axes([0.10 + i * 0.17, 0.04, 0.12, 0.05]) for i in range(4)]
btns = [Button(ax, label, color='#0d1829', hovercolor='#00d2ff') for ax, label in zip(btn_axs, btn_labels)]

for b in btns: 
    b.label.set_color('white')
    b.label.set_fontsize(10)
    b.label.set_fontweight('bold')

def set_pause(val): 
    global is_paused, speed_label
    is_paused = True
    speed_label = "Paused"
    update_stats()
    fig.canvas.draw_idle()

def set_play(val):
    global is_paused, speed_label
    is_paused = False
    speed_label = "Playing"
    update_stats()
    fig.canvas.draw_idle()

def set_step(val): 
    global is_paused, speed_label
    is_paused = True
    speed_label = "Paused"
    step_sim()
    im.set_array(grid)
    update_stats()
    fig.canvas.draw_idle()

def set_randomize(val):
    global is_paused, speed_label
    is_paused = True
    speed_label = "Paused"
    apply_random_distribution()
    im.set_array(grid)
    update_stats()
    fig.canvas.draw_idle()

btns[0].on_clicked(set_pause)
btns[1].on_clicked(set_play)
btns[2].on_clicked(set_step)
btns[3].on_clicked(set_randomize)

update_stats()
ani = animation.FuncAnimation(fig, update, interval = 3, blit = True)
plt.show()
