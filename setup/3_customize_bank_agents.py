import streamlit as st
import inspect
import textwrap
from code_editor import code_editor
from PSSimPy import Bank

st.write('# Customize Bank Agents')

existing_strategy_implementation = inspect.getsource(Bank.strategy)
existing_strategy_implementation = "\n".join(existing_strategy_implementation.splitlines()[1:])
existing_strategy_implementation = textwrap.dedent(existing_strategy_implementation)

custom_btns = [{
  "name": "Submit",
#   "feather": "Submit",
  "hasText": True,
  "alwaysOn": True,
  "commands": ["submit"],
  "style": {"top": "0.46rem", "right": "0.4rem"}
}]
new_strategy_implementation = code_editor(existing_strategy_implementation, height=[5, 1000], lang='python', buttons=custom_btns)
if (existing_strategy_implementation != new_strategy_implementation['text']) and (existing_strategy_implementation != ''):
    existing_strategy_implementation = new_strategy_implementation['text']
    st.success('Strategy implementation updated')