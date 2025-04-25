import pytest
from app.api.errors import MissDataError
from app.models.base import ModelStored


class TestModel(ModelStored):
    __test__ = False  # To avoid PytestCollectionWarning: cannot collect test class
    field_one: str = ""
    field_two: int | None


def test_base_model():
    with pytest.raises(MissDataError):
        TestModel(id=0)

    TestModel(id=1, field_one="str", field_two=None)

    with pytest.raises(MissDataError):
        TestModel(id=2, field_one="", field_two=None)
