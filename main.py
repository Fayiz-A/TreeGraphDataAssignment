"""
Ontario Road Closure Analysis App
================================

The entry point file to run this program. This file runs streamlit code for web displays, and
due to streamlit's architecture, is rerun from top to bottom after every update. In case the update
has a callback, this file is rerun after that callback has been executed. In order to persist variables
across reruns, st.session_state will be used.

This file contains minimal sandboxing code that could not be put into class due to framework restrictions,
and rest of Streamlit code is in streamlit_manager.py. Any further logic in this should not be written.
"""

# the code below is top level and not in a function due to framework specific reasons. It needs a command to run,
# and that command does not execute functions but this top level code. Still, it is minimal bootstrapping code,
# and the main code is in streamlit_manager.py for streamlit related matters.

import streamlit as st

import constants
from streamlit_manager import StreamlitManager

streamlit_manager_key: str = constants.SESSION_STATE_STREAMLIT_MANAGER_KEY

if st.session_state.get(streamlit_manager_key) is None:
    streamlit_manager: StreamlitManager = StreamlitManager()

    st.session_state[streamlit_manager_key] = streamlit_manager

streamlit_manager: StreamlitManager = st.session_state.get(streamlit_manager_key)
streamlit_manager.display()

if __name__ == '__main__':
    # running this block is not the correct way to run our code. See project proposal.tex file for steps to operate.
    pass
