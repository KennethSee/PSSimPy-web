import streamlit as st
import inspect
import textwrap
from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler, MaxSizeConstraintHandler, MinBalanceConstraintHandler
from PSSimPy.transaction_fee import AbstractTransactionFee
from PSSimPy. transaction import Transaction
from code_editor import code_editor

from utils.object import SUBMIT_BUTTON
from utils.helper import get_function_header

st.write('# Customize Settlement Agent')

# Constraints
st.write('## Define Constraints')
# let users select an out-of-the-box constraint handler template or define their own
ootb_constraint_templates = {'Pass Through': PassThroughHandler, 'Maximum Size': MaxSizeConstraintHandler, 'Minimum Balance': MinBalanceConstraintHandler}
constraint_select = st.selectbox('Select constraint handler', ['', 'Pass Through', 'Maximum Size', 'Minimum Balance', '(No Template)'])
if constraint_select == '(No Template)':
    # get function header of abstract method in the Constraint Handler
    constraint_function_header = get_function_header(AbstractConstraintHandler.process_transaction, is_abstract_method=True)
    # format it to only include a "pass" in the function body as placeholder
    old_constraint_code = f"{constraint_function_header}\n{textwrap.indent('pass', '    ')}"
elif constraint_select == '':
    if st.session_state['Constraint Handler'][1] is None:
        old_constraint_code = '# please select a template'
    else:
        old_constraint_code = st.session_state['Constraint Handler'][1]
else:
    constraint_template_code = inspect.getsource(ootb_constraint_templates[constraint_select].process_transaction)
    old_constraint_code = textwrap.dedent("\n".join(constraint_template_code.splitlines()[0:]))

# editor for user to implement function
constraint_implementation = code_editor(old_constraint_code, 
                                        height=[5, 1000], 
                                        lang='python', 
                                        buttons=SUBMIT_BUTTON,
                                        options={'wrap': True})
# save to session state on submit
if (constraint_implementation['text'] != '') and (constraint_implementation['text'] != st.session_state['Constraint Handler'][1]):
    # initialize constraint handler class with provided implementation
    class CustomConstraintHandler(AbstractConstraintHandler):
        def __init__(self):
            super().__init__()

        # implement placeholder abstract function
        def process_transaction(self, transaction):        
            pass

    # Use exec to dynamically define the new constraint method
    local_vars = {}
    exec(constraint_implementation['text'], globals(), local_vars)

    # overwrite placeholder abstract function
    CustomConstraintHandler.process_transaction = local_vars['process_transaction']

    # commit to session state
    st.session_state['Constraint Handler'] = (CustomConstraintHandler, constraint_implementation['text'])

    st.success('Constraint logic saved')

# Transaction Fee