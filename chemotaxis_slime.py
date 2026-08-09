import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Button
from scipy.signal import convolve2d

# --- CONSTANTS & SETTINGS ---
GW, GH = 160, 100
SA = np.pi * 0.42
SD = 4.5
SDEPO = 6
SDECAY = 0.982
STURN = 0.32
N_AGENTS = 450

COLORS = ['#0e0500', '#20dc82', '#ffb414', '#6e6964']
LABELS = ['Empty', 'Food', 'Trail', 'Wall']
cmap = ListedColormap(COLORS)

# --- STATE MATRICES ---
grid = np.zeros((GH, GW), dtype=np.uint8)
phero = np.zeros((GH, GW), dtype=np.float32)
nrg = np.zeros((GH, GW), dtype=np.float32)
agents = np.zeros((N_AGENTS, 3))  # [x, y, angle]

gen_n = 0
is_paused = True
speed_label = "Paused"

def apply_random_distribution():
    global grid, phero, nrg, agents, gen_n
    grid.fill(0)
    phero.fill(0)
    nrg.fill(0)
    gen_n = 0
    
    # Build Food Clusters
    for _ in range(7):
        fx = np.random.randint(8, GW - 8)
        fy = np.random.randint(8, GH - 8)
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                if dx * dx + dy * dy < 16:
                    nx, ny = fx + dx, fy + dy
                    if 0 <= nx < GW and 0 <= ny < GH:
                        grid[ny, nx] = 1
                        nrg[ny, nx] = 100
                        
    # Build Walls
    for _ in range(4):
        wx = np.random.randint(5, GW - 20)
        wy = np.random.randint(5, GH - 5)
        wl = np.random.randint(8, 24)
        for j in range(wl):
            px = wx + j
            if px < GW:
                grid[wy, px] = 3
                
    # Initialize Slime Agents
    agents[:, 0] = GW / 2 + (np.random.rand(N_AGENTS) - 0.5) * 22
    agents[:, 1] = GH / 2 + (np.random.rand(N_AGENTS) - 0.5) * 22
    agents[:, 2] = np.random.rand(N_AGENTS) * 2 * np.pi

apply_random_distribution()

# --- UI SETUP ---
fig = plt.figure(figsize=(13, 7.5))
fig.canvas.manager.set_window_title('Cellular Architect - Slime')
fig.patch.set_facecolor('#04080f')

ax = fig.add_axes([0.05, 0.15, 0.7, 0.8])
ax.set_axis_off()

im = ax.imshow(grid, cmap=cmap, vmin=0, vmax=len(COLORS)-1, animated=True)
agent_scatter = ax.scatter([], [], s=4, c='yellow', alpha=0.75, animated=True, zorder=2)

# --- CUSTOM STATS & LEGEND PANEL ---
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

# --- CORE SIMULATION LOGIC ---
def sense_pheromone(angles):
    sx = np.round(agents[:, 0] + np.cos(angles) * SD).astype(int)
    sy = np.round(agents[:, 1] + np.sin(angles) * SD).astype(int)
    
    valid = (sx >= 0) & (sx < GW) & (sy >= 0) & (sy < GH)
    
    vals = np.zeros(N_AGENTS)
    vsx, vsy = sx[valid], sy[valid]
    
    if len(vsx) > 0:
        p_vals = phero[vsy, vsx]
        f_vals = np.where(grid[vsy, vsx] == 1, 120, 0)
        vals[valid] = p_vals + f_vals
        
    return vals

