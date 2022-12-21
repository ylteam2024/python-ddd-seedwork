import traceback

from fastapi import HTTPException, status

from dino_seedwork_be.adapters.logger import SIMPLE_LOGGER
from dino_seedwork_be.adapters.rest import error_detail_with_code
from dino_seedwork_be.exceptions import MainException


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
            raise exception
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exception),
            )
