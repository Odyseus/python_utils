# -*- coding: utf-8 -*-
"""Utilities to validate data from JSON schemas.
"""
import json

from collections.abc import Callable
from copy import deepcopy

from . import shell_utils
from . import yaml_utils

from .exceptions import ExceptionWhitoutTraceBack
from .exceptions import MissingDependencyModule

try:
    from jsonschema import Draft7Validator as schema_validator
    from jsonschema import draft7_format_checker as format_checker
    JSONSCHEMA_INSTALLED = True
except ImportError:
    JSONSCHEMA_INSTALLED = False


_extra_types = {
    "custom_callable": Callable,
    "custom_tuple": tuple
}


class SchemaValidationError(ExceptionWhitoutTraceBack):
    """SchemaValidationError
    """

    def __init__(self, msg):
        """Initialization.

        Parameters
        ----------
        msg : str
            Message that the exception should display.
        """
        super().__init__(msg)


def validate(instance, schema,
             raise_error=True,
             error_message_extra_info="",
             error_header="Data didn't pass validation!",
             extra_types={},
             logger=None):
    """Validate data using a JSON schema.

    Parameters
    ----------
    instance : dict|list
        The data to validate.
    schema : dict, str
        The schema to use for validation. It can also be a path to a JSON or YAML file.
    raise_error : bool, optional
        Whether or not to raise an exception.
    error_message_extra_info : str, optional
        Extra information to display wehn raising a :any:`SchemaValidationError` error.
    error_header : str, optional
        Text to be displayed as "CLI header".
    extra_types : dict, optional
        Extra type checks.
    logger : LogSystem
        The logger.

    Returns
    -------
    int
        1 (one) if errors were found. 0 (zero) if no errors were found.
        It only returns if raise_error is False.

    Raises
    ------
    MissingDependencyModule
        Module ``jsonschema`` not installed.
    SchemaValidationError
        See :any:`SchemaValidationError`.
    """
    if not JSONSCHEMA_INSTALLED:
        raise MissingDependencyModule("Missing 'jsonschema' module.")

    # Just in case, use a copy of instance to validate, not the original.
    try:
        instance_copy = deepcopy(instance)
    except Exception as err:
        instance_copy = instance
        logger.warning(err)

    if isinstance(schema, str):
        try:
            if schema.endswith(".yaml") or schema.endswith(".yml"):
                with open(schema, "r") as yaml_file:
                    schema = yaml_utils.load(yaml_file)
            elif schema.endswith(".json"):
                with open(schema, "r") as json_file:
                    schema = json.load(json_file)
        except IOError as err:
            print(err)
            raise SystemExit(1)

    v = schema_validator(schema,
                         types={**extra_types, **_extra_types},
                         format_checker=format_checker)
    errors = sorted(v.iter_errors(instance_copy), key=lambda e: e.path)

    if errors:
        logger.header(error_header)

        for error in errors:
            logger.sub_section()

            abs_path = " > ".join([str(key) for key in list(error.absolute_path)])

            if bool(abs_path):
                logger.info("**Index or property path:** %s" % str(abs_path))

            logger.info(error.message)

            if error.context:
                for e in error.context:
                    logger.info(e.message)

            extra_info_keys = ["title", "description", "default"]
            error_schema = error.schema

            if any(key in error_schema for key in extra_info_keys):
                logger.info("**Extra information**")

                for x in extra_info_keys:
                    if error_schema.get(x):
                        logger.info("**%s:** %s" %
                                    (x.capitalize(), error_schema.get(x)))

        logger.sub_section()

        error_message = "\n".join(["%sTo continue, all errors must be fixed." %
                                   ("" if raise_error else "**SchemaValidationError:** "),
                                   "**Total errors found:** %s" % str(len(errors)),
                                   error_message_extra_info])
        if raise_error:
            raise SchemaValidationError(error_message)
        else:
            logger.error(error_message)
            return 1

    return 0


if __name__ == "__main__":
    pass
