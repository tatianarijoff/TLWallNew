"""
Plot Utilities for PyTLWall

This module provides plotting functions for visualizing impedance calculation results.
Supports various plot types, scales, and customization options.

Authors: Tatiana Rijoff, Carlo Zannini
Date: 01/03/2013
Updated: December 2025
Copyright: CERN
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union
import logging

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


# Configure logging
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Impedance units by type
IMPEDANCE_UNITS = {
    'L': r'$\Omega$',           # Longitudinal [Ohm]
    'T': r'$\Omega$/m',          # Transverse [Ohm/m]
    'S': r'$\Omega$ m',          # Surface [Ohm·m]
}

# Wake function units by type (time domain).
# Generic placeholders matching the codebase conventions; users can override
# the label via the `ylabel` argument of the plotting functions.
WAKE_UNITS = {
    'WL': r'V$\,$C$^{-1}\,$m$^{-1}$',   # Longitudinal wake
    'WT': r'V$\,$C$^{-1}\,$m$^{-2}$',   # Transverse wake
}

# Default plot style
DEFAULT_PLOT_STYLE = {
    'linewidth': 5,
    'title_fontsize': 24,
    'label_fontsize': 20,
    'tick_fontsize': 18,
    'legend_fontsize': 20,
    'grid': True,
}


# =============================================================================
# Helper Functions
# =============================================================================

def _get_impedance_unit(imped_type: str) -> str:
    """
    Get LaTeX formatted unit string for impedance type.
    
    Args:
        imped_type: Impedance type ('L', 'T', 'S')
    
    Returns:
        LaTeX formatted unit string
    """
    return IMPEDANCE_UNITS.get(imped_type, r'$\Omega$/m')


def _ensure_output_directory(savedir: Union[str, Path]) -> Path:
    """
    Ensure output directory exists, create if necessary.
    
    Args:
        savedir: Directory path
    
    Returns:
        Path object of the directory
    """
    dir_path = Path(savedir)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def _save_figure(
    fig: Figure,
    savedir: Optional[str],
    savename: Optional[str]
) -> None:
    """
    Save figure to file if savename is provided.
    
    Args:
        fig: Matplotlib figure to save
        savedir: Output directory path
        savename: Output filename
    """
    if savename is None:
        return
    
    if savedir is None:
        savedir = '.'
    
    output_path = _ensure_output_directory(savedir) / savename
    
    try:
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Figure saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving figure: {e}")
        raise


def _apply_scale(ax: plt.Axes, xscale: str, yscale: str) -> None:
    """
    Apply axis scales to plot.
    
    Args:
        ax: Matplotlib axes
        xscale: X-axis scale ('lin', 'log', 'symlog')
        yscale: Y-axis scale ('lin', 'log', 'symlog')
    """
    valid_scales = ['lin', 'log', 'symlog']
    
    if xscale in valid_scales and xscale != 'lin':
        ax.set_xscale(xscale)
    
    if yscale in valid_scales and yscale != 'lin':
        ax.set_yscale(yscale)


def _filter_nan_values(
    f: np.ndarray,
    Z: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove NaN values from frequency and impedance arrays.
    
    Args:
        f: Frequency array
        Z: Impedance array (may be complex)
    
    Returns:
        Tuple of (filtered_f, filtered_Z)
    """
    # Handle complex impedance
    if np.iscomplexobj(Z):
        mask = np.logical_not(np.isnan(Z.real) | np.isnan(Z.imag))
    else:
        mask = np.logical_not(np.isnan(Z))
    
    return f[mask], Z[mask]


# =============================================================================
# Main Plotting Functions
# =============================================================================

