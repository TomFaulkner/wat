from wat.lib import pyd

model_dict = {
    "name": ("str", None),
    "number": ("int", 42),
    "truth": ("bool", True),
}


result_dict = {"name": (str, ...), "number": (int, 42), "truth": (bool, True)}


def test__dict_to_typed():
    res = pyd._dict_to_typed(model_dict)
    assert res == result_dict


def test_create_model_from_dict():
    res = pyd.create_model_from_dict("Model", model_dict)

    assert res.schema() == {
        "title": "Model",
        "type": "object",
        "properties": {
            "name": {"title": "Name", "type": "string"},
            "number": {"title": "Number", "default": 42, "type": "integer"},
            "truth": {"title": "Truth", "default": True, "type": "boolean"},
        },
        "required": ["name"],
    }


def test_create_model_from_dict_schema_validates():
    model = pyd.create_model_from_dict("Model", model_dict)
    instance = model(name="Tom", truth=False)

    assert instance.name == "Tom"
    assert instance.number == 42
    assert instance.truth is False
