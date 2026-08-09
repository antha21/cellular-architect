import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Button
from scipy.signal import convolve2d

# CONSTANTS & SETTINGS
GW, GH = 160, 100
FP = {
    'spread': 0.42,
    'grow': 0.002,
    'lightning': 0.000022
}

COLORS = ['#140f0a', '#20dc82', '#05aa73', '#04825a', '#c86414', '#ff6400', '#ff1e1e', '#00c8ff', '#6e6964']
LABELS = ['Bare', 'Sapling', 'Bush', 'Tree', 'DryTree', 'Fire', 'Ember', 'Water', 'Firebrk']
cmap = ListedColormap(COLORS)

DELTAS4 = ((0, -1), (0, 1), (-1, 0), (1, 0))

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
        if r < 0.28:
            grid[y, x] = 3
        elif r < 0.40:
            grid[y, x] = 2
        elif r < 0.46:
            grid[y, x] = 1
        elif r < 0.52:
            grid[y, x] = 4
        elif r < 0.57:
            grid[y, x] = 7

    # Center ignition point
    fx, fy = np.random.randint(GW//3, 2*GW//3), np.random.randint(GH//3, 2*GH//3)
    grid[fy, fx] = 5
    nrg[fy, fx] = 6

apply_random_distribution()

# THE UI SETUP
fig = plt.figure(figsize=(13, 7.5))
fig.canvas.manager.set_window_title('Cellular Architect - Wildfire')
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
    
    # 8-Way Moore calculations mapping matrix convolution
    kernel8 = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    fire_n = convolve2d((grid == 5).astype(float), kernel8, mode='same', boundary='wrap')
    ember_n = convolve2d((grid == 6).astype(float), kernel8, mode='same', boundary='wrap')
    water_n = convolve2d((grid == 7).astype(float), kernel8, mode='same', boundary='wrap')
    
    rand_matrix = np.random.rand(GH, GW)
    
    # Age increment
    age[(grid == 1) | (grid == 2) | (grid == 3)] += 1
    
    # RULE: BARE
    grow_mask = (grid == 0) & (rand_matrix < FP['grow'])
    next_grid[grow_mask] = 1
    
    # RULE: SAPLING
    sap_mask = (grid == 1)
    ignite_sap = sap_mask & (fire_n > 0) & (rand_matrix < FP['spread'])
    next_grid[ignite_sap] = 5
    next_nrg[ignite_sap] = 6
    
    mature_sap = sap_mask & (~ignite_sap) & (age > 55) & (np.random.rand(GH, GW) < 0.012)
    next_grid[mature_sap] = 2
    age[mature_sap] = 0
    
    # RULE: BUSH & TREE COMMON IGNITION
    bush_tree = (grid == 2) | (grid == 3)
    nearFire = fire_n + ember_n * 0.5
    ignite_bt = bush_tree & (nearFire > 0) & (rand_matrix < (FP['spread'] * nearFire))
    next_grid[ignite_bt] = 5
    next_nrg[ignite_bt] = 6
    
    # RULE: BUSH
    bush_mask = (grid == 2) & (~ignite_bt)
    spread_bush = bush_mask & (np.random.rand(GH, GW) < FP['grow'] * 0.8)
    for y, x in zip(*np.where(spread_bush)):
        ns4 = [(x+dx, y+dy) for dx, dy in DELTAS4 if 0 <= x+dx < GW and 0 <= y+dy < GH and next_grid[y+dy, x+dx] == 0]
        if ns4:
            nx, ny = ns4[np.random.randint(len(ns4))]
            next_grid[ny, nx] = 2
            
    mature_bush = bush_mask & (age > 200) & (np.random.rand(GH, GW) < 0.004)
    next_grid[mature_bush] = 3
    age[mature_bush] = 0
    
    # RULE: TREE
    tree_mask = (grid == 3) & (~ignite_bt)
    spread_tree = tree_mask & (np.random.rand(GH, GW) < FP['grow'] * 0.3)
    for y, x in zip(*np.where(spread_tree)):
        ns4 = [(x+dx, y+dy) for dx, dy in DELTAS4 if 0 <= x+dx < GW and 0 <= y+dy < GH and next_grid[y+dy, x+dx] == 0]
        if ns4:
            nx, ny = ns4[np.random.randint(len(ns4))]
            next_grid[ny, nx] = 1
            
    dry_tree = tree_mask & (water_n == 0) & (np.random.rand(GH, GW) < FP['grow'] * 0.22)
    next_grid[dry_tree] = 4
    
    lightning_tree = tree_mask & (~dry_tree) & (np.random.rand(GH, GW) < FP['lightning'])
    next_grid[lightning_tree] = 5
    next_nrg[lightning_tree] = 6
    
    # RULE: DRY TREE
    dry_mask = (grid == 4)
    dryNearFire = fire_n + ember_n
    dryIgnite = min(FP['spread'] * 2.8, 0.97)
    
    ignite_dry = dry_mask & (dryNearFire > 0) & (rand_matrix < dryIgnite)
    next_grid[ignite_dry] = 5
    next_nrg[ignite_dry] = 6
    
    lightning_dry = dry_mask & (~ignite_dry) & (np.random.rand(GH, GW) < FP['lightning'] * 4)
    next_grid[lightning_dry] = 5
    next_nrg[lightning_dry] = 6
    
    # RULE: FIRE
    fire_mask = (grid == 5)
    next_nrg[fire_mask] -= 1
    die_fire = fire_mask & (next_nrg <= 0)
    next_grid[die_fire] = 6
    next_nrg[die_fire] = 4
    
    # RULE: EMBER
    ember_mask = (grid == 6)
    next_nrg[ember_mask] -= 1
    die_ember = ember_mask & (next_nrg <= 0)
    next_grid[die_ember] = 0
    
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