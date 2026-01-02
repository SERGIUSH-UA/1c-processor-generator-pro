   

import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass

from .models import (
    DeclarativeTest,
    TestSetup,
    TestAssertion,
    MessageAssertion,
    TableAssertion,
    TestFixture,
)
from ._conn import BaseConnection

                                                  
                                                                 
try:
    from ._ext_conn import HAS_COM_SUPPORT
except ImportError:
                                                        
    HAS_COM_SUPPORT = False

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
                                            
    test_name: str
    passed: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0           
    module_type: str = "ObjectModule"                                  


class EPFTester:
           

    def __init__(self, connection: BaseConnection, fixtures: Optional[dict] = None):
                   
        self.connection = connection
        self.fixtures = fixtures or {}                             

    def connect(self) -> bool:
                   
        return self.connection.connect()

    def disconnect(self):
                               
        self.connection.disconnect()

    def get_processor(self):
                                       
        return self.connection.get_processor()

    def set_attribute(self, attr_name: str, value):
                                            
        self.connection.set_attribute(attr_name, value)

    def get_attribute(self, attr_name: str):
                                            
        return self.connection.get_attribute(attr_name)

    def execute_command(self, command_name: str):
                                        
        self.connection.execute_command(command_name)

    def execute_procedure(self, procedure_name: str):
                                    
        self.connection.execute_procedure(procedure_name)

    def start_message_recording(self):
                                      
        self.connection.start_message_recording()

    def get_test_messages(self) -> List[str]:
                                    
        return self.connection.get_test_messages()

    def apply_setup(self, setup: TestSetup):
                                                        
                        
        for attr_name, value in setup.attributes.items():
            self.set_attribute(attr_name, value)

                     
        for table_name, rows in setup.table_rows.items():
            self.connection.fill_table(table_name, rows)

    def apply_fixtures(self, fixture_names: List[str]):
                   
        for fixture_name in fixture_names:
            if fixture_name not in self.fixtures:
                raise ValueError(f"Fixture '{fixture_name}' not found. Available fixtures: {list(self.fixtures.keys())}")

            fixture = self.fixtures[fixture_name]
            logger.debug(f"Applying fixture: {fixture_name}")
            self.apply_setup(fixture.setup)

    def check_assertion(self, assertion: TestAssertion) -> Tuple[bool, Optional[str]]:
                   
                                          
        from .assertion_helper import check_extended_assertion, check_message_assertion_extended

                                                             
        for attr_name, expected in assertion.attributes.items():
            actual_value = self.get_attribute(attr_name)

                                            
            passed, error = check_extended_assertion(actual_value, expected, attr_name)
            if not passed:
                return False, error

                                                                    
        if assertion.messages:
            messages = self.get_test_messages()
            for msg_assert in assertion.messages:
                                                        
                passed, error = check_message_assertion_extended(messages, msg_assert)
                if not passed:
                    return False, error

                      
        for table_assert in assertion.tables:
            if not self._check_table_assertion(table_assert):
                return False, f"Table {table_assert.table_name} does not match assertions"

        return True, None

    def _check_message_assertion(self, messages: List[str], assertion: MessageAssertion) -> bool:
                                      
        if assertion.count is not None:
            if len(messages) != assertion.count:
                logger.error(f"Message count: expected {assertion.count}, got {len(messages)}")
                return False

        if assertion.contains:
            found = any(assertion.contains in msg for msg in messages)
            if not found:
                logger.error(f"Message does not contain '{assertion.contains}'. Received: {messages}")
                return False

        if assertion.equals:
            found = any(assertion.equals == msg for msg in messages)
            if not found:
                logger.error(f"Message does not equal '{assertion.equals}'. Received: {messages}")
                return False

        return True

    def _check_table_assertion(self, assertion: TableAssertion) -> bool:
                                    
        try:
            processor = self.get_processor()
            obj = getattr(processor, "Объект", processor)
            table = getattr(obj, assertion.table_name)

                             
            if assertion.row_count is not None:
                actual_count = table.Количество()
                if actual_count != assertion.row_count:
                    logger.error(f"Table {assertion.table_name}: expected {assertion.row_count} rows, got {actual_count}")
                    return False

                                               
            for column in assertion.columns:
                try:
                                                            
                    if table.Количество() > 0:
                        first_row = table.Получить(0)
                        getattr(first_row, column)
                except:
                    logger.error(f"Table {assertion.table_name}: column {column} not found")
                    return False

            return True

        except Exception as e:
            logger.error(f"❌ Error checking table {assertion.table_name}: {e}")
            return False

    def run_declarative_test(self, test: DeclarativeTest) -> TestResult:
                   
        import time
        start_time = time.time()

        try:
            logger.info(f"▶️  Running test: {test.name}")

                                        
            self.start_message_recording()

                                          
            if test.use_fixtures:
                self.apply_fixtures(test.use_fixtures)

                                               
            if test.setup:
                self.apply_setup(test.setup)

                        
            if test.execute_command:
                self.execute_command(test.execute_command)
            elif test.execute_procedure:
                self.execute_procedure(test.execute_procedure)

                       
            if test.assert_result:
                                     
                if test.assert_result.exception:
                                                                     
                    if test.assert_result.exception.raised:
                        return TestResult(
                            test_name=test.name,
                            passed=False,
                            error_message="Expected exception but none was raised",
                            execution_time=time.time() - start_time,
                        )
                else:
                                      
                    passed, error = self.check_assertion(test.assert_result)
                    if not passed:
                        return TestResult(
                            test_name=test.name,
                            passed=False,
                            error_message=error,
                            execution_time=time.time() - start_time,
                        )

                         
            logger.info(f"✅ Test {test.name} passed")
            return TestResult(
                test_name=test.name,
                passed=True,
                execution_time=time.time() - start_time,
            )

        except Exception as e:
                                    
            if test.assert_result and test.assert_result.exception:
                if test.assert_result.exception.raised:
                    error_text = str(e)

                                                               
                    if test.assert_result.exception.contains:
                        if test.assert_result.exception.contains in error_text:
                            logger.info(f"✅ Test {test.name} passed (exception expected)")
                            return TestResult(
                                test_name=test.name,
                                passed=True,
                                execution_time=time.time() - start_time,
                            )
                        else:
                            return TestResult(
                                test_name=test.name,
                                passed=False,
                                error_message=f"Exception does not contain '{test.assert_result.exception.contains}'. Got: {error_text}",
                                execution_time=time.time() - start_time,
                            )
                    else:
                                                                
                        logger.info(f"✅ Test {test.name} passed (exception expected)")
                        return TestResult(
                            test_name=test.name,
                            passed=True,
                            execution_time=time.time() - start_time,
                        )

                                    
            logger.error(f"❌ Test {test.name} failed: {e}")
            return TestResult(
                test_name=test.name,
                passed=False,
                error_message=str(e),
                execution_time=time.time() - start_time,
            )

    def run_procedural_test(self, procedure_name: str) -> TestResult:
                   
        import time
        start_time = time.time()

        try:
            logger.info(f"▶️  Running BSL test: {procedure_name}")

                               
            self.execute_procedure(procedure_name)

                                           
            logger.info(f"✅ Test {procedure_name} passed")
            return TestResult(
                test_name=procedure_name,
                passed=True,
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            logger.error(f"❌ Test {procedure_name} failed: {e}")
            return TestResult(
                test_name=procedure_name,
                passed=False,
                error_message=str(e),
                execution_time=time.time() - start_time,
            )
