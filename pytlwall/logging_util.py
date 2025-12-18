#!/usr/bin/env python3
"""
Centralized logging configuration module for PyTLWall.

This module provides a unified logging setup that can be used across:
- Base unit tests
- Complete integration tests
- Normal library usage

Features:
- Timestamped log files
- Configurable verbosity levels
- Both file and console output
- Consistent formatting across all modules
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class LogConfig:
    """
    Configuration class for logging setup.
    
    Attributes
    ----------
    log_dir : Path
        Directory where log files will be saved
    log_basename : str
        Base name for log files (timestamp will be appended)
    verbosity : int
        Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)
    add_timestamp : bool
        Whether to add timestamp to log filename
    console_output : bool
        Whether to output to console in addition to file
    """
    
    def __init__(
        self,
        log_dir: str | Path = "./logs/",
        log_basename: str = "pytlwall",
        verbosity: int = 2,
        add_timestamp: bool = True,
        console_output: bool = True,
    ):
        self.log_dir = Path(log_dir)
        self.log_basename = log_basename
        self.verbosity = verbosity
        self.add_timestamp = add_timestamp
        self.console_output = console_output
        
    def get_log_level(self) -> int:
        """
        Convert verbosity to logging level.
        
        Returns
        -------
        log_level : int
            Logging level (WARNING, INFO, or DEBUG)
        """
        if self.verbosity <= 1:
            return logging.WARNING
        elif self.verbosity == 2:
            return logging.INFO
        else:
            return logging.DEBUG
    
    def get_log_path(self) -> Path:
        """
        Generate the full log file path with optional timestamp.
        
        Returns
        -------
        log_path : Path
            Full path to the log file
        """
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        if self.add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            logfile_path = Path(self.log_basename)
            base_name = logfile_path.stem
            suffix = logfile_path.suffix or ".log"
            log_filename = f"{base_name}_{timestamp}{suffix}"
        else:
            log_filename = self.log_basename if self.log_basename.endswith('.log') else f"{self.log_basename}.log"
        
        return self.log_dir / log_filename


def setup_logging(config: Optional[LogConfig] = None) -> Path:
    """
    Configure logging for PyTLWall.
    
    This function sets up the root logger with appropriate handlers
    for both file and console output (if enabled).
    
    Parameters
    ----------
    config : LogConfig, optional
        Configuration object. If None, uses default configuration.
    
    Returns
    -------
    log_path : Path
        Path to the created log file
    
    Examples
    --------
    Basic usage with defaults:
    >>> log_path = setup_logging()
    
    Custom configuration:
    >>> config = LogConfig(
    ...     log_dir="./my_logs/",
    ...     log_basename="my_app",
    ...     verbosity=3,
    ... )
    >>> log_path = setup_logging(config)
    
    For tests without console output:
    >>> config = LogConfig(console_output=False)
    >>> log_path = setup_logging(config)
    """
    if config is None:
        config = LogConfig()
    
    log_path = config.get_log_path()
    log_level = config.get_log_level()
    
    # Clear any existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create handlers list
    handlers = [
        logging.FileHandler(log_path, mode='w', encoding='utf-8'),
    ]
    
    if config.console_output:
        handlers.append(logging.StreamHandler(sys.stdout))
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,  # Override any existing configuration
    )
    
    return log_path


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Parameters
    ----------
    name : str
        Name of the logger (typically __name__)
    
    Returns
    -------
    logger : logging.Logger
        Configured logger instance
    
    Examples
    --------
    >>> logger = get_logger(__name__)
    >>> logger.info("This is an info message")
    """
    return logging.getLogger(name)


def log_section_header(logger: logging.Logger, title: str, char: str = "=", width: int = 80) -> None:
    """
    Log a formatted section header.
    
    Parameters
    ----------
    logger : logging.Logger
        Logger instance to use
    title : str
        Title of the section
    char : str
        Character to use for the separator line
    width : int
        Width of the separator line
    
    Examples
    --------
    >>> logger = get_logger(__name__)
    >>> log_section_header(logger, "TEST RESULTS")
    """
    logger.info(char * width)
    logger.info(title)
    logger.info(char * width)


def log_test_summary(
    logger: logging.Logger,
    tests_run: int,
    failures: int,
    errors: int,
    success: bool,
) -> None:
    """
    Log a standardized test summary.
    
    Parameters
    ----------
    logger : logging.Logger
        Logger instance to use
    tests_run : int
        Total number of tests run
    failures : int
        Number of failures
    errors : int
        Number of errors
    success : bool
        Whether all tests passed
    
    Examples
    --------
    >>> logger = get_logger(__name__)
    >>> log_test_summary(logger, tests_run=10, failures=0, errors=0, success=True)
    """
    log_section_header(logger, "TEST SUMMARY")
    logger.info(f"Tests run: {tests_run}")
    logger.info(f"Failures: {failures}")
    logger.info(f"Errors: {errors}")
    logger.info("")
    
    if success:
        logger.info("RESULT: ALL TESTS PASSED ✓")
    else:
        logger.info("RESULT: SOME TESTS FAILED ✗")


# Convenience function for quick setup
def quick_setup(
    log_dir: str = "./logs/",
    log_basename: str = "pytlwall",
    verbosity: int = 2,
) -> tuple[Path, logging.Logger]:
    """
    Quick setup function that configures logging and returns a logger.
    
    Parameters
    ----------
    log_dir : str
        Directory for log files
    log_basename : str
        Base name for log file
    verbosity : int
        Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)
    
    Returns
    -------
    log_path : Path
        Path to the log file
    logger : logging.Logger
        Configured logger instance
    
    Examples
    --------
    >>> log_path, logger = quick_setup(verbosity=3)
    >>> logger.info("Logging is configured!")
    """
    config = LogConfig(
        log_dir=log_dir,
        log_basename=log_basename,
        verbosity=verbosity,
    )
    log_path = setup_logging(config)
    logger = get_logger(__name__)
    
    return log_path, logger
