#!/usr/bin/env python3
"""
Command-line utility to run Python unittests with flexible selection and logging.

Features:
- Run all discovered tests or only selected modules.
- Log errors and failures, with full tracebacks.
- At higher verbosity levels, log successful tests using their docstring
  (or their fully qualified name if no docstring is provided).
- Configurable directly in file without shell arguments
- Uses centralized logging module
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Optional, Sequence

# Add parent directory to path to allow imports when running from tests/ directory
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

# Import centralized logging module from pytlwall package
from pytlwall import logging_util


# ============================================================================
# CONFIGURATION SECTION - Edit these parameters to customize test execution
# ============================================================================

class TestConfig:
    """Configuration for test execution - edit these values as needed."""
    
    # Test directory
    TEST_DIR: str = "./tests/"
    
    # Log file configuration
    LOG_DIR: str = "./tests/logs/"
    LOG_BASENAME: str = "tlwall_test"  # Timestamp will be appended automatically
    
    # Test pattern for discovery
    PATTERN: str = "test*.py"
    
    # Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)
    VERBOSITY: int = 2
    
    # Select specific test modules to run (None = run all discovered tests)
    # Example: ["test_beam.py", "test_other.py"]
    SELECTED_MODULES: Optional[list[str]] = None
    
    # Alternative: run only specific test modules
    # Uncomment and edit to run only selected modules:
    # SELECTED_MODULES = ["test_beam.py"]


# ============================================================================
# TEST RUNNER IMPLEMENTATION
# ============================================================================

class LoggingTestResult(unittest.TextTestResult):
    """
    Custom TestResult that logs successful tests when verbosity is high enough.

    For each successful test, it logs a line of the form:
        "Test that default construction uses expected default values. ... ok"
    or, if no docstring is defined:
        "test_gammarel (test_beam.TestBeam.test_gammarel) ... ok"
    """

    def __init__(self, stream, descriptions: bool, verbosity: int, logger) -> None:
        super().__init__(stream, descriptions, verbosity)
        self.log_success: bool = verbosity >= 2
        self.logger = logger
        self._current_module = None

    def startTest(self, test):  # type: ignore[override]
        test_id = test.id()  # es: "test_beam.TestBeam.test_gammarel"
        module_name = test_id.split(".")[0]
        if module_name != self._current_module:
            self._current_module = module_name
            self.logger.info(" =============================================")
            self.logger.info(" =============   testing %s =================", module_name)
            self.logger.info(" =============================================")
        super().startTest(test)

    def addSuccess(self, test: unittest.case.TestCase) -> None:  # type: ignore[override]
        super().addSuccess(test)
        if self.log_success:
            description = test.shortDescription() or str(test)
            self.logger.info("%s ... ok", description)


def build_suite_from_modules(
    test_dir: Path,
    selected_modules: Sequence[str],
    loader: unittest.TestLoader,
    logger,
) -> unittest.TestSuite:
    """
    Build a unittest suite from a list of module filenames.

    Parameters
    ----------
    test_dir:
        Directory containing the test modules.
    selected_modules:
        Iterable of filenames (e.g., "test_beam.py").
    loader:
        Instance of unittest.TestLoader used to load tests.
    logger:
        Logger instance for error reporting.

    Returns
    -------
    suite:
        A unittest.TestSuite containing all loaded tests.
    """
    suite = unittest.TestSuite()

    for module_filename in selected_modules:
        module_path = test_dir / module_filename
        if not module_path.is_file():
            logger.error("File not found: %s", module_path)
            continue

        module_name = module_path.stem

        # Temporarily add test_dir to sys.path so imports work reliably.
        sys.path.insert(0, str(test_dir))
        try:
            imported_module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(imported_module))
        except Exception as exc:  # noqa: BLE001 - broad but safe in CLI.
            logger.error("Import error in %s: %s", module_filename, exc)
        finally:
            # Remove the injected path to avoid side effects.
            sys.path.pop(0)

    return suite


def discover_suite(test_dir: Path, pattern: str, loader: unittest.TestLoader) -> unittest.TestSuite:
    """
    Discover tests automatically in test_dir matching the given pattern.

    Parameters
    ----------
    test_dir:
        Directory to search for test modules.
    pattern:
        Glob-style pattern for test files, e.g. "test*.py".

    Returns
    -------
    suite:
        A unittest.TestSuite containing all discovered tests.
    """
    return loader.discover(start_dir=str(test_dir), pattern=pattern)


def run_selected_unittests_with_log(
    test_dir: Path | str,
    logdir: Path | str,
    logfile: str,
    pattern: str = "test*.py",
    verbosity: int = 2,
    selected_modules: Optional[Sequence[str]] = None,
) -> bool:
    """
    Run unit tests and log the results.

    Parameters
    ----------
    test_dir:
        Directory containing test files.
    logdir:
        Directory where the log file will be created.
    logfile:
        Base name of the log file to write (a timestamp will be appended).
        Example: "tlwall_test.log" → "tlwall_test_20250129_153012.log"
    pattern:
        Pattern used for automatic test discovery (default: "test*.py").
    verbosity:
        Verbosity level for the unittest runner (default: 2).
    selected_modules:
        Optional sequence of specific test filenames to load.
        If None, automatic discovery is used.

    Returns
    -------
    success : bool
        True if all tests passed

    Notes
    -----
    - Errors and failures are always logged.
    - At higher verbosity, successful tests are logged too.
    """
    test_dir_path = Path(test_dir).resolve()
    
    # Setup logging using centralized module
    log_config = logging_util.LogConfig(
        log_dir=logdir,
        log_basename=logfile,
        verbosity=verbosity,
        add_timestamp=True,
        console_output=True,
    )
    log_path = logging_util.setup_logging(log_config)
    logger = logging_util.get_logger(__name__)

    # Log test session info
    logging_util.log_section_header(logger, "START TEST SESSION")
    logger.info(f"Timestamp: {logging_util.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_path}")
    logger.info(f"Test directory: {test_dir_path}")
    logger.info(f"Pattern: {pattern}")
    logger.info(f"Verbosity: {verbosity}")
    if selected_modules:
        logger.info(f"Selected modules: {', '.join(selected_modules)}")
    else:
        logger.info("Mode: Discover all tests")
    logger.info("")

    loader = unittest.TestLoader()

    if selected_modules:
        suite = build_suite_from_modules(test_dir_path, selected_modules, loader, logger)
    else:
        suite = discover_suite(test_dir_path, pattern, loader)

    # Create runner with custom result class that uses our logger
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        resultclass=lambda stream, descriptions, verbosity: LoggingTestResult(
            stream, descriptions, verbosity, logger
        ),
    )
    result = runner.run(suite)

    # Log summary using centralized function
    logging_util.log_test_summary(
        logger=logger,
        tests_run=result.testsRun,
        failures=len(result.failures),
        errors=len(result.errors),
        success=result.wasSuccessful(),
    )
    
    # Log detailed errors and failures
    if not result.wasSuccessful():
        if result.failures:
            logger.error("\n%d tests failed:", len(result.failures))
            for test, traceback in result.failures:
                logger.error("FAIL: %s\n%s", test.id(), traceback)

        if result.errors:
            logger.error("\n%d tests raised errors:", len(result.errors))
            for test, traceback in result.errors:
                logger.error("ERROR: %s\n%s", test.id(), traceback)

    logging_util.log_section_header(logger, "")
    print(f"\nUnit test run completed. See log file: {log_path}")
    
    return result.wasSuccessful()


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Parameters
    ----------
    argv:
        Optional iterable of arguments. If None, sys.argv[1:] is used.

    Returns
    -------
    argparse.Namespace
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run unittests selectively or all, with logging to a file.",
    )

    parser.add_argument(
        "--test_dir",
        type=str,
        default=TestConfig.TEST_DIR,
        help="Directory containing test files.",
    )
    parser.add_argument(
        "--logdir",
        type=str,
        default=TestConfig.LOG_DIR,
        help="Directory for the log file.",
    )
    parser.add_argument(
        "--logfile",
        type=str,
        default=TestConfig.LOG_BASENAME,
        help=(
            "Base name of the log file. A timestamp will be appended, "
            "e.g. tlwall_test_YYYYMMDD_HHMMSS.log."
        ),
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default=TestConfig.PATTERN,
        help="Pattern for test modules (used for discovery).",
    )
    parser.add_argument(
        "--modules",
        type=str,
        nargs="*",
        default=TestConfig.SELECTED_MODULES,
        help="Specific test files to run, e.g. test_beam.py test_other.py.",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=TestConfig.VERBOSITY,
        help="Verbosity level for unittest output (0, 1, 2, 3...).",
    )

    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    """
    Main entry point for command-line execution.
    
    Can be called with no arguments to use configuration from TestConfig class,
    or with command-line arguments to override the configuration.
    """
    args = parse_args(argv)
    success = run_selected_unittests_with_log(
        test_dir=args.test_dir,
        logdir=args.logdir,
        logfile=args.logfile,
        pattern=args.pattern,
        verbosity=args.verbosity,
        selected_modules=args.modules,
    )
    
    sys.exit(0 if success else 1)


def run_tests_base() -> None:
    """
    Run tests using the configuration defined in TestConfig class.
    
    This function can be called directly from Python without command-line arguments.
    All configuration is taken from the TestConfig class above.
    
    Example usage:
        # Run all tests with default configuration
        run_tests_base()
        
        # Or modify TestConfig first:
        TestConfig.SELECTED_MODULES = ["test_beam.py"]
        TestConfig.VERBOSITY = 3
        run_tests_base()
    """
    success = run_selected_unittests_with_log(
        test_dir=TestConfig.TEST_DIR,
        logdir=TestConfig.LOG_DIR,
        logfile=TestConfig.LOG_BASENAME,
        pattern=TestConfig.PATTERN,
        verbosity=TestConfig.VERBOSITY,
        selected_modules=TestConfig.SELECTED_MODULES,
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # When run as script, use configuration from TestConfig class
    # Comment out the next line and uncomment main() to use command-line args instead
    run_tests_base()
    
    # Uncomment this line to enable command-line argument parsing:
    # main()
