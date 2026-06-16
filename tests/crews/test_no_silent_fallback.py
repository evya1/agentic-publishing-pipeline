from __future__ import annotations

import pytest

from agentic_publishing_pipeline.crews import LiveAdapterUnavailable, run_cli


def test_live_mode_with_credentials_does_not_fall_back_to_fixture() -> None:
    with pytest.raises(LiveAdapterUnavailable):
        run_cli(
            [
                "--mode",
                "live",
                "--i-understand-this-makes-paid-calls",
            ],
            env={"OPENAI_API_KEY": "present"},
        )
