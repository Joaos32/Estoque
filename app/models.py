from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class ItemBase(SQLModel):
    name: str = Field(index=True, description="Nome do material")
    unit: str = Field(default="unid", description="Unidade (ex.: unid, cx, pct, kg)")
    quantity: int = Field(default=0, ge=0, description="Quantidade em estoque")
    min_qty: int = Field(default=0, ge=0, description="Estoque mínimo")
    category: Optional[str] = Field(default=None, description="Categoria (opcional)")

class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Criado em")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Atualizado em")

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ItemUpdate(SQLModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[int] = None
    min_qty: Optional[int] = None
    category: Optional[str] = None
