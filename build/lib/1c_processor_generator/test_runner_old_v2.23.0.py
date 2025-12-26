   

import logging
import sys
import time
import threading
from pathlib import Path
from typing import List, Optional

from ._tester import EPFTester, TestResult
from .test_parser import TestParser
from .models import TestsConfig, DeclarativeTest
from .external_connection import ExternalConnection
from .automation_connection import AutomationServerConnection

logger = logging.getLogger(__name__)


class TimeoutException(Exception):
                                                                  
    pass


class TestRunner:
           

    def __init__(
        self,
        tests_config: TestsConfig,
        epf_path: str,
        ib_path: str,
        processor_name: Optional[str] = None,
        use_automation_server: bool = False,
        verbose: bool = False,
    ):
                   
        self.tests_config = tests_config
        self.epf_path = Path(epf_path)
        self.ib_path = Path(ib_path)
        self.processor_name = processor_name
        self.use_automation_server = use_automation_server
        self.verbose = verbose

        self.tester: Optional[EPFTester] = None
        self.results: List[TestResult] = []

    def setup(self) -> bool:
                   
        try:
            print("\n" + "=" * 80)
            print("🔧 SETUP: Connecting to 1C...")
            print("=" * 80)

                                                              
            load_from_config = bool(self.processor_name)

            if self.verbose:
                print(f"EPF: {self.epf_path}")
                print(f"IB: {self.ib_path}")
                print(f"Connection type: {'Automation Server' if self.use_automation_server else 'External Connection'}")
                print(f"Load from configuration: {load_from_config}")
                if load_from_config:
                    print(f"Processor name: {self.processor_name}")

                                                                       
            if self.use_automation_server:
                                                             
                connection = AutomationServerConnection(
                    epf_path=self.epf_path,
                    ib_path=self.ib_path,
                    load_from_configuration=load_from_config,
                    processor_name=self.processor_name,
                    debug=self.verbose,
                )
            else:
                                                                
                connection = ExternalConnection(
                    epf_path=self.epf_path,
                    ib_path=self.ib_path,
                    load_from_configuration=load_from_config,
                    processor_name=self.processor_name,
                    debug=self.verbose,
                )

                                                                     
                                                                
            self.tester = EPFTester(
                connection=connection,
                fixtures=self.tests_config.fixtures
            )

                     
            success = self.tester.connect()

            if success:
                print("✅ Successfully connected to 1C")
                return True
            else:
                print("❌ Error connecting to 1C")
                return False

        except Exception as e:
            print(f"❌ SETUP ERROR: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

    def teardown(self):
                                
        if self.tester:
            self.tester.disconnect()
            print("✅ Disconnected from 1C")

    def run_declarative_tests(self) -> List[TestResult]:
                   
        if not self.tests_config.declarative_tests:
            return []

        print("\n" + "=" * 80)
        print(f"📋 DECLARATIVE TESTS ({len(self.tests_config.declarative_tests)} tests)")
        print("=" * 80)

        results = []

        for i, test in enumerate(self.tests_config.declarative_tests, 1):
            print(f"\n[{i}/{len(self.tests_config.declarative_tests)}] {test.name}")
            print("-" * 80)

            start_time = time.time()
            result = self.tester.run_declarative_test(test)

                              
            if result.passed:
                print(f"✅ PASSED ({result.execution_time:.2f}s)")
            else:
                print(f"❌ FAILED ({result.execution_time:.2f}s)")
                print(f"   Error: {result.error_message}")

            results.append(result)

        return results

    def run_procedural_tests(self) -> List[TestResult]:
                   
        if not self.tests_config.procedural_tests:
            return []

        procedures = self.tests_config.procedural_tests.procedures
        if not procedures:
            return []

        print("\n" + "=" * 80)
        print(f"📋 PROCEDURAL TESTS ({len(procedures)} procedures)")
        print("=" * 80)

        results = []

        for i, procedure_name in enumerate(procedures, 1):
            print(f"\n[{i}/{len(procedures)}] {procedure_name}")
            print("-" * 80)

            result = self.tester.run_procedural_test(procedure_name)

                              
            if result.passed:
                print(f"✅ PASSED ({result.execution_time:.2f}s)")
            else:
                print(f"❌ FAILED ({result.execution_time:.2f}s)")
                print(f"   Error: {result.error_message}")

            results.append(result)

        return results

    def _timeout_handler(self):
                                                              
        print(f"\n\n⏱️  TIMEOUT: Test execution exceeded {self.tests_config.timeout}s limit")
        print("⚠️  Terminating test execution...")
                                                        
        import _thread
        _thread.interrupt_main()

    def run_all_tests(self) -> bool:
                   
               
        if not self.setup():
            print("\n❌ SETUP FAILED - Tests not executed")
            return False

                                         
        timeout_timer = None
        if self.tests_config.timeout and self.tests_config.timeout > 0:
            logger.info(f"⏱️  Test timeout: {self.tests_config.timeout}s")
            timeout_timer = threading.Timer(self.tests_config.timeout, self._timeout_handler)
            timeout_timer.daemon = True
            timeout_timer.start()

        try:
                                       
            declarative_results = self.run_declarative_tests()
            self.results.extend(declarative_results)

                                      
            procedural_results = self.run_procedural_tests()
            self.results.extend(procedural_results)

                                                      
            if timeout_timer:
                timeout_timer.cancel()

                     
            self.print_summary()

                                 
            all_passed = all(r.passed for r in self.results)
            return all_passed

        except KeyboardInterrupt:
                             
            if timeout_timer:
                timeout_timer.cancel()

            print("\n\n❌ TEST EXECUTION TIMEOUT")
            print(f"   Executed {len(self.results)} tests before timeout")
            self.print_summary()
            return False

        finally:
                                           
            if timeout_timer and timeout_timer.is_alive():
                timeout_timer.cancel()

                                      
            self.teardown()

    def print_summary(self):
                                      
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)

        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        total_time = sum(r.execution_time for r in self.results)

        print(f"\nTotal tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Execution time: {total_time:.2f}s")

                              
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"   - {result.test_name}: {result.error_message}")

                      
        print("\n" + "=" * 80)
        if failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {failed} TEST{'S' if failed != 1 else ''} FAILED")
        print("=" * 80)


