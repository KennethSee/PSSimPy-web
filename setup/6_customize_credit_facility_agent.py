import streamlit as st
import inspect
import textwrap
from copy import copy
from code_editor import code_editor
from PSSimPy.credit_facilities import AbstractCreditFacility, SimpleCollateralized, SimplePriced
from PSSimPy import Account

from utils.object import SUBMIT_BUTTON
from utils.helper import get_function_header, add_parameter_row, ClassImplementationModifier

# Initialize session state variables if they don't exist
if "temp_facility_params" not in st.session_state:
    st.session_state["temp_facility_params"] = []  # List to store parameter rows
if "facility_param_counter" not in st.session_state:
    st.session_state["facility_param_counter"] = 0  # Counter for unique keys
if "current_facility" not in st.session_state:
    st.session_state["current_facility"] = ""

st.write('# Customize Credit Facility Agent')

ootb_facility_templates = {'Simple Priced': SimplePriced, 'Simple Collateralized': SimpleCollateralized}
facility_select = st.selectbox('Select credit facility template', ['', 'Simple Priced', 'Simple Collateralized', '(No Template)'])

if facility_select == '(No Template)':
    if st.session_state["current_facility"] != facility_select:
        st.session_state["temp_facility_params"] = [] # reset
        st.session_state["facility_param_counter"] = 0
    st.session_state["current_facility"] = facility_select
    # get abstract function headers
    calculate_fee_function_header = get_function_header(AbstractCreditFacility.calculate_fee, True, False)
    lend_credit_function_header = get_function_header(AbstractCreditFacility.lend_credit, True, False)
    collect_repayment_function_header = get_function_header(AbstractCreditFacility.collect_repayment, True, False)
    # format them to only include a "pass" in the function body as placeholder
    old_calculate_fee_code = f"{calculate_fee_function_header}\n{textwrap.indent('pass', '    ')}"
    old_lend_credit_code = f"{lend_credit_function_header}\n{textwrap.indent('pass', '    ')}"
    old_collect_repayment_code = f"{collect_repayment_function_header}\n{textwrap.indent('pass', '    ')}"
    old_merged_code = f"{old_calculate_fee_code}\n\n{old_lend_credit_code}\n\n{old_collect_repayment_code}"
elif facility_select == '':
    if st.session_state["current_facility"] != facility_select:
        st.session_state["temp_facility_params"] = st.session_state['Credit Facility']['params'] # reset
        st.session_state["facility_param_counter"] = 0
    st.session_state["current_facility"] = facility_select
    # display stored implemented code, or display blank code canvas if not implemented yet
    if st.session_state['Credit Facility']['implementation'] is None:
        old_merged_code = '# please select a template'
    else:
        old_merged_code = st.session_state['Credit Facility']['implementation']
else:
    if st.session_state["current_facility"] != facility_select:
        st.session_state["temp_facility_params"] = [] # reset
        st.session_state["facility_param_counter"] = 0
    temp_facility_params = (
        ClassImplementationModifier.extract_init_params(
            inspect.getsource(ootb_facility_templates[facility_select])
        )
    )
    for key, value in temp_facility_params.items():
        existing_param = {"name": key, "default": value}
        if existing_param["name"] not in [param["name"] for param in st.session_state["temp_facility_params"]]:
            st.session_state["temp_facility_params"].append({"name": key, "default": value})
    
    st.session_state["current_facility"] = facility_select
    # display selected code implementation
    calculate_fee_template_code = inspect.getsource(ootb_facility_templates[facility_select].calculate_fee)
    lend_credit_template_code = inspect.getsource(ootb_facility_templates[facility_select].lend_credit)
    collect_repayment_template_code = inspect.getsource(ootb_facility_templates[facility_select].collect_repayment)
    old_calculate_fee_code = textwrap.dedent("\n".join(calculate_fee_template_code.splitlines()[0:]))
    old_lend_credit_code = textwrap.dedent("\n".join(lend_credit_template_code.splitlines()[0:]))
    old_collect_repayment_code = textwrap.dedent("\n".join(collect_repayment_template_code.splitlines()[0:]))
    old_merged_code = f"{old_calculate_fee_code}\n\n{old_lend_credit_code}\n\n{old_collect_repayment_code}"

st.write("### Custom Parameters")

# Add Parameter Button
if st.button("Add Parameter"):
    add_parameter_row()

# Display Parameter Inputs
for i, param in enumerate(st.session_state["temp_facility_params"]):
    col1, col2 = st.columns(2)
    with col1:
        param_name = st.text_input(
            "Parameter Name", 
            key=f"param_name_{i}", 
            value=param["name"], 
            placeholder="Enter parameter name"
        )
        st.session_state["temp_facility_params"][i]["name"] = param_name

    with col2:
        default_value = st.text_input(
            "Default Value (optional)", 
            key=f"default_value_{i}", 
            value=param["default"] or "", 
            placeholder="Enter default value"
        )
        # Store None if the input is blank
        st.session_state["temp_facility_params"][i]["default"] = default_value if default_value.strip() else None

st.write("### Credit Facility Logic")
facility_implementation = code_editor('\n' + old_merged_code, # pad empty first line
                                        height=[5, 1000], 
                                        lang='python', 
                                        buttons=SUBMIT_BUTTON,
                                        options={'wrap': True},
                                        key=f'queue_code_{facility_select}')

# save to session state on save
facility_implementation['text'] = "\n".join(facility_implementation['text'].splitlines()[1:]) # strip first empty line
if (facility_implementation['text'] != '') and (facility_implementation['text'] != st.session_state['Credit Facility']['implementation']):
    # initialize credit facility class with provided implementation
    class CustomCreditFacility(AbstractCreditFacility):

        def __init__(self):
            super().__init__()

        # placeholder abstract function implementations
        def calculate_fee(self, amount):
            pass
        def lend_credit(self, account, amount):
            pass
        def collect_repayment(self, account):
            pass

    init_implementation = ClassImplementationModifier.generate_init_method({param["name"]: param["default"] for param in st.session_state['temp_facility_params']}, True, "AbstractCreditFacility")
    # Use exec to dynamically define the new methods
    exec_env = {
            'AbstractCreditFacility': AbstractCreditFacility,
            'Account': Account
    }
    exec(init_implementation, globals(), exec_env)
    exec(facility_implementation['text'], globals(), exec_env)

    # add abstract function implementation
    CustomCreditFacility.__init__ = exec_env['__init__']
    CustomCreditFacility.calculate_fee = exec_env['calculate_fee']
    CustomCreditFacility.lend_credit = exec_env['lend_credit']
    CustomCreditFacility.collect_repayment = exec_env['collect_repayment']

    # commit to session state
    st.session_state['Credit Facility']['class'] = CustomCreditFacility
    st.session_state['Credit Facility']['implementation'] = facility_implementation['text']
    st.session_state['Credit Facility']['params'] = copy(st.session_state['temp_facility_params'])

    st.success('Credit Facility logic saved')