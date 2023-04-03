from typing import List
from sqlalchemy.orm import Session

from ms_invoicer.sql_app import models, schemas


# TopInfo ----------------------------------------------------------
def get_topinfos(db: Session):
    return db.query(models.TopInfo).all()


def get_topinfo_by_id(db: Session, model_id: str):
    return db.query(models.TopInfo).filter(models.TopInfo.id == model_id).first()


def patch_topinfo(db: Session, model_id: int, update_dict: dict):
    result = (
        db.query(models.TopInfo)
        .filter(models.TopInfo.id == model_id)
        .update(update_dict)
    )
    db.commit()
    return result


# Globals ----------------------------------------------------------
def get_global(db: Session, global_name: str):
    return db.query(models.Globals).filter(models.Globals.name == global_name).first()


def get_global_by_id(db: Session, model_id: str):
    return db.query(models.Globals).filter(models.Globals.id == model_id).first()


def get_globals(db: Session):
    return db.query(models.Globals).all()


def patch_global(db: Session, model_id: int, update_dict: dict):
    result = (
        db.query(models.Globals)
        .filter(models.Globals.id == model_id)
        .update(update_dict)
    )
    db.commit()
    return result


# Contract ----------------------------------------------------------
def get_contract(db: Session, model_id: int):
    return db.query(models.Contract).filter(models.Contract.id == model_id).first()


def get_contracts(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Customer]:
    return db.query(models.Contract).offset(skip).limit(limit).all()


def get_contracts_by_customer(db: Session, model_id: int):
    return (
        db.query(models.Contract).filter(models.Contract.customer_id == model_id).all()
    )


def delete_contracts_by_customer(db: Session, model_id: int):
    result = (
        db.query(models.Contract)
        .filter(models.Contract.customer_id == model_id)
        .delete()
    )
    db.commit()
    return result


def delete_contract(db: Session, model_id: int):
    result = db.query(models.Contract).filter(models.Contract.id == model_id).delete()
    db.commit()
    return result


def patch_contract(db: Session, model_id: int, update_dict: dict):
    result = (
        db.query(models.Contract)
        .filter(models.Contract.id == model_id)
        .update(update_dict)
    )
    db.commit()
    return result


def create_contract(db: Session, model: schemas.ContractBase):
    print(model)
    db_model = models.Contract(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Customer ----------------------------------------------------------
def get_customer(db: Session, model_id: int):
    return db.query(models.Customer).filter(models.Customer.id == model_id).first()


def get_customers(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Customer]:
    return db.query(models.Customer).offset(skip).limit(limit).all()


def patch_customer(db: Session, model_id: int, update_dict: dict):
    result = (
        db.query(models.Customer)
        .filter(models.Customer.id == model_id)
        .update(update_dict)
    )
    db.commit()
    return result


def delete_customer(db: Session, model_id: int):
    result = db.query(models.Customer).filter(models.Customer.id == model_id).delete()
    db.commit()
    return result


def create_customer(db: Session, model: schemas.CustomerCreate):
    db_model = models.Customer(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# File ----------------------------------------------------------
def get_file(db: Session, model_id: int):
    return db.query(models.File).filter(models.File.id == model_id).first()


def get_files(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.File).offset(skip).limit(limit).all()


def get_files_by_invoice(db: Session, model_id: int):
    return db.query(models.File).filter(models.File.invoice_id == model_id).all()


def patch_file(db: Session, model_id: int, update_dict: dict):
    result = (
        db.query(models.File).filter(models.File.id == model_id).update(update_dict)
    )
    db.commit()
    return result


def delete_file(db: Session, model_id: int):
    result = db.query(models.File).filter(models.File.id == model_id).delete()
    db.commit()
    return result


def delete_files_by_invoice(db: Session, model_id: int):
    return db.query(models.File).filter(models.File.invoice_id == model_id).delete()


def create_file(db: Session, model: schemas.FileCreate):
    db_model = models.File(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Bill_to ----------------------------------------------------------
def get_billto(db: Session, model_id: int):
    return db.query(models.BillTo).filter(models.BillTo.id == model_id).first()


def get_billtos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BillTo).offset(skip).limit(limit).all()


def patch_billto(db: Session, model_id: int, update_dict: dict):
    return (
        db.query(models.BillTo).filter(models.BillTo.id == model_id).update(update_dict)
    )


def delete_billto(db: Session, model_id: int):
    result = db.query(models.BillTo).filter(models.BillTo.id == model_id).delete()
    db.commit()
    return result


def create_billto(db: Session, model: schemas.BillToCreate):
    db_model = models.BillTo(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Service ----------------------------------------------------------
def get_service(db: Session, model_id: int):
    return db.query(models.Service).filter(models.Service.id == model_id).first()


def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Service).offset(skip).limit(limit).all()


def patch_service(db: Session, model_id: int, update_dict: dict):
    return (
        db.query(models.Service)
        .filter(models.Service.id == model_id)
        .update(update_dict)
    )


def delete_services_by_file(db: Session, model_id: int):
    return db.query(models.Service).filter(models.Service.file_id == model_id).delete()


def delete_service(db: Session, model_id: int):
    return db.query(models.Service).filter(models.Service.id == model_id).delete()


def create_service(db: Session, model: schemas.ServiceCreate):
    db_model = models.Service(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# Invoice ----------------------------------------------------------
def get_invoice(db: Session, model_id: int):
    return db.query(models.Invoice).filter(models.Invoice.id == model_id).first()


def get_invoices_by_contract(db: Session, model_id: int):
    return db.query(models.Invoice).filter(models.Invoice.contract_id == model_id).all()


def get_invoices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Invoice).offset(skip).limit(limit).all()


def patch_invoice(db: Session, model_id: int, update_dict: dict):
    result = (
        db.query(models.Invoice)
        .filter(models.Invoice.id == model_id)
        .update(update_dict)
    )
    db.commit()
    return result


def delete_invoice(db: Session, model_id: int):
    result = db.query(models.Invoice).filter(models.Invoice.id == model_id).first()
    db.delete(result)
    db.commit()


def delete_invoices_by_contract(db: Session, model_id: int):
    return (
        db.query(models.Invoice).filter(models.Invoice.contract_id == model_id).delete()
    )


def create_invoice(db: Session, model: schemas.InvoiceCreate):
    db_model = models.Invoice(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model
