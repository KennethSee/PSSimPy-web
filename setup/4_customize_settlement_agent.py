import streamlit as st
import inspect
import textwrap
from copy import copy
from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler, MaxSizeConstraintHandler, MinBalanceConstraintHandler
from PSSimPy.transaction_fee import AbstractTransactionFee, FixedTransactionFee
from PSSimPy.transaction import Transaction
from PSSimPy.account import Account
from PSSimPy.utils import min_balance_maintained
from code_editor import code_editor
from typing import Union, Dict

from utils.object import SUBMIT_BUTTON
from utils.helper import get_function_header, ClassImplementationModifier
from utils.date_time import is_24_hour_format


# Initialize session state variables if they don't exist
if "temp_params" not in st.session_state:
    st.session_state["temp_params"] = []  # List to store parameter rows
if "param_counter" not in st.session_state:
    st.session_state["param_counter"] = 0  # Counter for unique keys
if "current_constraint_handler" not in st.session_state:
    st.session_state["current_constraint_handler"] = ""

def add_parameter_row():
    """Add a new parameter row."""
    st.session_state["temp_params"].append(
        {"name": "", "default": None}
    )
    st.session_state["param_counter"] += 1

st.write('# Customize Settlement Agent')

st.write("## Define Constraints")

# Out-of-the-box templates
ootb_constraint_templates = {
    "Pass Through": PassThroughHandler,
    "Maximum Size": MaxSizeConstraintHandler,
    "Minimum Balance": MinBalanceConstraintHandler,
}

constraint_select = st.selectbox(
    "Select constraint handler",
    ["", "Pass Through", "Maximum Size", "Minimum Balance", "(No Template)"],
)

if constraint_select == "(No Template)":
    if st.session_state["current_constraint_handler"] != constraint_select:
        st.session_state["temp_params"] = [] # reset
        st.session_state["param_counter"] = 0
    st.session_state["current_constraint_handler"] = constraint_select
    constraint_function_header = get_function_header(
        AbstractConstraintHandler.process_transaction, is_abstract_method=True
    )
    old_constraint_code = f"{constraint_function_header}\n{textwrap.indent('pass', '    ')}"

elif constraint_select == "":
    if st.session_state["current_constraint_handler"] != constraint_select:
        st.session_state["temp_params"] = st.session_state['Constraint Handler']['params'] # reset
        st.session_state["param_counter"] = 0
    st.session_state["current_constraint_handler"] = constraint_select
    if st.session_state.get("Constraint Handler", {}).get("implementation") is None:
        old_constraint_code = "# please select a template"
    else:
        old_constraint_code = st.session_state["Constraint Handler"]["implementation"]
else:
    if st.session_state["current_constraint_handler"] != constraint_select:
        st.session_state["temp_params"] = [] # reset
        st.session_state["param_counter"] = 0
    st.session_state["current_constraint_handler"] = constraint_select
    temp_settlement_params = (
        ClassImplementationModifier.extract_init_params(
            inspect.getsource(ootb_constraint_templates[constraint_select])
        )
    )
    for key, value in temp_settlement_params.items():
        existing_param = {"name": key, "default": value}
        if existing_param["name"] not in [param["name"] for param in st.session_state["temp_params"]]:
            st.session_state["temp_params"].append({"name": key, "default": value})
    constraint_template_code = inspect.getsource(
        ootb_constraint_templates[constraint_select].process_transaction
    )
    old_constraint_code = textwrap.dedent("\n".join(constraint_template_code.splitlines()))

st.write("### Custom Parameters")

# Add Parameter Button
if st.button("Add Parameter"):
    add_parameter_row()

# Display Parameter Inputs
for i, param in enumerate(st.session_state["temp_params"]):
    col1, col2 = st.columns(2)
    with col1:
        param_name = st.text_input(
            "Parameter Name", 
            key=f"param_name_{i}", 
            value=param["name"], 
            placeholder="Enter parameter name"
        )
        st.session_state["temp_params"][i]["name"] = param_name

    with col2:
        default_value = st.text_input(
            "Default Value (optional)", 
            key=f"default_value_{i}", 
            value=param["default"] or "", 
            placeholder="Enter default value"
        )
        # Store None if the input is blank
        st.session_state["temp_params"][i]["default"] = default_value if default_value.strip() else None



st.write('### Constraint Logic')
# editor for user to implement function
constraint_implementation = code_editor('\n' + old_constraint_code, # pad empty first line
                                        height=[5, 1000], 
                                        lang='python', 
                                        buttons=SUBMIT_BUTTON,
                                        options={'wrap': True},
                                        key=f'constraint_code_{constraint_select}')
