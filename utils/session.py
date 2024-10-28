import streamlit as st
import pandas as pd
import json
import shutil
import inspect
import zipfile
from pathlib import Path
from PSSimPy import Bank, Transaction
from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler
from PSSimPy.transaction_fee import AbstractTransactionFee, FixedTransactionFee
from PSSimPy.queues import AbstractQueue, DirectQueue
from PSSimPy.credit_facilities import AbstractCreditFacility, SimplePriced

from utils.helper import initialize_dict_key, replace_whitespace_with_underscore, ClassImplementationModifier

def initialize_session_state_variables():
        # Parameters
        initialize_dict_key(st.session_state, 'Parameters', {
                'Opening Time': None,
                'Closing Time': None,
                'Processing Window': None,
                'Number of Days': None,
                'EOD Clear Queue': None,
                'EOD Force Settlement': None
        })
        # Input Data
        initialize_dict_key(st.session_state, 'Input Data', {
                'Banks': pd.DataFrame(columns=['name']),
                'Accounts': pd.DataFrame(columns=['id', 'owner', 'balance']),
                'Transactions': None
        })
        # Random Transactions
        initialize_dict_key(st.session_state, 'Random Transactions', False)
        # Transaction Probability
        initialize_dict_key(st.session_state, 'Transaction Probability', None)
        # Transaction Amount Range
        initialize_dict_key(st.session_state, 'Transaction Amount Range', None)
        # Bank Strategies
        initialize_dict_key(st.session_state, 'Bank Strategies', {})
        # Constraint Handler
        initialize_dict_key(st.session_state, 'Constraint Handler', {'class': PassThroughHandler, 'implementation': None, 'params':[]}) # default to pass through
        # Transaction Fee
        initialize_dict_key(st.session_state, 'Transaction Fee', {
                'rate': 0.0,
                'class': FixedTransactionFee, # placeholder
                'implementation': None,
                'params': []
        })
        # Queue Handler
        initialize_dict_key(st.session_state, 'Queue', {'class': DirectQueue, 'implementation': None, 'params': []})
        # Credit Facility
        initialize_dict_key(st.session_state, 'Credit Facility', {'class': SimplePriced, 'implementation': None, 'params': []})
        # Output Files
        initialize_dict_key(st.session_state, 'Log Files', {
                'Processed Transactions': pd.DataFrame(),
                'Transaction Fees': pd.DataFrame(),
                'Queue Stats': pd.DataFrame(),
                'Account Balance': pd.DataFrame(),
                'Credit Facility': pd.DataFrame(),
                'Transactions Arrival': pd.DataFrame()
        })


