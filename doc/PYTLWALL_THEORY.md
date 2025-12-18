---
title: PyTlWall theory
---

# PyTlWall theory

This page summarizes the theoretical model implemented in **PyTlWall/TLwall** for computing resistive-wall beam coupling impedance in **multilayer** vacuum chambers, and collects the key assumptions and validity limits discussed in the original TLwall internal presentation (HSC, 2021). fileciteturn1file0

## Background

The TLwall approach builds on the **transmission-line (TL)** analogy for layered media (planar case), extended to circular chambers through a controlled approximation, and on the **inductive bypass** concept introduced by **L. Vos** for the transverse impedance in the resistive-wall problem.

A main goal is to provide a **fast and robust** way to compute:
- longitudinal impedance,
- transverse (dipolar / quadrupolar) impedance,
- equivalent multilayer **surface impedance**,

for **PEC / vacuum / material** boundary conditions, with optional extension to non-ultrarelativistic beams.

## Multilayer wall as a recursive transmission line

### Physical model

A round chamber of radius *b* is loaded by a stack of layers (conductors/dielectrics) and terminated by a boundary condition (PEC, vacuum, or material half-space). Each layer is represented by a TL segment with its own propagation constant and characteristic impedance.

The TL equations can be applied **recursively** to any number of layers to obtain the **equivalent surface impedance** seen at the vacuum–wall interface.

> Practical note: in PyTlWall the same equivalent surface impedance can then be mapped to non-circular cross-sections using **Yokoya form factors** (rectangular/elliptical approximations).

### Equivalent surface impedance

The computation returns an equivalent surface impedance \(Z_s(\omega)\) of the full multilayer stack.
This is then used through the **Leontovich boundary condition** to relate tangential electric and magnetic fields at the interface, and to compute the beam coupling impedance.

## Applicability and TLwall hypothesis

Transmission-line equations are exact for **planar geometries**. In circular structures they remain usable when the **attenuation of cylindrical waves** inside the wall can be neglected, so that the equivalent surface impedance is effectively independent of the incident-wave direction.

A commonly used sufficient condition is:

- **skin depth** \(\delta \ll b\)

The TLwall implementation also estimates a **maximum frequency** up to which the TL approximation is expected to remain accurate for a given configuration.

## Transverse impedance and the inductive bypass (Vos)

For the transverse impedance, TLwall uses the **inductive bypass** concept (Vos formalism), which introduces an additional inductive contribution (often denoted \(L_1\)) to capture the transverse coupling consistently within the TL approach.

In the ultrarelativistic limit, a common constant appearing in the formalism is:

\[
L_1 = rac{\mu_0}{4\pi}
\]

The method is extended in the code to cover the **non-ultrarelativistic** regime with improved approximations for the field radial dependence and related corrections.

## Benchmarks and reference solutions

TLwall has been benchmarked against **ReWall** and **IW2D**.

- **IW2D** should be regarded as the reference when the highest fidelity is needed, because it solves Maxwell equations without the TL approximation.
- TLwall typically agrees well in practical cases; for some parameter sets, the validity is restricted to a limited frequency range (as per the TLwall hypothesis).

## When TLwall is convenient

Typical cases where TLwall is particularly attractive:

- building an impedance model from an aperture model (many elements → many evaluations),
- very large number of layers (e.g. metamaterial-like stacks),
- avoiding numerical difficulties that can arise in other methods,
- simulating ideal boundary conditions or very low resistivity,
- using the computed surface impedance as an input to more complex calculations,
- including roughness effects through simple surface-impedance modifications (basic Hammerstad model included in the referenced slides).


</details>

## References mentioned in the slides

- L. Vos, resistive wall impedance calculations (CERN-AB-2003-093).
- IW2D (field-matching technique) as reference solver.
- “Resistive wall impedance in elliptical multilayer vacuum chambers”, *Phys. Rev. Accel. Beams* 22, 121001 (2019).
