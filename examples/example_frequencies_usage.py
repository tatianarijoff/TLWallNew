#!/usr/bin/env python3
"""
Example usage of the pytlwall.Frequencies module

This script demonstrates how to use the Frequencies class for creating
and managing frequency arrays for impedance calculations.
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


def example_basic_logarithmic():
    """Example: Basic logarithmic frequency array."""
    print_separator()
    print("EXAMPLE 1: Basic Logarithmic Frequency Array")
    print_separator()
    
    # Create frequency array from 1 Hz to 1 MHz with default step
    freqs = pytlwall.Frequencies(fmin=0, fmax=6, fstep=2)
    
    print(f"Frequency array parameters:")
    print(f"  Minimum exponent:    {freqs.fmin}")
    print(f"  Maximum exponent:    {freqs.fmax}")
    print(f"  Step exponent:       {freqs.fstep}")
    print(f"  Number of points:    {len(freqs)}")
    print(f"  Minimum frequency:   {freqs.freq[0]:.2e} Hz")
    print(f"  Maximum frequency:   {freqs.freq[-1]:.2e} Hz")
    
    print(f"\nFirst 10 frequencies:")
    for i, f in enumerate(freqs.freq[:10]):
        print(f"  [{i+1:2d}] {f:12.2e} Hz  ({f/1e3:8.2f} kHz)")
    
    print(f"\nLast 5 frequencies:")
    for i, f in enumerate(freqs.freq[-5:], start=len(freqs)-4):
        print(f"  [{i:3d}] {f:12.2e} Hz  ({f/1e6:8.2f} MHz)")


def example_explicit_list():
    """Example: Using an explicit frequency list."""
    print_separator()
    print("EXAMPLE 2: Explicit Frequency List")
    print_separator()
    
    # Define specific frequencies of interest (e.g., resonant modes)
    resonances = [
        455e3,    # 455 kHz
        1.2e6,    # 1.2 MHz
        2.8e6,    # 2.8 MHz
        5.5e6,    # 5.5 MHz
        12.0e6,   # 12 MHz
        25.0e6,   # 25 MHz
    ]
    
    freqs = pytlwall.Frequencies(freq_list=resonances)
    
    print(f"Custom frequency list:")
    print(f"  Number of points:    {len(freqs)}")
    print(f"  Minimum frequency:   {freqs.fmin:.2e} Hz")
    print(f"  Maximum frequency:   {freqs.fmax:.2e} Hz")
    print(f"  Step exponent:       {freqs.fstep} (N/A for explicit list)")
    
    print(f"\nAll frequencies:")
    for i, f in enumerate(freqs.freq):
        print(f"  Mode {i+1}: {f/1e6:6.2f} MHz  ({f:.2e} Hz)")
    
    print(f"\nNotes:")
    print(f"  - Frequencies are automatically sorted")
    print(f"  - Useful for analyzing specific resonant modes")
    print(f"  - fstep is set to 0 for explicit lists")


def example_lhc_range():
    """Example: LHC impedance calculation range."""
    print_separator()
    print("EXAMPLE 3: LHC Impedance Calculation Range (1 Hz to 10 GHz)")
    print_separator()
    
    # LHC typically uses wide frequency range
    freqs = pytlwall.Frequencies(fmin=0, fmax=10, fstep=2)
    
    print(f"LHC frequency range:")
    print(f"  Range:               10^{freqs.fmin} to 10^{freqs.fmax} Hz")
    print(f"  Actual range:        {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
    print(f"  Number of points:    {len(freqs)}")
    print(f"  Step parameter:      {freqs.fstep}")
    
    # Analyze distribution
    decades = []
    for decade in range(int(freqs.fmin), int(freqs.fmax) + 1):
        low = 10**decade
        high = 10**(decade + 1)
        count = np.sum((freqs.freq >= low) & (freqs.freq < high))
        decades.append((decade, count))
    
    print(f"\nPoints per decade:")
    for decade, count in decades:
        print(f"  10^{decade:2d} - 10^{decade+1:2d} Hz: {count:4d} points")
    
    print(f"\nNotes:")
    print(f"  - Wide range covers all relevant impedance contributions")
    print(f"  - From resistive wall (low f) to broadband (high f)")
    print(f"  - Typical calculation time: minutes to hours")


def example_resolution_comparison():
    """Example: Comparing different resolutions."""
    print_separator()
    print("EXAMPLE 4: Resolution Comparison (fstep effect)")
    print_separator()
    
    # Create three arrays with different resolutions
    # NOTE: Larger fstep = MORE points per decade
    freqs_coarse = pytlwall.Frequencies(fmin=3, fmax=6, fstep=1)   # Low resolution (fewer points)
    freqs_medium = pytlwall.Frequencies(fmin=3, fmax=6, fstep=2)   # Medium resolution
    freqs_fine = pytlwall.Frequencies(fmin=3, fmax=6, fstep=3)     # High resolution (more points)
    
    print(f"Same range (1 kHz to 1 MHz), different resolutions:")
    print(f"\n  Coarse  (fstep=1): {len(freqs_coarse):5d} points  [Low resolution]")
    print(f"  Medium  (fstep=2): {len(freqs_medium):5d} points  [Medium resolution]")
    print(f"  Fine    (fstep=3): {len(freqs_fine):5d} points  [High resolution]")
    
    print(f"\nRatio fine/coarse:   {len(freqs_fine)/len(freqs_coarse):.1f}x more points")
    print(f"\nNote: Larger fstep gives MORE points per decade (higher resolution)")
    
    print(f"\nFirst 10 points comparison:")
    print(f"{'Index':>6} {'Coarse (fstep=1)':>18} {'Medium (fstep=2)':>18} {'Fine (fstep=3)':>18}")
    print(f"{'-'*6} {'-'*18} {'-'*18} {'-'*18}")
    
    for i in range(min(10, len(freqs_coarse))):
        coarse_str = f"{freqs_coarse.freq[i]:.2e}" if i < len(freqs_coarse) else "-"
        medium_str = f"{freqs_medium.freq[i]:.2e}" if i < len(freqs_medium) else "-"
        fine_str = f"{freqs_fine.freq[i]:.2e}" if i < len(freqs_fine) else "-"
        print(f"{i+1:6d} {coarse_str:>18} {medium_str:>18} {fine_str:>18}")
    
    print(f"\nRecommendations:")
    print(f"  - Use fstep=1 for quick broad scans (low resolution, fewer points)")
    print(f"  - Use fstep=2 or 3 for detailed analysis (high resolution, more points)")
    print(f"  - Verify convergence by comparing results at different resolutions")


def example_dynamic_update():
    """Example: Dynamically updating frequency range."""
    print_separator()
    print("EXAMPLE 5: Dynamic Frequency Range Update")
    print_separator()
    
    # Start with broad scan (low resolution, fewer points)
    print("Step 1: Initial broad scan (low resolution)")
    freqs = pytlwall.Frequencies(fmin=0, fmax=10, fstep=1)
    print(f"  Range: {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
    print(f"  Points: {len(freqs)}")
    print(f"  Resolution: fstep=1 (low, fewer points)")
    
    # Identify region of interest (example: 1 MHz to 100 MHz)
    print("\nStep 2: Identify interesting region (1 MHz - 100 MHz)")
    print(f"  Interesting frequency range: 10^6 to 10^8 Hz")
    
    # Update to zoom in with higher resolution (more points with higher fstep)
    print("\nStep 3: Zoom in with higher resolution")
    freqs.update_from_exponents(fmin=6, fmax=8, fstep=3)
    print(f"  New range: {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
    print(f"  New points: {len(freqs)}")
    print(f"  Resolution: fstep=3 (high, many more points)")
    
    print(f"\nUse case:")
    print(f"  1. Quick scan (fstep=1, low res) to identify impedance peaks")
    print(f"  2. Detailed scan (fstep=3, high res) around peaks for accurate analysis")
    print(f"  3. Saves computation time compared to always using high resolution")


def example_integration_tlwall():
    """Example: Integration with TlWall calculations."""
    print_separator()
    print("EXAMPLE 6: Integration with TlWall (Impedance Calculation)")
    print_separator()
    
    # Create frequency array
    freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)
    
    print(f"Setting up impedance calculation:")
    print(f"  Frequency points:    {len(freqs)}")
    print(f"  Range:               {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
    print(f"                       ({freqs.freq[0]/1e3:.0f} kHz to {freqs.freq[-1]/1e9:.1f} GHz)")
    
    # This is a conceptual example - actual integration depends on your TlWall implementation
    print(f"\nTypical usage with TlWall:")
    print(f"  # Create beam and chamber")
    print(f"  beam = pytlwall.Beam(gamma=7460.52)")
    print(f"  chamber = pytlwall.Chamber(radius=0.02, shape='circular')")
    print(f"  layer = pytlwall.Layer(material='copper', thickness=0.001)")
    print(f"  ")
    print(f"  # Create TlWall with frequencies")
    print(f"  wall = pytlwall.TlWall(beam=beam, chamber=chamber,")
    print(f"                          layers=[layer], frequencies=freqs)")
    print(f"  ")
    print(f"  # Calculate impedances")
    print(f"  wall.calc_ZLong()   # Longitudinal impedance")
    print(f"  wall.calc_ZTrans()  # Transverse impedance")
    print(f"  ")
    print(f"  # Results available at all frequency points")
    print(f"  print(f'Z_Long at 1 MHz: {{wall.ZLong[idx_1MHz]:.3e}} Ohm')")
    
    print(f"\nNotes:")
    print(f"  - Frequencies object is passed to TlWall during initialization")
    print(f"  - All impedance arrays will have same length as frequency array")
    print(f"  - Calculation time scales linearly with number of frequencies")


def example_validation_errors():
    """Example: Handling validation and errors."""
    print_separator()
    print("EXAMPLE 7: Error Handling and Validation")
    print_separator()
    
    print("Test 1: Empty frequency list")
    try:
        freqs = pytlwall.Frequencies(freq_list=[])
        print(f"  Result: Created with default exponents (fmin={freqs.fmin}, fmax={freqs.fmax})")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\nTest 2: Negative frequencies (should fail)")
    try:
        freqs = pytlwall.Frequencies(freq_list=[-100, 1e6, 1e9])
        print(f"  ✗ Accepted negative frequency (should not happen!)")
    except ValueError as e:
        print(f"  ✓ Correctly rejected: {e}")
    
    print("\nTest 3: Invalid fmin > fmax (triggers warning)")
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        freqs = pytlwall.Frequencies(fmin=8, fmax=3, fstep=2)
        if w:
            print(f"  ⚠ Warning issued: {w[0].message}")
        print(f"  Result: {len(freqs)} frequency points")
    
    print("\nTest 4: Negative fstep (triggers warning)")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        freqs = pytlwall.Frequencies(fmin=0, fmax=6, fstep=-1)
        if w:
            print(f"  ⚠ Warning issued: {w[0].message}")
    
    print("\nTest 5: Valid unsorted list (should auto-sort)")
    freq_list = [1e6, 100, 1e9, 1e3]
    freqs = pytlwall.Frequencies(freq_list=freq_list)
    print(f"  Input:  {[f'{f:.0e}' for f in freq_list]}")
    print(f"  Output: {[f'{f:.0e}' for f in freqs.freq]}")
    print(f"  ✓ Automatically sorted")
    
    print("\nBest practices:")
    print(f"  - Always validate user input before creating Frequencies")
    print(f"  - Use try/except blocks for robust error handling")
    print(f"  - Check warnings for potential issues")


def example_visualization():
    """Example: Visualizing frequency distributions."""
    print_separator()
    print("EXAMPLE 8: Visualizing Frequency Distributions")
    print_separator()
    
    # Create different frequency arrays
    # Higher fstep = more points (higher resolution)
    freqs_low = pytlwall.Frequencies(fmin=0, fmax=10, fstep=1)   # Low resolution
    freqs_med = pytlwall.Frequencies(fmin=0, fmax=10, fstep=2)   # Medium resolution
    freqs_high = pytlwall.Frequencies(fmin=0, fmax=10, fstep=3)  # High resolution
    
    print(f"Creating visualization of three frequency distributions:")
    print(f"  Low res  (fstep=1): {len(freqs_low)} points")
    print(f"  Med res  (fstep=2): {len(freqs_med)} points")
    print(f"  High res (fstep=3): {len(freqs_high)} points")
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left plot: Frequency distribution
    ax1.semilogx(freqs_low.freq, np.ones(len(freqs_low)), 'r.', 
                 markersize=4, alpha=0.6, label=f'Low res (n={len(freqs_low)})')
    ax1.semilogx(freqs_med.freq, 2*np.ones(len(freqs_med)), 'g.', 
                 markersize=4, alpha=0.6, label=f'Med res (n={len(freqs_med)})')
    ax1.semilogx(freqs_high.freq, 3*np.ones(len(freqs_high)), 'b.', 
                 markersize=4, alpha=0.6, label=f'High res (n={len(freqs_high)})')
    ax1.set_xlabel('Frequency (Hz)', fontsize=12)
    ax1.set_ylabel('Resolution Level', fontsize=12)
    ax1.set_yticks([1, 2, 3])
    ax1.set_yticklabels(['Low', 'Medium', 'High'])
    ax1.set_title('Frequency Point Distribution', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Right plot: Points per decade
    decades = range(0, 11)
    points_low = []
    points_med = []
    points_high = []
    
    for decade in decades:
        low = 10**decade
        high = 10**(decade + 1)
        points_low.append(np.sum((freqs_low.freq >= low) & (freqs_low.freq < high)))
        points_med.append(np.sum((freqs_med.freq >= low) & (freqs_med.freq < high)))
        points_high.append(np.sum((freqs_high.freq >= low) & (freqs_high.freq < high)))
    
    x = np.arange(len(decades))
    width = 0.25
    
    ax2.bar(x - width, points_low, width, label='Low res (fstep=1)', alpha=0.7, color='red')
    ax2.bar(x, points_med, width, label='Med res (fstep=2)', alpha=0.7, color='green')
    ax2.bar(x + width, points_high, width, label='High res (fstep=3)', alpha=0.7, color='blue')
    
    ax2.set_xlabel('Frequency Decade', fontsize=12)
    ax2.set_ylabel('Number of Points', fontsize=12)
    ax2.set_title('Points per Decade', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'10^{d}' for d in decades], rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save figure
    # Create examples/img directory if it doesn't exist
    img_dir = os.path.join('examples', 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    output_file = os.path.join(img_dir, 'frequency_distribution_comparison.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Figure saved as: {output_file}")
    
    # Show plot
    try:
        plt.show()
        print(f"✓ Plot displayed")
    except:
        print(f"  (Display not available, but file saved)")


def example_practical_workflow():
    """Example: Practical workflow for impedance studies."""
    print_separator()
    print("EXAMPLE 9: Practical Workflow for Impedance Studies")
    print_separator()
    
    print("SCENARIO: Analyzing impedance of a new chamber design")
    print("\nStep 1: Preliminary broad scan")
    freqs_broad = pytlwall.Frequencies(fmin=0, fmax=10, fstep=1)
    print(f"  Created broad frequency scan: {len(freqs_broad)} points")
    print(f"  Range: 1 Hz to 10 GHz")
    print(f"  Resolution: fstep=1 (low resolution, fast computation)")
    print(f"  Purpose: Identify general impedance behavior and peaks")
    
    print("\nStep 2: Identify critical frequency regions")
    print(f"  Analysis shows peaks at:")
    print(f"    - Low frequency: < 1 kHz (resistive wall)")
    print(f"    - Mid frequency: 10-100 MHz (trapped modes)")
    print(f"    - High frequency: > 1 GHz (broadband)")
    
    print("\nStep 3: Detailed scan of trapped mode region")
    freqs_detailed = pytlwall.Frequencies(fmin=7, fmax=8, fstep=3)
    print(f"  Created detailed scan: {len(freqs_detailed)} points")
    print(f"  Range: 10 MHz to 100 MHz")
    print(f"  Resolution: fstep=3 (high resolution, more accurate)")
    print(f"  Purpose: Accurate characterization of resonant modes")
    
    print("\nStep 4: Critical frequencies for beam dynamics")
    # Revolution frequency and harmonics for LHC
    f_rev = 11.245e3  # Hz
    harmonics = [f_rev * n for n in [1, 10, 100, 1000, 10000]]
    freqs_beam = pytlwall.Frequencies(freq_list=harmonics)
    print(f"  Created beam harmonic array: {len(freqs_beam)} points")
    print(f"  Frequencies: {[f'{f/1e3:.1f} kHz' if f < 1e6 else f'{f/1e6:.1f} MHz' for f in freqs_beam.freq]}")
    print(f"  Purpose: Check impedance at beam revolution harmonics")
    
    print("\nStep 5: Export for documentation")
    print(f"  Frequency ranges used:")
    print(f"    - Broad scan: {freqs_broad}")
    print(f"    - Detailed scan: {freqs_detailed}")
    print(f"    - Beam harmonics: {freqs_beam}")
    
    print("\nWorkflow summary:")
    print(f"  1. Broad scan (low res) → overall behavior")
    print(f"  2. Identify peaks → critical regions")
    print(f"  3. Detailed scan (high res) → accurate values")
    print(f"  4. Beam frequencies → stability analysis")
    print(f"  5. Document → reproducibility")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print(" " * 10 + "EXAMPLES OF USAGE OF THE PYTLWALL.FREQUENCIES MODULE")
    print("=" * 80)
    
    # Run all examples
    example_basic_logarithmic()
    example_explicit_list()
    example_lhc_range()
    example_resolution_comparison()
    example_dynamic_update()
    example_integration_tlwall()
    example_validation_errors()
    example_visualization()
    example_practical_workflow()
    
    # Final summary
    print_separator()
    print("SUMMARY")
    print_separator()
    print("The pytlwall.Frequencies module allows you to:")
    print("  ✓ Create logarithmic frequency arrays with flexible resolution")
    print("  ✓ Use explicit frequency lists for specific modes")
    print("  ✓ Dynamically update frequency ranges during analysis")
    print("  ✓ Handle validation and error checking")
    print("  ✓ Integrate seamlessly with TlWall impedance calculations")
    print("  ✓ Optimize computation time through smart frequency selection")
    print("\nBest practices:")
    print("  • Start with low resolution (fstep=1) for quick scans")
    print("  • Increase resolution (fstep=2, 3) for detailed analysis")
    print("  • Use explicit lists for known resonances")
    print("  • Always validate convergence with different resolutions")
    print("  • Document frequency choices in your analysis")
    print("\n⚠️  Important: Larger fstep = MORE points per decade (higher resolution)")
    print("     fstep=1 → fewer points (low resolution)")
    print("     fstep=3 → many more points (high resolution)")
    print("\nFor more information, see:")
    print("  - docs/API_REFERENCE.md: Complete API documentation")
    print("  - README.md: Full package documentation")
    print_separator()


if __name__ == "__main__":
    main()
