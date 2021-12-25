from pathlib import Path
from typing import Any, Dict
import json

MockData = Dict[str, Any]


class Mock:
    mock: MockData = {}

    @staticmethod
    def populate(mock_path: Path) -> None:
        if not mock_path.exists():
            raise Exception(f"Mock file {mock_path} does not exists!")

        with mock_path.open("r") as f:
            mock_data: MockData = json.load(f)
            Mock.mock = mock_data
