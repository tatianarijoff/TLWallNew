#!/usr/bin/env python3
"""
Example usage of pytlwall.logging_util module for normal (non-test) usage.

This demonstrates how to use the centralized logging module
in your regular PyTLWall scripts and applications.
"""

# Add parent directory to path to allow imports when running from examples/ directory
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pytlwall import logging_util


def example_basic_usage():
    """Example 1: Basic usage with quick setup."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Usage")
    print("="*80)
    
    # Quick setup - returns log path and logger
    log_path, logger = logging_util.quick_setup(
        log_dir="./my_logs/",
        log_basename="my_calculation",
        verbosity=2,
    )
    
    logger.info("Starting calculation...")
    logger.info("Processing data...")
    logger.warning("This is a warning message")
    logger.info("Calculation completed successfully")
    
    print(f"\nLog saved to: {log_path}")


def example_detailed_configuration():
    """Example 2: Detailed configuration with LogConfig class."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Detailed Configuration")
    print("="*80)
    
    # Create custom configuration
    config = logging_util.LogConfig(
        log_dir="./my_logs/",
        log_basename="detailed_calculation",
        verbosity=3,  # DEBUG level
        add_timestamp=True,
        console_output=True,
    )
    
    # Setup logging
    log_path = logging_util.setup_logging(config)
    logger = logging_util.get_logger(__name__)
    
    logger.debug("Debug message - only visible at verbosity >= 3")
    logger.info("Info message - visible at verbosity >= 2")
    logger.warning("Warning message - visible at verbosity >= 1")
    logger.error("Error message - always visible")
    
    print(f"\nLog saved to: {log_path}")


def example_with_sections():
    """Example 3: Using section headers for organized logs."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Organized Logging with Sections")
    print("="*80)
    
    log_path, logger = logging_util.quick_setup(
        log_dir="./my_logs/",
        log_basename="organized_calculation",
        verbosity=2,
    )
    
    # Main header
    logging_util.log_section_header(logger, "STARTING IMPEDANCE CALCULATION")
    
    # Setup section
    logging_util.log_section_header(logger, "Configuration", char="-", width=60)
    logger.info("Chamber radius: 50 mm")
    logger.info("Number of layers: 3")
    logger.info("Frequency range: 1e3 - 1e9 Hz")
    
    # Computation section
    logging_util.log_section_header(logger, "Computation", char="-", width=60)
    logger.info("Computing longitudinal impedance...")
    logger.info("Computing transverse impedance...")
    
    # Results section
    logging_util.log_section_header(logger, "Results", char="-", width=60)
    logger.info("Maximum ZLong: 1.23e-3 Ohm")
    logger.info("Maximum ZTrans: 4.56e-2 Ohm/m")
    
    logging_util.log_section_header(logger, "CALCULATION COMPLETED SUCCESSFULLY")
    
    print(f"\nLog saved to: {log_path}")


def example_without_console_output():
    """Example 4: File-only logging (no console output)."""
    print("\n" + "="*80)
    print("EXAMPLE 4: File-Only Logging")
    print("="*80)
    
    config = logging_util.LogConfig(
        log_dir="./my_logs/",
        log_basename="silent_calculation",
        verbosity=2,
        console_output=False,  # No console output
    )
    
    log_path = logging_util.setup_logging(config)
    logger = logging_util.get_logger(__name__)
    
    # These messages will only go to the file
    logger.info("This message appears only in the log file")
    logger.info("No console clutter!")
    
    print(f"Log saved to: {log_path} (no console output was produced)")


def example_multiple_loggers():
    """Example 5: Using multiple named loggers."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Multiple Named Loggers")
    print("="*80)
    
    log_path, _ = logging_util.quick_setup(
        log_dir="./my_logs/",
        log_basename="multi_logger",
        verbosity=2,
    )
    
    # Get different loggers for different modules
    logger_main = logging_util.get_logger("main")
    logger_calc = logging_util.get_logger("calculation")
    logger_io = logging_util.get_logger("io")
    
    logger_main.info("Main program started")
    logger_calc.info("Starting calculation module")
    logger_io.info("Reading input file")
    logger_calc.info("Calculation completed")
    logger_io.info("Writing output file")
    logger_main.info("Main program completed")
    
    print(f"\nLog saved to: {log_path}")


def example_pytlwall_workflow():
    """Example 6: Complete PyTLWall workflow with logging."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Complete PyTLWall Workflow")
    print("="*80)
    
    # Setup logging for the entire workflow
    config = logging_util.LogConfig(
        log_dir="./my_logs/",
        log_basename="pytlwall_workflow",
        verbosity=2,
        add_timestamp=True,
    )
    
    log_path = logging_util.setup_logging(config)
    logger = logging_util.get_logger("pytlwall_workflow")
    
    # Start workflow
    logging_util.log_section_header(logger, "PYTLWALL IMPEDANCE CALCULATION WORKFLOW")
    logger.info(f"Timestamp: {logging_util.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_path}")
    logger.info("")
    
    # Phase 1: Configuration
    logging_util.log_section_header(logger, "Phase 1: Configuration", char="-", width=60)
    logger.info("Reading configuration file: config.cfg")
    logger.info("Validating parameters...")
    logger.info("Configuration loaded successfully")
    logger.info("")
    
    # Phase 2: Geometry setup
    logging_util.log_section_header(logger, "Phase 2: Geometry Setup", char="-", width=60)
    logger.info("Building wall structure...")
    logger.info("  - Number of layers: 3")
    logger.info("  - Chamber type: circular")
    logger.info("  - Radius: 50.0 mm")
    logger.info("Geometry setup completed")
    logger.info("")
    
    # Phase 3: Frequency setup
    logging_util.log_section_header(logger, "Phase 3: Frequency Setup", char="-", width=60)
    logger.info("Frequency range: 1.0e+03 to 1.0e+09 Hz")
    logger.info("Number of points: 1000")
    logger.info("Scale: logarithmic")
    logger.info("")
    
    # Phase 4: Computation
    logging_util.log_section_header(logger, "Phase 4: Impedance Computation", char="-", width=60)
    logger.info("Computing longitudinal impedance...")
    logger.info("  - Progress: 100%")
    logger.info("Computing transverse impedance...")
    logger.info("  - Progress: 100%")
    logger.info("Computation completed successfully")
    logger.info("")
    
    # Phase 5: Output
    logging_util.log_section_header(logger, "Phase 5: Output Generation", char="-", width=60)
    logger.info("Saving Excel output: results.xlsx")
    logger.info("Generating plots:")
    logger.info("  - Longitudinal impedance plot: ZLong.png")
    logger.info("  - Transverse impedance plot: ZTrans.png")
    logger.info("Output generation completed")
    logger.info("")
    
    # Summary
    logging_util.log_section_header(logger, "WORKFLOW COMPLETED SUCCESSFULLY")
    logger.info(f"Total execution time: 12.34 seconds")
    logger.info(f"Full log saved to: {log_path}")
    
    print(f"\nWorkflow completed. See log file: {log_path}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("PYTLWALL LOGGING MODULE - USAGE EXAMPLES")
    print("="*80)
    
    # Run all examples
    example_basic_usage()
    example_detailed_configuration()
    example_with_sections()
    example_without_console_output()
    example_multiple_loggers()
    example_pytlwall_workflow()
    
    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("Check the ./my_logs/ directory for generated log files")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
