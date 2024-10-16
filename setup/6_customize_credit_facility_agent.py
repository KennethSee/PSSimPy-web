import streamlit as st
import inspect
import textwrap
from code_editor import code_editor
from PSSimPy.credit_facilities import AbstractCreditFacility, SimpleCollateralized, SimplePriced
from PSSimPy import Account

from utils.object import SUBMIT_BUTTON
from utils.helper import get_function_header

st.write('# Customize Credit Facility Agent')

ootb_facility_templates = {'Simple Priced': SimplePriced, 'Simple Collateralized': SimpleCollateralized}
facility_select = st.selectbox('Select credit facility template', ['', 'Simple Priced', 'Simple Collateralized', '(No Template)'])

if facility_select == '(No Template)':
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
    if st.session_state['Credit Facility']['implementation'] is None:
        old_merged_code = '# please select a template'
    else:
        old_merged_code = st.session_state['Credit Facility']['implementation']
else:
    calculate_fee_template_code = inspect.getsource(ootb_facility_templates[facility_select].calculate_fee)
    lend_credit_template_code = inspect.getsource(ootb_facility_templates[facility_select].lend_credit)
    collect_repayment_template_code = inspect.getsource(ootb_facility_templates[facility_select].collect_repayment)
    old_calculate_fee_code = textwrap.dedent("\n".join(calculate_fee_template_code.splitlines()[0:]))
    old_lend_credit_code = textwrap.dedent("\n".join(lend_credit_template_code.splitlines()[0:]))
    old_collect_repayment_code = textwrap.dedent("\n".join(collect_repayment_template_code.splitlines()[0:]))
    old_merged_code = f"{old_calculate_fee_code}\n\n{old_lend_credit_code}\n\n{old_collect_repayment_code}"

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

    # Use exec to dynamically define the new methods
    local_vars = {}
    exec(facility_implementation['text'], globals(), local_vars)

    # add abstract function implementation
    CustomCreditFacility.calculate_fee = local_vars['calculate_fee']
    CustomCreditFacility.lend_credit = local_vars['lend_credit']
    CustomCreditFacility.collect_repayment = local_vars['collect_repayment']

    # commit to session state
    st.session_state['Credit Facility']['class'] = CustomCreditFacility
    st.session_state['Credit Facility']['implementation'] = facility_implementation['text']

    st.success('Credit Facility logic saved')