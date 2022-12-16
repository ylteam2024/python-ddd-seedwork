from fastapi import HTTPException, status

from src.seedwork.adapters.rest import errorDetailWithCode
from src.seedwork.domain.exceptions import DomainException


def basicHandleException(exception):
    match exception:
        case DomainException():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=errorDetailWithCode(exception, detail=str(exception)),
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exception),
            )
