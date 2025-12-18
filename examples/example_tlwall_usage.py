"""
Examples for tlwall module.

Demonstrates impedance calculations with various configurations.
"""

import numpy as np
import sys
import os

# Add parent directory to path for non-installed package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try package import first
    from pytlwall.tlwall import TlWall
    from pytlwall.chamber import Chamber
    from pytlwall.beam import Beam
    from pytlwall.frequencies import Frequencies
    from pytlwall.layer import Layer
except ModuleNotFoundError:
    # Fallback to direct import
    from pytlwall.tlwall import TlWall
    from pytlwall.chamber import Chamber
    from pytlwall.beam import Beam
    from pytlwall.frequencies import Frequencies
    from pytlwall.layer import Layer

# Suppress warnings for cleaner output
import warnings
warnings.filterwarnings('ignore')


def example_1_basic_copper_chamber():
    """Example 1: Basic copper chamber - LHC-style."""
    print("=" * 70)
    print("Example 1: Basic Copper Chamber (LHC-style)")
    print("=" * 70)
    
    # Setup
    freqs = Frequencies(fmin=3, fmax=9, fstep=2)
    beam = Beam(gamma=7460.52)  # LHC 7 TeV protons
    chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
    copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
    chamber.layers = [copper]
    
    # Calculate
    wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
    ZLong = wall.calc_ZLong()
    ZTrans = wall.calc_ZTrans()
    
    print(f"\nConfiguration:")
    print(f"  Beam: LHC protons, γ = {beam.gammarel:.2f}")  # Use gammarel for reading
    print(f"  Chamber: circular, r = {chamber.pipe_rad_m*1000:.1f} mm")
    print(f"  Layer: copper, t = {copper.thick_m*1000:.1f} mm")
    print(f"  Frequencies: {len(freqs)} points from {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
    
    print(f"\nResults:")
    print(f"  ZLong at 1 kHz:  {abs(ZLong[0]):.3e} Ω")
    print(f"  ZLong at 1 GHz:  {abs(ZLong[-1]):.3e} Ω")
    print(f"  ZTrans at 1 kHz: {abs(ZTrans[0]):.3e} Ω/m")
    print(f"  ZTrans at 1 GHz: {abs(ZTrans[-1]):.3e} Ω/m")
    print()


def example_2_elliptical_chamber_yokoya():
    """Example 2: Elliptical chamber with Yokoya factors."""
    print("=" * 70)
    print("Example 2: Elliptical Chamber with Yokoya Factors")
    print("=" * 70)
    
    # Setup
    freqs = Frequencies(fmin=6, fmax=9, fstep=2)
    beam = Beam(gamma=7460.52)
    chamber = Chamber(
        pipe_hor_m=0.030,  # 30 mm horizontal
        pipe_ver_m=0.020,  # 20 mm vertical
        chamber_shape='ELLIPTICAL',
        betax=100.0,
        betay=50.0
    )
    copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
    chamber.layers = [copper]
    
    # Calculate
    wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
    
    print(f"\nConfiguration:")
    print(f"  Chamber: elliptical, {chamber.pipe_hor_m*1000:.1f} × {chamber.pipe_ver_m*1000:.1f} mm")
    print(f"  Yokoya q: {chamber.yokoya_q:.4f}")
    print(f"  Beta functions: βx = {chamber.betax:.1f} m, βy = {chamber.betay:.1f} m")
    
    print(f"\nImpedances at 1 MHz:")
    idx = np.argmin(np.abs(freqs.freq - 1e6))
    print(f"  ZDipX:  {abs(wall.ZDipX[idx]):.3e} Ω")
    print(f"  ZDipY:  {abs(wall.ZDipY[idx]):.3e} Ω")
    print(f"  ZQuadX: {abs(wall.ZQuadX[idx]):.3e} Ω")
    print(f"  ZQuadY: {abs(wall.ZQuadY[idx]):.3e} Ω")
    print()


def example_3_multilayer_coating():
    """Example 3: Multilayer - copper coating on stainless steel."""
    print("=" * 70)
    print("Example 3: Multilayer Copper Coating on Stainless Steel")
    print("=" * 70)
    
    # Setup
    freqs = Frequencies(fmin=3, fmax=9, fstep=2)
    beam = Beam(gamma=7460.52)
    chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
    
    # Layers: thin copper coating + thick steel substrate
    copper_coating = Layer(thick_m=50e-6, sigmaDC=5.96e7, freq_Hz=freqs.freq)
    steel_substrate = Layer(thick_m=2e-3, sigmaDC=1.45e6, freq_Hz=freqs.freq)
    chamber.layers = [copper_coating, steel_substrate]
    
    # Calculate
    wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
    ZLong = wall.calc_ZLong()
    
    print(f"\nConfiguration:")
    print(f"  Layer 1: copper coating, t = {copper_coating.thick_m*1e6:.1f} μm")
    print(f"  Layer 2: steel substrate, t = {steel_substrate.thick_m*1000:.1f} mm")
    
    print(f"\nLongitudinal Impedance:")
    for i in [0, len(freqs)//2, -1]:
        print(f"  f = {freqs.freq[i]:.2e} Hz: |ZLong| = {abs(ZLong[i]):.3e} Ω")
    print()


def example_4_space_charge_effects():
    """Example 4: Space charge impedances at low energy."""
    print("=" * 70)
    print("Example 4: Space Charge Effects at Low Energy")
    print("=" * 70)
    
    # Setup - lower energy beam for significant space charge
    freqs = Frequencies(fmin=3, fmax=7, fstep=2)
    beam_low = Beam(gamma=10.0)  # Low energy
    beam_high = Beam(gamma=7460.52)  # High energy
    
    chamber = Chamber(pipe_rad_m=0.050, chamber_shape='CIRCULAR')
    aluminum = Layer(thick_m=0.001, sigmaDC=3.77e7, freq_Hz=freqs.freq)
    chamber.layers = [aluminum]
    
    # Calculate for both beams
    wall_low = TlWall(chamber=chamber, beam=beam_low, frequencies=freqs)
    wall_high = TlWall(chamber=chamber, beam=beam_high, frequencies=freqs)
    
    print(f"\nSpace charge at 10 MHz:")
    idx = np.argmin(np.abs(freqs.freq - 1e7))
    
    print(f"\nLow energy (γ = {beam_low.gammarel:.1f}):")
    print(f"  ZLongDSC:  {abs(wall_low.ZLongDSC[idx]):.3e} Ω")
    print(f"  ZLongISC:  {abs(wall_low.ZLongISC[idx]):.3e} Ω")
    print(f"  ZTransDSC: {abs(wall_low.ZTransDSC[idx]):.3e} Ω/m")
    print(f"  ZTransISC: {abs(wall_low.ZTransISC[idx]):.3e} Ω/m")
    
    print(f"\nHigh energy (γ = {beam_high.gammarel:.1f}):")
    print(f"  ZLongDSC:  {abs(wall_high.ZLongDSC[idx]):.3e} Ω (negligible)")
    print(f"  ZLongISC:  {abs(wall_high.ZLongISC[idx]):.3e} Ω (negligible)")
    print()


def example_5_all_impedances():
    """Example 5: Calculate and display all impedances."""
    print("=" * 70)
    print("Example 5: All Impedances Summary")
    print("=" * 70)
    
    # Setup
    freqs = Frequencies(fmin=6, fmax=8, fstep=1)
    beam = Beam(gamma=7460.52)
    chamber = Chamber(
        pipe_rad_m=0.022,
        chamber_shape='CIRCULAR',
        betax=100.0,
        betay=100.0
    )
    copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
    chamber.layers = [copper]
    
    # Calculate all
    wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
    all_Z = wall.get_all_impedances()
    
    print(f"\nAll impedances at f = {freqs.freq[0]:.2e} Hz:")
    print(f"  {'Impedance':<20} {'Magnitude':<15} {'Unit'}")
    print(f"  {'-'*20} {'-'*15} {'-'*10}")
    
    units = {
        'ZLong': 'Ω', 'ZTrans': 'Ω/m',
        'ZDipX': 'Ω', 'ZDipY': 'Ω',
        'ZQuadX': 'Ω', 'ZQuadY': 'Ω',
        'ZLongSurf': 'Ω', 'ZTransSurf': 'Ω',
        'ZLongDSC': 'Ω', 'ZLongISC': 'Ω',
        'ZTransDSC': 'Ω/m', 'ZTransISC': 'Ω/m'
    }
    
    for name, Z in all_Z.items():
        unit = units.get(name, "Ω/m" if "Trans" in name else "Ω")
        print(f"  {name:<20} {abs(Z[0]):<15.3e} {unit}")
    print()


def example_6_summary_and_info():
    """Example 6: Using summary and utility methods."""
    print("=" * 70)
    print("Example 6: TlWall Summary and Information")
    print("=" * 70)
    
    # Setup
    freqs = Frequencies(fmin=3, fmax=9, fstep=2)
    beam = Beam(gamma=7460.52)
    chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
    copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
    chamber.layers = [copper]
    
    wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
    
    # Calculate some impedances
    _ = wall.ZLong
    _ = wall.ZTrans
    
    # Display summary
    print("\n" + wall.summary())
    
    # Display repr
    print(f"\nObject representation:")
    print(f"  {repr(wall)}")
    print()


if __name__ == '__main__':
    # Run all examples
    example_1_basic_copper_chamber()
    example_2_elliptical_chamber_yokoya()
    example_3_multilayer_coating()
    example_4_space_charge_effects()
    example_5_all_impedances()
    example_6_summary_and_info()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
