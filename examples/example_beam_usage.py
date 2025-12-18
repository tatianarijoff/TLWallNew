#!/usr/bin/env python3
"""
Example usage of the pytlwall.Beam module

This script demonstrates how to use the Beam class for relativistic
physics calculations on particle beams.
"""

import sys
import os
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytlwall


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def example_lhc_beam():
    """Example: Proton beam of the Large Hadron Collider."""
    print_separator()
    print("EXAMPLE 1: Large Hadron Collider (LHC) - Proton Beam at 7 TeV")
    print_separator()
    
    # LHC: protons at 7 TeV kinetic energy
    lhc_beam = pytlwall.Beam(Ekin_MeV=7e6)
    
    print(f"LHC beam parameters:")
    print(f"  Kinetic energy:      {lhc_beam.Ekin_MeV:.2e} MeV  ({lhc_beam.Ekin_MeV/1e6:.1f} TeV)")
    print(f"  Beta (v/c):          {lhc_beam.betarel:.12f}")
    print(f"  Gamma:               {lhc_beam.gammarel:.2f}")
    print(f"  Momentum:            {lhc_beam.p_MeV_c:.2e} MeV/c")
    print(f"  Total energy:        {lhc_beam.E_tot_MeV:.2e} MeV")
    print(f"  Velocity:            {lhc_beam.velocity_m_s:.6e} m/s")
    print(f"  (Speed of light:     {299792458:.6e} m/s)")
    print(f"  Rest mass:           {lhc_beam.mass_MeV_c2:.4f} MeV/c²")
    
    print(f"\nNotes:")
    print(f"  - The beam travels at {lhc_beam.betarel*100:.10f}% of the speed of light")
    print(f"  - The energy is {lhc_beam.gammarel:.1f} times the rest energy")


def example_electron_linac():
    """Example: Electron in a linear accelerator."""
    print_separator()
    print("EXAMPLE 2: Electron Linear Accelerator - 1 GeV")
    print_separator()
    
    # Electron: mass much smaller than the proton mass
    electron_mass = 0.511  # MeV/c²
    electron_beam = pytlwall.Beam(Ekin_MeV=1000, mass_MeV_c2=electron_mass)
    
    print(f"Electron parameters:")
    print(f"  Rest mass:           {electron_beam.mass_MeV_c2:.3f} MeV/c²")
    print(f"  Kinetic energy:      {electron_beam.Ekin_MeV:.2f} MeV  (1 GeV)")
    print(f"  Beta (v/c):          {electron_beam.betarel:.10f}")
    print(f"  Gamma:               {electron_beam.gammarel:.1f}")
    print(f"  Momentum:            {electron_beam.p_MeV_c:.2f} MeV/c")
    print(f"  Velocity:            {electron_beam.velocity_m_s:.6e} m/s")
    
    print(f"\nNotes:")
    print(f"  - Time dilation factor: {electron_beam.gammarel:.1f}x")
    print(f"  - A resting electron 'ages' {electron_beam.gammarel:.1f}x faster")


def example_medical_proton():
    """Example: Medical proton therapy."""
    print_separator()
    print("EXAMPLE 3: Proton Therapy for Tumor Treatment - 200 MeV")
    print_separator()
    
    # Protons for medical therapy: ~200 MeV
    medical_beam = pytlwall.Beam(Ekin_MeV=200)
    
    print(f"Medical beam parameters:")
    print(f"  Kinetic energy:      {medical_beam.Ekin_MeV:.2f} MeV")
    print(f"  Beta (v/c):          {medical_beam.betarel:.6f}")
    print(f"  Gamma:               {medical_beam.gammarel:.6f}")
    print(f"  Momentum:            {medical_beam.p_MeV_c:.2f} MeV/c")
    print(f"  Velocity:            {medical_beam.velocity_m_s:.3e} m/s")
    
    print(f"\nNotes:")
    print(f"  - Optimal energy to penetrate deep tissues")
    print(f"  - Velocity: {medical_beam.betarel*100:.2f}% of the speed of light")


def example_parameter_conversion():
    """Example: Conversion between different parameters."""
    print_separator()
    print("EXAMPLE 4: Conversion between Relativistic Parameters")
    print_separator()
    
    print("Initialize with momentum p = 1000 MeV/c:")
    beam = pytlwall.Beam(p_MeV_c=1000)
    
    print(f"\nFrom p = {beam.p_MeV_c:.2f} MeV/c, we obtain:")
    print(f"  Beta:                {beam.betarel:.6f}")
    print(f"  Gamma:               {beam.gammarel:.6f}")
    print(f"  Kinetic energy:      {beam.Ekin_MeV:.2f} MeV")
    print(f"  Total energy:        {beam.E_tot_MeV:.2f} MeV")
    
    print(f"\nNow we change the kinetic energy to 500 MeV:")
    beam.Ekin_MeV = 500
    
    print(f"\nAfter setting E_kin = {beam.Ekin_MeV:.2f} MeV:")
    print(f"  Beta:                {beam.betarel:.6f}")
    print(f"  Gamma:               {beam.gammarel:.6f}")
    print(f"  Momentum:            {beam.p_MeV_c:.2f} MeV/c")
    print(f"  Total energy:        {beam.E_tot_MeV:.2f} MeV")
    
    print(f"\nAll parameters remain automatically consistent!")


