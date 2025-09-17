from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from sqlmodel import Session, select, SQLModel, col, func
from starlette.staticfiles import StaticFiles
from datetime import datetime
import csv
import io

from .database import engine, init_db
from .models import Item, ItemCreate, ItemRead, ItemUpdate

app = FastAPI(title="Sistema de Estoque (MVP)", version="1.0.0")

# CORS (útil se servir o frontend separado). Aqui não é estritamente necessário.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o banco na primeira execução
@app.on_event("startup")
def on_startup():
    init_db()

# --------------------------
#        API REST
# --------------------------

@app.get("/api/items", response_model=List[ItemRead])
def list_items(q: Optional[str] = None, low_stock: bool = False, order_by: str = "name", order: str = "asc"):
    valid_order = {"name": Item.name, "quantity": Item.quantity, "created_at": Item.created_at, "updated_at": Item.updated_at, "category": Item.category}
    order_col = valid_order.get(order_by, Item.name)
    sort = order_col.asc() if order.lower() != "desc" else order_col.desc()

    with Session(engine) as session:
        statement = select(Item)
        if q:
            like = f"%{q.lower()}%"
            statement = statement.where(func.lower(Item.name).like(like) | func.lower(Item.category if Item.category is not None else "").like(like) | func.lower(Item.unit).like(like))
        if low_stock:
            statement = statement.where(Item.quantity <= Item.min_qty)
        statement = statement.order_by(sort)
        items = session.exec(statement).all()
        return items

@app.post("/api/items", response_model=ItemRead)
def create_or_add_item(payload: ItemCreate):
    name = payload.name.strip()
    unit = payload.unit.strip() if payload.unit else "unid"
    qty = max(0, payload.quantity or 0)

    if not name:
        raise HTTPException(status_code=400, detail="Nome é obrigatório.")

    with Session(engine) as session:
        # Buscar item existente (case-insensitive) por nome + unidade
        stmt = select(Item).where(func.lower(Item.name) == name.lower(), func.lower(Item.unit) == unit.lower())
        item = session.exec(stmt).first()
        if item:
            item.quantity = int(item.quantity) + int(qty)
            if payload.category:
                item.category = payload.category
            if payload.min_qty is not None:
                item.min_qty = payload.min_qty
            item.updated_at = datetime.utcnow()
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

        # Criar novo
        item = Item(
            name=name,
            unit=unit,
            quantity=qty,
            min_qty=payload.min_qty or 0,
            category=payload.category,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

@app.patch("/api/items/{item_id}/adjust", response_model=ItemRead)
def adjust_quantity(item_id: int, delta: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item não encontrado.")
        new_qty = item.quantity + delta
        item.quantity = max(0, new_qty)
        item.updated_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

@app.put("/api/items/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item não encontrado.")

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(item, field, value)
        if item.quantity is not None and item.quantity < 0:
            item.quantity = 0
        item.updated_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item não encontrado.")
        session.delete(item)
        session.commit()
        return {"ok": True}

@app.get("/api/export/csv")
def export_csv():
    # Gera um CSV na hora com todos os itens
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["id", "name", "unit", "quantity", "min_qty", "category", "created_at", "updated_at"])
    with Session(engine) as session:
        for it in session.exec(select(Item).order_by(Item.name.asc())).all():
            writer.writerow([it.id, it.name, it.unit, it.quantity, it.min_qty, it.category or "", it.created_at.isoformat(), it.updated_at.isoformat()])
    output.seek(0)
    headers = {"Content-Disposition": "attachment; filename=estoque.csv"}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)

# --------------------------
#        FRONTEND
# --------------------------

# Servir arquivos estáticos (index.html, css, js) em '/'
static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
