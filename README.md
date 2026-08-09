# Cellular Architect

**Author:** Anthony Artino

## Project Overview

This is a collection of high-performance simulation engines that map out continuous Ordinary Differential Equations (ODESs) and Partial Differential Equations (PDEs) into discrete spatial matrices. This repository contains standalone Python scripts for various cellular automata and complex systems, utilizing `numpy` for matrix calculations and `matplotlib` for rendering.

### Ecosystem Dynamics (`ecosystem_lv.py`)

* This simulates a complete trophic web as it precisely demonstrates energy flow all across multiple levels.
* **Mathematics:** Predator-prey interactions form non-linear harmonic oscillators via localized Lotka-Volterra equations:

$$\frac{dx}{dt}=\alpha x-\beta xy \quad \quad \frac{dy}{dt}=\delta xy-\gamma y$$

To guarantee thermodynamic conservation of energy throughout the spatial ecosystem, floating-point arrays hold mass across discrete grid movements rather than relying purely on state toggles.

### Epidemic Spread (`disease_sir.py`)
* This models the spread and containment of a pathogen throughout a mobile population, tracking exposures, infections, recoveries, and immunities.
* **Mathematics:** Standard SIR compartmental epidemiology is mapped to 5x5 Moore neighborhood probabilities:

$$\frac{dS}{dt}=-\frac{\beta I S}{N} \quad \quad \frac{dI}{dt}=\frac{\beta I S}{N}-\gamma I \quad \quad \frac{dR}{dt}=\gamma I$$

The $\beta$ (infection probability) and $\gamma$ (recovery rate) variables directly drive localized cellular state transitions based on the density of infected neighbors.

### Wildfire Percolation (`wildfire_percolation.py`)
* This simulates the ignition, spread, and regrowth cycles of a forest as it factors in age maturity, dry states, as well as spontaneous lightning strikes.
* **Mathematics:** Driven by the Drossel-Schwabl forest fire model predicting self-organized criticality (SOC):

$$P(\text{Tree} \to \text{Fire}) \propto N_{\text{Fire}}$$

A delicate statistical balance between fractional tree growth and rapid ignition events pushes the grid to a constant critical state.

### Cellular Automata (`conway_life.py`)
* This is a pure implementation of Conway's Game of Life as it demonstrates how complex structures emerge from simple localized rules.
* **Mathematics:** Utilizes pure, discrete Boolean logic without continuous derivatives:

$$C_{t+1}=\begin{cases}1&\text{if }N \in B \lor (C_t=1 \land N \in S)\\\\0&\text{otherwise}\end{cases}$$

Calculates surviving ($S$) or born ($B$) cells strictly based on their total neighboring matrix sum ($N$).

### Chemotaxis & Slime Mold (`chemotaxis_slime.py`)
* This simulates the *Physarum polycephalum* also known as slime mold which self-organizes into minimum Steiner trees to solve spatial graph routing problems between food sources.
* **Mathematics:** Calculates pheromone diffusion via Stochastic Partial Differential approximations:

$$\frac{\partial p}{\partial t}=D\nabla^2 p-f(p)+E$$

Independent agents continuously sample the spatial grid gradient $\nabla p$ to optimize geographic routing and dynamically alter their trajectory vectors.

### Falling Sand Physics (`sand_thermo.py`)
* This is a gravity and thermodynamics engine thar features fluid dynamics, mass displacement, and phase transitions.
* **Mathematics:** Gravity sorting is combined with fluid state transitions driven by thermal exchange:

$$\Delta Q=m \cdot c \cdot \Delta T$$

Calculates downward displacement vectors for mass gravity, overriding physical states if localized heat thresholds force a phase shift.

---

## The Open Sandbox Simulation

Want to interact with these systems directly, mix cell types, and trigger environmental disasters? 

Then check out the full interactive open sandbox experience of Cellular Architect where you can rule the grid. 

**[Link to Live Project Website]** [Cellular Architect](https://anthony-artino-portfolio.netlify.app/projects/games/cellular_architect/cellular_architect)

**Main Features in the HTML Sandbox:**
*   **Live Drawing Tools:** Draw, erase, and paint materials dynamically while the simulations are running.
*   **Display Lenses:** Toggle overlay lenses to visualize the hidden floating-point mechanics, including the *Energy Heatmap* and *Age Map*.
*   **Live Parameters:** Tweak variables like infection rates, animal breeding chances, and wildfire spread probabilities in real-time.
*   **Research Tree:** Earn points by hitting specific threshold achievements to physically mutate and alter the simulation math.
