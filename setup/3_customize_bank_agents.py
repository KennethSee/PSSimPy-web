import streamlit as st
import textwrap
from code_editor import code_editor # uses streamlit-code-editor package
from PSSimPy import Bank

st.write('# Customize Bank Agents')

# select strategy
strategy_options = list(st.session_state['Bank Strategies'].keys()) + ["(Add New Bank Strategy)"]
selected_strategy_option = st.selectbox("Choose a Bank Strategy", strategy_options)
if selected_strategy_option == "(Add New Bank Strategy)":
    strategy_name = st.text_input("Enter a name for the new Bank Strategy")
    existing_strategy_implementation = ''
else:
    strategy_name = selected_strategy_option
    selected_strategy = st.session_state['Bank Strategies'][selected_strategy_option]
    existing_strategy_implementation = selected_strategy['implementation']
    # existing_strategy_implementation = "\n".join(existing_strategy_implementation.splitlines()[1:])
    # existing_strategy_implementation = textwrap.dedent(existing_strategy_implementation)

# code editor for editing strategy logic
custom_btns = [{
  "name": "Submit",
#   "feather": "Submit",
  "hasText": True,
  "alwaysOn": True,
  "commands": ["submit"],
  "style": {"top": "0.46rem", "right": "0.4rem"}
}]
new_strategy_implementation = code_editor(existing_strategy_implementation, height=[5, 1000], lang='python', buttons=custom_btns)
if (existing_strategy_implementation != new_strategy_implementation['text']) and (new_strategy_implementation['text'] != '') and (strategy_name != ''):
    existing_strategy_implementation = new_strategy_implementation['text']
    class CustomBank(Bank):
        pass  # Placeholder until we overwrite the strategy method below

    full_strategy_code = f"def strategy(self):\n{textwrap.indent(existing_strategy_implementation, '    ')}"

    # Use exec to dynamically define the new strategy method
    local_vars = {}
    exec(full_strategy_code, globals(), local_vars)

    # Overwrite the strategy method of CustomBank with the dynamically created function
    CustomBank.strategy = local_vars['strategy']

    # Store new Bank class in session state
    st.session_state['Bank Strategies'][strategy_name] = {'class': CustomBank, 'implementation': existing_strategy_implementation}


    st.success(f'Strategy "{strategy_name}" implementation updated!')