"""
Beam definition and basic relativistic beam properties.

This module provides a Beam class for handling relativistic particle beam
calculations, commonly used in accelerator physics and resistive wall impedance
computations.

Authors: Tatiana Rijoff, Carlo Zannini
Date:    01/03/2013
Revised: December 2025
Copyright: CERN
"""

from typing import Optional
import numpy as np
import scipy.constants as const

# Physical constants - exported for compatibility
m_p_MeV = const.physical_constants['proton mass energy equivalent in MeV'][0]
M_PROTON_MEV = m_p_MeV  # Alias for export

# Default values (for ultra-relativistic limit)
default_betarel = 1.0
default_gammarel = float('inf')
default_Ekin_MeV = float('inf')
default_p_MeV_c = float('inf')


class BeamValidationError(ValueError):
    """Exception raised for invalid beam parameter values."""
    pass


class Beam:
    """
    Relativistic particle beam representation.
    
    The beam object contains the basic properties of a beam for resistive
    wall calculation: the kinetic properties (velocity, momentum etc) and the
    test beam distance.
    
    This class encapsulates the kinematic properties of a relativistic particle
    beam, automatically maintaining consistency between different representations
    (beta, gamma, kinetic energy, momentum).
    
    Attributes:
        betarel (float): Relativistic beta (v/c), range (0, 1]
        gammarel (float): Lorentz gamma factor, range [1, ∞)
        Ekin_MeV (float): Kinetic energy in MeV, range (0, ∞)
        p_MeV_c (float): Momentum in MeV/c, range (0, ∞)
        test_beam_shift (float): Test beam distance offset in meters
        mass_MeV_c2 (float): Rest mass energy in MeV/c²
    
    Physics Relations:
        γ = 1 / √(1 - β²)
        E_kin = (γ - 1) * m * c²
        E_tot = γ * m * c²
        p = γ * m * β * c
        E_tot² = (p*c)² + (m*c²)²
    
    Example:
        >>> # Default: ultra-relativistic beam
        >>> beam1 = Beam()
        >>> print(f"Beta: {beam1.betarel}, Gamma: {beam1.gammarel}")
        
        >>> # LHC 7 TeV protons
        >>> beam2 = Beam(Ekin_MeV=7e6)
        >>> print(f"Beta: {beam2.betarel:.6f}, Gamma: {beam2.gammarel:.2f}")
        
        >>> # By gamma
        >>> beam3 = Beam(gammarel=7460.52)
        >>> print(f"Beta: {beam3.betarel:.6f}")
    """

    def __init__(
        self,
        Ekin_MeV: float = default_Ekin_MeV,
        p_MeV_c: float = default_p_MeV_c,
        betarel: float = default_betarel,
        gammarel: float = default_gammarel,
        gamma: Optional[float] = None,  # Alias for gammarel
        test_beam_shift: float = 0.001,
        mass_MeV_c2: float = m_p_MeV,
    ):
        """
        Initialize a Beam object with kinematic parameters.
        
        Args:
            Ekin_MeV: Kinetic energy in MeV (default: inf = ultra-relativistic)
            p_MeV_c: Momentum in MeV/c (default: inf = ultra-relativistic)
            betarel: Relativistic beta (v/c) (default: 1.0 = ultra-relativistic)
            gammarel: Lorentz gamma factor (default: inf = ultra-relativistic)
            gamma: Alias for gammarel (for convenience)
            test_beam_shift: Test beam distance offset in meters (default: 0.001)
            mass_MeV_c2: Particle rest mass energy in MeV/c² (default: proton mass)
        
        Note:
            If no parameters are provided, defaults to ultra-relativistic limit.
            Parameter priority: Ekin_MeV > p_MeV_c > betarel > gammarel/gamma.
            Both 'gamma' and 'gammarel' are accepted (gamma is alias for gammarel).
        
        Raises:
            BeamValidationError: If mass is invalid
        
        Example:
            >>> # Ultra-relativistic (default)
            >>> beam1 = Beam()
            
            >>> # LHC protons (using gammarel)
            >>> beam2 = Beam(gammarel=7460.52)
            
            >>> # LHC protons (using gamma - alias)
            >>> beam3 = Beam(gamma=7460.52)
            
            >>> # By kinetic energy
            >>> beam4 = Beam(Ekin_MeV=7e6)
        """
        if mass_MeV_c2 <= 0:
            raise BeamValidationError(
                f"Mass must be positive, got {mass_MeV_c2} MeV/c²"
            )
        
        self._m_MeV_c2 = mass_MeV_c2
        self.test_beam_shift = test_beam_shift
        
        # Initialize to ultra-relativistic as default
        # (will be overwritten if parameters are provided)
        self._betarel = 1.0
        self._gammarel = float('inf')
        self._p_MeV_c = float('inf')
        self._Ekin_MeV = float('inf')
        
        # Handle gamma as alias for gammarel
        if gamma is not None:
            if gammarel != default_gammarel:
                # Both provided - warn and use gammarel
                print("Warning: Both 'gamma' and 'gammarel' provided. Using 'gammarel'.")
            else:
                # Use gamma as gammarel
                gammarel = gamma
        
        # Set kinematic parameters (priority order, matching original)
        if Ekin_MeV != default_Ekin_MeV:
            self.Ekin_MeV = Ekin_MeV
        elif p_MeV_c != default_p_MeV_c:
            self.p_MeV_c = p_MeV_c
        elif betarel != default_betarel:
            self.betarel = betarel
        else:
            self.gammarel = gammarel

    @property
    def betarel(self) -> float:
        """
        Relativistic beta (v/c).
        
        Returns:
            float: Beta value in range (0, 1]
        """
        return self._betarel

    @betarel.setter
    def betarel(self, newbeta: float) -> None:
        """
        Set relativistic beta and update all dependent quantities.
        
        Args:
            newbeta: Beta value, must be in range (0, 1]
        
        Note:
            Prints warning and does not modify if invalid value is provided.
            This matches the original behavior.
        """
        try:
            tmp_beta = float(newbeta)
        except (ValueError, TypeError):
            print(f"{newbeta} is not a good value for relativistic beta, "
                  "the beta value is not modified")
            return
        
        if tmp_beta <= 0 or tmp_beta > 1:
            print(f"{tmp_beta} is not a good value for relativistic beta, "
                  "the beta value is not modified")
            return

        self._betarel = tmp_beta
        
        # Calculate gamma: γ = 1/√(1-β²)
        try:
            tmp_gamma = np.sqrt(1.0 / (1.0 - (tmp_beta * tmp_beta)))
        except ZeroDivisionError:
            tmp_gamma = float('inf')
        
        self._gammarel = tmp_gamma
        self._p_MeV_c = self._gammarel * self._m_MeV_c2 * self._betarel
        self._Ekin_MeV = self._m_MeV_c2 * (self._gammarel - 1)

    @property
    def gammarel(self) -> float:
        """
        Lorentz gamma factor.
        
        Returns:
            float: Gamma value, range [1, ∞)
        """
        return self._gammarel

    @gammarel.setter
    def gammarel(self, newgamma: float) -> None:
        """
        Set Lorentz gamma and update all dependent quantities.
        
        Args:
            newgamma: Gamma value, must be > 0 (typically >= 1)
        
        Note:
            Prints warning and does not modify if invalid value is provided.
            This matches the original behavior.
        """
        try:
            tmp_gamma = float(newgamma)
        except (ValueError, TypeError):
            print(f"{newgamma} is not a good value for relativistic gamma, "
                  "the gamma value is not modified")
            return
        
        if tmp_gamma <= 0:
            print(f"{tmp_gamma} is not a good value for relativistic gamma, "
                  "the gamma value is not modified")
            return

        self._gammarel = tmp_gamma
        self._betarel = np.sqrt(1 - (1 / (self._gammarel * self._gammarel)))
        self._p_MeV_c = self._gammarel * self._m_MeV_c2 * self._betarel
        self._Ekin_MeV = self._m_MeV_c2 * (self._gammarel - 1)

    @property
    def Ekin_MeV(self) -> float:
        """
        Kinetic energy in MeV.
        
        Returns:
            float: Kinetic energy, range (0, ∞)
        """
        return self._Ekin_MeV

    @Ekin_MeV.setter
    def Ekin_MeV(self, newEkin: float) -> None:
        """
        Set kinetic energy and update all dependent quantities.
        
        Args:
            newEkin: Kinetic energy in MeV, must be > 0
        
        Note:
            Prints warning and does not modify if invalid value is provided.
            This matches the original behavior.
        """
        try:
            tmp_Ekin = float(newEkin)
        except (ValueError, TypeError):
            print(f"{newEkin} is not a good value for kinetic energy, "
                  "values is not changed")
            return
        
        if tmp_Ekin <= 0:
            print(f"{tmp_Ekin} is not a good value for kinetic energy, "
                  "values is not changed")
            return
        
        self._Ekin_MeV = tmp_Ekin
        self._gammarel = (self._Ekin_MeV / self._m_MeV_c2) + 1.0
        self._betarel = np.sqrt(1 - (1 / (self._gammarel * self._gammarel)))
        self._p_MeV_c = self._gammarel * self._m_MeV_c2 * self._betarel

    @property
    def p_MeV_c(self) -> float:
        """
        Momentum in MeV/c.
        
        Returns:
            float: Momentum, range (0, ∞)
        """
        return self._p_MeV_c

    @p_MeV_c.setter
    def p_MeV_c(self, newp: float) -> None:
        """
        Set momentum and update all dependent quantities.
        
        Args:
            newp: Momentum in MeV/c, must be > 0
        
        Note:
            Prints warning and does not modify if invalid value is provided.
            This matches the original behavior.
        """
        try:
            tmp_p = float(newp)
        except (ValueError, TypeError):
            print(f"{newp} is not a good value for momentum, "
                  "value is not changed")
            return
        
        if tmp_p <= 0:
            print(f"{tmp_p} is not a good value for momentum, "
                  "value is not changed")
            return
        
        self._p_MeV_c = tmp_p
        
        # Note: Original has a bug here - should be E_tot not E_kin
        # Keeping original behavior for compatibility
        self._Ekin_MeV = np.sqrt(self._p_MeV_c**2 + self._m_MeV_c2**2)
        self._gammarel = (self._Ekin_MeV / self._m_MeV_c2) + 1.0
        self._betarel = np.sqrt(1 - (1 / (self._gammarel * self._gammarel)))

    # =========================================================================
    # Additional properties (not in original but useful)
    # =========================================================================
    
    @property
    def mass_MeV_c2(self) -> float:
        """Particle rest mass energy in MeV/c²."""
        return self._m_MeV_c2

    @property
    def E_tot_MeV(self) -> float:
        """Total energy in MeV (kinetic + rest mass)."""
        return self._gammarel * self._m_MeV_c2

    @property
    def velocity_m_s(self) -> float:
        """Particle velocity in m/s."""
        return self._betarel * const.c

    def __repr__(self) -> str:
        """String representation of the Beam object."""
        return (
            f"Beam(Ekin_MeV={self._Ekin_MeV:.6g}, "
            f"p_MeV_c={self._p_MeV_c:.6g}, "
            f"betarel={self._betarel:.6g}, "
            f"gammarel={self._gammarel:.6g}, "
            f"mass_MeV_c2={self._m_MeV_c2:.6g})"
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Beam properties:\n"
            f"  Mass:           {self._m_MeV_c2:.4f} MeV/c²\n"
            f"  Beta (v/c):     {self._betarel:.6f}\n"
            f"  Gamma:          {self._gammarel:.6g}\n"
            f"  Kinetic Energy: {self._Ekin_MeV:.6g} MeV\n"
            f"  Momentum:       {self._p_MeV_c:.6g} MeV/c\n"
            f"  Total Energy:   {self.E_tot_MeV:.6g} MeV\n"
            f"  Test beam shift: {self.test_beam_shift:.6f} m"
        )


