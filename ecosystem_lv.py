import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Button

# CONSTANTS & SETTINGS
GW, GH = 160, 100
EP = {
    'grassGrow': 0.016,
    'plantE': 20,
    'breedE': 38,
    'foxBreed': 60,
    'wolfBreed': 80,
    'breedChance': 0.28
}

COLORS = ['#0e0500', '#20dc82', '#05aa73', '#04825a', '#00c8ff', '#646978', '#fff5dc', '#ff7800', '#ff3232']
LABELS = ['Empty', 'Grass', 'Bush', 'Tree', 'Water', 'Rock', 'Rabbit', 'Fox', 'Wolf']
cmap = ListedColormap(COLORS)

# Pre-allocated tuples for faster neighbor math
DELTAS8 = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))
DELTAS4 = ((0, -1), (0, 1), (-1, 0), (1, 0))

# STATE MATRICES
grid = np.zeros((GH, GW), dtype=np.uint8)
nrg = np.zeros((GH, GW), dtype=np.float32)
age = np.zeros((GH, GW), dtype=np.uint16)
gen_n = 0
is_paused = True
speed_label = "Paused"

def apply_random_distribution():
    global grid, nrg, age
    grid.fill(0)
    nrg.fill(0)
    age.fill(0)
    for i in range(GW * GH):
        y, x = divmod(i, GW)
        r = np.random.rand()
        if r < 0.30:
            grid[y, x] = 1
        elif r < 0.37:
            grid[y, x] = 2
        elif r < 0.40:
            grid[y, x] = 3
        elif r < 0.46:
            grid[y, x] = 4
        elif r < 0.49:
            grid[y, x] = 5
        elif r < 0.54:
            grid[y, x] = 6
            nrg[y, x] = 65
        elif r < 0.565:
            grid[y, x] = 7
            nrg[y, x] = 80
        elif r < 0.572:
            grid[y, x] = 8
            nrg[y, x] = 90
# Match initial exact randomizer distribution
apply_random_distribution()

# THE UI SETUP
fig = plt.figure(figsize=(13, 7.5))
fig.canvas.manager.set_window_title('Cellular Architect - Ecosystem')
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
def step_animal(x, y, i, a_type, prey, bE, fE, eCost, bChance, next_grid, next_nrg, moved, ns8):
    e = nrg[y, x] - (eCost * 0.1)
    
    if e <= 0:
        next_grid[y, x] = 0
        next_nrg[y, x] = 0
        moved[i] = True
        return
        
    prey_n = [(nx, ny) for nx, ny in ns8 if grid[ny, nx] in prey]
    
    if prey_n and np.random.rand() < 0.72:
        nx, ny = prey_n[np.random.randint(len(prey_n))]
        ni = ny * GW + nx
        next_grid[ny, nx] = a_type
        next_nrg[ny, nx] = min(120, e + fE)
        next_grid[y, x] = 0
        next_nrg[y, x] = 0
        moved[ni] = True
        moved[i] = True
        return
        
    empty_n = [(nx, ny) for nx, ny in ns8 if grid[ny, nx] == 0]
    
    if empty_n and np.random.rand() < 0.6:
        nx, ny = empty_n[np.random.randint(len(empty_n))]
        ni = ny * GW + nx
        if e >= bE and np.random.rand() < bChance:
            next_grid[ny, nx] = a_type
            next_nrg[ny, nx] = e * 0.5
            next_nrg[y, x] = e * 0.5
            moved[ni] = True
        else:
            next_grid[ny, nx] = a_type
            next_nrg[ny, nx] = e
            next_grid[y, x] = 0
            next_grid[y, x] = 0
            moved[ni] = True
            moved[i] = True
    else:
        next_nrg[y, x] = e

def step_sim():
    global grid, nrg, age, gen_n
    
    next_grid = grid.copy()
    next_nrg = nrg.copy()
    moved = np.zeros(GW * GH, dtype=bool)
    
    active_indices = np.flatnonzero(grid)
    np.random.shuffle(active_indices)
    
    for i in active_indices:
        if moved[i]: 
            continue
            
        y, x = divmod(i, GW)
        t = grid[y, x]
            
        if age[y, x] < 65535:
            age[y, x] += 1
            
        ns8 = [(x+dx, y+dy) for dx, dy in DELTAS8 if 0 <= x+dx < GW and 0 <= y+dy < GH]
        
        if t == 1:
            empty_n = [(nx, ny) for nx, ny in ns8 if grid[ny, nx] == 0]
            if empty_n and np.random.rand() < EP['grassGrow']:
                nx, ny = empty_n[np.random.randint(len(empty_n))]
                next_grid[ny, nx] = 1
                next_nrg[ny, nx] = 10
            if age[y, x] > 280 and np.random.rand() < 0.0018:
                next_grid[y, x] = 2 
                next_nrg[y, x] = 35
                age[y, x] = 0
                
        elif t == 2:
            empty_n = [(nx, ny) for nx, ny in ns8 if grid[ny, nx] == 0]
            if empty_n and np.random.rand() < (EP['grassGrow'] * 0.4):
                nx, ny = empty_n[np.random.randint(len(empty_n))]
                next_grid[ny, nx] = 2
                next_nrg[ny, nx] = 30
            if age[y, x] > 520 and np.random.rand() < 0.0009:
                next_grid[y, x] = 3 
                next_nrg[y, x] = 55
                age[y, x] = 0
                
        elif t == 3:
            empty_n = [(nx, ny) for nx, ny in ns8 if grid[ny, nx] == 0]
            if empty_n and np.random.rand() < (EP['grassGrow'] * 0.2):
                nx, ny = empty_n[np.random.randint(len(empty_n))]
                next_grid[ny, nx] = 1
                next_nrg[ny, nx] = 8
                
        elif t == 4:
            if np.random.rand() < 0.003:
                ns4 = [(x+dx, y+dy) for dx, dy in DELTAS4 if 0 <= x+dx < GW and 0 <= y+dy < GH and grid[y+dy, x+dx] == 0]
                if ns4 and np.random.rand() < 0.2:
                    nx, ny = ns4[np.random.randint(len(ns4))]
                    next_grid[ny, nx] = 4
                    
        elif t == 6:
            step_animal(x, y, i, 6, [1, 2], EP['breedE'], EP['plantE'], 7, EP['breedChance'], next_grid, next_nrg, moved, ns8)
            
        elif t == 7:
            step_animal(x, y, i, 7, [6], EP['foxBreed'], EP['plantE'] * 1.6, 4, EP['breedChance'] * 0.7, next_grid, next_nrg, moved, ns8)
            
        elif t == 8:
            step_animal(x, y, i, 8, [6, 7], EP['wolfBreed'], EP['plantE'] * 2.2, 2, EP['breedChance'] * 0.5, next_grid, next_nrg, moved, ns8)
                
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
    global is_paused, speed_label, gen_n
    is_paused = True
    speed_label = "Paused"
    gen_n = 0
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