import streamlit as st
import inspect
import textwrap
from typing import Tuple, List, Set
from sortedcontainers import SortedList
from code_editor import code_editor
from PSSimPy.queues import AbstractQueue, DirectQueue, FIFOQueue, PriorityQueue
from PSSimPy.utils import min_balance_maintained
from PSSimPy import Transaction

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

# save to session state on save
queue_implementation['text'] = "\n".join(queue_implementation['text'].splitlines()[1:]) # strip first empty line
if (queue_implementation['text'] != '') and (queue_implementation['text'] != st.session_state['Queue']['implementation']):
    # initialize transaction fee handler class with provided implementation
    class CustomQueue(AbstractQueue):

        def __init__(self):
            super().__init__()

    # Use exec to dynamically define the new constraint method
    exec_env = {
            'AbstractQueue': AbstractQueue,
            'Transaction': Transaction,
            'Tuple': Tuple,
            'List': List,
            'Set': Set,
            'SortedList': SortedList,
            'min_balance_maintained': min_balance_maintained
    }
    exec(queue_implementation['text'], globals(), exec_env)

    # add abstract function implementation
    CustomQueue.sorting_logic = exec_env['sorting_logic']
    CustomQueue.dequeue_criteria = exec_env['dequeue_criteria']

    # commit to session state
    st.session_state['Queue']['class'] = CustomQueue
    st.session_state['Queue']['implementation'] = queue_implementation['text']

    st.success('Queue logic saved')