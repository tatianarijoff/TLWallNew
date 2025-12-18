"""
Impedance constants for pytlwall GUI.

This module defines the available impedance types and their display properties.

Authors: Tatiana Rijoff
Date: December 2025
"""

# List of all available impedance names
# Order determines display order in the GUI
IMPEDANCE_NAMES = [
    # Longitudinal impedances
    "ZLong",          # Base longitudinal (wall contribution) - MANDATORY
    "ZLongTotal",     # Total longitudinal (wall + space charge)
    "ZLongSurf",      # Surface longitudinal impedance
    "ZLongDSC",       # Direct space charge longitudinal
    "ZLongISC",       # Indirect/image space charge longitudinal
    
    # Transverse impedances
    "ZTrans",         # Base transverse (wall contribution) - MANDATORY
    "ZTransTotal",    # Total transverse (wall + space charge)
    "ZTransSurf",     # Surface transverse impedance
    "ZTransDSC",      # Direct space charge transverse
    "ZTransISC",      # Indirect/image space charge transverse
    
    # Dipolar impedances
    "ZDipX",          # Horizontal dipolar (wall contribution)
    "ZDipY",          # Vertical dipolar (wall contribution)
    "ZDipXTotal",     # Total horizontal dipolar
    "ZDipYTotal",     # Total vertical dipolar
    
    # Quadrupolar impedances
    "ZQuadX",         # Horizontal quadrupolar (wall contribution)
    "ZQuadY",         # Vertical quadrupolar (wall contribution)
    "ZQuadXTotal",    # Total horizontal quadrupolar
    "ZQuadYTotal",    # Total vertical quadrupolar
]

# Impedances that cannot be deselected (always computed)
MANDATORY_IMPEDANCES = {"ZLong", "ZTrans"}

# Impedances that are checked by default
# Note: ZTransTotal, ZDipXTotal, ZDipYTotal, ZQuadXTotal, ZQuadYTotal are NOT default
# because they showed inconsistencies with IW2D reference calculations
DEFAULT_IMPEDANCES = {
    "ZLong",        # mandatory
    "ZTrans",       # mandatory
    "ZLongISC",     # Indirect space charge longitudinal
    "ZLongTotal",   # Long Total is consistent with IW2D
    "ZDipX",        # Dipolar X wall contribution
    "ZDipY",        # Dipolar Y wall contribution
    "ZQuadX",       # Quadrupolar X wall contribution
    "ZQuadY",       # Quadrupolar Y wall contribution
}

# Mapping of impedance names to display names (optional)
IMPEDANCE_DISPLAY_NAMES = {
    "ZLong": "Z Longitudinal",
    "ZLongTotal": "Z Longitudinal Total",
    "ZLongSurf": "Z Longitudinal Surface",
    "ZLongDSC": "Z Long DSC",
    "ZLongISC": "Z Long ISC",
    "ZTrans": "Z Transverse",
    "ZTransTotal": "Z Transverse Total",
    "ZTransSurf": "Z Transverse Surface",
    "ZTransDSC": "Z Trans DSC",
    "ZTransISC": "Z Trans ISC",
    "ZDipX": "Z Dipolar X",
    "ZDipY": "Z Dipolar Y",
    "ZDipXTotal": "Z Dipolar X Total",
    "ZDipYTotal": "Z Dipolar Y Total",
    "ZQuadX": "Z Quadrupolar X",
    "ZQuadY": "Z Quadrupolar Y",
    "ZQuadXTotal": "Z Quadrupolar X Total",
    "ZQuadYTotal": "Z Quadrupolar Y Total",
}

# Impedance types for plotting (L = longitudinal, T = transverse)
IMPEDANCE_TYPES = {
    "ZLong": "L",
    "ZLongTotal": "L",
    "ZLongSurf": "L",
    "ZLongDSC": "L",
    "ZLongISC": "L",
    "ZTrans": "T",
    "ZTransTotal": "T",
    "ZTransSurf": "T",
    "ZTransDSC": "T",
    "ZTransISC": "T",
    "ZDipX": "T",
    "ZDipY": "T",
    "ZDipXTotal": "T",
    "ZDipYTotal": "T",
    "ZQuadX": "T",
    "ZQuadY": "T",
    "ZQuadXTotal": "T",
    "ZQuadYTotal": "T",
}

# ID used for the "Total" chamber (sum of all chambers in accelerator)
TOTAL_CHAMBER_ID = "Total"