def save_simulation_settings(simulation_setting_name: str, include_data: bool=False) -> bool:
        # create saved settings folder if it does not exist
        Path("./saved_settings").mkdir(parents=True, exist_ok=True)

        # create folder to contain settings
        simulation_setting_name = replace_whitespace_with_underscore(simulation_setting_name)
        settings_folder = f"./saved_settings/{simulation_setting_name}"
        Path(settings_folder).mkdir(parents=True)

        # create json file for static data
        static_data = {
                'Parameters': st.session_state['Parameters'], 
                'Random Transactions': st.session_state['Random Transactions'],
                'Transaction Probability': st.session_state['Transaction Probability'],
                'Transaction Amount Range': st.session_state['Transaction Amount Range'],
                'Transaction Fee Rate': st.session_state['Transaction Fee']['rate']
                }
        with open(f"{settings_folder}/static_data.json", "w") as file:
                json.dump(static_data , file) 

        # create bank strategy implementations
        if st.session_state['Bank Strategies']:
                Path(f"{settings_folder}/bank_strategies").mkdir(parents=True)
                base_bank_code = inspect.getsource(Bank)
                for strategy_name, value in st.session_state['Bank Strategies'].items():
                        strategy_name = replace_whitespace_with_underscore(strategy_name)
                        strategy_mod = ClassImplementationModifier(base_bank_code)
                        strategy_mod.replace_class_name(strategy_name)
                        strategy_mod.replace_function('strategy', value['implementation'])
                        strategy_mod.insert_import_statement('from PSSimPy.queues import AbstractQueue')
                        # Save the generated code to a file
                        with open(f"{settings_folder}/bank_strategies/{strategy_name}.py", "w") as f:
                                f.write(strategy_mod.code)

        # constraint handler
        if st.session_state['Constraint Handler']['implementation'] is not None:
                Path(f"{settings_folder}/constraint_handler").mkdir(parents=True)
                base_constraint_handler_code = inspect.getsource(AbstractConstraintHandler)
                constraint_handler_mod = ClassImplementationModifier(base_constraint_handler_code)
                constraint_handler_mod.replace_class_name("CustomConstraintHandler(AbstractConstraintHandler)")
                constraint_handler_init_params = ClassImplementationModifier.generate_init_method(
                        {param["name"]: param["default"] for param in st.session_state['Constraint Handler']['params']}, 
                        True,
                        "AbstractConstraintHandler"
                )
                constraint_handler_mod.replace_function('__init__', constraint_handler_init_params)
                constraint_handler_mod.replace_function('process_transaction', st.session_state['Constraint Handler']['implementation'])
                constraint_handler_mod.insert_import_statement('from PSSimPy.constraint_handler import AbstractConstraintHandler')
                constraint_handler_mod.insert_import_statement('from PSSimPy.transaction import Transaction')
                # Save the generated code to a file
                with open(f"{settings_folder}/constraint_handler/custom_constraint_handler.py", "w") as f:
                        f.write(constraint_handler_mod.code)
        
        # transaction fee handler
        if st.session_state['Transaction Fee']['implementation'] is not None:
                Path(f"{settings_folder}/transaction_fee_handler").mkdir(parents=True)
                base_transaction_fee_handler_code = inspect.getsource(AbstractTransactionFee)
                transaction_fee_handler_mod = ClassImplementationModifier(base_transaction_fee_handler_code)
                transaction_fee_handler_mod.replace_class_name("CustomTransactionFee(AbstractTransactionFee)")
                transaction_fee_handler_init_params = ClassImplementationModifier.generate_init_method(
                        {param["name"]: param["default"] for param in st.session_state['Transaction Fee']['params']}, 
                        True,
                        "AbstractTransactionFee"
                )
                transaction_fee_handler_mod.replace_function('__init__', transaction_fee_handler_init_params)
                transaction_fee_handler_mod.replace_function('calculate_fee', st.session_state['Transaction Fee']['implementation'])
                transaction_fee_handler_mod.insert_import_statement('from PSSimPy.transaction_fee import AbstractTransactionFee')
                # Save the generated code to a file
                with open(f"{settings_folder}/transaction_fee_handler/custom_transaction_fee_handler.py", "w") as f:
                        f.write(transaction_fee_handler_mod.code)

        # queue
        if st.session_state['Queue']['implementation'] is not None:
                Path(f"{settings_folder}/queue").mkdir(parents=True)
                base_queue_code = inspect.getsource(AbstractQueue)
                queue_mod = ClassImplementationModifier(base_queue_code)
                queue_mod.replace_class_name("CustomQueue(AbstractQueue)")

                # replace init
                queue_init_params = ClassImplementationModifier.generate_init_method(
                        {param["name"]: param["default"] for param in st.session_state['Queue']['params']}, 
                        True,
                        "AbstractQueue"
                )
                queue_mod.replace_function('__init__', queue_init_params)

                # extract and replace custom implementation of queue functions
                sorting_logic_code = queue_mod.extract_function_code(st.session_state['Queue']['implementation'], 'sorting_logic')
                queue_mod.replace_function('sorting_logic', sorting_logic_code)
                dequeue_criteria_code = queue_mod.extract_function_code(st.session_state['Queue']['implementation'], 'dequeue_criteria')
                queue_mod.replace_function('dequeue_criteria', dequeue_criteria_code)

                queue_mod.insert_import_statement('from PSSimPy.utils import min_balance_maintained')
                queue_mod.insert_import_statement('from PSSimPy import Transaction')
                queue_mod.insert_import_statement('from PSSimPy.queues import AbstractQueue')
                queue_mod.insert_import_statement('from typing import Tuple')
                # Save the generated code to a file
                with open(f"{settings_folder}/queue/custom_queue.py", "w") as f:
                        f.write(queue_mod.code)

        # credit facility
        if st.session_state['Credit Facility']['implementation'] is not None:
                Path(f"{settings_folder}/credit_facility").mkdir(parents=True)
                base_credit_facility_code = inspect.getsource(AbstractCreditFacility)
                credit_facility_mod = ClassImplementationModifier(base_credit_facility_code)
                credit_facility_mod.replace_class_name("CustomCreditFacility(AbstractCreditFacility)")

                # replace init
                credit_facility_init_params = ClassImplementationModifier.generate_init_method(
                        {param["name"]: param["default"] for param in st.session_state['Credit Facility']['params']}, 
                        True,
                        "AbstractCreditFacility"
                )
                credit_facility_mod.replace_function('__init__', credit_facility_init_params)

                # extract and replace custom implementation of queue functions
                calculate_fee_code = credit_facility_mod.extract_function_code(st.session_state['Credit Facility']['implementation'], 'calculate_fee')
                credit_facility_mod.replace_function('calculate_fee', calculate_fee_code)
                lend_credit_code = credit_facility_mod.extract_function_code(st.session_state['Credit Facility']['implementation'], 'lend_credit')
                credit_facility_mod.replace_function('lend_credit', lend_credit_code)
                collect_repayment_code = credit_facility_mod.extract_function_code(st.session_state['Credit Facility']['implementation'], 'collect_repayment')
                credit_facility_mod.replace_function('collect_repayment', collect_repayment_code)

                credit_facility_mod.insert_import_statement('from PSSimPy import Account')
                credit_facility_mod.insert_import_statement('from PSSimPy.credit_facilities import AbstractCreditFacility')
                # Save the generated code to a file
                with open(f"{settings_folder}/credit_facility/custom_credit_facility.py", "w") as f:
                        f.write(credit_facility_mod.code)

        if include_data:
                Path(f"{settings_folder}/data").mkdir(parents=True)
                if st.session_state['Input Data']['Banks'] is not None:
                        st.session_state['Input Data']['Banks'].to_csv(f'{settings_folder}/data/banks.csv', index=False)
                if st.session_state['Input Data']['Accounts'] is not None:
                        st.session_state['Input Data']['Accounts'].to_csv(f'{settings_folder}/data/accounts.csv', index=False)
                if st.session_state['Input Data']['Transactions'] is not None:
                        st.session_state['Input Data']['Transactions'].to_csv(f'{settings_folder}/data/transactions.csv', index=False)

        # zip settings folder
        shutil.make_archive(f"saved_settings/{simulation_setting_name}", 'zip', settings_folder)

        return True

