#!/usr/bin/env python3
"""
Example usage of the pytlwall.Layer module

This script demonstrates how to use the Layer class for defining
material layers with electromagnetic properties in vacuum chambers.
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


def example_copper_layer():
    """Example: Copper layer with typical parameters."""
    print_separator()
    print("EXAMPLE 1: Copper Layer - High Conductivity Metal")
    print_separator()
    
    # Define frequency range
    freq = np.logspace(3, 9, 100)  # 1 kHz to 1 GHz
    
    # Create copper layer
    copper = pytlwall.Layer(
        layer_type='CW',
        thick_m=0.001,  # 1 mm thickness
        sigmaDC=5.96e7,  # Copper conductivity (S/m)
        epsr=1.0,       # Relative permittivity
        freq_Hz=freq
    )
    
    print(f"Copper layer parameters:")
    print(f"  Type:                {copper.layer_type}")
    print(f"  Thickness:           {copper.thick_m*1000:.2f} mm")
    print(f"  DC Conductivity:     {copper.sigmaDC:.2e} S/m")
    print(f"  Relative εᵣ:         {copper.epsr}")
    print(f"  Frequency points:    {len(copper.freq_Hz)}")
    
    # Calculate properties at 1 MHz
    idx_1MHz = np.argmin(np.abs(freq - 1e6))
    print(f"\nProperties at 1 MHz:")
    print(f"  Skin depth δ:        {abs(copper.delta[idx_1MHz])*1e6:.2f} μm")
    print(f"  Surface resistance:  {copper.RS[idx_1MHz].real:.3e} Ω")
    
    # Calculate properties at 1 GHz
    idx_1GHz = np.argmin(np.abs(freq - 1e9))
    print(f"\nProperties at 1 GHz:")
    print(f"  Skin depth δ:        {abs(copper.delta[idx_1GHz])*1e6:.2f} μm")
    print(f"  Surface resistance:  {copper.RS[idx_1GHz].real:.3e} Ω")
    
    print(f"\nNotes:")
    print(f"  - Copper has excellent conductivity")
    print(f"  - Skin depth decreases with frequency")
    print(f"  - Commonly used in RF cavities and beam pipes")


def example_stainless_steel():
    """Example: Stainless steel layer with surface roughness."""
    print_separator()
    print("EXAMPLE 2: Stainless Steel - Lower Conductivity with Roughness")
    print_separator()
    
    freq = np.logspace(3, 9, 100)
    
    # Stainless steel layer
    steel = pytlwall.Layer(
        layer_type='CW',
        thick_m=0.002,  # 2 mm thickness
        sigmaDC=1.45e6,  # Stainless steel conductivity (S/m)
        epsr=1.0,
        RQ=1e-6,  # 1 μm surface roughness
        freq_Hz=freq
    )
    
    print(f"Stainless steel layer parameters:")
    print(f"  Type:                {steel.layer_type}")
    print(f"  Thickness:           {steel.thick_m*1000:.2f} mm")
    print(f"  DC Conductivity:     {steel.sigmaDC:.2e} S/m")
    print(f"  Surface roughness:   {steel.RQ*1e6:.2f} μm")
    
    # Compare with smooth surface
    steel_smooth = pytlwall.Layer(
        thick_m=0.002,
        sigmaDC=1.45e6,
        RQ=0.0,  # Smooth surface
        freq_Hz=freq
    )
    
    idx_1GHz = np.argmin(np.abs(freq - 1e9))
    
    print(f"\nSurface resistance at 1 GHz:")
    print(f"  Smooth surface:      {steel_smooth.RS[idx_1GHz].real:.3e} Ω")
    print(f"  Rough surface:       {steel.RS[idx_1GHz].real:.3e} Ω")
    print(f"  Roughness increase:  {(steel.RS[idx_1GHz].real/steel_smooth.RS[idx_1GHz].real - 1)*100:.1f}%")
    
    print(f"\nNotes:")
    print(f"  - Stainless steel has ~40x lower conductivity than copper")
    print(f"  - Surface roughness increases resistance")
    print(f"  - Effect more pronounced at higher frequencies")


def example_vacuum_boundary():
    """Example: Vacuum boundary layer."""
    print_separator()
    print("EXAMPLE 3: Vacuum Boundary Layer")
    print_separator()
    
    # Create vacuum boundary
    vacuum = pytlwall.Layer(boundary=True)
    
    print(f"Vacuum boundary parameters:")
    print(f"  Type:                {vacuum.layer_type}")
    print(f"  DC Conductivity:     {vacuum.sigmaDC:.2e} S/m")
    print(f"  Relative εᵣ:         {vacuum.epsr}")
    
    print(f"\nNotes:")
    print(f"  - Vacuum has type 'V' (automatically set with boundary=True)")
    print(f"  - Used as outer boundary in multi-layer calculations")
    print(f"  - Represents free space outside the chamber")


def example_material_comparison():
    """Example: Comparing different materials."""
    print_separator()
    print("EXAMPLE 4: Material Comparison - Copper vs Aluminum vs Stainless Steel")
    print_separator()
    
    freq = np.logspace(6, 9, 50)  # 1 MHz to 1 GHz
    
    # Define materials
    materials = {
        'Copper': {'sigmaDC': 5.96e7, 'color': 'orange'},
        'Aluminum': {'sigmaDC': 3.77e7, 'color': 'gray'},
        'Stainless Steel': {'sigmaDC': 1.45e6, 'color': 'blue'}
    }
    
    layers = {}
    for name, props in materials.items():
        layers[name] = pytlwall.Layer(
            thick_m=0.001,
            sigmaDC=props['sigmaDC'],
            freq_Hz=freq
        )
    
    print(f"Conductivity comparison:")
    for name, layer in layers.items():
        print(f"  {name:20s}: {layer.sigmaDC:.2e} S/m")
    
    print(f"\nSkin depth at 10 MHz:")
    idx = np.argmin(np.abs(freq - 1e7))
    for name, layer in layers.items():
        delta = abs(layer.delta[idx]) * 1e6  # Convert to microns
        print(f"  {name:20s}: {delta:.1f} μm")
    
    print(f"\nSurface resistance at 1 GHz:")
    idx = np.argmin(np.abs(freq - 1e9))
    for name, layer in layers.items():
        RS = layer.RS[idx].real
        print(f"  {name:20s}: {RS:.3e} Ω")
    
    print(f"\nNotes:")
    print(f"  - Better conductors have smaller skin depth")
    print(f"  - Better conductors have lower surface resistance")
    print(f"  - Stainless steel has significantly higher losses")


def example_skin_depth_frequency():
    """Example: Skin depth vs frequency."""
    print_separator()
    print("EXAMPLE 5: Skin Depth Frequency Dependence")
    print_separator()
    
    freq = np.logspace(3, 9, 100)  # 1 kHz to 1 GHz
    copper = pytlwall.Layer(sigmaDC=5.96e7, freq_Hz=freq)
    
    delta = abs(copper.delta)
    
    print(f"Skin depth variation with frequency:")
    test_frequencies = [1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9]
    
    for f in test_frequencies:
        idx = np.argmin(np.abs(freq - f))
        d = delta[idx]
        
        if d > 1e-3:
            print(f"  {f:.0e} Hz: {d*1000:.2f} mm")
        elif d > 1e-6:
            print(f"  {f:.0e} Hz: {d*1e6:.2f} μm")
        else:
            print(f"  {f:.0e} Hz: {d*1e9:.2f} nm")
    
    print(f"\nTheoretical relationship:")
    print(f"  δ ∝ 1/√f  (skin depth inversely proportional to √frequency)")
    print(f"  Doubling frequency reduces skin depth by factor of √2 ≈ 1.41")


def example_surface_impedance():
    """Example: Surface impedance calculation and setting."""
    print_separator()
    print("EXAMPLE 6: Surface Impedance")
    print_separator()
    
    freq = np.logspace(6, 9, 50)
    copper = pytlwall.Layer(sigmaDC=5.96e7, freq_Hz=freq)
    
    # Get default surface impedance
    KZ_default = copper.KZ
    
    print(f"Surface impedance (automatically calculated):")
    idx_10MHz = np.argmin(np.abs(freq - 1e7))
    idx_1GHz = np.argmin(np.abs(freq - 1e9))
    
    print(f"  At 10 MHz:")
    print(f"    Real part:      {KZ_default[idx_10MHz].real:.3e} Ω")
    print(f"    Imaginary part: {KZ_default[idx_10MHz].imag:.3e} Ω")
    
    print(f"  At 1 GHz:")
    print(f"    Real part:      {KZ_default[idx_1GHz].real:.3e} Ω")
    print(f"    Imaginary part: {KZ_default[idx_1GHz].imag:.3e} Ω")
    
    # Set custom surface impedance (e.g., from measurements)
    print(f"\nSetting custom surface impedance from measurements:")
    measured_freq = np.array([1e6, 1e8, 1e9])
    measured_KZ = np.array([1e-3+1e-3j, 5e-3+5e-3j, 1e-2+1e-2j])
    
    copper.set_surf_imped(measured_freq, measured_KZ)
    print(f"  ✓ Interpolated to {len(freq)} frequency points")
    
    print(f"\nNotes:")
    print(f"  - Surface impedance is complex (resistance + reactance)")
    print(f"  - Can be calculated or measured")
    print(f"  - set_surf_imped() interpolates measured data")


def example_multilayer_preparation():
    """Example: Preparing layers for multilayer structure."""
    print_separator()
    print("EXAMPLE 7: Multilayer Structure Preparation")
    print_separator()
    
    freq = np.logspace(3, 9, 100)
    
    print(f"Creating vacuum chamber with coating:")
    
    # Layer 1: Inner copper coating
    layer1 = pytlwall.Layer(
        layer_type='CW',
        thick_m=50e-6,  # 50 μm copper coating
        sigmaDC=5.96e7,
        freq_Hz=freq
    )
    print(f"\n  Layer 1 - Copper coating:")
    print(f"    Thickness:     {layer1.thick_m*1e6:.1f} μm")
    print(f"    Conductivity:  {layer1.sigmaDC:.2e} S/m")
    
    # Layer 2: Stainless steel substrate
    layer2 = pytlwall.Layer(
        layer_type='CW',
        thick_m=2e-3,  # 2 mm stainless steel
        sigmaDC=1.45e6,
        freq_Hz=freq
    )
    print(f"\n  Layer 2 - Stainless steel substrate:")
    print(f"    Thickness:     {layer2.thick_m*1000:.1f} mm")
    print(f"    Conductivity:  {layer2.sigmaDC:.2e} S/m")
    
    # Layer 3: Vacuum boundary
    layer3 = pytlwall.Layer(boundary=True)
    print(f"\n  Layer 3 - Vacuum boundary:")
    print(f"    Type:          {layer3.layer_type}")
    
    print(f"\nNotes:")
    print(f"  - Multiple layers can model complex structures")
    print(f"  - Inner layer affects high-frequency impedance")
    print(f"  - Outer layers important at low frequencies")
    print(f"  - All layers must share same frequency array")


def example_perfect_conductor():
    """Example: Perfect electrical conductor."""
    print_separator()
    print("EXAMPLE 8: Perfect Electrical Conductor (PEC)")
    print_separator()
    
    # Create PEC layer
    pec = pytlwall.Layer(layer_type='PEC')
    
    print(f"Perfect conductor parameters:")
    print(f"  Type:              {pec.layer_type}")
    print(f"  Conductivity:      Infinite (σ → ∞)")
    print(f"  Skin depth:        Zero (δ → 0)")
    print(f"  Surface resistance: Zero (Rs → 0)")
    
    print(f"\nUse cases:")
    print(f"  - Theoretical calculations")
    print(f"  - Comparison benchmark")
    print(f"  - Ideal cavity analysis")
    
    print(f"\nNotes:")
    print(f"  - PEC is an idealization")
    print(f"  - Real materials have finite conductivity")
    print(f"  - Useful for validation and limiting cases")


def example_frequency_dependent_properties():
    """Example: Visualizing frequency-dependent properties."""
    print_separator()
    print("EXAMPLE 9: Visualizing Frequency-Dependent Properties")
    print_separator()
    
    freq = np.logspace(3, 9, 200)
    copper = pytlwall.Layer(sigmaDC=5.96e7, freq_Hz=freq)
    
    print(f"Creating visualization of copper properties...")
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Skin depth
    ax1.loglog(freq, abs(copper.delta)*1e6, 'b-', linewidth=2)
    ax1.set_xlabel('Frequency (Hz)', fontsize=11)
    ax1.set_ylabel('Skin Depth (μm)', fontsize=11)
    ax1.set_title('Skin Depth vs Frequency', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Surface resistance
    ax2.loglog(freq, copper.RS.real, 'r-', linewidth=2)
    ax2.set_xlabel('Frequency (Hz)', fontsize=11)
    ax2.set_ylabel('Surface Resistance (Ω)', fontsize=11)
    ax2.set_title('Surface Resistance vs Frequency', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Surface impedance magnitude
    ax3.loglog(freq, abs(copper.KZ), 'g-', linewidth=2)
    ax3.set_xlabel('Frequency (Hz)', fontsize=11)
    ax3.set_ylabel('|Surface Impedance| (Ω)', fontsize=11)
    ax3.set_title('Surface Impedance Magnitude', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: AC conductivity magnitude
    ax4.loglog(freq, abs(copper.sigmaAC), 'm-', linewidth=2)
    ax4.set_xlabel('Frequency (Hz)', fontsize=11)
    ax4.set_ylabel('|AC Conductivity| (S/m)', fontsize=11)
    ax4.set_title('AC Conductivity Magnitude', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    # Create examples/img directory if it doesn't exist
    img_dir = os.path.join('examples', 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    output_file = os.path.join(img_dir, 'copper_layer_properties.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Figure saved as: {output_file}")
    
    # Show plot
    try:
        plt.show()
        print(f"✓ Plot displayed")
    except:
        print(f"  (Display not available, but file saved)")
    
    print(f"\nKey observations:")
    print(f"  - All properties vary with frequency")
    print(f"  - Skin depth decreases as √(1/f)")
    print(f"  - Surface resistance increases as √f")
    print(f"  - Important for impedance calculations")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print(" " * 15 + "EXAMPLES OF USAGE OF THE PYTLWALL.LAYER MODULE")
    print("=" * 80)
    
    # Run all examples
    example_copper_layer()
    example_stainless_steel()
    example_vacuum_boundary()
    example_material_comparison()
    example_skin_depth_frequency()
    example_surface_impedance()
    example_multilayer_preparation()
    example_perfect_conductor()
    example_frequency_dependent_properties()
    
    # Final summary
    print_separator()
    print("SUMMARY")
    print_separator()
    print("The pytlwall.Layer module allows you to:")
    print("  ✓ Define material layers with electromagnetic properties")
    print("  ✓ Calculate frequency-dependent skin depth and resistance")
    print("  ✓ Handle surface roughness effects")
    print("  ✓ Set custom or calculated surface impedance")
    print("  ✓ Model vacuum boundaries and perfect conductors")
    print("  ✓ Prepare multilayer structures for impedance calculations")
    print("\nCommon materials:")
    print("  • Copper:           σ = 5.96×10⁷ S/m (excellent conductor)")
    print("  • Aluminum:         σ = 3.77×10⁷ S/m (good conductor)")
    print("  • Stainless Steel:  σ = 1.45×10⁶ S/m (poor conductor)")
    print("\nKey concepts:")
    print("  • Skin depth decreases with frequency: δ ∝ 1/√f")
    print("  • Surface resistance increases with frequency: Rs ∝ √f")
    print("  • Roughness increases resistance at high frequencies")
    print("  • Multiple layers can model complex structures")
    print("\nFor more information, see:")
    print("  - docs/API_REFERENCE.md: Complete API documentation")
    print("  - README.md: Full package documentation")
    print_separator()


if __name__ == "__main__":
    main()
