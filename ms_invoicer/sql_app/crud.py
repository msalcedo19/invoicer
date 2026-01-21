from datetime import datetime
from typing import List

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func

from ms_invoicer.sql_app import models, schemas


# Template ----------------------------------------------------------
def get_templates(db: Session, current_user_id: int):
    return (
        db.query(models.Template)
        .filter(models.Template.user_id == current_user_id)
        .all()
    )


def get_template(db: Session, current_user_id: int):
    return (
        db.query(models.Template)
        .filter(
            models.Template.user_id == current_user_id,
        )
        .first()
    )


def create_template(db: Session, model: schemas.TemplateCreate):
    db_model = models.Template(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# TopInfo ----------------------------------------------------------
def get_topinfos(db: Session, current_user_id: int):
    return (
        db.query(models.TopInfo).filter(models.TopInfo.user_id == current_user_id).all()
    )


def patch_topinfo(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.TopInfo)
        .filter(
            models.TopInfo.id == model_id, models.TopInfo.user_id == current_user_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def create_topinfo(db: Session, model: schemas.TopInfoCreate):
    db_model = models.TopInfo(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Globals ----------------------------------------------------------
def get_global(db: Session, identifier: int, current_user_id: int):
    return (
        db.query(models.Globals)
        .filter(
            models.Globals.identifier == identifier,
            models.Globals.user_id == current_user_id,
        )
        .first()
    )


def get_global_by_id(db: Session, model_id: str, current_user_id: int):
    return (
        db.query(models.Globals)
        .filter(
            models.Globals.id == model_id, models.Globals.user_id == current_user_id
        )
        .first()
    )


def get_globals(db: Session, current_user_id: int):
    return (
        db.query(models.Globals).filter(models.Globals.user_id == current_user_id).all()
    )


def patch_global(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.Globals)
        .filter(
            models.Globals.id == model_id, models.Globals.user_id == current_user_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def create_global(db: Session, model: schemas.GlobalCreate):
    db_model = models.Globals(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Customer ----------------------------------------------------------
def get_customer(db: Session, model_id: int, current_user_id: int):
    invoice_count_subquery = (
        db.query(
            models.Invoice.customer_id,
            func.count(models.Invoice.id).label("num_invoices"),
        )
        .group_by(models.Invoice.customer_id)
        .subquery()
    )

    query_results = (
        db.query(
            models.Customer.id,
            models.Customer.name,
            func.coalesce(invoice_count_subquery.c.num_invoices, 0).label(
                "num_invoices"
            ),
        )
        .outerjoin(
            invoice_count_subquery,
            models.Customer.id == invoice_count_subquery.c.customer_id,
        )
        .filter(models.Customer.user_id == current_user_id, models.Customer.id == model_id)
        .first()
    )
    return {"id": query_results.id, "name": query_results.name, "num_invoices": query_results.num_invoices}
    


def get_customers(
    db: Session, current_user_id: int, skip: int = 0, limit: int = 1000
) -> List[models.Customer]:
    # Define the subquery for counting invoices
    invoice_count_subquery = (
        db.query(
            models.Invoice.customer_id,
            func.count(models.Invoice.id).label("num_invoices"),
        )
        .group_by(models.Invoice.customer_id)
        .subquery()
    )

    query_results = (
        db.query(
            models.Customer.id,
            models.Customer.name,
            func.coalesce(invoice_count_subquery.c.num_invoices, 0).label(
                "num_invoices"
            ),
        )
        .outerjoin(
            invoice_count_subquery,
            models.Customer.id == invoice_count_subquery.c.customer_id,
        )
        .filter(models.Customer.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    # Transform query results into a list of dictionaries
    return [
        {"id": id, "name": name, "num_invoices": num_invoices}
        for id, name, num_invoices in query_results
    ]


def get_total_customers(db: Session, current_user_id: int) -> int:
    return (
        db.query(func.count(models.Customer.id))
        .filter(models.Customer.user_id == current_user_id)
        .scalar()
    )


def get_all_customers(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Customer]:
    return db.query(models.Customer).offset(skip).limit(limit).all()


def patch_customer(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.Customer)
        .filter(
            models.Customer.id == model_id, models.Customer.user_id == current_user_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def patch_all_customer_by_user_id(db: Session, user_id: int, update_dict: dict):
    result = (
        db.query(models.Customer)
        .filter(models.Customer.user_id == user_id)
        .update(update_dict)
    )
    db.commit()
    return result


def delete_customer(db: Session, model_id: int, current_user_id: int):
    result = (
        db.query(models.Customer)
        .filter(
            models.Customer.id == model_id, models.Customer.user_id == current_user_id
        )
        .delete()
    )
    db.commit()
    return result


def create_customer(db: Session, model: schemas.CustomerCreate):
    db_model = models.Customer(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return {"id": db_model.id, "name": db_model.name, "num_invoices": 0}


# File ----------------------------------------------------------
def get_file(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.File)
        .filter(models.File.id == model_id, models.File.user_id == current_user_id)
        .first()
    )


def get_file_with_relations(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.File)
        .options(
            joinedload(models.File.services),
            joinedload(models.File.bill_to),
            joinedload(models.File.invoice),
        )
        .filter(models.File.id == model_id, models.File.user_id == current_user_id)
        .first()
    )


def get_files(db: Session, current_user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.File)
        .filter(models.File.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_files_by_invoice(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.File)
        .filter(
            models.File.invoice_id == model_id, models.File.user_id == current_user_id
        )
        .order_by(desc(models.File.created))
        .all()
    )


def patch_file(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.File)
        .filter(models.File.id == model_id, models.File.user_id == current_user_id)
        .update(update_dict)
    )
    db.commit()
    return result


def patch_all_files_by_invoice_user_id(
    db: Session, user_id: int, invoice_id: int, update_dict: dict
):
    result = (
        db.query(models.File)
        .filter(models.File.user_id == user_id, models.File.invoice_id == invoice_id)
        .update(update_dict)
    )
    db.commit()
    return result


def delete_file(db: Session, model_id: int, current_user_id: int):
    result = (
        db.query(models.File)
        .filter(models.File.id == model_id, models.File.user_id == current_user_id)
        .delete()
    )
    db.commit()
    return result


def delete_files_by_invoice(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.File)
        .filter(
            models.File.invoice_id == model_id, models.File.user_id == current_user_id
        )
        .delete()
    )


def create_file(db: Session, model: schemas.FileCreate):
    db_model = models.File(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Bill_to ----------------------------------------------------------
def get_billto(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.BillTo)
        .filter(models.BillTo.id == model_id, models.BillTo.user_id == current_user_id)
        .first()
    )


def get_billtos(db: Session, current_user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.BillTo)
        .filter(models.BillTo.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_billtos_no_user(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BillTo).offset(skip).limit(limit).all()


def patch_billto(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.BillTo)
        .filter(models.BillTo.id == model_id, models.BillTo.user_id == current_user_id)
        .update(update_dict)
    )

    db.commit()
    return result


def delete_billto(db: Session, model_id: int, current_user_id: int):
    result = (
        db.query(models.BillTo)
        .filter(models.BillTo.id == model_id, models.BillTo.user_id == current_user_id)
        .delete()
    )
    db.commit()
    return result


def create_billto(db: Session, model: schemas.BillToCreate):
    db_model = models.BillTo(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Service ----------------------------------------------------------
def get_service(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Service)
        .filter(
            models.Service.id == model_id, models.Service.user_id == current_user_id
        )
        .first()
    )


def get_services(db: Session, current_user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Service)
        .filter(models.Service.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def patch_service(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    return (
        db.query(models.Service)
        .filter(
            models.Service.id == model_id, models.Service.user_id == current_user_id
        )
        .update(update_dict)
    )


def delete_services_by_file(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Service)
        .filter(
            models.Service.file_id == model_id,
            models.Service.user_id == current_user_id,
        )
        .delete()
    )


def delete_service(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Service)
        .filter(
            models.Service.id == model_id, models.Service.user_id == current_user_id
        )
        .delete()
    )


def create_service(db: Session, model: schemas.ServiceCreate):
    db_model = models.Service(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Invoice ----------------------------------------------------------
def get_invoice(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Invoice)
        .filter(
            models.Invoice.id == model_id, models.Invoice.user_id == current_user_id
        )
        .first()
    )


def get_invoices_by_customer(
    db: Session, model_id: int, current_user_id: int, skip: int, limit: int = 1000
):
    query_results = (
        db.query(models.Invoice)
        .filter(
            models.Invoice.customer_id == model_id,
            models.Invoice.user_id == current_user_id,
        )
        .order_by(desc(models.Invoice.number_id))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return query_results


def get_total_invoices_by_customer(
    db: Session, model_id: int, current_user_id: int
) -> int:
    return (
        db.query(func.count(models.Invoice.id))
        .filter(
            models.Invoice.customer_id == model_id,
            models.Invoice.user_id == current_user_id,
        )
        .scalar()
    )


def get_invoices_by_customer_and_date_range(
    db: Session,
    model_id: int,
    current_user_id: int,
    start_date: datetime,
    end_date: datetime,
):
    return (
        db.query(models.Invoice)
        .filter(
            models.Invoice.customer_id == model_id,
            models.Invoice.user_id == current_user_id,
            models.Invoice.created.between(start_date, end_date),
        )
        .all()
    )


def get_invoices_by_number_id(
    db: Session, number_id: int, customer_id: int, current_user_id: int
):
    return (
        db.query(models.Invoice)
        .filter(
            models.Invoice.number_id == number_id,
            models.Invoice.user_id == current_user_id,
            models.Invoice.customer_id == customer_id,
        )
        .first()
    )


def get_invoices(db: Session, current_user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Invoice)
        .order_by(desc(models.Invoice.number_id))
        .filter(models.Invoice.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def patch_invoice(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.Invoice)
        .filter(
            models.Invoice.id == model_id, models.Invoice.user_id == current_user_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def patch_all_invoice_by_customer_user_id(
    db: Session, customer_id: int, user_id: int, update_dict: dict
):
    result = (
        db.query(models.Invoice)
        .filter(
            models.Invoice.user_id == user_id, models.Invoice.customer_id == customer_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def delete_invoice(db: Session, model_id: int, current_user_id: int):
    result = (
        db.query(models.Invoice)
        .filter(
            models.Invoice.id == model_id, models.Invoice.user_id == current_user_id
        )
        .first()
    )
    db.delete(result)
    db.commit()


def delete_invoices_by_customer(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Invoice)
        .filter(
            models.Invoice.customer_id == model_id,
            models.Invoice.user_id == current_user_id,
        )
        .delete()
    )


def create_invoice(db: Session, model: schemas.InvoiceCreate):
    db_model = models.Invoice(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# User -----------------------------------
def create_user(db: Session, model: schemas.UserCreate):
    db_model = models.User(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session):
    return db.query(models.User).all()


def delete_user(db: Session, model_id: int):
    result = (
        db.query(models.User)
        .filter(
            models.User.id == model_id,
        )
        .delete()
    )
    db.delete(result)
    db.commit()
