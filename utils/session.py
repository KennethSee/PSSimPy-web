import streamlit as st
import pandas as pd
import json
import shutil
import inspect
from pathlib import Path
from PSSimPy import Bank
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
        initialize_dict_key(st.session_state, 'Constraint Handler', {'class': PassThroughHandler, 'implementation': None}) # default to pass through
        # Transaction Fee
        initialize_dict_key(st.session_state, 'Transaction Fee', {
                'rate': 0.0,
                'class': FixedTransactionFee, # placeholder
                'implementation': None
        })
        # Queue Handler
        initialize_dict_key(st.session_state, 'Queue', {'class': DirectQueue, 'implementation': None})
        # Credit Facility
        initialize_dict_key(st.session_state, 'Credit Facility', {'class': SimplePriced, 'implementation': None})
        # Output Files
        initialize_dict_key(st.session_state, 'Log Files', {
                'Processed Transactions': pd.DataFrame(),
                'Transaction Fees': pd.DataFrame(),
                'Queue Stats': pd.DataFrame(),
                'Account Balance': pd.DataFrame(),
                'Credit Facility': pd.DataFrame(),
                'Transactions Arrival': pd.DataFrame()
        })


def save_simulation_settings(simulation_setting_name: str) -> bool:
        # create saved settings folder if it does not exist
        Path("./saved_settings").mkdir(parents=True, exist_ok=True)

        # create folder to contain settings
        simulation_setting_name = replace_whitespace_with_underscore(simulation_setting_name)
        settings_folder = f"./saved_settings/{simulation_setting_name}"
        Path(settings_folder).mkdir(parents=True)

        # create json file for static data
        static_data = {'Parameters': st.session_state['Parameters'], 'Transaction Fee Rate': st.session_state['Transaction Fee']['rate']}
        with open(f"{settings_folder}/{static_data}", "w") as file:
                json.dump(static_data , file) 

        # create bank strategy implementations
        # save_class_to_file(st.session_state['Bank Strategies']['Test']['class'], f'{settings_folder}/test.py')
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
        

        # zip settings folder
        shutil.make_archive(simulation_setting_name, 'zip', settings_folder)

        return True