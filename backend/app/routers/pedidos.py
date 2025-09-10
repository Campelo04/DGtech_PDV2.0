# routers/pedidos.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
from ..auth_deps import get_current_user

router = APIRouter(prefix="/pedidos", tags=["pedidos"],dependencies=[Depends(get_current_user)])

# Conexão com o MongoDB
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["DGtech"]
pedidos_col = db["Pedidos"]

class Pedido(BaseModel):
    codigo: str
    id_cliente: str
    id_funcionario: str
    origem: str
    itens: Optional[List[dict]] = None
    formas_pagamento: Optional[List[dict]] = None
    valor_total: str
    abertura: Optional[str] = None
    fechamento: Optional[str] = None
    estado: str
    obs: str

def pedido_serializer(doc):
    return {
        "id": str(doc["_id"]),
        "codigo": str(doc.get("codigo", "")),
        "id_cliente": str(doc.get("id_cliente", "")),
        "id_funcionario": str(doc.get("id_funcionario", "")),
        "origem": str(doc.get("origem", "")),
        "itens": doc.get("itens", []),
        "formas_pagamento":doc.get("itens", []),
        "valor_total": str(doc.get("valor_total", "")),
        "abertura": str(doc.get("abertura", "")),
        "fechamento": str(doc.get("fechamento", "")),
        "estado": str(doc.get("estado", "")),
        "obs": str(doc.get("obs", "")),
        
    }

@router.post("/", response_model=dict)
async def criar_pedido(pedido: Pedido):
    # validações simples
    # campos_obrig = [pedido.id_cliente, pedido.id_funcionario, pedido.valor, pedido.obs]
    # if any(v == "" for v in campos_obrig):
    #     raise HTTPException(status_code=400, detail="É obrigatório preencher todos os campos, com exceção dos itens.")

    existente = await pedidos_col.find_one({"codigo": pedido.codigo})
    if existente:
        raise HTTPException(status_code=400, detail="Código já está registrado.")

    data = pedido.model_dump()
    if data.get("itens") is None:
        data["itens"] = []

    if data.get("formas_pagamento") is None:
        data["formas_pagamento"] = []

    result = await pedidos_col.insert_one(data)
    return {"id": str(result.inserted_id)}

@router.get("/", response_model=list)
async def listar_pedidos():
    docs = await pedidos_col.find().to_list(100)
    return [pedido_serializer(d) for d in docs]

@router.get("/{pedido_id}", response_model=dict)
async def obter_pedido(pedido_id: str):
    try:
        oid = ObjectId(pedido_id)
    except Exception:
        raise HTTPException(status_code=404, detail="ID inválido informado")

    doc = await pedidos_col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="pedido não encontrado")
    return pedido_serializer(doc)

@router.put("/{pedido_id}", response_model=dict)
async def atualizar_pedido(pedido_id: str, pedido: Pedido):
    try:
        oid = ObjectId(pedido_id)
    except Exception:
        raise HTTPException(status_code=404, detail="ID inválido informado")

    result = await pedidos_col.update_one({"_id": oid}, {"$set": pedido.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="pedido não encontrado")
    return {"mensagem": "pedido atualizado com sucesso"}

# Deletar um pedido
@router.delete("/{pedido_id}", response_model=dict)
async def deletar_pedido(pedido_id: str):
    collection = db["Pedidos"]
    try:
        resultado = await collection.find_one({"_id": ObjectId(pedido_id)})
    except:
        return {"mensagem": "ID inválido informado"}
    if not resultado:
        return {"mensagem": "Registro não encontrado."}
    elif resultado:
        resultado = await collection.delete_one({"_id": ObjectId(pedido_id)})
        if resultado:
            return {"mensagem": "pedido deletado com sucesso"}
    raise HTTPException(status_code=404, detail="pedido não encontrado")

#---------------------------------------------------------------------
@router.put("/{pedido_id}/itens/add")
async def add_item(pedido_id: str, payload: dict):
    """
    payload esperado:
    {
        "item": {"cod": "100", "nome": "sushi", "valor": 10},
        "novo_valor": 50.0   # valor total já recalculado
    }
    """
    try:
        oid = ObjectId(pedido_id)
    except Exception:
        raise HTTPException(400, "ID inválido")

    item = payload.get("item")
    novo_valor = payload.get("novo_valor")

    if not item or novo_valor is None:
        raise HTTPException(400, "É necessário enviar item e novo_valor")

    try:
        novo_valor = float(str(novo_valor).replace(",", "."))
    except Exception:
        raise HTTPException(400, "novo_valor inválido")

    result = await db.Pedidos.update_one(
        {"_id": oid},
        {
            "$push": {"itens": item},
            "$set": {"valor": novo_valor}
        },
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Pedido não encontrado")

    return {
        "ok": True,
        "matched": result.matched_count,
        "modified": result.modified_count
    }