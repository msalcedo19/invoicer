from typing import Any, Dict, Union

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from ms_invoicer.cache_manager import get_cached_data
from ms_invoicer.db_pool import get_db
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, models, schemas
from ms_invoicer.utils import BreadCrumbs


router = APIRouter()


def get_default() -> Dict[str, list[Dict[str, object]]]:
    """Get default."""
    return {
        "options": [
            {
                "value": "Clientes",
                "href": "/customer",
                "active": True,
            },
        ]
    }


def object_to_object(
    object: Union[models.File, models.Invoice, Dict[str, Any]]
) -> BreadCrumbs:
    """Object to object."""
    if isinstance(object, models.File):
        return BreadCrumbs(
            value="Contratos",
            href="/files/{}".format(object.id),
            required_id=object.invoice_id,
        )
    elif isinstance(object, dict):
        return BreadCrumbs(
            href="/customer/{}".format(object["id"]),
            value=object["name"],
        )
    elif isinstance(object, models.Invoice):
        return BreadCrumbs(
            value="Factura {}".format(object.number_id),
            href="/invoice/{}".format(object.id),
            required_id=object.customer_id,
        )


@router.post("/breadcrumbs")
def get_breadcrumbs(
    data: dict,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, list[Dict[str, object]]]:
    """Generate breadcrumbs for a UI path.

    Example JSON:
    {
      "current_path": "/customer/1"
    }
    """
    current_path = data.get("current_path", None)
    default_result = {
        "options": [
            {
                "value": "Clientes",
                "href": "/customer",
                "active": True,
            },
        ]
    }

    key = "default"
    if current_path:
        parts = current_path.split("/")[1:]
        if len(parts) == 2:
            for option in default_result["options"]:
                option["active"] = False
            if parts[0] == "customer":
                key = "user_{}_customer_{}".format(current_user.id, parts[1])
                breadcrumb = get_cached_data(
                    key,
                    fetch_function=lambda: object_to_object(
                        crud.get_customer(
                            db=db, model_id=parts[1], current_user_id=current_user.id
                        )
                    ),
                )

                next_option = {
                    "value": breadcrumb.value,
                    "href": breadcrumb.href,
                    "active": True,
                }
                default_result["options"].append(next_option)
            elif parts[0] == "files":
                key = "user_{}_file_{}".format(current_user.id, parts[1])
                breadcrumb = get_cached_data(
                    key,
                    fetch_function=lambda: object_to_object(
                        crud.get_file(
                            db=db, model_id=parts[1], current_user_id=current_user.id
                        )
                    ),
                )
                next_option3 = {
                    "value": breadcrumb.value,
                    "href": breadcrumb.href,
                    "active": True,
                }

                key = "user_{}_invoice_{}".format(current_user.id, breadcrumb.required_id)
                breadcrumb = get_cached_data(
                    key,
                    fetch_function=lambda: object_to_object(
                        crud.get_invoice(
                            db=db,
                            model_id=breadcrumb.required_id,
                            current_user_id=current_user.id,
                        )
                    ),
                )
                next_option2 = {
                    "value": breadcrumb.value,
                    "href": breadcrumb.href,
                    "active": False,
                }

                key = "user_{}_customer_{}".format(current_user.id, breadcrumb.required_id)
                breadcrumb = get_cached_data(
                    key,
                    fetch_function=lambda: object_to_object(
                        crud.get_customer(
                            db=db,
                            model_id=breadcrumb.required_id,
                            current_user_id=current_user.id,
                        )
                    ),
                )

                next_option1 = {
                    "value": breadcrumb.value,
                    "href": breadcrumb.href,
                    "active": False,
                }
                default_result["options"].append(next_option1)
                default_result["options"].append(next_option2)
                default_result["options"].append(next_option3)
            elif parts[0] == "invoice":
                key = "user_{}_invoice_{}".format(current_user.id, parts[1])
                breadcrumb = get_cached_data(
                    key,
                    fetch_function=lambda: object_to_object(
                        crud.get_invoice(
                            db=db, model_id=parts[1], current_user_id=current_user.id
                        )
                    ),
                )
                next_option2 = {
                    "value": breadcrumb.value,
                    "href": breadcrumb.href,
                    "active": True,
                }

                key = "user_{}_customer_{}".format(current_user.id, breadcrumb.required_id)
                breadcrumb = get_cached_data(
                    key,
                    fetch_function=lambda: object_to_object(
                        crud.get_customer(
                            db=db,
                            model_id=breadcrumb.required_id,
                            current_user_id=current_user.id,
                        )
                    ),
                )
                next_option1 = {
                    "value": breadcrumb.value,
                    "href": breadcrumb.href,
                    "active": False,
                }
                default_result["options"].append(next_option1)
                default_result["options"].append(next_option2)
    return default_result