def import_simulation_setting(uploaded_file):
        with zipfile.ZipFile(uploaded_file) as z:
                # import parameters
                if 'static_data.json' in z.namelist():
                        with z.open('static_data.json') as f:
                                data = json.load(f)
                                st.session_state['Parameters'] = data['Parameters']
                                st.session_state['Random Transactions'] = data['Random Transactions']
                                st.session_state['Transaction Probability'] = data['Transaction Probability']
                                st.session_state['Transaction Amount Range'] = data['Transaction Amount Range']
                                st.session_state['Transaction Fee']['rate'] = data['Transaction Fee Rate']

                # import data
                if 'data/banks.csv' in z.namelist():
                        with z.open('data/banks.csv') as f:
                                df_banks = pd.read_csv(f)
                                st.session_state['Input Data']['Banks'] = df_banks
                if 'data/accounts.csv' in z.namelist():
                        with z.open('data/accounts.csv') as f:
                                df_accounts = pd.read_csv(f)
                                st.session_state['Input Data']['Accounts'] = df_accounts
                if 'data/transactions.csv' in z.namelist():
                        with z.open('data/transactions.csv') as f:
                                df_accounts = pd.read_csv(f)
                                st.session_state['Input Data']['Transactions'] = df_accounts

                # import constraint handler
                constraint_handler_files = [f for f in z.namelist() if f.startswith('constraint_handler/') and f.endswith('.py')]
                if constraint_handler_files:
                        constraint_handler_file = constraint_handler_files[0]
                        with z.open(constraint_handler_file) as f:
                                file_content = f.read().decode('utf-8')  # Decode bytes to string
                                st.code(file_content, language='python')

                                # compile constraint handler class
                                constraint_handler_class_name = ClassImplementationModifier.get_first_class_name(file_content)
                                exec_env = {
                                        'Transaction': Transaction,
                                        'AbstractConstraintHandler': AbstractConstraintHandler,
                                }
                                exec(file_content, globals(), exec_env)
                                CustomConstraintHandler = exec_env[constraint_handler_class_name]

                                # populate session_state
                                st.session_state['Constraint Handler']['class'] = CustomConstraintHandler
                                st.session_state['Constraint Handler']['implementation'] = ClassImplementationModifier.extract_function_code(file_content, 'process_transaction')
                                st.session_state['Constraint Handler']['params'] = [{'name': name, 'default': default_val} for name, default_val in ClassImplementationModifier.extract_init_params(file_content).items()]