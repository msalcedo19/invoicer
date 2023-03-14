from sqlalchemy.orm import Session

from ms_invoicer.sql_app import models, schemas


# Customer
def get_global(db: Session, global_name: str):
    return db.query(models.Globals).filter(models.Globals.name == global_name).first()


# Customer
def get_customer(db: Session, model_id: int):
    return db.query(models.Customer).filter(models.Customer.id == model_id).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()


def patch_customer(db: Session, model_id: int, update_dict: dict):
    return db.query(models.Customer).filter(models.Customer.id == model_id).update(update_dict)


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

# File
def get_file(db: Session, model_id: int):
    return db.query(models.File).filter(models.File.id == model_id).first()

def get_files_by_invoice(db: Session, model_id: int):
    return db.query(models.File).filter(models.File.invoice_id == model_id).all()

def get_files(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.File).offset(skip).limit(limit).all()


def get_files_by_invoice(db: Session, model_id: int):
    return db.query(models.File).filter(models.File.invoice_id == model_id).all()


def patch_file(db: Session, model_id: int, update_dict: dict):
    result = db.query(models.File).filter(models.File.id == model_id).update(update_dict)
    db.commit()
    return result


def delete_file(db: Session, model_id: int):
    result = db.query(models.File).filter(models.File.id == model_id).first()
    db.delete(result)
    db.commit()
    return len(result)


def delete_file_by_invoice(db: Session, model_id: int):
    return db.query(models.File).filter(models.File.invoice_id == model_id).delete()


def create_file(db: Session, model: schemas.FileCreate):
    db_model = models.File(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

# Bill_to
def get_billto(db: Session, model_id: int):
    return db.query(models.BillTo).filter(models.BillTo.id == model_id).first()


def get_billtos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BillTo).offset(skip).limit(limit).all()


def patch_billto(db: Session, model_id: int, update_dict: dict):
    return db.query(models.BillTo).filter(models.BillTo.id == model_id).update(update_dict)


def delete_billto(db: Session, model_id: int):
    return db.query(models.BillTo).filter(models.BillTo.id == model_id).delete()


def create_billto(db: Session, model: schemas.BillToCreate):
    db_model = models.BillTo(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

# Service
def get_service(db: Session, model_id: int):
    return db.query(models.Service).filter(models.Service.id == model_id).first()


def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Service).offset(skip).limit(limit).all()


def patch_service(db: Session, model_id: int, update_dict: dict):
    return db.query(models.Service).filter(models.Service.id == model_id).update(update_dict)


def delete_service_by_file(db: Session, model_id: int):
    return db.query(models.Service).filter(models.Service.file_id == model_id).delete()


def delete_service(db: Session, model_id: int):
    return db.query(models.Service).filter(models.Service.id == model_id).delete()


def create_service(db: Session, model: schemas.ServiceCreate):
    db_model = models.Service(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

# Invoice
def get_invoice(db: Session, model_id: int):
    return db.query(models.Invoice).filter(models.Invoice.id == model_id).first()


def get_invoice_by_customer(db: Session, model_id: int):
    return db.query(models.Invoice).filter(models.Invoice.customer_id == model_id).all()


def get_invoices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Invoice).offset(skip).limit(limit).all()


def patch_invoice(db: Session, model_id: int, update_dict: dict):
    return db.query(models.Invoice).filter(models.Invoice.id == model_id).update(update_dict)


def delete_invoice(db: Session, model_id: int):
    result = db.query(models.Invoice).filter(models.Invoice.id == model_id).first()
    db.delete(result)
    db.commit()


def delete_invoices_by_customer(db: Session, model_id: int):
    return db.query(models.Invoice).filter(models.Invoice.customer_id == model_id).delete()


def create_invoice(db: Session, model: schemas.InvoiceCreate):
    db_model = models.Invoice(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model
