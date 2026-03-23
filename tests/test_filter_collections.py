import re
import pytest
from unittest.mock import patch
from filter_collections import apply_filter, SizeMatcher, PatternMatcher, RandomMatcher


# ---------------------------------------------------------------------------
# apply_filter
# ---------------------------------------------------------------------------

class TestApplyFilter:
    def test_empty_collection_returns_empty_list(self):
        assert apply_filter([], [SizeMatcher(">", 0)]) == []

    def test_none_collection_raises_type_error(self):
        with pytest.raises(TypeError):
            apply_filter(None, [])

    def test_empty_matchers_returns_all_elements(self):
        data = ["a", "bb", "ccc"]
        assert apply_filter(data, []) == data

    def test_single_matcher_filters_correctly(self):
        data = ["hi", "hello", "hey", "world"]
        result = apply_filter(data, [SizeMatcher(">", 3)])
        assert result == ["hello", "world"]

    def test_multiple_matchers_and_logic(self):
        # Must have size > 2 AND match pattern starting with 'h'
        data = ["hi", "hey", "hello", "world", "ha"]
        result = apply_filter(data, [SizeMatcher(">", 2), PatternMatcher(r"^h")])
        assert result == ["hey", "hello"]

    def test_tuple_input(self):
        data = ("a", "bb", "ccc")
        assert apply_filter(data, [SizeMatcher(">=", 2)]) == ["bb", "ccc"]

    def test_set_input(self):
        data = {"x", "yy", "zzz"}
        result = apply_filter(data, [SizeMatcher("==", 1)])
        assert result == ["x"]

    def test_generator_input(self):
        data = (x for x in ["ab", "c", "def"])
        result = apply_filter(data, [SizeMatcher(">", 1)])
        assert result == ["ab", "def"]

    def test_returns_list_type(self):
        result = apply_filter(("a", "b"), [])
        assert isinstance(result, list)

    def test_all_elements_filtered_out(self):
        data = ["a", "b", "c"]
        assert apply_filter(data, [SizeMatcher(">", 100)]) == []


# ---------------------------------------------------------------------------
# SizeMatcher
# ---------------------------------------------------------------------------

class TestSizeMatcher:
    # --- operator coverage ---
    def test_operator_greater_than(self):
        m = SizeMatcher(">", 3)
        assert m.match("hello") is True
        assert m.match("hi") is False

    def test_operator_greater_equal(self):
        m = SizeMatcher(">=", 5)
        assert m.match("hello") is True
        assert m.match("hi") is False

    def test_operator_less_than(self):
        m = SizeMatcher("<", 3)
        assert m.match("hi") is True
        assert m.match("hello") is False

    def test_operator_less_equal(self):
        m = SizeMatcher("<=", 2)
        assert m.match("hi") is True
        assert m.match("hey") is False

    def test_operator_equal(self):
        m = SizeMatcher("==", 5)
        assert m.match("hello") is True
        assert m.match("hi") is False

    def test_operator_not_equal(self):
        m = SizeMatcher("!=", 5)
        assert m.match("hi") is True
        assert m.match("hello") is False

    # --- collection types ---
    def test_matches_string_by_length(self):
        assert SizeMatcher("==", 5).match("hello") is True

    def test_matches_list_by_length(self):
        assert SizeMatcher("==", 3).match([1, 2, 3]) is True

    def test_matches_dict_by_length(self):
        assert SizeMatcher("==", 1).match({"a": 1}) is True

    def test_matches_tuple_by_length(self):
        assert SizeMatcher("==", 2).match((1, 2)) is True

    # --- edge / null cases ---
    def test_none_element_returns_false(self):
        assert SizeMatcher(">", 0).match(None) is False

    def test_int_element_returns_false(self):
        assert SizeMatcher(">", 0).match(42) is False

    def test_float_element_returns_false(self):
        assert SizeMatcher(">", 0).match(3.14) is False

    def test_empty_string_has_size_zero(self):
        assert SizeMatcher("==", 0).match("") is True
        assert SizeMatcher(">", 0).match("") is False

    def test_empty_list_has_size_zero(self):
        assert SizeMatcher("==", 0).match([]) is True

    def test_empty_dict_has_size_zero(self):
        assert SizeMatcher("==", 0).match({}) is True

    # --- constructor validation ---
    def test_invalid_operator_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported operator"):
            SizeMatcher("??", 5)

    def test_non_int_size_raises_type_error(self):
        with pytest.raises(TypeError):
            SizeMatcher(">", "5")

    def test_float_size_raises_type_error(self):
        with pytest.raises(TypeError):
            SizeMatcher(">", 5.0)


# ---------------------------------------------------------------------------
# PatternMatcher
# ---------------------------------------------------------------------------

