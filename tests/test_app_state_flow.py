import unittest
from unittest.mock import patch

import streamlit as st

from webapp.app import initialize_app_state, update_app_state
from webapp.state.session_state import APP_STATE_AUTHENTICATED_NO_FARM, APP_STATE_NOT_AUTHENTICATED


class AppStateFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        st.session_state.clear()

    def test_initialize_app_state_bootstraps_once_and_preserves_authenticated_state(self) -> None:
        initialize_app_state()
        st.session_state.authenticated = True
        st.session_state.farm = None
        update_app_state()

        self.assertEqual(st.session_state.app_state, APP_STATE_AUTHENTICATED_NO_FARM)
        self.assertEqual(st.session_state.active_view, "login")

    def test_initialize_app_state_keeps_default_state_for_unauthenticated_users(self) -> None:
        initialize_app_state()
        update_app_state()

        self.assertEqual(st.session_state.app_state, APP_STATE_NOT_AUTHENTICATED)
        self.assertFalse(st.session_state.authenticated)


if __name__ == "__main__":
    unittest.main()
