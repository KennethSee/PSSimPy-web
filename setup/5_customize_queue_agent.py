import streamlit as st
import inspect
import textwrap
from code_editor import code_editor
from PSSimPy.queues import AbstractQueue, DirectQueue, FIFOQueue, PriorityQueue

from utils.object import SUBMIT_BUTTON
from utils.helper import get_function_header

st.write('# Customize Queue Agent')

ootb_queue_templates = {'Direct Queue': DirectQueue, 'FIFO Queue': FIFOQueue, 'Priority Queue': PriorityQueue}
queue_select = st.selectbox('Select queue template', ['', 'Direct Queue', 'FIFO Queue', 'Priority Queue', '(No Template)'])

if queue_select == '(No Template)':
    # get abstract function headers
    sorting_function_header = get_function_header(AbstractQueue.sorting_logic, True, True)
    dequeue_function_header = get_function_header(AbstractQueue.dequeue_criteria, True, True)
    # format them to only include a "pass" in the function body as placeholder
    old_sorting_code = f"{sorting_function_header}\n{textwrap.indent('pass', '    ')}"
    old_dequeue_code = f"{dequeue_function_header}\n{textwrap.indent('pass', '    ')}"
    old_merged_code = f"@staticmethod\n{old_sorting_code}\n\n@staticmethod\n{old_dequeue_code}"
elif queue_select == '':
    if st.session_state['Queue']['implementation'] is None:
        old_merged_code = '# please select a template'
    else:
        old_merged_code = st.session_state['Queue']['implementation']
else:
    sorting_template_code = inspect.getsource(ootb_queue_templates[queue_select].sorting_logic)
    dequeue_template_code = inspect.getsource(ootb_queue_templates[queue_select].dequeue_criteria)
    old_sorting_code = textwrap.dedent("\n".join(sorting_template_code.splitlines()[0:]))
    old_dequeue_code = textwrap.dedent("\n".join(dequeue_template_code.splitlines()[0:]))
    old_merged_code = f"{old_sorting_code}\n\n{old_dequeue_code}"

queue_implementation = code_editor('\n' + old_merged_code, # pad empty first line
                                        height=[5, 1000], 
                                        lang='python', 
                                        buttons=SUBMIT_BUTTON,
                                        options={'wrap': True},
                                        key=f'queue_code_{queue_select}')