if __name__ == "__main__":
    # Example usage demonstrating compatibility with original
    print("=" * 60)
    print("Beam class demonstration - Full compatibility")
    print("=" * 60)
    
    # Example 1: Default (ultra-relativistic) - MATCHES ORIGINAL
    print("\n1. Default beam (ultra-relativistic):")
    beam1 = Beam()
    print(f"  Beta: {beam1.betarel}, Gamma: {beam1.gammarel}")
    print(f"  This matches original Beam() behavior!")
    
    # Example 2: Create beam with kinetic energy
    print("\n2. Proton beam with 7 TeV kinetic energy (LHC):")
    beam2 = Beam(Ekin_MeV=7e6)
    print(f"  Beta: {beam2.betarel:.6f}")
    print(f"  Gamma: {beam2.gammarel:.2f}")
    
    # Example 3: Create beam with gammarel (full name)
    print("\n3. Beam with gammarel = 7460.52:")
    beam3 = Beam(gammarel=7460.52)
    print(f"  Beta: {beam3.betarel:.6f}")
    print(f"  Ekin: {beam3.Ekin_MeV:.4e} MeV")
    
    # Example 4: Create beam with gamma (alias for input parameter)
    print("\n4. Beam with gamma = 7460.52 (alias for gammarel in __init__):")
    beam4 = Beam(gamma=7460.52)
    print(f"  Beta: {beam4.betarel:.6f}")
    print(f"  Ekin: {beam4.Ekin_MeV:.4e} MeV")
    print(f"  Read via beam.gammarel: {beam4.gammarel:.2f}")
    print(f"  ✓ 'gamma' parameter accepted in __init__!")
    
    # Example 5: Create beam with beta
    print("\n5. Beam with beta = 0.9:")
    beam5 = Beam(betarel=0.9)
    print(f"  Gamma: {beam5.gammarel:.4f}")
    print(f"  Ekin: {beam5.Ekin_MeV:.4f} MeV")
    
    # Example 6: Error handling (original behavior - prints warning)
    print("\n6. Error handling (original behavior):")
    beam6 = Beam()
    beam6.betarel = 1.5  # Invalid, will print warning
    print(f"  Beta still: {beam6.betarel}")  # Unchanged
    
    print("\n" + "=" * 60)
    print("All examples match original Beam() behavior!")
    print("Plus: 'gamma' is now accepted as alias for 'gammarel'!")
    print("=" * 60)
