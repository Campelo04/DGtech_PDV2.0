# routers/produtos.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
from ..auth_deps import get_current_user

router = APIRouter(prefix="/produtos", tags=["produtos"],dependencies=[Depends(get_current_user)])

# Conexão com o MongoDB
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["DGtech"]
produtos_col = db["Produtos"]

# Modelo de produto
class Produto(BaseModel):
    codigo: str
    categoria:str
    nome: str
    valor: str
    descricao: str


# Converter documentos do MongoDB para um formato JSON serializável
def produto_serializer(produto):
    return {
        "id": str(produto["_id"]),
        "codigo":str(produto["codigo"]),
        "categoria":str(produto["categoria"]),
        "nome": str(produto["nome"]),
        "valor": str(produto["valor"]),
        "descricao": str(produto["descricao"])

    }

@router.post("/", response_model=dict)
async def criar_produto(produto: Produto):
    # validações simples
    campos_obrig = [produto.id_cliente, produto.id_funcionario, produto.valor, produto.obs]
    if any(v == "" for v in campos_obrig):
        raise HTTPException(status_code=400, detail="É obrigatório preencher todos os campos, com exceção dos itens.")

    existente = await produtos_col.find_one({"codigo": produto.codigo})
    if existente:
        raise HTTPException(status_code=400, detail="Código já está registrado.")

    data = produto.model_dump()
    if data.get("itens") is None:
        data["itens"] = []

    result = await produtos_col.insert_one(data)
    return {"id": str(result.inserted_id)}

@router.get("/", response_model=list)
async def listar_produtos():
    docs = await produtos_col.find().to_list(100)
    return [produto_serializer(d) for d in docs]

@router.get("/{produto_id}", response_model=dict)
async def obter_produto(produto_id: str):
    try:
        oid = ObjectId(produto_id)
    except Exception:
        raise HTTPException(status_code=404, detail="ID inválido informado")

    doc = await produtos_col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="produto não encontrado")
    return produto_serializer(doc)

@router.put("/{produto_id}", response_model=dict)
async def atualizar_produto(produto_id: str, produto: Produto):
    try:
        oid = ObjectId(produto_id)
    except Exception:
        raise HTTPException(status_code=404, detail="ID inválido informado")

    result = await produtos_col.update_one({"_id": oid}, {"$set": produto.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="produto não encontrado")
    return {"mensagem": "produto atualizado com sucesso"}
#---------------------------------------------------------------------