def step_sim():
    global grid, phero, nrg, agents, gen_n
    
    # 1. Diffuse and Decay Pheromones
    mask = (grid != 3).astype(float)
    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    valid_counts = convolve2d(mask, kernel, mode='same', boundary='fill', fillvalue=0)
    phero_sum = convolve2d(phero * mask, kernel, mode='same', boundary='fill', fillvalue=0)
    
    phero = np.where(valid_counts > 0, (phero_sum / valid_counts) * SDECAY, phero * SDECAY)
    phero[grid == 3] = 0 
    
    # 2. Agent Movement Physics
    sL = sense_pheromone(agents[:, 2] - SA)
    sC = sense_pheromone(agents[:, 2])
    sR = sense_pheromone(agents[:, 2] + SA)
    
    turnMod = 0.08
    rnd_turn = np.random.rand(N_AGENTS) * turnMod
    
    c_straight = (sC > sL) & (sC > sR)
    c_left = (~c_straight) & (sL > sR)
    c_right = (~c_straight) & (~c_left) & (sR > sL)
    c_rand = (~c_straight) & (~c_left) & (~c_right)
    
    agents[c_left, 2] -= STURN + rnd_turn[c_left]
    agents[c_right, 2] += STURN + rnd_turn[c_right]
    agents[c_rand, 2] += (np.random.rand(np.sum(c_rand)) - 0.5) * 0.5
    
    agents[:, 0] += np.cos(agents[:, 2]) * 1.4
    agents[:, 1] += np.sin(agents[:, 2]) * 1.4
    
    # 3. Canvas Boudary Collisions
    out_x_low = agents[:, 0] < 0
    agents[out_x_low, 0] = 0
    agents[out_x_low, 2] = np.pi - agents[out_x_low, 2]
    
    out_x_high = agents[:, 0] >= GW
    agents[out_x_high, 0] = GW - 1
    agents[out_x_high, 2] = np.pi - agents[out_x_high, 2]
    
    out_y_low = agents[:, 1] < 0
    agents[out_y_low, 1] = 0
    agents[out_y_low, 2] = -agents[out_y_low, 2]
    
    out_y_high = agents[:, 1] >= GH
    agents[out_y_high, 1] = GH - 1
    agents[out_y_high, 2] = -agents[out_y_high, 2]
    
    ax_int = agents[:, 0].astype(int)
    ay_int = agents[:, 1].astype(int)
    
    # 4. Wall Collisions
    wall_mask = grid[ay_int, ax_int] == 3
    agents[wall_mask, 2] += np.pi
    agents[wall_mask, 0] += np.cos(agents[wall_mask, 2]) * 2
    agents[wall_mask, 1] += np.sin(agents[wall_mask, 2]) * 2
    
    ax_int = agents[:, 0].astype(int)
    ay_int = agents[:, 1].astype(int)
    
    # 5. Food Consumption
    food_mask = grid[ay_int, ax_int] == 1
    if np.any(food_mask):
        fy, fx = ay_int[food_mask], ax_int[food_mask]
        np.add.at(nrg, (fy, fx), -0.25)
        depleted = (nrg <= 0) & (grid == 1)
        grid[depleted] = 0
        
    # 6. Pheromone Deposition
    np.add.at(phero, (ay_int, ax_int), SDEPO)
    np.clip(phero, 0, 255, out=phero)
    
    # 7. Update Grid States
    updatable = (grid != 1) & (grid != 3)
    grid[updatable] = np.where(phero[updatable] > 4, 2, 0)
    
    gen_n += 1

def update(frame):
    if not is_paused:
        step_sim()

    im.set_array(grid)
    agent_scatter.set_offsets(agents[:, :2])
    update_stats()
    return [im, agent_scatter, speed_text, gen_text, pop_text] + list(stats_texts.values())

# --- PLAYBACK CONTROLS ---
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
    agent_scatter.set_offsets(agents[:, :2])
    update_stats()
    fig.canvas.draw_idle()

def set_randomize(val):
    global is_paused, speed_label
    is_paused = True
    speed_label = "Paused"
    apply_random_distribution()
    im.set_array(grid)
    agent_scatter.set_offsets(agents[:, :2])
    update_stats()
    fig.canvas.draw_idle()

btns[0].on_clicked(set_pause)
btns[1].on_clicked(set_play)
btns[2].on_clicked(set_step)
btns[3].on_clicked(set_randomize)

update_stats()
ani = animation.FuncAnimation(fig, update, interval = 3, blit = True)
plt.show()