def plot_Z_vs_f_simple(
    f: np.ndarray,
    Z: np.ndarray,
    imped_type: str = 'L',
    title: Optional[str] = None,
    savedir: Optional[str] = None,
    savename: Optional[str] = None,
    xscale: str = 'lin',
    yscale: str = 'lin',
    figsize: Tuple[float, float] = (10, 6)
) -> Optional[Figure]:
    """
    Plot impedance vs frequency (real and imaginary parts separately).
    
    Args:
        f: Frequency array [Hz]
        Z: Complex impedance array
        imped_type: Impedance type ('L'=longitudinal, 'T'=transverse, 'S'=surface)
        title: Plot title
        savedir: Output directory for saving plot
        savename: Output filename
        xscale: X-axis scale ('lin', 'log', 'symlog')
        yscale: Y-axis scale ('lin', 'log', 'symlog')
        figsize: Figure size (width, height) in inches
    
    Returns:
        Matplotlib figure or None if no data
    
    Example:
        >>> fig = plot_Z_vs_f_simple(f, Z, imped_type='L', xscale='log')
        >>> plt.show()
    """
    # Filter NaN values separately for real and imaginary parts
    mask_real = np.logical_not(np.isnan(Z.real))
    fRe = f[mask_real]
    ZRe = Z[mask_real].real
    
    mask_imag = np.logical_not(np.isnan(Z.imag))
    fIm = f[mask_imag]
    ZIm = Z[mask_imag].imag
    
    # Check if we have data to plot
    if len(fRe) == 0 and len(fIm) == 0:
        logger.warning("No valid data to plot")
        return None
    
    if savename:
        logger.info(f"Creating plot: {savename}")
    
    # Get impedance unit
    Z_unit = _get_impedance_unit(imped_type)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Set title
    if title is not None:
        ax.set_title(title, fontsize=DEFAULT_PLOT_STYLE['title_fontsize'])
    
    # Plot data
    if len(fRe) > 0:
        ax.plot(fRe, ZRe, linewidth=DEFAULT_PLOT_STYLE['linewidth'], 
                label='Real', color='blue')
    
    if len(fIm) > 0:
        ax.plot(fIm, ZIm, linewidth=DEFAULT_PLOT_STYLE['linewidth'], 
                label='Imaginary', color='red')
    
    # Labels and formatting
    ax.set_ylabel(f'Z [{Z_unit}]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax.set_xlabel('f [Hz]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    
    # Apply scales
    _apply_scale(ax, xscale, yscale)
    
    # Tick formatting
    ax.tick_params(labelsize=DEFAULT_PLOT_STYLE['tick_fontsize'])
    
    # Grid and legend
    if DEFAULT_PLOT_STYLE['grid']:
        ax.grid(True, alpha=0.3)
    
    ax.legend(loc='best', fontsize=DEFAULT_PLOT_STYLE['legend_fontsize'])
    
    # Layout
    fig.tight_layout()
    
    # Save if requested
    _save_figure(fig, savedir, savename)
    
    return fig


def plot_Z_vs_f_simple_single(
    f: np.ndarray,
    Z: np.ndarray,
    imped_type: str = 'L',
    title: Optional[str] = None,
    savedir: Optional[str] = None,
    savename: Optional[str] = None,
    xscale: str = 'lin',
    yscale: str = 'lin',
    figsize: Tuple[float, float] = (10, 6),
    color: str = 'blue'
) -> Optional[Figure]:
    """
    Plot single impedance component vs frequency.
    
    Args:
        f: Frequency array [Hz]
        Z: Impedance array (real or complex)
        imped_type: Impedance type ('L'=longitudinal, 'T'=transverse, 'S'=surface)
        title: Plot title
        savedir: Output directory for saving plot
        savename: Output filename
        xscale: X-axis scale ('lin', 'log', 'symlog')
        yscale: Y-axis scale ('lin', 'log', 'symlog')
        figsize: Figure size (width, height) in inches
        color: Line color
    
    Returns:
        Matplotlib figure or None if no data
    
    Example:
        >>> fig = plot_Z_vs_f_simple_single(f, Z.real, xscale='log')
        >>> plt.show()
    """
    # Filter NaN values
    f_clean, Z_clean = _filter_nan_values(f, Z)
    
    # Check if we have data
    if len(f_clean) == 0:
        logger.warning("No valid data to plot")
        return None
    
    # Get impedance unit
    Z_unit = _get_impedance_unit(imped_type)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Set title
    if title is not None:
        ax.set_title(title, fontsize=DEFAULT_PLOT_STYLE['title_fontsize'])
    
    # Plot data
    ax.plot(f_clean, Z_clean, linewidth=DEFAULT_PLOT_STYLE['linewidth'], 
            color=color)
    
    # Labels and formatting
    ax.set_ylabel(f'Z [{Z_unit}]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax.set_xlabel('f [Hz]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    
    # Apply scales
    _apply_scale(ax, xscale, yscale)
    
    # Tick formatting
    ax.tick_params(labelsize=DEFAULT_PLOT_STYLE['tick_fontsize'])
    
    # Grid
    if DEFAULT_PLOT_STYLE['grid']:
        ax.grid(True, alpha=0.3)
    
    # Layout
    fig.tight_layout()
    
    # Save if requested
    _save_figure(fig, savedir, savename)
    
    return fig


def plot_Z_vs_f_simple_single_compare(
    list_f: List[np.ndarray],
    list_Z: List[np.ndarray],
    list_label: List[str],
    imped_type: str = 'L',
    title: Optional[str] = None,
    savedir: Optional[str] = None,
    savename: Optional[str] = None,
    xscale: str = 'lin',
    yscale: str = 'lin',
    figsize: Tuple[float, float] = (10, 6)
) -> Optional[Figure]:
    """
    Compare multiple impedance curves on a single plot.
    
    Args:
        list_f: List of frequency arrays [Hz]
        list_Z: List of impedance arrays
        list_label: List of labels for each curve
        imped_type: Impedance type ('L'=longitudinal, 'T'=transverse, 'S'=surface)
        title: Plot title
        savedir: Output directory for saving plot
        savename: Output filename
        xscale: X-axis scale ('lin', 'log', 'symlog')
        yscale: Y-axis scale ('lin', 'log', 'symlog')
        figsize: Figure size (width, height) in inches
    
    Returns:
        Matplotlib figure or None if no data
    
    Example:
        >>> fig = plot_Z_vs_f_simple_single_compare(
        ...     [f1, f2], [Z1, Z2], ['Model 1', 'Model 2'],
        ...     xscale='log'
        ... )
        >>> plt.show()
    """
    if not list_f or not list_Z or not list_label:
        logger.warning("Empty input lists")
        return None
    
    if len(list_f) != len(list_Z) or len(list_f) != len(list_label):
        logger.error("Input lists must have same length")
        raise ValueError("list_f, list_Z, and list_label must have same length")
    
    # Get impedance unit
    Z_unit = _get_impedance_unit(imped_type)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Set title
    if title is not None:
        ax.set_title(title, fontsize=DEFAULT_PLOT_STYLE['title_fontsize'])
    
    # Plot each curve with decreasing linewidth
    num_curves = len(list_label)
    for i, (f, Z, label) in enumerate(zip(list_f, list_Z, list_label)):
        # Filter NaN values
        f_clean, Z_clean = _filter_nan_values(f, Z)
        
        if len(f_clean) == 0:
            logger.warning(f"No valid data for '{label}'")
            continue
        
        # Linewidth decreases for overlaid plots
        linewidth = num_curves * 3 - 2 * i
        ax.plot(f_clean, Z_clean, linewidth=linewidth, label=label)
    
    # Labels and formatting
    ax.set_ylabel(f'Z [{Z_unit}]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax.set_xlabel('f [Hz]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    
    # Apply scales
    _apply_scale(ax, xscale, yscale)
    
    # Tick formatting
    ax.tick_params(labelsize=DEFAULT_PLOT_STYLE['tick_fontsize'])
    
    # Grid and legend
    if DEFAULT_PLOT_STYLE['grid']:
        ax.grid(True, alpha=0.3)
    
    ax.legend(loc='best', fontsize=DEFAULT_PLOT_STYLE['legend_fontsize'])
    
    # Layout
    fig.tight_layout()
    
    # Save if requested
    _save_figure(fig, savedir, savename)
    
    return fig


def plot_list_Z_vs_f(
    f: np.ndarray,
    list_Z: List[np.ndarray],
    list_label: List[str],
    imped_type: str = 'L',
    title: Optional[str] = None,
    savedir: Optional[str] = None,
    savename: Optional[str] = None,
    xscale: str = 'lin',
    yscale: str = 'lin',
    figsize: Tuple[float, float] = (10, 6)
) -> Optional[Figure]:
    """
    Plot multiple impedance curves with shared frequency axis.
    
    Args:
        f: Common frequency array [Hz]
        list_Z: List of impedance arrays
        list_label: List of labels for each curve
        imped_type: Impedance type ('L'=longitudinal, 'T'=transverse, 'S'=surface)
        title: Plot title
        savedir: Output directory for saving plot
        savename: Output filename
        xscale: X-axis scale ('lin', 'log', 'symlog')
        yscale: Y-axis scale ('lin', 'log', 'symlog')
        figsize: Figure size (width, height) in inches
    
    Returns:
        Matplotlib figure or None if no data
    
    Example:
        >>> fig = plot_list_Z_vs_f(
        ...     f, [ZLong, ZTrans], ['Longitudinal', 'Transverse'],
        ...     xscale='log'
        ... )
        >>> plt.show()
    """
    if not list_Z or not list_label:
        logger.warning("Empty input lists")
        return None
    
    if len(list_Z) != len(list_label):
        logger.error("Input lists must have same length")
        raise ValueError("list_Z and list_label must have same length")
    
    # Get impedance unit
    Z_unit = _get_impedance_unit(imped_type)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Set title
    if title is not None:
        ax.set_title(title, fontsize=DEFAULT_PLOT_STYLE['title_fontsize'])
    
    # Plot each curve with decreasing linewidth
    num_curves = len(list_label)
    for i, (Z, label) in enumerate(zip(list_Z, list_label)):
        # Filter NaN values
        f_clean, Z_clean = _filter_nan_values(f, Z)
        
        if len(f_clean) == 0:
            logger.warning(f"No valid data for '{label}'")
            continue
        
        # Linewidth decreases for overlaid plots
        linewidth = num_curves * 3 - 2 * i
        ax.plot(f_clean, Z_clean, linewidth=linewidth, label=label)
    
    # Labels and formatting
    ax.set_ylabel(f'Z [{Z_unit}]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax.set_xlabel('f [Hz]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    
    # Apply scales
    _apply_scale(ax, xscale, yscale)
    
    # Tick formatting
    ax.tick_params(labelsize=DEFAULT_PLOT_STYLE['tick_fontsize'])
    
    # Grid and legend
    if DEFAULT_PLOT_STYLE['grid']:
        ax.grid(True, alpha=0.3)
    
    ax.legend(loc='best', fontsize=DEFAULT_PLOT_STYLE['legend_fontsize'])
    
    # Layout
    fig.tight_layout()
    
    # Save if requested
    _save_figure(fig, savedir, savename)
    
    return fig


# =============================================================================
# Advanced Plotting Functions
# =============================================================================

def plot_impedance_magnitude_phase(
    f: np.ndarray,
    Z: np.ndarray,
    imped_type: str = 'L',
    title: Optional[str] = None,
    savedir: Optional[str] = None,
    savename: Optional[str] = None,
    xscale: str = 'log',
    figsize: Tuple[float, float] = (10, 8)
) -> Optional[Figure]:
    """
    Plot impedance magnitude and phase in two subplots.
    
    Args:
        f: Frequency array [Hz]
        Z: Complex impedance array
        imped_type: Impedance type ('L'=longitudinal, 'T'=transverse, 'S'=surface)
        title: Plot title
        savedir: Output directory for saving plot
        savename: Output filename
        xscale: X-axis scale ('lin', 'log', 'symlog')
        figsize: Figure size (width, height) in inches
    
    Returns:
        Matplotlib figure or None if no data
    
    Example:
        >>> fig = plot_impedance_magnitude_phase(f, Z, xscale='log')
        >>> plt.show()
    """
    # Filter NaN values
    f_clean, Z_clean = _filter_nan_values(f, Z)
    
    if len(f_clean) == 0:
        logger.warning("No valid data to plot")
        return None
    
    # Calculate magnitude and phase
    magnitude = np.abs(Z_clean)
    phase = np.angle(Z_clean, deg=True)
    
    # Get impedance unit
    Z_unit = _get_impedance_unit(imped_type)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
    
    # Overall title
    if title is not None:
        fig.suptitle(title, fontsize=DEFAULT_PLOT_STYLE['title_fontsize'])
    
    # Magnitude plot
    ax1.plot(f_clean, magnitude, linewidth=DEFAULT_PLOT_STYLE['linewidth'], 
             color='blue')
    ax1.set_ylabel(f'|Z| [{Z_unit}]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax1.tick_params(labelsize=DEFAULT_PLOT_STYLE['tick_fontsize'])
    ax1.grid(True, alpha=0.3)
    
    # Phase plot
    ax2.plot(f_clean, phase, linewidth=DEFAULT_PLOT_STYLE['linewidth'], 
             color='red')
    ax2.set_ylabel('Phase [°]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax2.set_xlabel('f [Hz]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax2.tick_params(labelsize=DEFAULT_PLOT_STYLE['tick_fontsize'])
    ax2.grid(True, alpha=0.3)
    
    # Apply scale to both plots
    if xscale != 'lin':
        ax1.set_xscale(xscale)
        ax2.set_xscale(xscale)
    
    # Layout
    fig.tight_layout()
    
    # Save if requested
    _save_figure(fig, savedir, savename)
    
    return fig


# =============================================================================
# Time-Domain Wake Plotting Functions
# =============================================================================
#
# These helpers mirror the frequency-domain plotting functions but accept a
# time array (in seconds) and a real-valued wake array. They are the
# counterpart used by :class:`pytlwall.tlwall_wake.TLWallWake`.


def _get_wake_unit(wake_type: str) -> str:
    """
    Return a LaTeX-formatted unit string for a wake plot.

    Args:
        wake_type: 'WL' for longitudinal wake or 'WT' for transverse wake.

    Returns:
        LaTeX-formatted unit string.
    """
    return WAKE_UNITS.get(wake_type, r'V$\,$C$^{-1}\,$m$^{-1}$')


def _filter_nan_real(t: np.ndarray, W: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Drop NaN samples from a (time, real-wake) pair.

    Args:
        t: Time array.
        W: Real-valued wake array.

    Returns:
        Tuple of cleaned (t, W) arrays.
    """
    W = np.asarray(W, dtype=float)
    mask = np.isfinite(W)
    return np.asarray(t, dtype=float)[mask], W[mask]


def plot_W_vs_t_simple(
    t: np.ndarray,
    W: np.ndarray,
    wake_type: str = 'WL',
    title: Optional[str] = None,
    savedir: Optional[str] = None,
    savename: Optional[str] = None,
    xscale: str = 'log',
    yscale: str = 'log',
    figsize: Tuple[float, float] = (10, 6),
    color: str = 'tab:blue',
    label: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> Optional[Figure]:
    """
    Plot a single real-valued wake function versus time.

    Args:
        t: Time array [s].
        W: Real-valued wake array (same length as ``t``).
        wake_type: 'WL' (longitudinal) or 'WT' (transverse); selects the
            default y-axis unit label.
        title: Optional plot title.
        savedir: Output directory for saving the figure.
        savename: Output filename (extension determines format).
        xscale: X-axis scale: 'lin', 'log' (default), or 'symlog'.
        yscale: Y-axis scale: 'lin', 'log' (default), or 'symlog'.
        figsize: Figure size in inches.
        color: Line color.
        label: Optional legend label for the curve.
        ylabel: Override the default y-axis label.

    Returns:
        The matplotlib :class:`Figure`, or ``None`` if there is no
        finite data to plot.

    Example
    -------
    >>> fig = plot_W_vs_t_simple(times.time_s, wake.WLong, 'WL',
    ...                          xscale='log', yscale='log')
    """
    t_clean, W_clean = _filter_nan_real(t, W)

    if len(t_clean) == 0:
        logger.warning("No valid data to plot")
        return None

    if savename:
        logger.info(f"Creating wake plot: {savename}")

    W_unit = _get_wake_unit(wake_type)

    fig, ax = plt.subplots(figsize=figsize)

    if title is not None:
        ax.set_title(title, fontsize=DEFAULT_PLOT_STYLE['title_fontsize'])

    ax.plot(
        t_clean, W_clean,
        linewidth=DEFAULT_PLOT_STYLE['linewidth'],
        label=label, color=color,
    )

    default_ylabel = f'W [{W_unit}]'
    ax.set_ylabel(ylabel if ylabel is not None else default_ylabel,
                  fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax.set_xlabel('t [s]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])

    _apply_scale(ax, xscale, yscale)
    ax.tick_params(labelsize=DEFAULT_PLOT_STYLE['tick_fontsize'])

    if DEFAULT_PLOT_STYLE['grid']:
        ax.grid(True, which='both', alpha=0.3)

    if label is not None:
        ax.legend(loc='best', fontsize=DEFAULT_PLOT_STYLE['legend_fontsize'])

    fig.tight_layout()
    _save_figure(fig, savedir, savename)
    return fig


def plot_list_W_vs_t(
    t: np.ndarray,
    list_W: List[np.ndarray],
    list_label: List[str],
    wake_type: str = 'WL',
    title: Optional[str] = None,
    savedir: Optional[str] = None,
    savename: Optional[str] = None,
    xscale: str = 'log',
    yscale: str = 'log',
    figsize: Tuple[float, float] = (10, 6),
    colors: Optional[List[str]] = None,
    linestyles: Optional[List[str]] = None,
    ylabel: Optional[str] = None,
) -> Optional[Figure]:
    """
    Plot several wake curves versus a common time axis.

    Intended primarily for comparing the calculator output against the
    Thick-/Thin-wall analytical reference wakes on the same axes.

    Args:
        t: Common time array [s].
        list_W: List of real-valued wake arrays. All must have the same
            length as ``t``.
        list_label: List of legend labels (must match ``list_W`` in length).
        wake_type: 'WL' or 'WT' — selects the default y-axis label unit.
        title: Optional plot title.
        savedir: Output directory for saving the figure.
        savename: Output filename.
        xscale: X-axis scale: 'lin', 'log' (default), or 'symlog'.
        yscale: Y-axis scale: 'lin', 'log' (default), or 'symlog'.
        figsize: Figure size in inches.
        colors: Optional list of matplotlib color specs, one per curve.
        linestyles: Optional list of matplotlib linestyles, one per curve.
        ylabel: Override the default y-axis label.

    Returns:
        The matplotlib :class:`Figure`, or ``None`` if all inputs were
        empty.

    Example
    -------
    >>> fig = plot_list_W_vs_t(
    ...     t,
    ...     [wake.WLong, wake.WLongThick, wake.WLongThin],
    ...     ['Calc', 'Thick limit', 'Thin limit'],
    ...     wake_type='WL', xscale='log', yscale='log',
    ... )
    """
    if not list_W or not list_label:
        logger.warning("Empty input lists")
        return None

    if len(list_W) != len(list_label):
        logger.error("list_W and list_label must have the same length")
        raise ValueError("list_W and list_label must have the same length")

    W_unit = _get_wake_unit(wake_type)

    fig, ax = plt.subplots(figsize=figsize)

    if title is not None:
        ax.set_title(title, fontsize=DEFAULT_PLOT_STYLE['title_fontsize'])

    num_curves = len(list_label)
    for i, (W, label) in enumerate(zip(list_W, list_label)):
        t_clean, W_clean = _filter_nan_real(t, W)
        if len(t_clean) == 0:
            logger.warning(f"No valid data for '{label}'")
            continue

        # Decreasing linewidth so overlaid curves remain visible.
        linewidth = max(2, num_curves * 3 - 2 * i)
        color = colors[i] if (colors is not None and i < len(colors)) else None
        ls = linestyles[i] if (linestyles is not None and i < len(linestyles)) else '-'

        ax.plot(t_clean, W_clean, linewidth=linewidth, label=label,
                color=color, linestyle=ls)

    default_ylabel = f'W [{W_unit}]'
    ax.set_ylabel(ylabel if ylabel is not None else default_ylabel,
                  fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])
    ax.set_xlabel('t [s]', fontsize=DEFAULT_PLOT_STYLE['label_fontsize'])

    _apply_scale(ax, xscale, yscale)
    ax.tick_params(labelsize=DEFAULT_PLOT_STYLE['tick_fontsize'])

    if DEFAULT_PLOT_STYLE['grid']:
        ax.grid(True, which='both', alpha=0.3)

    ax.legend(loc='best', fontsize=DEFAULT_PLOT_STYLE['legend_fontsize'])

    fig.tight_layout()
    _save_figure(fig, savedir, savename)
    return fig


def plot_wake_vs_limits(
    t: np.ndarray,
    W_calc: np.ndarray,
    W_thick: np.ndarray,
    W_thin: np.ndarray,
    wake_type: str = 'WL',
    title: Optional[str] = None,
    savedir: Optional[str] = None,
    savename: Optional[str] = None,
    calc_label: str = 'TLWallWake (full)',
    thick_label: str = 'Thick-wall limit',
    thin_label: str = 'Thin-wall limit',
    figsize: Tuple[float, float] = (10, 6),
) -> Optional[Figure]:
    """
    Plot a computed wake against its Thick-wall and Thin-wall analytical limits.

    Convenience wrapper around :func:`plot_list_W_vs_t` with a fixed colour
    and linestyle scheme suitable for visually validating the calculator
    against the two asymptotic regimes.

    Args:
        t: Time array [s].
        W_calc: Wake from :class:`TLWallWake` (full calculation).
        W_thick: Thick-wall (resistive) analytical limit.
        W_thin: Thin-wall (inductive) analytical limit.
        wake_type: 'WL' or 'WT'.
        title: Optional plot title.
        savedir, savename: Output directory and filename.
        calc_label, thick_label, thin_label: Override the legend labels.
        figsize: Figure size in inches.

    Returns:
        The matplotlib :class:`Figure`, or ``None`` if all inputs were empty.
    """
    return plot_list_W_vs_t(
        t=t,
        list_W=[W_calc, W_thick, W_thin],
        list_label=[calc_label, thick_label, thin_label],
        wake_type=wake_type,
        title=title,
        savedir=savedir,
        savename=savename,
        xscale='log',
        yscale='log',
        figsize=figsize,
        colors=['tab:blue', 'tab:red', 'tab:green'],
        linestyles=['-', '--', ':'],
    )


# =============================================================================
# Convenience Functions
# =============================================================================

def close_all_figures() -> None:
    """Close all matplotlib figures."""
    plt.close('all')
    logger.info("All figures closed")


def set_plot_style(style: str = 'default') -> None:
    """
    Set matplotlib plot style.
    
    Args:
        style: Style name ('default', 'seaborn', 'ggplot', etc.)
    
    Example:
        >>> set_plot_style('seaborn')
    """
    try:
        plt.style.use(style)
        logger.info(f"Plot style set to: {style}")
    except Exception as e:
        logger.warning(f"Could not set style '{style}': {e}")
