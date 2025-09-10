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
    endereco: str
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
        "endereco": str(doc.get("endereco", "")),
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

#alterar atributos isoladamente
@router.patch("/{pedido_id}/update")
async def atualizar_atributo(pedido_id: str, campo: str, valor: str):
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await pedidos_col.update_one(
        {"_id": ObjectId(pedido_id)},
        {"$set": {campo: valor}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return {"msg": f"Atributo '{campo}' atualizado com sucesso!", "valor": valor}

class Item(BaseModel):
    codigo: str
    nome: str
    valor_und: str
    qnt: str

#adicionar itens
@router.put("/{pedido_id}/itens/add")
async def add_item(pedido_id: str, item: Item):
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    oid = ObjectId(pedido_id)
    pedido = await pedidos_col.find_one({"_id": oid})
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # tratar valor_und (troca vírgula por ponto)
    try:
        valor_unit = float(item.valor_und.replace(",", ".").strip())
        quantidade = int(item.qnt.strip())
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao converter valor ou quantidade")

    valor_item = valor_unit * quantidade

    # garantir que valor_total seja número
    vt = pedido.get("valor_total", 0)
    if not isinstance(vt, (int, float)):
        try:
            if isinstance(vt, str):
                vt = float(vt.replace(",", ".").strip())
            else:
                vt = float(vt)
        except Exception:
            vt = 0.0
        await pedidos_col.update_one({"_id": oid}, {"$set": {"valor_total": vt}})

    # atualizar banco: adiciona item e incrementa valor_total
    result = await pedidos_col.update_one(
        {"_id": oid},
        {
            "$push": {"itens": item.model_dump()},
            "$inc": {"valor_total": valor_item}
        }
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Falha ao adicionar item")

    novo = await pedidos_col.find_one({"_id": oid}, {"valor_total": 1})
    return {
        "msg": "Item adicionado com sucesso",
        "incremento": valor_item,
        "novo_valor_total": float(novo.get("valor_total", vt + valor_item))
    }


@router.delete("/{pedido_id}/itens/{index}")
async def remover_item_por_indice(pedido_id: str, index: int):
    # valida id
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    oid = ObjectId(pedido_id)

    # carrega pedido
    pedido = await pedidos_col.find_one({"_id": oid})
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    itens = list(pedido.get("itens") or [])
    if not itens:
        raise HTTPException(status_code=400, detail="Pedido não possui itens")

    # valida índice
    if index < 0 or index >= len(itens):
        raise HTTPException(status_code=400, detail="Index fora do intervalo")

    # remove item e calcula decremento (valor_und * qnt)
    item_removido = itens.pop(index)
    aux = str(item_removido.get("valor_und", 0))
    valor_und = float(aux.replace(",","."))
    qnt = float(item_removido.get("qnt", 0))
    try:
        qnt = int(qnt)
    except Exception:
        pass
    decremento = float(valor_und * qnt)

    # normaliza total atual e calcula novo
    vt_atual = float(pedido.get("valor_total", 0))
    novo_total = max(0.0, vt_atual - decremento)

    # persiste
    result = await pedidos_col.update_one(
        {"_id": oid},
        {"$set": {"itens": itens, "valor_total": novo_total}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Nenhuma modificação aplicada")

    return {
        "msg": "Item removido com sucesso",
        "index_removido": index,
        "item_removido": item_removido,
        "decremento": decremento,
        "valor_total_anterior": vt_atual,
        "valor_total_atual": novo_total,
    }

@router.put("/{pedido_id}/itens/{index}/update_qnt")
async def atualizar_quantidade_item(pedido_id: str, index: int, quantidade: int):
    if quantidade < 1:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que 0.")

    pedido = await pedidos_col.find_one({"_id": ObjectId(pedido_id)})
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    try:
        item = pedido["itens"][index]
    except IndexError:
        raise HTTPException(status_code=404, detail="Item não encontrado nesse pedido.")

    # valores atuais
    valor_unitario = float(str(item["valor_und"]).replace(",", "."))
    quantidade_antiga = int(item.get("qnt", 1))

    # recalcular total removendo o valor antigo e somando o novo
    valor_total = float(str(pedido.get("valor_total", 0)).replace(",", "."))
    valor_total -= valor_unitario * quantidade_antiga
    valor_total += valor_unitario * quantidade

    # atualizar o item no pedido
    pedido["itens"][index]["qnt"] = str(quantidade)
    pedido["valor_total"] = round(valor_total, 2)

    await pedidos_col.update_one(
        {"_id": ObjectId(pedido_id)},
        {"$set": {"itens": pedido["itens"], "valor_total": pedido["valor_total"]}}
    )

    return {"msg": "Quantidade atualizada com sucesso", "pedido": pedido}