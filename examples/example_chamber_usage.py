#!/usr/bin/env python3
"""
Example usage of the pytlwall.Chamber module

This script demonstrates how to use the Chamber class for defining
vacuum chamber geometries with different cross-sectional shapes and
calculating Yokoya correction factors for impedance calculations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytlwall
import numpy as np
import matplotlib.pyplot as plt


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def example_circular_chamber():
    """Example: Circular chamber - most common geometry."""
    print_separator()
    print("EXAMPLE 1: Circular Chamber")
    print_separator()
    
    # Create a circular chamber (typical for beam pipes)
    chamber = pytlwall.Chamber(
        pipe_rad_m=0.022,        # 22 mm radius (LHC-like)
        pipe_len_m=1.0,          # 1 meter length
        chamber_shape='CIRCULAR',
        betax=100.0,             # 100 m beta function (typical arc)
        betay=100.0,
        component_name='arc_dipole'
    )
    
    print(chamber.summary())
    
    print("\nKey properties:")
    print(f"  - Circular symmetry: hor = ver = {chamber.pipe_rad_m*1000:.1f} mm")
    print(f"  - Yokoya q parameter: {chamber.yokoya_q:.6f} (zero for circular)")
    print(f"  - All Yokoya factors = 1.0 (no geometric correction)")
    
    print("\nUse case:")
    print("  - Standard beam pipes in straight sections")
    print("  - Dipole and quadrupole magnets")
    print("  - Simplest geometry for impedance calculations")


def example_elliptical_chamber():
    """Example: Elliptical chamber - common in modern machines."""
    print_separator()
    print("EXAMPLE 2: Elliptical Chamber")
    print_separator()
    
    # Create elliptical chamber with different horizontal/vertical apertures
    chamber = pytlwall.Chamber(
        pipe_hor_m=0.030,        # 30 mm horizontal half-aperture
        pipe_ver_m=0.020,        # 20 mm vertical half-aperture
        pipe_len_m=1.0,
        chamber_shape='ELLIPTICAL',
        betax=50.0,              # Different beta functions
        betay=25.0,
        component_name='elliptical_section'
    )
    
    print(chamber.summary())
    
    print("\nAspect ratio analysis:")
    aspect_ratio = chamber.pipe_hor_m / chamber.pipe_ver_m
    print(f"  Aspect ratio (h/v):  {aspect_ratio:.2f}")
    print(f"  Yokoya q parameter:  {chamber.yokoya_q:.4f}")
    
    print("\nYokoya corrections:")
    print(f"  Longitudinal factor: {chamber.long_yokoya_factor:.4f}")
    print(f"  Horizontal driving:  {chamber.drivx_yokoya_factor:.4f}")
    print(f"  Vertical driving:    {chamber.drivy_yokoya_factor:.4f}")
    
    print("\nUse case:")
    print("  - Flat chambers in modern colliders")
    print("  - Accommodates beam separation")
    print("  - Reduces vertical aperture where beta_y is small")


def example_rectangular_chamber():
    """Example: Rectangular chamber - for special applications."""
    print_separator()
    print("EXAMPLE 3: Rectangular Chamber")
    print_separator()
    
    # Create rectangular chamber
    chamber = pytlwall.Chamber(
        pipe_hor_m=0.040,        # 40 mm horizontal half-width
        pipe_ver_m=0.015,        # 15 mm vertical half-height
        pipe_len_m=1.0,
        chamber_shape='RECTANGULAR',
        betax=30.0,
        betay=10.0,
        component_name='rectangular_section'
    )
    
    print(chamber.summary())
    
    print("\nGeometric properties:")
    print(f"  Full width:          {chamber.pipe_hor_m*2*1000:.1f} mm")
    print(f"  Full height:         {chamber.pipe_ver_m*2*1000:.1f} mm")
    print(f"  Yokoya q parameter:  {chamber.yokoya_q:.4f}")
    
    factors = chamber.get_yokoya_factors()
    print("\nAll Yokoya factors:")
    for key, value in factors.items():
        print(f"  {key:15s}: {value:8.4f}")
    
    print("\nUse case:")
    print("  - Kickers and septa")
    print("  - Special insertion devices")
    print("  - Strong geometric effects on impedance")


def example_chamber_comparison():
    """Example: Comparing different chamber geometries."""
    print_separator()
    print("EXAMPLE 4: Chamber Geometry Comparison")
    print_separator()
    
    # Define same average dimensions for all shapes
    avg_dim = 0.025  # 25 mm average aperture
    
    chambers = {
        'Circular': pytlwall.Chamber(
            pipe_rad_m=avg_dim,
            chamber_shape='CIRCULAR'
        ),
        'Elliptical (mild)': pytlwall.Chamber(
            pipe_hor_m=avg_dim * 1.2,
            pipe_ver_m=avg_dim * 0.8,
            chamber_shape='ELLIPTICAL'
        ),
        'Elliptical (flat)': pytlwall.Chamber(
            pipe_hor_m=avg_dim * 2.0,
            pipe_ver_m=avg_dim * 0.5,
            chamber_shape='ELLIPTICAL'
        ),
        'Rectangular': pytlwall.Chamber(
            pipe_hor_m=avg_dim * 1.5,
            pipe_ver_m=avg_dim * 0.67,
            chamber_shape='RECTANGULAR'
        )
    }
    
    print(f"Comparison of chamber geometries (average aperture = {avg_dim*1000:.1f} mm):")
    print(f"\n{'Geometry':<20} {'q param':>10} {'Long':>10} {'Driv_x':>10} {'Driv_y':>10}")
    print("-" * 70)
    
    for name, chamber in chambers.items():
        print(f"{name:<20} {chamber.yokoya_q:>10.4f} "
              f"{chamber.long_yokoya_factor:>10.4f} "
              f"{chamber.drivx_yokoya_factor:>10.4f} "
              f"{chamber.drivy_yokoya_factor:>10.4f}")
    
    print("\nObservations:")
    print("  - Yokoya q increases with aspect ratio (flatness)")
    print("  - Circular chamber (q=0) has no geometric corrections")
    print("  - Flat chambers have strongest corrections")
    print("  - Rectangular chambers differ from elliptical")


def example_lhc_chambers():
    """Example: Realistic LHC chamber configurations."""
    print_separator()
    print("EXAMPLE 5: LHC Chamber Examples")
    print_separator()
    
    # LHC Arc dipole
    arc_dipole = pytlwall.Chamber(
        pipe_rad_m=0.022,        # 44 mm diameter beam screen
        pipe_len_m=14.3,         # Dipole length
        chamber_shape='CIRCULAR',
        betax=180.0,             # Typical arc optics
        betay=180.0,
        component_name='MB_dipole'
    )
    
    # LHC Interaction region
    ir_chamber = pytlwall.Chamber(
        pipe_hor_m=0.021,        # 42 mm horizontal
        pipe_ver_m=0.021,        # 42 mm vertical (circular)
        pipe_len_m=4.0,
        chamber_shape='CIRCULAR',
        betax=0.55,              # IP beta* = 55 cm
        betay=0.55,
        component_name='IP1_triplet'
    )
    
    # LHC Injection region
    injection = pytlwall.Chamber(
        pipe_hor_m=0.025,        # Wider horizontal
        pipe_ver_m=0.025,
        pipe_len_m=1.0,
        chamber_shape='CIRCULAR',
        betax=70.0,
        betay=70.0,
        component_name='injection_kicker'
    )
    
    lhc_chambers = {
        'Arc Dipole': arc_dipole,
        'IR Triplet': ir_chamber,
        'Injection': injection
    }
    
    print("LHC chamber configurations:\n")
    for name, chamber in lhc_chambers.items():
        print(f"{name}:")
        print(f"  Shape: {chamber.chamber_shape}")
        print(f"  Aperture: {chamber.pipe_rad_m*1000:.1f} mm radius")
        print(f"  Length: {chamber.pipe_len_m:.1f} m")
        print(f"  Beta_x/y: {chamber.betax:.1f}/{chamber.betay:.1f} m")
        print()


def example_yokoya_factor_dependency():
    """Example: Yokoya factor dependency on aspect ratio."""
    print_separator()
    print("EXAMPLE 6: Yokoya Factors vs Aspect Ratio")
    print_separator()
    
    # Test range of aspect ratios
    aspect_ratios = np.linspace(1.0, 4.0, 50)
    base_ver = 0.020  # Fixed vertical aperture
    
    q_values = []
    long_factors = []
    drivx_factors = []
    drivy_factors = []
    
    print("Computing Yokoya factors for various aspect ratios...")
    
    for ar in aspect_ratios:
        hor = base_ver * ar
        
        # Elliptical chamber
        chamber = pytlwall.Chamber(
            pipe_hor_m=hor,
            pipe_ver_m=base_ver,
            chamber_shape='ELLIPTICAL'
        )
        
        q_values.append(chamber.yokoya_q)
        long_factors.append(chamber.long_yokoya_factor)
        drivx_factors.append(chamber.drivx_yokoya_factor)
        drivy_factors.append(chamber.drivy_yokoya_factor)
    
    # Display sample values
    print("\nSample Yokoya factors for elliptical chambers:")
    print(f"{'Aspect Ratio':>15} {'q param':>12} {'Long':>12} {'Driv_x':>12} {'Driv_y':>12}")
    print("-" * 70)
    
    for i in [0, 12, 24, 36, 49]:
        print(f"{aspect_ratios[i]:>15.2f} {q_values[i]:>12.4f} "
              f"{long_factors[i]:>12.4f} {drivx_factors[i]:>12.4f} "
              f"{drivy_factors[i]:>12.4f}")
    
    print("\nObservations:")
    print("  - Yokoya q increases with aspect ratio")
    print("  - Longitudinal factor increases (more loss)")
    print("  - Driving factors change with geometry")
    print("  - Important for accurate impedance predictions")


def example_chamber_modification():
    """Example: Modifying chamber parameters dynamically."""
    print_separator()
    print("EXAMPLE 7: Dynamic Chamber Modification")
    print_separator()
    
    # Create initial chamber
    chamber = pytlwall.Chamber(
        pipe_rad_m=0.025,
        chamber_shape='CIRCULAR',
        component_name='initial_design'
    )
    
    print("Initial design:")
    print(f"  Shape: {chamber.chamber_shape}")
    print(f"  Radius: {chamber.pipe_rad_m*1000:.1f} mm")
    print(f"  Yokoya q: {chamber.yokoya_q:.6f}")
    
    # Modify to elliptical
    print("\nModifying to elliptical chamber...")
    chamber.chamber_shape = 'ELLIPTICAL'
    chamber.pipe_hor_m = 0.035
    chamber.pipe_ver_m = 0.020
    chamber.component_name = 'optimized_design'
    
    print("Updated design:")
    print(f"  Shape: {chamber.chamber_shape}")
    print(f"  Horizontal: {chamber.pipe_hor_m*1000:.1f} mm")
    print(f"  Vertical: {chamber.pipe_ver_m*1000:.1f} mm")
    print(f"  Yokoya q: {chamber.yokoya_q:.4f}")
    print(f"  Long factor: {chamber.long_yokoya_factor:.4f}")
    
    print("\nUse case:")
    print("  - Design optimization studies")
    print("  - Parameter scans")
    print("  - Sensitivity analysis")


def example_error_handling():
    """Example: Error handling and validation."""
    print_separator()
    print("EXAMPLE 8: Error Handling and Validation")
    print_separator()
    
    print("Test 1: Invalid chamber shape")
    try:
        chamber = pytlwall.Chamber(chamber_shape='INVALID')
    except pytlwall.chamber.ChamberShapeError as e:
        print(f"  ✓ Correctly caught error: {e}")
    
    print("\nTest 2: Negative dimension")
    try:
        chamber = pytlwall.Chamber(pipe_rad_m=-0.025)
    except pytlwall.chamber.ChamberDimensionError as e:
        print(f"  ✓ Correctly caught error: {e}")
    
    print("\nTest 3: Zero dimension")
    try:
        chamber = pytlwall.Chamber(pipe_rad_m=0.0)
    except pytlwall.chamber.ChamberDimensionError as e:
        print(f"  ✓ Correctly caught error: {e}")
    
    print("\nTest 4: Invalid beta function")
    try:
        chamber = pytlwall.Chamber(betax=-10.0)
    except pytlwall.chamber.ChamberDimensionError as e:
        print(f"  ✓ Correctly caught error: {e}")
    
    print("\nTest 5: Valid chamber creation")
    try:
        chamber = pytlwall.Chamber(
            pipe_rad_m=0.025,
            chamber_shape='CIRCULAR',
            betax=100.0,
            betay=50.0
        )
        print(f"  ✓ Chamber created successfully: {chamber}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
    
    print("\nBest practices:")
    print("  - Always validate user input")
    print("  - Use try/except blocks for robust code")
    print("  - Check dimensions are positive")
    print("  - Verify chamber shape is valid")


def example_visualization():
    """Example: Visualizing chamber geometries and Yokoya factors."""
    print_separator()
    print("EXAMPLE 9: Visualizing Chamber Properties")
    print_separator()
    
    print("Creating visualization of chamber geometries and Yokoya factors...")
    
    # Create range of aspect ratios
    aspect_ratios = np.linspace(1.0, 5.0, 100)
    base_aperture = 0.020
    
    # Compute Yokoya factors for elliptical and rectangular
    q_ellipt = []
    long_ellipt = []
    drivx_ellipt = []
    
    q_rect = []
    long_rect = []
    drivx_rect = []
    
    for ar in aspect_ratios:
        # Elliptical
        chamber_e = pytlwall.Chamber(
            pipe_hor_m=base_aperture * ar,
            pipe_ver_m=base_aperture,
            chamber_shape='ELLIPTICAL'
        )
        q_ellipt.append(chamber_e.yokoya_q)
        long_ellipt.append(chamber_e.long_yokoya_factor)
        drivx_ellipt.append(chamber_e.drivx_yokoya_factor)
        
        # Rectangular
        chamber_r = pytlwall.Chamber(
            pipe_hor_m=base_aperture * ar,
            pipe_ver_m=base_aperture,
            chamber_shape='RECTANGULAR'
        )
        q_rect.append(chamber_r.yokoya_q)
        long_rect.append(chamber_r.long_yokoya_factor)
        drivx_rect.append(chamber_r.drivx_yokoya_factor)
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Yokoya q vs aspect ratio
    ax1.plot(aspect_ratios, q_ellipt, 'b-', linewidth=2, label='Elliptical')
    ax1.plot(aspect_ratios, q_rect, 'r-', linewidth=2, label='Rectangular')
    ax1.set_xlabel('Aspect Ratio (h/v)', fontsize=12)
    ax1.set_ylabel('Yokoya q Parameter', fontsize=12)
    ax1.set_title('Asymmetry Parameter vs Aspect Ratio', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(1, 5)
    
    # Plot 2: Longitudinal Yokoya factor
    ax2.plot(aspect_ratios, long_ellipt, 'b-', linewidth=2, label='Elliptical')
    ax2.plot(aspect_ratios, long_rect, 'r-', linewidth=2, label='Rectangular')
    ax2.axhline(y=1.0, color='k', linestyle='--', alpha=0.5, label='Circular (reference)')
    ax2.set_xlabel('Aspect Ratio (h/v)', fontsize=12)
    ax2.set_ylabel('Longitudinal Yokoya Factor', fontsize=12)
    ax2.set_title('Longitudinal Correction vs Aspect Ratio', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(1, 5)
    
    plt.tight_layout()
    
    # Save figure
    # Create examples/img directory if it doesn't exist
    img_dir = os.path.join('examples', 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    output_file = os.path.join(img_dir, 'chamber_yokoya_factors.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Figure saved as: {output_file}")
    
    # Show plot
    try:
        plt.show()
        print(f"✓ Plot displayed")
    except:
        print(f"  (Display not available, but file saved)")
    
    print("\nKey insights:")
    print("  - Yokoya q increases monotonically with aspect ratio")
    print("  - Elliptical and rectangular have different corrections")
    print("  - Flat chambers (high AR) have significant corrections")
    print("  - Important for accurate impedance predictions")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print(" " * 15 + "EXAMPLES OF USAGE OF THE PYTLWALL.CHAMBER MODULE")
    print("=" * 80)
    
    # Run all examples
    example_circular_chamber()
    example_elliptical_chamber()
    example_rectangular_chamber()
    example_chamber_comparison()
    example_lhc_chambers()
    example_yokoya_factor_dependency()
    example_chamber_modification()
    example_error_handling()
    example_visualization()
    
    # Final summary
    print_separator()
    print("SUMMARY")
    print_separator()
    print("The pytlwall.Chamber module allows you to:")
    print("  ✓ Define vacuum chambers with various geometries")
    print("  ✓ Calculate Yokoya correction factors automatically")
    print("  ✓ Handle circular, elliptical, and rectangular shapes")
    print("  ✓ Specify beam optics parameters (beta functions)")
    print("  ✓ Validate chamber dimensions and parameters")
    print("  ✓ Support multi-layer chamber structures")
    print("\nSupported chamber shapes:")
    print("  • CIRCULAR:     q = 0, no geometric corrections")
    print("  • ELLIPTICAL:   q > 0, smooth wall approximation")
    print("  • RECTANGULAR:  q > 0, different corrections than elliptical")
    print("\nKey concepts:")
    print("  • Yokoya factors correct impedance for non-circular geometry")
    print("  • Asymmetry parameter q quantifies chamber flatness")
    print("  • Beta functions affect transverse impedance calculation")
    print("  • Different shapes have different electromagnetic properties")
    print("\nTypical applications:")
    print("  • Circular: standard beam pipes, most magnets")
    print("  • Elliptical: flat chambers in modern colliders")
    print("  • Rectangular: kickers, septa, special devices")
    print("\nFor more information, see:")
    print("  - docs/API_REFERENCE.md: Complete API documentation")
    print("  - README.md: Full package documentation")
    print("  - Examples directory: More usage examples")
    print_separator()


if __name__ == "__main__":
    main()
