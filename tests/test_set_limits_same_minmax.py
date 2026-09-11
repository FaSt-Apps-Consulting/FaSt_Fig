"""Tests for set_xlim/set_ylim warning prevention when min == max."""

import numpy as np
import warnings

import pytest

from fast_fig import FFig


class TestSetLimitsSameMinMax:
    """Test that set_xlim/set_ylim don't warn when min equals max."""

    def _assert_no_user_warning(self, func, *args, **kwargs):
        """Helper to assert a function call produces no UserWarnings."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            func(*args, **kwargs)
            # Filter out any warnings that might come from matplotlib internals
            user_warnings = [x for x in w if x.category is UserWarning]
            assert len(user_warnings) == 0, (
                f"Expected no UserWarnings, got {len(user_warnings)}: "
                f"{[str(x.message) for x in user_warnings]}"
            )

    def test_set_xlim_same_values_no_user_warning(self):
        """set_xlim(0, 0) should not produce UserWarning."""
        fig = FFig()
        fig.plot([1, 2, 3], [4, 5, 6])
        self._assert_no_user_warning(fig.set_xlim, 0, 0)

    def test_set_ylim_same_values_no_user_warning(self):
        """set_ylim(0, 0) should not produce UserWarning."""
        fig = FFig()
        fig.plot([1, 2, 3], [4, 5, 6])
        self._assert_no_user_warning(fig.set_ylim, 0, 0)

    def test_set_xlim_different_values_no_user_warning(self):
        """set_xlim(0, 10) should not produce UserWarning."""
        fig = FFig()
        fig.plot([1, 2, 3], [4, 5, 6])
        self._assert_no_user_warning(fig.set_xlim, 0, 10)
        # Verify limits are set correctly
        assert fig.current_axis.get_xlim() == (0.0, 10.0)

    def test_set_ylim_different_values_no_user_warning(self):
        """set_ylim(0, 10) should not produce UserWarning."""
        fig = FFig()
        fig.plot([1, 2, 3], [4, 5, 6])
        self._assert_no_user_warning(fig.set_ylim, 0, 10)
        # Verify limits are set correctly
        assert fig.current_axis.get_ylim() == (0.0, 10.0)

    def test_set_xlim_list_same_values_no_user_warning(self):
        """set_xlim([0, 0]) should not produce UserWarning."""
        fig = FFig()
        fig.plot([1, 2, 3], [4, 5, 6])
        self._assert_no_user_warning(fig.set_xlim, [0, 0])

    def test_set_ylim_list_same_values_no_user_warning(self):
        """set_ylim([0, 0]) should not produce UserWarning."""
        fig = FFig()
        fig.plot([1, 2, 3], [4, 5, 6])
        self._assert_no_user_warning(fig.set_ylim, [0, 0])

    def test_set_xlim_auto_same_values_no_user_warning(self):
        """set_xlim() with auto mode and same min/max should not warn."""
        fig = FFig()
        fig.plot([5], [5])
        self._assert_no_user_warning(fig.set_xlim)

    def test_set_ylim_auto_same_values_no_user_warning(self):
        """set_ylim() with auto mode and same min/max should not warn."""
        fig = FFig()
        fig.plot([5], [5])
        self._assert_no_user_warning(fig.set_ylim)

    def test_set_xlim_list_different_values_works(self):
        """set_xlim([0, 10]) should work normally."""
        fig = FFig()
        fig.plot([1, 2, 3], [4, 5, 6])
        self._assert_no_user_warning(fig.set_xlim, [0, 10])
        assert fig.current_axis.get_xlim() == (0.0, 10.0)

    def test_set_ylim_list_different_values_works(self):
        """set_ylim([0, 10]) should work normally."""
        fig = FFig()
        fig.plot([1, 2, 3], [4, 5, 6])
        self._assert_no_user_warning(fig.set_ylim, [0, 10])
        assert fig.current_axis.get_ylim() == (0.0, 10.0)
