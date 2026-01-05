   

import sys
import time
import logging
import threading
from pathlib import Path
from typing import List, Optional

from .models import TestsConfig, ObjectModuleTestsConfig, FormTestsConfig
from .test_parser import parse_tests_yaml
from ._tester import EPFTester
from .external_connection import ExternalConnection
from .automation_connection import AutomationServerConnection

logger = logging.getLogger(__name__)


class TestRunner:
           

    def __init__(
        self,
        tests_config: TestsConfig,
        epf_path: str,
        ib_path: str,
        processor_name: Optional[str] = None,
        verbose: bool = False,
    ):
                   
        self.tests_config = tests_config
        self.epf_path = Path(epf_path)
        self.ib_path = Path(ib_path)
        self.processor_name = processor_name
        self.verbose = verbose

        self.all_results: List = []

    def run_all_tests(self) -> bool:
                   
        print("\n" + "=" * 80)
        print("🚀 RUNNING TESTS (v2.23.2 - auto-detection)")
        print("=" * 80)

        try:
                                                  
            if self.tests_config.objectmodule_tests:
                om_results = self._run_objectmodule_tests()
                self.all_results.extend(om_results)

                                          
            if self.tests_config.forms:
                for form_config in self.tests_config.forms:
                    form_results = self._run_form_tests(form_config)
                    self.all_results.extend(form_results)

                              
            self._print_summary()

                                    
            all_passed = all(r.passed for r in self.all_results)
            return all_passed

        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

    def _run_objectmodule_tests(self) -> List:
                   
        print("\n" + "=" * 80)
        print("📋 OBJECTMODULE TESTS - External Connection (fast, no UI)")
        print("=" * 80)

        results = []
        om_config = self.tests_config.objectmodule_tests

                     
        declarative_count = len(om_config.declarative) if om_config.declarative else 0
        procedural_count = len(om_config.procedural.procedures) if om_config.procedural and om_config.procedural.procedures else 0
        total_count = declarative_count + procedural_count

        print(f"Tests: {declarative_count} declarative + {procedural_count} procedural = {total_count} total\n")

                          
        connection = None
        tester = None

        try:
                                                             
            load_from_config = bool(self.processor_name)

                               
            connection = ExternalConnection(
                epf_path=self.epf_path,
                ib_path=self.ib_path,
                load_from_configuration=load_from_config,
                processor_name=self.processor_name,
                debug=self.verbose,
            )

                           
            tester = EPFTester(
                connection=connection,
                fixtures=self.tests_config.fixtures,
            )

                     
            print("🔧 Connecting to 1C...")
            if not tester.connect():
                print("❌ Connection failed")
                return results

            print("✅ Connected\n")

                                   
            if om_config.declarative:
                for i, test in enumerate(om_config.declarative, 1):
                    print(f"[{i}/{total_count}] {test.name}")
                    print("-" * 80)

                    result = tester.run_declarative_test(test)

                    if result.passed:
                        print(f"✅ PASSED ({result.execution_time:.2f}s)\n")
                    else:
                        print(f"❌ FAILED ({result.execution_time:.2f}s)")
                        print(f"   Error: {result.error_message}\n")

                    results.append(result)

                                  
            if om_config.procedural and om_config.procedural.procedures:
                for i, procedure_name in enumerate(om_config.procedural.procedures, declarative_count + 1):
                    print(f"[{i}/{total_count}] {procedure_name}")
                    print("-" * 80)

                    result = tester.run_procedural_test(procedure_name)

                    if result.passed:
                        print(f"✅ PASSED ({result.execution_time:.2f}s)\n")
                    else:
                        print(f"❌ FAILED ({result.execution_time:.2f}s)")
                        print(f"   Error: {result.error_message}\n")

                    results.append(result)

        finally:
                     
            if tester:
                tester.disconnect()
                print("✅ Disconnected from 1C")

        return results

    def _run_form_tests(self, form_config: FormTestsConfig) -> List:
                   
        print("\n" + "=" * 80)
        print(f"📋 FORM TESTS: {form_config.name} - Automation Server (slow, with UI)")
        print("=" * 80)

        results = []

                     
        declarative_count = len(form_config.declarative) if form_config.declarative else 0
        procedural_count = len(form_config.procedural.procedures) if form_config.procedural and form_config.procedural.procedures else 0
        total_count = declarative_count + procedural_count

        print(f"Tests: {declarative_count} declarative + {procedural_count} procedural = {total_count} total\n")

                          
        connection = None
        tester = None

        try:
                                                             
            load_from_config = bool(self.processor_name)

                               
            connection = AutomationServerConnection(
                epf_path=self.epf_path,
                ib_path=self.ib_path,
                load_from_configuration=load_from_config,
                processor_name=self.processor_name,
                debug=self.verbose,
            )

                           
            tester = EPFTester(
                connection=connection,
                fixtures=self.tests_config.fixtures,
            )

                     
            print("🔧 Connecting to 1C (Automation Server)...")
            if not tester.connect():
                print("❌ Connection failed")
                return results

            print("✅ Connected\n")

                                   
            if form_config.declarative:
                for i, test in enumerate(form_config.declarative, 1):
                    print(f"[{i}/{total_count}] {test.name}")
                    print("-" * 80)

                    result = tester.run_declarative_test(test)

                    if result.passed:
                        print(f"✅ PASSED ({result.execution_time:.2f}s)\n")
                    else:
                        print(f"❌ FAILED ({result.execution_time:.2f}s)")
                        print(f"   Error: {result.error_message}\n")

                    results.append(result)

                                  
            if form_config.procedural and form_config.procedural.procedures:
                for i, procedure_name in enumerate(form_config.procedural.procedures, declarative_count + 1):
                    print(f"[{i}/{total_count}] {procedure_name}")
                    print("-" * 80)

                    result = tester.run_procedural_test(procedure_name)

                    if result.passed:
                        print(f"✅ PASSED ({result.execution_time:.2f}s)\n")
                    else:
                        print(f"❌ FAILED ({result.execution_time:.2f}s)")
                        print(f"   Error: {result.error_message}\n")

                    results.append(result)

        finally:
                     
            if tester:
                tester.disconnect()
                print("✅ Disconnected from 1C")

        return results

    def _print_summary(self):
                                      
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)

        total = len(self.all_results)
        passed = sum(1 for r in self.all_results if r.passed)
        failed = total - passed

        total_time = sum(r.execution_time for r in self.all_results)

        print(f"\nTotal tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Execution time: {total_time:.2f}s")

                                              
        om_tests = [r for r in self.all_results if r.module_type == "ObjectModule"]
        fm_tests = [r for r in self.all_results if r.module_type == "FormModule"]

        if om_tests:
            om_passed = sum(1 for r in om_tests if r.passed)
            print(f"   ObjectModule: {om_passed}/{len(om_tests)} passed")
        if fm_tests:
            fm_passed = sum(1 for r in fm_tests if r.passed)
            print(f"   FormModule: {fm_passed}/{len(fm_tests)} passed")

                              
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.all_results:
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
        description="Run tests for 1C processor (v2.23.2+ auto-detection)"
    )

    parser.add_argument(
        "--tests-config",
        required=True,
        help="Path to tests.yaml"
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
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    try:
                                  
        print(f"Loading tests from {args.tests_config}...")
        tests_config = parse_tests_yaml(Path(args.tests_config))

        if not tests_config:
            print("❌ Failed to load tests configuration")
            sys.exit(1)

                     
        om_decl = len(tests_config.objectmodule_tests.declarative) if tests_config.objectmodule_tests and tests_config.objectmodule_tests.declarative else 0
        om_proc = len(tests_config.objectmodule_tests.procedural.procedures) if tests_config.objectmodule_tests and tests_config.objectmodule_tests.procedural and tests_config.objectmodule_tests.procedural.procedures else 0

        form_count = 0
        for form_config in tests_config.forms:
            form_decl = len(form_config.declarative) if form_config.declarative else 0
            form_proc = len(form_config.procedural.procedures) if form_config.procedural and form_config.procedural.procedures else 0
            form_count += form_decl + form_proc

        print(f"✅ Loaded tests:")
        if om_decl + om_proc > 0:
            print(f"   ObjectModule: {om_decl} declarative + {om_proc} procedural")
        if form_count > 0:
            print(f"   Forms: {len(tests_config.forms)} form(s), {form_count} total tests")

                       
        runner = TestRunner(
            tests_config=tests_config,
            epf_path=args.epf_path,
            ib_path=args.ib_path,
            processor_name=args.processor_name,
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
