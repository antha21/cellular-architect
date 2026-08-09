import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Button
from scipy.signal import convolve2d

# CONSTANTS & SETTINGS
GW, GH = 160, 100

COLORS = ['#0e0500', '#00d2ff']
LABELS = ['Dead', 'Alive']
cmap = ListedColormap(COLORS)

# STATE MATRICES
grid = np.zeros((GH, GW), dtype=np.uint8)
age = np.zeros((GH, GW), dtype=np.uint16)
gen_n = 0
is_paused = True
speed_label = "Paused"

def apply_random_distribution():
    global grid, age, gen_n
    grid = np.random.choice([0, 1], size=(GH, GW), p=[0.67, 0.33]).astype(np.uint8)
    age.fill(0)
    gen_n = 0

# Match initial exact randomizer distribution
apply_random_distribution()

# THE UI SETUP
fig = plt.figure(figsize=(13, 7.5))
fig.canvas.manager.set_window_title('Cellular Architect - Life')
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
y_step = 0.07

for i in range(len(LABELS)):
    y_pos = y_start - i * y_step
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
    
    for i in range(len(LABELS)):
        stats_texts[i].set_text(f"{LABELS[i]}: {counts[i]}")

# CORE SIMULATION LOGIC
def step_sim():
    global grid, age, gen_n
    
    # 8-Way Moore calculations mapped via matrix convolution with toroidal wrapping
    kernel8 = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    neighbors = convolve2d(grid, kernel8, mode='same', boundary='wrap')
    
    next_grid = np.zeros_like(grid)
    
    # B3 / S23 Rules (Conway's Game of Life)
    alive_mask = (grid == 1)
    dead_mask = (grid == 0)
    
    next_grid[alive_mask & ((neighbors == 2) | (neighbors == 3))] = 1
    next_grid[dead_mask & (neighbors == 3)] = 1
    
    age[(grid == 1) & (next_grid == 1)] += 1
    age[next_grid == 0] = 0
    
    grid = next_grid
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
