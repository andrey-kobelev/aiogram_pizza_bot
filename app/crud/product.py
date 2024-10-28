from app.models import Product
from app.crud.base import CRUDBase


class CRUDProduct(CRUDBase):
    pass


product_crud = CRUDProduct(model=Product)
