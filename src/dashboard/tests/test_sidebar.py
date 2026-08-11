import pytest
import streamlit as st

from sidebar import FILTER_STATE_KEYS, initialise_filter_state, reset_filters

CONFIGURED_DEFAULTS = {
    "region": "Uusimaa",
    "job_field": "Information Technology",
    "seniority_level": "Mid-Senior level",
    "period": "Past month",
}

FILTER_OPTIONS = {
    "region": ["All regions", "Uusimaa", "Pirkanmaa"],
    "job_field": ["All fields", "Information Technology", "Engineering"],
    "seniority_level": ["All levels", "Mid-Senior level", "Entry level"],
    "period": ["Past week", "Past month", "Past year"],
}


@pytest.fixture(autouse=True)
def clear_session_state():
    st.session_state.clear()
    yield
    st.session_state.clear()


class TestInitialiseFilterState:
    def test_seeds_every_filter_from_the_configuration(self):
        initialise_filter_state(CONFIGURED_DEFAULTS, FILTER_OPTIONS)
        for key, value in CONFIGURED_DEFAULTS.items():
            assert st.session_state[key] == value

    def test_seeds_the_tab_search_and_page_state(self):
        initialise_filter_state(CONFIGURED_DEFAULTS, FILTER_OPTIONS)
        assert st.session_state["tab"] == "Analysis"
        assert st.session_state["search_query"] == ""
        assert st.session_state["page"] == 1

    def test_keeps_a_selection_the_user_has_already_made(self):
        st.session_state["region"] = "Pirkanmaa"
        initialise_filter_state(CONFIGURED_DEFAULTS, FILTER_OPTIONS)
        assert st.session_state["region"] == "Pirkanmaa"

    @pytest.mark.parametrize("key", FILTER_STATE_KEYS)
    def test_rejects_a_default_that_is_not_an_option(self, key):
        defaults = {**CONFIGURED_DEFAULTS, key: "not an option"}
        with pytest.raises(ValueError, match=key):
            initialise_filter_state(defaults, FILTER_OPTIONS)


class TestResetFilters:
    def test_returns_every_filter_to_its_configured_default(self):
        initialise_filter_state(CONFIGURED_DEFAULTS, FILTER_OPTIONS)
        st.session_state["region"] = "Pirkanmaa"
        st.session_state["period"] = "Past year"
        st.session_state["search_query"] = "data"
        st.session_state["page"] = 4

        reset_filters()

        for key, value in CONFIGURED_DEFAULTS.items():
            assert st.session_state[key] == value
        assert st.session_state["search_query"] == ""
        assert st.session_state["page"] == 1
