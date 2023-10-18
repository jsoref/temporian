# Copyright 2021 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for both core and implementation window op base classes.

Use it to test expected behavior from the base classes, such as errors or
warnings."""

from unittest.mock import patch

from absl.testing import absltest

from temporian.implementation.numpy.data.io import event_set
from temporian.implementation.numpy.operators.window import (
    base as base_window_impl,
)
from temporian.test.utils import f32


class SimpleMovingAverageTest(absltest.TestCase):
    def test_variable_winlen_empty_features(self):
        evset = event_set(timestamps=[0], features={"a": [1]})
        window_length = event_set(timestamps=[1, 2])

        with self.assertRaisesRegex(
            ValueError, "`window_length` must have exactly one float64 feature"
        ):
            evset.simple_moving_average(window_length=window_length)

    def test_variable_winlen_several_features(self):
        evset = event_set(timestamps=[0], features={"a": [1]})
        window_length = event_set(timestamps=[1], features={"a": [1], "b": [1]})
        with self.assertRaisesRegex(
            ValueError, "`window_length` must have exactly one float64 feature"
        ):
            evset.simple_moving_average(window_length=window_length)

    def test_variable_winlen_invalid_dtype(self):
        evset = event_set(timestamps=[0], features={"a": [1]})
        window_length = event_set(
            timestamps=[1],
            features={"a": f32([1])},
        )
        with self.assertRaisesRegex(
            ValueError, "`window_length` must have exactly one float64 feature"
        ):
            evset.simple_moving_average(window_length=window_length)

    @patch.object(base_window_impl, "logging")
    def test_invalid_window_length_warning(self, logging_mock):
        """Tests that warning is shown when receiving non strictly positive
        values in window_length."""
        evset = event_set(
            timestamps=[0],
            features={"a": [1.0]},
        )
        window_length = event_set(
            timestamps=[1, 2],
            features={"a": [1.0, -1.0]},
        )
        evset.simple_moving_average(window_length=window_length)
        logging_mock.warning.assert_called_with(
            "`window_length`'s values should be strictly positive. 0, NaN and"
            " negative window lengths will output missing values."
        )

    def test_sampling_and_variable_winlen(self):
        evset = event_set(timestamps=[1], features={"a": [10.0]})
        sampling = event_set(timestamps=[2])
        window_length = event_set(timestamps=[2], features={"a": [0.5]})

        with self.assertRaisesRegex(
            ValueError,
            (
                "`sampling` cannot be specified if a variable `window_length`"
                " is specified"
            ),
        ):
            evset.moving_sum(window_length=window_length, sampling=sampling)


if __name__ == "__main__":
    absltest.main()
