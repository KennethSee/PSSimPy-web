import streamlit as st
import textwrap
from code_editor import code_editor # uses streamlit-code-editor package
from PSSimPy import Bank
from PSSimPy.queues import AbstractQueue

from utils.object import SUBMIT_BUTTON
from utils.helper import get_function_header

st.write('# Customize Bank Agents')

# select strategy
strategy_options = list(st.session_state['Bank Strategies'].keys()) + ["(Add New Bank Strategy)"]
selected_strategy_option = st.selectbox("Choose a Bank Strategy", strategy_options)
if selected_strategy_option == "(Add New Bank Strategy)":
    strategy_name = st.text_input("Enter a name for the new Bank Strategy")
    existing_strategy_implementation = f"\n{get_function_header(Bank.strategy, False)}\n{textwrap.indent('pass', '    ')}"
else:
    strategy_name = selected_strategy_option
    selected_strategy = st.session_state['Bank Strategies'][selected_strategy_option]
    existing_strategy_implementation = '\n' + selected_strategy['implementation']
    # existing_strategy_implementation = "\n".join(existing_strategy_implementation.splitlines()[1:])
    # existing_strategy_implementation = textwrap.dedent(existing_strategy_implementation)

# code editor for editing strategy logic
new_strategy_implementation = code_editor(existing_strategy_implementation, 
                                          height=[5, 1000], 
                                          lang='python', 
                                          buttons=SUBMIT_BUTTON,
                                          options={'wrap': True})

if (existing_strategy_implementation != new_strategy_implementation['text']) and (new_strategy_implementation['text'] != '') and (strategy_name != ''):
    existing_strategy_implementation = "\n".join(new_strategy_implementation['text'].splitlines()[1:])
    class CustomBank(Bank):

        def __init__(self, name, strategy_type=strategy_name, **kwargs):
            super().__init__(name, strategy_type, **kwargs)

    # full_strategy_code = f"def strategy(self):\n{textwrap.indent(existing_strategy_implementation, '    ')}"

    # Use exec to dynamically define the new strategy method
    local_vars = {}
    exec(existing_strategy_implementation, globals(), local_vars)

    # Overwrite the strategy method of CustomBank with the dynamically created function
    CustomBank.strategy = local_vars['strategy']

    # Store new Bank class in session state
    st.session_state['Bank Strategies'][strategy_name] = {'class': CustomBank, 'implementation': existing_strategy_implementation}


    st.success(f'Strategy "{strategy_name}" implementation updated!')