class TestPatternMatcher:
    def test_matching_pattern_returns_true(self):
        assert PatternMatcher(r"\d+").match("abc123") is True

    def test_non_matching_pattern_returns_false(self):
        assert PatternMatcher(r"\d+").match("abcdef") is False

    def test_none_element_returns_false(self):
        assert PatternMatcher(r"\w+").match(None) is False

    def test_int_element_returns_false(self):
        assert PatternMatcher(r"\d+").match(123) is False

    def test_list_element_returns_false(self):
        assert PatternMatcher(r"\w+").match(["hello"]) is False

    def test_empty_string_element_with_matching_pattern(self):
        assert PatternMatcher(r"^$").match("") is True

    def test_empty_string_element_with_non_matching_pattern(self):
        assert PatternMatcher(r"\w+").match("") is False

    def test_empty_pattern_matches_everything(self):
        # empty regex matches any string
        m = PatternMatcher("")
        assert m.match("anything") is True
        assert m.match("") is True

    def test_invalid_regex_raises_at_construction(self):
        with pytest.raises(re.error):
            PatternMatcher(r"[(invalid")

    def test_anchored_pattern(self):
        m = PatternMatcher(r"^hello")
        assert m.match("hello world") is True
        assert m.match("say hello") is False

    def test_case_sensitive_by_default(self):
        m = PatternMatcher(r"hello")
        assert m.match("Hello") is False
        assert m.match("hello") is True

    def test_special_chars_in_pattern(self):
        m = PatternMatcher(r"\bhello\b")
        assert m.match("say hello there") is True
        assert m.match("helloworld") is False


# ---------------------------------------------------------------------------
# RandomMatcher
# ---------------------------------------------------------------------------

class TestRandomMatcher:
    def test_probability_zero_always_true(self):
        m = RandomMatcher(0)
        for _ in range(100):
            assert m.match("anything") is True

    def test_probability_100_always_false(self):
        m = RandomMatcher(100)
        for _ in range(100):
            assert m.match("anything") is False

    def test_probability_50_uses_random(self):
        m = RandomMatcher(50)
        with patch("filter_collections.matchers.random.random", return_value=0.6):
            assert m.match("x") is True  # 0.6 >= 0.5
        with patch("filter_collections.matchers.random.random", return_value=0.4):
            assert m.match("x") is False  # 0.4 < 0.5

    def test_probability_boundary_low(self):
        with patch("filter_collections.matchers.random.random", return_value=0.0):
            assert RandomMatcher(0).match("x") is True

    def test_probability_boundary_high(self):
        # random.random() returns [0, 1), never 1.0; any realistic value fails against threshold 1.0
        with patch("filter_collections.matchers.random.random", return_value=0.99):
            assert RandomMatcher(100).match("x") is False

    def test_float_probability_accepted(self):
        m = RandomMatcher(50.5)
        with patch("filter_collections.matchers.random.random", return_value=0.6):
            assert m.match("x") is True
        with patch("filter_collections.matchers.random.random", return_value=0.4):
            assert m.match("x") is False

    def test_none_element_still_subject_to_random(self):
        # RandomMatcher doesn't inspect the element, so None is treated like anything else
        m = RandomMatcher(0)
        assert m.match(None) is True

    def test_negative_probability_raises_value_error(self):
        with pytest.raises(ValueError, match="probability must be between 0 and 100"):
            RandomMatcher(-1)

    def test_probability_above_100_raises_value_error(self):
        with pytest.raises(ValueError, match="probability must be between 0 and 100"):
            RandomMatcher(101)

    def test_string_probability_raises_type_error(self):
        with pytest.raises(TypeError, match="probability must be a number"):
            RandomMatcher("50")

    def test_none_probability_raises_type_error(self):
        with pytest.raises(TypeError, match="probability must be a number"):
            RandomMatcher(None)


# ---------------------------------------------------------------------------
# Integration / edge cases
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_mixed_types_with_pattern_matcher(self):
        data = ["hello", 42, None, "world", 3.14, ["list"]]
        result = apply_filter(data, [PatternMatcher(r"^h")])
        assert result == ["hello"]

    def test_mixed_types_with_size_matcher(self):
        data = ["hi", 42, None, "hello", [], [1, 2, 3]]
        result = apply_filter(data, [SizeMatcher("==", 5)])
        assert result == ["hello"]

    def test_size_and_pattern_combined(self):
        data = ["hi", "hey", "hello", "howdy", "world"]
        result = apply_filter(data, [SizeMatcher(">", 3), PatternMatcher(r"^h")])
        assert result == ["hello", "howdy"]

    def test_random_and_pattern_combined(self):
        data = ["hello", "world", "hi"]
        with patch("filter_collections.matchers.random.random", return_value=1.0):
            # probability=0 → always True; random.random=1.0 >= 0.0 → True
            result = apply_filter(data, [RandomMatcher(0), PatternMatcher(r"^h")])
        assert result == ["hello", "hi"]

    def test_random_rejects_all_when_probability_100(self):
        data = ["hello", "world"]
        result = apply_filter(data, [RandomMatcher(100)])
        assert result == []

    def test_collection_with_all_none_elements(self):
        data = [None, None, None]
        assert apply_filter(data, [SizeMatcher(">", 0)]) == []
        assert apply_filter(data, [PatternMatcher(r"\w")]) == []

    def test_collection_with_empty_strings(self):
        data = ["", "", "hello"]
        assert apply_filter(data, [SizeMatcher(">", 0)]) == ["hello"]

    def test_single_element_collection_passes(self):
        assert apply_filter(["hello"], [SizeMatcher("==", 5)]) == ["hello"]

    def test_single_element_collection_fails(self):
        assert apply_filter(["hi"], [SizeMatcher("==", 5)]) == []
