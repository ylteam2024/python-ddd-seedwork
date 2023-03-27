import traceback

from fastapi import HTTPException, status
from returns.future import FutureFailure

from dino_seedwork_be.adapters.logger.SimpleLogger import SIMPLE_LOGGER
from dino_seedwork_be.adapters.rest import error_detail_with_code
from dino_seedwork_be.exceptions import MainException


def safe_basic_handle_exception(exception):
    match exception:
        case MainException():
            return FutureFailure(
                HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_detail_with_code(exception),
                )
            )
        case _:
            SIMPLE_LOGGER.info("Error Occured: %s", exception)
            traceback.print_exc()
            return FutureFailure(
                HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(exception),
                )
            )


def basic_handle_exception(exception):
    match exception:
        case MainException():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail_with_code(exception),
            )

        case _:
            SIMPLE_LOGGER.info("Error Occured: %s", exception)
            traceback.print_exc()
            # raise exception
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exception),
            )


def decor_basic_handler_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            basic_handle_exception(error)

    return wrapper
