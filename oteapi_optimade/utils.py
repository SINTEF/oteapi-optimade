"""Utility functions to be used in OTEAPI OPTIMADE."""
from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


def model2dict(
    model: BaseModel | dict[str, Any] | Any, **dict_kwargs: Any
) -> dict[str, Any]:
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

    def _internal(model_: Any) -> Any:
        """Internal function to be used recursively."""
        if isinstance(model_, dict):
            return {key: _internal(value) for key, value in model_.items()}
        if isinstance(model_, Iterable) and not isinstance(model_, (bytes, str)):
            return type(model_)(_internal(value) for value in model_)  # type: ignore[call-arg]
        if isinstance(model_, BaseModel):
            return _internal(model_.dict(**dict_kwargs))
        return model_

    if isinstance(model, BaseModel):
        res = model.dict(**dict_kwargs)
    elif isinstance(model, dict):
        res = deepcopy(model)
    else:
        error_message = "model must be either a pydantic model or a dict."
        raise TypeError(error_message)

    final = _internal(res)
    if not isinstance(final, dict):
        error_message = (
            "Something went wrong in the conversion of the model to a dictionary. "
            f"The final result ended up being a {type(final)} instead of a dict."
        )
        raise TypeError(error_message)

    return final