# save to session state on submit
constraint_implementation['text'] = "\n".join(constraint_implementation['text'].splitlines()[1:]) # strip first empty line
if (constraint_implementation['text'] != '') and (
    (constraint_implementation['text'] != st.session_state['Constraint Handler']['implementation'])
    or (st.session_state['Constraint Handler']['params'] != st.session_state['temp_params'])
    ):
    # initialize constraint handler class with provided implementation
    class CustomConstraintHandler(AbstractConstraintHandler):
        def __init__(self):
            super().__init__()

        # implement placeholder abstract function
        def process_transaction(self, transaction):        
            pass

    init_implementation = ClassImplementationModifier.generate_init_method({param["name"]: param["default"] for param in st.session_state['temp_params']}, True, "AbstractConstraintHandler")
    # Use exec to dynamically define the new constraint method
    exec_env = {
            'Transaction': Transaction,
            'AbstractConstraintHandler': AbstractConstraintHandler,
            'min_balance_maintained': min_balance_maintained
    }
    exec(init_implementation, globals(), exec_env)
    exec(constraint_implementation['text'], globals(), exec_env)

    # overwrite placeholder init and abstract functions
    CustomConstraintHandler.__init__ = exec_env['__init__']
    CustomConstraintHandler.process_transaction = exec_env['process_transaction']

    # commit to session state
    st.session_state['Constraint Handler'] = {'class': CustomConstraintHandler, 'implementation': constraint_implementation['text'], 'params': copy(st.session_state['temp_params'])}

    st.success('Constraint logic saved')

# Transaction Fee
st.write('## Define Transaction Fee')
st.write('### Fee Rate')
is_dynamic_fee = st.checkbox('Dynamic transaction fee', help='Check if rate varies throughout the day')
if is_dynamic_fee:
    # Dynamically handle multiple inputs for time and rate
    num_rows = st.number_input("Number of time-rate pairs", min_value=1, max_value=24, value=1, step=1)

    # Create input fields dynamically for each time-rate pair
    time_rate_pairs = {}
    for i in range(num_rows):
        cols = st.columns([2, 1])  # Adjust the column ratio
        with cols[0]:
            time = st.text_input(f"Time {i+1} (HH:MM)", value="00:00", key=f"time_{i}", help="Enter time in 24h format")
            if not is_24_hour_format(time):
                st.warning('Time is not in 24h format')
        with cols[1]:
            rate = st.number_input(f"Rate {i+1}", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f", key=f"rate_{i}")
        
        # Store the input in the dictionary
        time_rate_pairs[time] = rate

    # Save the dictionary to session state
    st.session_state['Transaction Fee']['rate'] = time_rate_pairs
    st.write('Current Time-Rate pairs:', st.session_state['Transaction Fee']['rate'])

    # Save the dictionary to session state
    st.session_state['Transaction Fee']['rate'] = time_rate_pairs
else:
    st.session_state['Transaction Fee']['rate'] = st.number_input('Fixed Rate', min_value=0.0, max_value=1.0, step=0.0001)

st.write('### Fee Logic')
# let users select from fee template or define their own
ootb_fee_templates = {'Fixed Rate': FixedTransactionFee}
fee_select = st.selectbox('Select constraint handler', ['', 'Fixed Rate', '(No Template)'])
if fee_select == '(No Template)':
    # get function header of abstract method in the Transaction Fee Handler
    fee_function_header = get_function_header(AbstractTransactionFee.calculate_fee, is_abstract_method=True)
    # format it to only include a "pass" in the function body as placeholder
    old_fee_code = f"{fee_function_header}\n{textwrap.indent('pass', '    ')}"
elif fee_select == '':
    if st.session_state['Transaction Fee']['implementation'] is None:
        old_fee_code = '# please select a template'
    else:
        old_fee_code = st.session_state['Transaction Fee']['implementation']
else:
    fee_template_code = inspect.getsource(ootb_fee_templates[fee_select].calculate_fee)
    old_fee_code = textwrap.dedent("\n".join(fee_template_code.splitlines()[0:]))

fee_implementation = code_editor('\n' + old_fee_code, # pad empty first line
                                        height=[5, 1000], 
                                        lang='python', 
                                        buttons=SUBMIT_BUTTON,
                                        options={'wrap': True},
                                        key=f'fee_code_{fee_select}')

# save session state on submit
fee_implementation['text'] = "\n".join(fee_implementation['text'].splitlines()[1:]) # strip first empty line
if (fee_implementation['text'] != '') and (fee_implementation['text'] != st.session_state['Transaction Fee']['implementation']):
    # initialize transactino fee handler class with provided implementation
    class CustomTransactionFee(AbstractTransactionFee):
        def __init__(self):
            super().__init__()

        # implement placeholder abstract function
        def calculate_fee(self, txn_amount: int, time: str, rate: Union[float, Dict[str, float]]) -> float:
            pass
    
    # Use exec to dynamically define the new constraint method
    local_vars = {}
    exec(fee_implementation['text'], globals(), local_vars)

    # overwrite placeholder abstract function
    CustomTransactionFee.process_transaction = local_vars['calculate_fee']

    # commit to session state
    st.session_state['Transaction Fee']['class'] = CustomTransactionFee
    st.session_state['Transaction Fee']['implementation'] = fee_implementation['text']

    st.success('Constraint logic saved')