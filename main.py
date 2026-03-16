"""
The entry point file to run this program. This file runs streamlit code for web displays, and
due to streamlit's architecture, is rerun from top to bottom after every update. In case the update
has a callback, this file is rerun after that callback has been executed. In order to persist variables
across reruns, st.session_state will be used.
TODO: continue this
"""

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
    ...
    # TODO: ask about this block, since the framework's way of running is different than running this block
    #  (one uses streamlit run main.py to run)