def main():
                                         
    import argparse

    parser = argparse.ArgumentParser(
        description="Standalone Test Runner for EPF tests (WITHOUT pytest)",
        prog="python -m 1c_processor_generator.test_runner"
    )

    parser.add_argument(
        "--tests-config",
        required=True,
        help="Path to tests.yaml file"
    )

    parser.add_argument(
        "--epf-path",
        required=True,
        help="Path to EPF file"
    )

    parser.add_argument(
        "--ib-path",
        required=True,
        help="Path to test infobase"
    )

    parser.add_argument(
        "--processor-name",
        help="Processor name (for load_from_configuration)"
    )

    parser.add_argument(
        "--use-automation-server",
        action="store_true",
        help="Use Automation Server (V83.Application) instead of External Connection (v2.18.0+)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

                   
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    try:
                         
        print(f"Loading tests from {args.tests_config}...")
        parser = TestParser(args.tests_config)
        tests_config = parser.parse()

        if not tests_config:
            print("❌ Error parsing tests.yaml")
            sys.exit(1)

        declarative_count = len(tests_config.declarative_tests) if tests_config.declarative_tests else 0
        procedural_count = len(tests_config.procedural_tests.procedures) if tests_config.procedural_tests and tests_config.procedural_tests.procedures else 0

        print(f"✅ Loaded {declarative_count} declarative + {procedural_count} procedural tests")

                                                                                 
        epf_path = Path(args.epf_path)
        test_epf_path = epf_path.parent / f"{epf_path.stem}_Tests.epf"

                                                                    
        use_test_epf = test_epf_path.exists() and procedural_count > 0

        if use_test_epf:
            print(f"\n💡 Detected test EPF with injected procedural tests: {test_epf_path.name}")
            print(f"   Using test EPF instead of clean EPF for procedural test execution")
            print(f"   ⚡ Loading from EPF file (not from configuration)")
            final_epf_path = test_epf_path
                                                                         
                                                                    
            final_processor_name = None
        else:
            if procedural_count > 0 and not test_epf_path.exists():
                print(f"\n⚠️  WARNING: Procedural tests found but test EPF not detected!")
                print(f"   Expected: {test_epf_path}")
                print(f"   Procedural tests may fail if not injected into ObjectModule")
            final_epf_path = epf_path
                                                                   
            final_processor_name = args.processor_name

                       
        runner = TestRunner(
            tests_config=tests_config,
            epf_path=str(final_epf_path),
            ib_path=args.ib_path,
            processor_name=final_processor_name,
            use_automation_server=args.use_automation_server,
            verbose=args.verbose,
        )

                       
        all_passed = runner.run_all_tests()

                   
        sys.exit(0 if all_passed else 1)

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
