from fastapi import HTTPException, status

from dino_seedwork_be.adapters.rest import error_detail_with_code
from dino_seedwork_be.domain.exceptions import DomainException


def basicHandleException(exception):
    match exception:
        case DomainException():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail_with_code(exception, detail=str(exception)),
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exception),
            )
