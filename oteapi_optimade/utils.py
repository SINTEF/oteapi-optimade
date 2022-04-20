"""Utility functions to be used in OTEAPI OPTIMADE."""
from copy import deepcopy
from typing import TYPE_CHECKING, Iterable

from pydantic import BaseModel

if TYPE_CHECKING:
    from typing import Any, Union


def model2dict(
    model: "Union[BaseModel, dict[str, Any]]", **dict_kwargs: "Any"
) -> "dict[str, Any]":
    """Convert a pydantic model to a Python dictionary.

    This works similarly to the `dict()` method for pydantic models, but ensures any
    and all nested pydantic models are also converted to dictionaries.

    Parameters:
        model: The pydantic model or Python dictionary to be converted fully to a
            Python dictionary, through and through.
        **dict_kwargs (Dict[Any, Any]): Keyword arguments to be passed to `dict()`
            method calls for pydantic models.
            Note, this will be used for _all_ `dict()` method calls.

    Returns:
        A Python dictionary, where all nested values that were pydantic models are also
        converted to Python dictionaries.

    """

    def _internal(model_: "Any") -> "Any":
        """Internal function to be used recursively."""
        if isinstance(model_, dict):
            return {key: _internal(value) for key, value in model_.items()}
        if isinstance(model_, Iterable) and not isinstance(model_, (bytes, str)):
            return type(model_)(_internal(value) for value in model_)  # type: ignore[call-arg]  # pylint: disable=line-too-long
        if isinstance(model_, BaseModel):
            return _internal(model_.dict(**dict_kwargs))
        return model_

    if isinstance(model, BaseModel):
        res = model.dict(**dict_kwargs)
    elif isinstance(model, dict):
        res = deepcopy(model)
    else:
        raise TypeError("model must be either a pydantic model or a dict.")

    return _internal(res)
