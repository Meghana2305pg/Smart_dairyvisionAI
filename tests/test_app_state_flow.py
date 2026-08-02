import unittest
from unittest.mock import patch

import streamlit as st

from webapp.app import _prepare_workspace_state, initialize_app_state, update_app_state
from webapp.state.session_state import APP_STATE_AUTHENTICATED_NO_FARM, APP_STATE_AUTHENTICATED_WITH_FARM, APP_STATE_NOT_AUTHENTICATED


from webapp.repositories.supabase_client import SupabaseClient


class AppStateFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        st.session_state.clear()
        st.query_params.clear()
        SupabaseClient.from_env().reset_in_memory_store()

    def tearDown(self) -> None:
        st.session_state.clear()
        st.query_params.clear()
        SupabaseClient.from_env().reset_in_memory_store()

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

    def test_prepare_workspace_state_restores_existing_farm_after_login(self) -> None:
        initialize_app_state()
        farm_service = st.session_state.farm_service
        farm_service.create_farm(farm_id="farm-restore", name="Restore Farm", location="Nairobi")

        st.session_state.authenticated = True
        st.session_state.user = None
        st.session_state.user_id = None
        st.session_state.farm = None
        st.session_state.farm_id = None
        st.query_params["user_id"] = "user-restore"
        st.query_params["user_email"] = "owner@example.com"
        st.query_params["farm_id"] = "farm-restore"
        st.query_params["active_section"] = "dashboard"

        _prepare_workspace_state()

        self.assertTrue(st.session_state.authenticated)
        self.assertEqual(st.session_state.user_id, "user-restore")
        self.assertEqual(st.session_state.farm_id, "farm-restore")
        self.assertEqual(st.session_state.farm["farm_id"], "farm-restore")
        self.assertEqual(st.session_state.app_state, APP_STATE_AUTHENTICATED_WITH_FARM)

    def test_prepare_workspace_state_keeps_registration_in_farm_setup_once(self) -> None:
        initialize_app_state()

        st.session_state.authenticated = True
        st.session_state.user = {"id": "user-new", "email": "new@example.com", "full_name": "New User"}
        st.session_state.user_id = "user-new"
        st.session_state.pending_farm_setup = True
        st.session_state.farm = None
        st.session_state.farm_id = None
        st.query_params["user_id"] = "user-new"
        st.query_params["pending_farm_setup"] = "1"

        _prepare_workspace_state()

        self.assertTrue(st.session_state.authenticated)
        self.assertTrue(st.session_state.pending_farm_setup)
        self.assertIsNone(st.session_state.farm)
        self.assertEqual(st.session_state.app_state, APP_STATE_AUTHENTICATED_NO_FARM)


if __name__ == "__main__":
    unittest.main()