def example_error_handling():
    """Example: Error handling."""
    print_separator()
    print("EXAMPLE 5: Handling Validation Errors")
    print_separator()
    
    print("Attempt 1: Beta greater than 1 (physically impossible)")
    try:
        beam = pytlwall.Beam(betarel=1.5)
        print("  ✗ Beam created (this should not happen!)")
    except pytlwall.BeamValidationError as e:
        print(f"  ✓ Error correctly caught: {e}")
    
    print("\nAttempt 2: Gamma smaller than 1 (impossible for massive particles)")
    try:
        beam = pytlwall.Beam(gammarel=0.5)
        print("  ✗ Beam created (this should not happen!)")
    except pytlwall.BeamValidationError as e:
        print(f"  ✓ Error correctly caught: {e}")
    
    print("\nAttempt 3: Negative energy (non-physical)")
    try:
        beam = pytlwall.Beam(Ekin_MeV=-100)
        print("  ✗ Beam created (this should not happen!)")
    except pytlwall.BeamValidationError as e:
        print(f"  ✓ Error correctly caught: {e}")
    
    print("\nAttempt 4: Non-numeric input")
    try:
        beam = pytlwall.Beam(betarel="not a number")
        print("  ✗ Beam created (this should not happen!)")
    except pytlwall.BeamValidationError as e:
        print(f"  ✓ Error correctly caught: {e}")
    
    print("\nCorrect handling with try/except:")
    print("try:")
    print("    beam = pytlwall.Beam(betarel=user_input)")
    print("except pytlwall.BeamValidationError:")
    print("    print('Invalid input, using default')")
    print("    beam = pytlwall.Beam()  # Ultra-relativistic")



def example_heavy_ion():
    """Example: Heavy ion beam."""
    print_separator()
    print("EXAMPLE 6: Carbon Ion Beam (C-12) - 100 MeV")
    print_separator()
    
    # Carbon-12 ion: mass much greater than the proton mass
    carbon_mass = 12 * 931.5  # MeV/c² (approximation)
    carbon_beam = pytlwall.Beam(Ekin_MeV=100, mass_MeV_c2=carbon_mass)
    
    print(f"Carbon ion parameters:")
    print(f"  Rest mass:           {carbon_beam.mass_MeV_c2:.1f} MeV/c² (~12 u)")
    print(f"  Kinetic energy:      {carbon_beam.Ekin_MeV:.2f} MeV")
    print(f"  Beta (v/c):          {carbon_beam.betarel:.6f}")
    print(f"  Gamma:               {carbon_beam.gammarel:.6f}")
    print(f"  Momentum:            {carbon_beam.p_MeV_c:.2f} MeV/c")
    print(f"  Velocity:            {carbon_beam.velocity_m_s:.3e} m/s")
    
    print(f"\nNotes:")
    print(f"  - Heavy ion at low energy → non-relativistic regime")
    print(f"  - Gamma close to 1: {carbon_beam.gammarel:.6f}")
    print(f"  - Velocity: only {carbon_beam.betarel*100:.2f}% of the speed of light")


def example_comparison():
    """Example: Comparison between different particles at the same energy."""
    print_separator()
    print("EXAMPLE 7: Comparison Proton vs Electron at 100 MeV")
    print_separator()
    
    # Same kinetic energy, different masses
    energy = 100.0  # MeV
    
    electron_mass = 0.511  # MeV/c²
    proton_mass = 938.272  # MeV/c²
    
    electron = pytlwall.Beam(Ekin_MeV=energy, mass_MeV_c2=electron_mass)
    proton = pytlwall.Beam(Ekin_MeV=energy, mass_MeV_c2=proton_mass)
    
    print(f"Kinetic energy: {energy} MeV\n")
    
    print(f"ELECTRON (m = {electron_mass:.3f} MeV/c²):")
    print(f"  Beta (v/c):          {electron.betarel:.10f}")
    print(f"  Gamma:               {electron.gammarel:.2f}")
    print(f"  Momentum:            {electron.p_MeV_c:.2f} MeV/c")
    print(f"  Velocity:            {electron.velocity_m_s:.6e} m/s")
    
    print(f"\nPROTON (m = {proton_mass:.3f} MeV/c²):")
    print(f"  Beta (v/c):          {proton.betarel:.10f}")
    print(f"  Gamma:               {proton.gammarel:.2f}")
    print(f"  Momentum:            {proton.p_MeV_c:.2f} MeV/c")
    print(f"  Velocity:            {proton.velocity_m_s:.6e} m/s")
    
    print(f"\nCOMPARISON:")
    print(f"  Mass ratio:          {proton_mass/electron_mass:.1f}:1")
    print(f"  Gamma ratio:         {electron.gammarel/proton.gammarel:.2f}:1")
    print(f"  Velocity ratio:      {electron.betarel/proton.betarel:.2f}:1")
    print(f"\nNotes:")
    print(f"  - The electron is much more relativistic than the proton")
    print(f"  - At equal energy, lighter particles move faster")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print(" " * 15 + "EXAMPLES OF USAGE OF THE PYTLWALL.BEAM MODULE")
    print("=" * 80)
    
    # Run all examples
    example_lhc_beam()
    example_electron_linac()
    example_medical_proton()
    example_parameter_conversion()
    example_error_handling()
    example_heavy_ion()
    example_comparison()
    
    # Final summary
    print_separator()
    print("SUMMARY")
    print_separator()
    print("The pytlwall.Beam module allows you to:")
    print("  ✓ Create particle beams with different relativistic parameters")
    print("  ✓ Automatically convert between beta, gamma, energy, and momentum")
    print("  ✓ Handle particles with different masses (protons, electrons, ions)")
    print("  ✓ Validate input with appropriate exceptions")
    print("  ✓ Compute additional properties (velocity, total energy)")
    print("\nFor more information, see:")
    print("  - README.md: Full documentation")

    print_separator()


if __name__ == "__main__":
    main()
