# Cellular Architect

A collection of discrete localized mathematical rules mapped into spatial matrices. This repository contains self-contained Python simulation engines for various cellular automata and complex systems.

## Mathematical Architecture

These simulations map continuous Partial and Ordinary Differential Equations into discrete spatial arrays to guarantee thermodynamic conservation and logical transitions.

### Ecosystem Dynamics
Predator-prey interactions form non-linear harmonic oscillators via Lotka-Volterra equations:
$$ (\frac{dx}{dt} = \alpha x - \beta xy \quad \quad \frac{dy}{dt} = \delta xy - \gamma y )$$
Floating-point arrays hold mass across discrete grid movements to guarantee conservation of energy.

### Epidemic Spread
Standard SIR compartmental epidemiology mapped to Moore neighborhood probabilities:
$$ \frac{dS}{dt} = -\frac{\beta I S}{N} \quad \quad \frac{dI}{dt} = \frac{\beta I S}{N} - \gamma I \quad \quad \frac{dR}{dt} = \gamma I $$
The infection probability and recovery rate variables directly drive localized cellular state transitions.

### Wildfire Percolation
Drossel-Schwabl forest fire model predicting self-organized criticality (SOC):
$$ P(\text{Tree} \to \text{Fire}) \propto N_{\text{Fire}} $$
A statistical balance between fractional tree growth and rapid ignition events pushes the grid to a constant critical state.

### Cellular Automata
Conway's Game of Life utilizing pure, discrete Boolean logic:
$$ C_{t+1} = \begin{cases} 1 & \text{if } N \in B \lor (C_t=1 \land N \in S) \\ 0 & \text{otherwise} \end{cases} $$
Calculates surviving or born cells strictly based on their total neighboring matrix sum.

### Chemotaxis Diffusion (Slime)
Calculates pheromone diffusion via Stochastic Partial Differential approximations:
$$ \frac{\partial p}{\partial t} = D \nabla^2 p - f(p) + E $$
Independent agents continuously sample the spatial grid gradient to optimize geographic routing.

### Falling Sand Physics
Gravity sorting combined with fluid state transitions driven by thermal exchange:
$$ \Delta Q = m \cdot c \cdot \Delta T $$
Calculates downward displacement vectors for mass gravity, overriding states if localized heat thresholds force a phase shift.
