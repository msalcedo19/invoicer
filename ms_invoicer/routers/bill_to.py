from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ms_invoicer.db_pool import get_db
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas

router = APIRouter()


@router.post("/bill_to", response_model=schemas.BillTo)
def create_bill_to(
    model: schemas.BillToBase,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.BillTo:
    """Create a bill-to record.

    Example JSON:
    {
      "to": "Acme LLC",
      "addr": "123 Main St",
      "phone": "+1 555-0100",
      "email": "billing@acme.com"
    }
    """
    obj_dict = model.model_dump()
    obj_dict["user_id"] = current_user.id
    return crud.create_billto(db=db, model=schemas.BillToCreate(**obj_dict))


@router.get("/bill_to", response_model=list[schemas.BillTo])
def get_billtos(
    current_user: schemas.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[schemas.BillTo]:
    """List bill-to records.

    Example request:
    GET /bill_to?skip=0&limit=100
    """
    return crud.get_billtos(
        db=db, current_user_id=current_user.id, skip=skip, limit=limit
    )


@router.patch("/bill_to/{model_id}", response_model=schemas.BillTo)
def update_billTo(
    model: schemas.BillToUpdate,
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[schemas.BillTo]:
    """Update a bill-to record.

    Example JSON:
    {
      "phone": "+1 555-0101"
    }
    """
    update_dict = model.model_dump(exclude_unset=True)
    result = crud.patch_billto(
        db=db,
        model_id=model_id,
        current_user_id=current_user.id,
        update_dict=update_dict,
    )
    if result:
        return crud.get_billto(
            db=db, model_id=model_id, current_user_id=current_user.id
        )
    else:
        return None


@router.delete("/bill_to/{model_id}", status_code=status.HTTP_200_OK)
def delete_bill_to(
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> int:
    """Soft-delete a bill-to record for the current user.

    Example request:
    DELETE /bill_to/123
    """
    return crud.patch_billto(db=db, model_id=model_id, current_user_id=current_user.id, update_dict={"user_id": None})
