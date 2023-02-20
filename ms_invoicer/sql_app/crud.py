from sqlalchemy.orm import Session

from ms_invoicer.sql_app import models, schemas

def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()


def create_customer(db: Session, model: schemas.CustomerCreate):
    db_model = models.Customer(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def create_file(db: Session, model: schemas.FileCreate):
    db_model = models.File(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def create_billto(db: Session, model: schemas.BillToCreate):
    db_model = models.BillTo(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def create_service(db: Session, model: schemas.ServiceCreate):
    db_model = models.Service(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model
