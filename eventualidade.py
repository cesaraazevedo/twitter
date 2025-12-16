from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from collections import defaultdict
import threading, sys, uvicorn, requests

app = FastAPI()

myId = 0
lamport = 0
posts = {}
respostas = defaultdict(list)
pendentes = defaultdict(list)
processos = [
    "localhost:9090",
    "localhost:9091",
    "localhost:9092",
]

# Modelo de dados para eventos
class Evento(BaseModel):
    processId: int
    evtId: str
    parentEvtId: Optional[str] = None
    autor: str
    texto: str
    ts: Optional[int] = None

@app.post("/post")
def postar(msg: Evento):
    global lamport
    if msg.processId == myId:
        lamport += 1
        msg.ts = lamport
    registrar(msg)
    payload = msg.dict()
    for i, addr in enumerate(processos):
        if i != myId:
            enviar_async(f"http://{addr}/share", payload)
    return {"status": "ok", "replica": myId}

# Endpoint para receber eventos compartilhados
@app.post("/share")
def compartilhar(msg: Evento):
    global lamport
    # Atualiza o relógio local com base no timestamp recebido
    lamport = max(lamport, msg.ts) + 1
    registrar(msg)
    return {"status": "ok", "recebidoPor": myId}

def enviar_async(url, payload):
    def worker():
        try:
            requests.post(url, json=payload, timeout=2)
        except Exception as e:
            print(f"[WARN] falha ao enviar para {url}: {e}")
    threading.Thread(target=worker, daemon=True).start()
    
# Registra o evento no estado local
def registrar(msg: Evento):
    if msg.parentEvtId is None:
        posts[msg.evtId] = msg
        if msg.evtId in pendentes:
            for r in pendentes[msg.evtId]:
                respostas[msg.evtId].append(r)
            del pendentes[msg.evtId]
    else:
        if msg.parentEvtId in posts:
            respostas[msg.parentEvtId].append(msg)
        else:
            pendentes[msg.parentEvtId].append(msg)
    exibir_feed()
    
# Mostra o feed atual 
def exibir_feed():
    print(f"\n=== FEED EVENTUAL (Replica {myId}) ===")
    for postId, p in posts.items():
        print(f"[POST] {p.evtId} by {p.autor} @ts={p.ts}: {p.texto}")
        if postId in respostas:
            for r in respostas[postId]:
                print(f"   [REPLY] {r.evtId} by {r.autor} @ts={r.ts}: {r.texto}")
    if pendentes:
        print("---- Pendentes ----")
        for pai, lst in pendentes.items():
            for r in lst:
                print(f"[ORPHAN] {r.evtId} -> {pai} by {r.autor}: {r.texto}")
    print("=== END FEED ===\n")

# Inicialização do servidor
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python eventualidade.py <id>")
        sys.exit(1)
    myId = int(sys.argv[1])
    host, port = processos[myId].split(":")
    uvicorn.run(app, host=host, port=int(port))