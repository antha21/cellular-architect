import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button

# --- CONSTANTS & SETTINGS ---
COLORS = ['#ffb414', '#00c8ff', '#82828c', '#ff6400', '#464650', '#a0f0ff', '#b4b4be', '#ff321e', '#f0f0fa']
LABELS = ['Sand', 'Water', 'Stone', 'Fire', 'Oil', 'Ice', 'Smoke', 'Lava', 'Steam']

TOTAL_STEPS = 500
time_arr = np.arange(TOTAL_STEPS)
pop_data = np.zeros((len(LABELS), TOTAL_STEPS))

# --- GENERATE RANDOMIZED POPULATION DATA ---
# Set initial states
pop_data[0, 0] = 3500  # Sand
pop_data[1, 0] = 2000  # Water
pop_data[2, 0] = 1200  # Stone
pop_data[4, 0] = 800   # Oil
pop_data[5, 0] = 500   # Ice
pop_data[7, 0] = 900   # Lava

for t in range(1, TOTAL_STEPS):
    # Apply baseline random walk to all materials
    for i in range(len(LABELS)):
        pop_data[i, t] = pop_data[i, t-1] + np.random.normal(0, 10)
    
    # 1. Fire Ignition & Decay
    if np.random.rand() < 0.03:  # 3% chance of sudden fire burst
        pop_data[3, t] += np.random.randint(150, 400)
    
    fire_decay = pop_data[3, t-1] * 0.15
    pop_data[3, t] -= fire_decay
    pop_data[6, t] += fire_decay * 0.85  # Fire converts to Smoke
    
    # 2. Smoke Dissipation
    pop_data[6, t] -= pop_data[6, t-1] * 0.08
    
    # 3. Lava Cooling into Stone
    lava_cool = pop_data[7, t-1] * 0.008
    pop_data[7, t] -= lava_cool
    pop_data[2, t] += lava_cool
    
    # 4. Thermodynamic Phase Change (Lava + Water = Steam)
    if pop_data[7, t] > 0 and pop_data[1, t] > 0:
        steam_gen = min(pop_data[7, t], pop_data[1, t]) * 0.015
        pop_data[1, t] -= steam_gen
        pop_data[8, t] += steam_gen
        
    # 5. Steam Condensation/Dissipation
    pop_data[8, t] -= pop_data[8, t-1] * 0.12
    
    # Prevent negative populations
    pop_data[:, t] = np.maximum(pop_data[:, t], 0)

# --- UI SETUP ---
fig = plt.figure(figsize=(13, 7.5))
fig.canvas.manager.set_window_title('Cellular Architect - Falling Sand Population')
fig.patch.set_facecolor('#04080f')

ax = fig.add_axes([0.08, 0.18, 0.65, 0.75])
ax.set_facecolor('#08101c')
ax.tick_params(colors='#e0f2fe')
for spine in ax.spines.values():
    spine.set_color('#00d2ff')
    spine.set_alpha(0.3)

ax.set_xlim(0, 100)
ax.set_ylim(0, np.max(pop_data) * 1.05)
ax.set_xlabel('Generations', color='#00d2ff', fontweight='bold', labelpad=10)
ax.set_ylabel('Cell Count', color='#00d2ff', fontweight='bold', labelpad=10)
ax.grid(color='#00d2ff', alpha=0.08, linestyle='--')

lines = []
for i in range(len(LABELS)):
    line, = ax.plot([], [], color=COLORS[i], linewidth=2.5, label=LABELS[i])
    lines.append(line)

# --- CUSTOM STATS & LEGEND PANEL ---
stats_ax = fig.add_axes([0.78, 0.18, 0.2, 0.75])
stats_ax.set_axis_off()

gen_text = stats_ax.text(0, 0.95, "GEN: 0", color='#00d2ff', fontfamily='monospace', fontsize=12, fontweight='bold')
pop_text = stats_ax.text(0, 0.88, "TOTAL: 0", color='#e0f2fe', fontfamily='monospace', fontsize=11)

stats_texts = {}
y_start = 0.78
y_step = 0.07

for i in range(len(LABELS)):
    y_pos = y_start - i * y_step
    rect = plt.Rectangle((0, y_pos - 0.015), 0.06, 0.035, color=COLORS[i], transform=stats_ax.transAxes)
    stats_ax.add_patch(rect)
    txt = stats_ax.text(0.10, y_pos, f"{LABELS[i]}: 0", color='#e0f2fe', fontfamily='monospace', fontsize=11, va='center')
    stats_texts[i] = txt

# --- ANIMATION & CONTROLS ---
gen_n = 0
is_paused = True

def update(frame):
    global gen_n
    if not is_paused and gen_n < TOTAL_STEPS - 1:
        gen_n += 1
        
        # Auto-scroll X axis
        if gen_n > ax.get_xlim()[1] * 0.9:
            ax.set_xlim(0, ax.get_xlim()[1] + 100)
            fig.canvas.draw_idle()

    # Update line data up to current gen
    for i in range(len(LABELS)):
        lines[i].set_data(time_arr[:gen_n+1], pop_data[i, :gen_n+1])
        stats_texts[i].set_text(f"{LABELS[i]}: {int(pop_data[i, gen_n])}")
        
    gen_text.set_text(f"GEN: {gen_n}")
    pop_text.set_text(f"TOTAL: {int(np.sum(pop_data[:, gen_n]))}")
    
    return lines + [gen_text, pop_text] + list(stats_texts.values())

btn_labels = ['Pause', 'Play', 'Reset']
btn_axs = [fig.add_axes([0.15 + i * 0.17, 0.05, 0.12, 0.05]) for i in range(3)]
btns = [Button(ax, label, color='#0d1829', hovercolor='#00d2ff') for ax, label in zip(btn_axs, btn_labels)]

for b in btns: 
    b.label.set_color('white')
    b.label.set_fontsize(10)
    b.label.set_fontweight('bold')

def set_pause(val): 
    global is_paused
    is_paused = True

def set_play(val):
    global is_paused
    is_paused = False

def set_reset(val):
    global gen_n, is_paused
    is_paused = True
    gen_n = 0
    ax.set_xlim(0, 100)
    for i in range(len(LABELS)):
        lines[i].set_data([], [])
    fig.canvas.draw_idle()

btns[0].on_clicked(set_pause)
btns[1].on_clicked(set_play)
btns[2].on_clicked(set_reset)

ani = animation.FuncAnimation(fig, update, interval=30, blit=False)
plt.show()