from typing import List

from sqlalchemy.orm import Session

from ms_invoicer.sql_app import models, schemas


# TopInfo ----------------------------------------------------------
def get_topinfos(db: Session, current_user_id: int):
    return (
        db.query(models.TopInfo).filter(models.TopInfo.user_id == current_user_id).all()
    )


def get_topinfo_by_id(db: Session, model_id: str, current_user_id: int):
    return (
        db.query(models.TopInfo)
        .filter(
            models.TopInfo.id == model_id and models.TopInfo.user_id == current_user_id
        )
        .first()
    )


def patch_topinfo(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.TopInfo)
        .filter(
            models.TopInfo.id == model_id and models.TopInfo.user_id == current_user_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def create_topinfo(db: Session, model: schemas.TopInfoCreate):
    db_model = models.TopInfo(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Globals ----------------------------------------------------------
def get_global(db: Session, global_name: str, current_user_id: int):
    return (
        db.query(models.Globals)
        .filter(
            models.Globals.name == global_name
            and models.Globals.user_id == current_user_id
        )
        .first()
    )


def get_global_by_id(db: Session, model_id: str, current_user_id: int):
    return (
        db.query(models.Globals)
        .filter(
            models.Globals.id == model_id and models.Globals.user_id == current_user_id
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
            models.Globals.id == model_id and models.Globals.user_id == current_user_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def create_global(db: Session, model: schemas.GlobalCreate):
    db_model = models.Globals(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Contract ----------------------------------------------------------
def get_contract(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Service)
        .filter(
            models.Service.id == model_id and models.Service.user_id == current_user_id
        )
        .first()
    )


def get_contracts(
    db: Session, current_user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Customer]:
    return (
        db.query(models.Service)
        .filter(models.Service.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_contracts_by_customer(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Service)
        .filter(
            models.Service.invoice_id == models.Invoice.id
            and models.Invoice.customer_id == model_id
            and models.Service.user_id == current_user_id
        )
        .all()
    )


def delete_contract(db: Session, model_id: int, current_user_id: int):
    result = (
        db.query(models.Service)
        .filter(
            models.Service.id == model_id and models.Service.user_id == current_user_id
        )
        .delete()
    )
    db.commit()
    return result


def patch_contract(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.Service)
        .filter(
            models.Service.id == model_id and models.Service.user_id == current_user_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def create_contract(db: Session, model: schemas.ServiceCreate):
    db_model = models.Service(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Customer ----------------------------------------------------------
def get_customer(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Customer)
        .filter(
            models.Customer.id == model_id
            and models.Customer.user_id == current_user_id
        )
        .first()
    )


def get_customers(
    db: Session, current_user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Customer]:
    return (
        db.query(models.Customer)
        .filter(models.Customer.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def patch_customer(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.Customer)
        .filter(
            models.Customer.id == model_id
            and models.Customer.user_id == current_user_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def delete_customer(db: Session, model_id: int, current_user_id: int):
    result = (
        db.query(models.Customer)
        .filter(
            models.Customer.id == model_id
            and models.Customer.user_id == current_user_id
        )
        .delete()
    )
    db.commit()
    return result


def create_customer(db: Session, model: schemas.CustomerCreate):
    db_model = models.Customer(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# File ----------------------------------------------------------
def get_file(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.File)
        .filter(models.File.id == model_id and models.File.user_id == current_user_id)
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
            models.File.invoice_id == model_id
            and models.File.user_id == current_user_id
        )
        .all()
    )


def patch_file(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.File)
        .filter(models.File.id == model_id and models.File.user_id == current_user_id)
        .update(update_dict)
    )
    db.commit()
    return result


def delete_file(db: Session, model_id: int, current_user_id: int):
    result = (
        db.query(models.File)
        .filter(models.File.id == model_id and models.File.user_id == current_user_id)
        .delete()
    )
    db.commit()
    return result


def delete_files_by_invoice(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.File)
        .filter(
            models.File.invoice_id == model_id
            and models.File.user_id == current_user_id
        )
        .delete()
    )


def create_file(db: Session, model: schemas.FileCreate):
    db_model = models.File(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Bill_to ----------------------------------------------------------
def get_billto(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.BillTo)
        .filter(
            models.BillTo.id == model_id and models.BillTo.user_id == current_user_id
        )
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


def patch_billto(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.BillTo)
        .filter(
            models.BillTo.id == model_id and models.BillTo.user_id == current_user_id
        )
        .update(update_dict)
    )

    db.commit()
    return result


def delete_billto(db: Session, model_id: int, current_user_id: int):
    result = (
        db.query(models.BillTo)
        .filter(
            models.BillTo.id == model_id and models.BillTo.user_id == current_user_id
        )
        .delete()
    )
    db.commit()
    return result


def create_billto(db: Session, model: schemas.BillToCreate):
    db_model = models.BillTo(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Service ----------------------------------------------------------
def get_service(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Service)
        .filter(
            models.Service.id == model_id and models.Service.user_id == current_user_id
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
            models.Service.id == model_id and models.Service.user_id == current_user_id
        )
        .update(update_dict)
    )


def delete_services_by_file(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Service)
        .filter(
            models.Service.file_id == model_id
            and models.Service.user_id == current_user_id
        )
        .delete()
    )


def delete_service(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Service)
        .filter(
            models.Service.id == model_id and models.Service.user_id == current_user_id
        )
        .delete()
    )


def create_service(db: Session, model: schemas.ServiceCreate):
    db_model = models.Service(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Invoice ----------------------------------------------------------
def get_invoice(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Invoice)
        .filter(
            models.Invoice.id == model_id and models.Invoice.user_id == current_user_id
        )
        .first()
    )


def get_invoices_by_customer(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Invoice)
        .filter(
            models.Invoice.customer_id == model_id
            and models.Invoice.user_id == current_user_id
        )
        .all()
    )


def get_invoices_by_number_id(db: Session, number_id: int, current_user_id: int):
    return (
        db.query(models.Invoice)
        .filter(
            models.Invoice.number_id == number_id
            and models.Invoice.user_id == current_user_id
        )
        .first()
    )


def get_invoices(db: Session, current_user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Invoice)
        .filter(models.Invoice.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def patch_invoice(db: Session, model_id: int, current_user_id: int, update_dict: dict):
    result = (
        db.query(models.Invoice)
        .filter(
            models.Invoice.id == model_id and models.Invoice.user_id == current_user_id
        )
        .update(update_dict)
    )
    db.commit()
    return result


def delete_invoice(db: Session, model_id: int, current_user_id: int):
    result = (
        db.query(models.Invoice)
        .filter(
            models.Invoice.id == model_id and models.Invoice.user_id == current_user_id
        )
        .first()
    )
    db.delete(result)
    db.commit()


def delete_invoices_by_customer(db: Session, model_id: int, current_user_id: int):
    return (
        db.query(models.Invoice)
        .filter(
            models.Invoice.customer_id == model_id
            and models.Invoice.user_id == current_user_id
        )
        .delete()
    )


def create_invoice(db: Session, model: schemas.InvoiceCreate):
    db_model = models.Invoice(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# User -----------------------------------
def create_user(db: Session, model: schemas.UserCreate):
    db_model = models.User(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
