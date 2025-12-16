from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from collections import defaultdict
import threading, sys, uvicorn, requests

app = FastAPI()
# Configurações iniciais
myId = 0
N = 3
clock = []
posts = {}
respostas = defaultdict(list)
buffer = []
processos = [
    "localhost:8080", # Mantido
    "localhost:8081",
    "localhost:8082",
]
# Modelo de dados para eventos
class Evento(BaseModel):
    processId: int
    evtId: str
    parentEvtId: Optional[str] = None
    autor: str
    texto: str
    vc: Optional[List[int]] = None
    
# Endpoint para postar um novo evento
@app.post("/post")
def postar(msg: Evento):
    if msg.processId == myId:
        clock[myId] += 1
        msg.vc = clock.copy()
        # Eventos locais são registrados diretamente
        registrar_evento(msg)
        payload = msg.dict()
        for i, addr in enumerate(processos):
            if i != myId:
                enviar_async(f"http://{addr}/share", payload)
    # Se o evento for de outro processo, encaminha para o fluxo normal
    else:
        processar_evento(msg)
    return {"status": "ok", "replica": myId}

# Endpoint para receber eventos compartilhados
@app.post("/share")
def compartilhar(msg: Evento):
    processar_evento(msg)
    return {"status": "ok", "recebidoPor": myId}

def enviar_async(url, payload):
    def worker():
        try:
            requests.post(url, json=payload, timeout=2)
        except Exception as e:
            print(f"[WARN] falha ao enviar para {url}: {e}")
    threading.Thread(target=worker, daemon=True).start()

# Verifica se uma mensagem pode ser entregue
def pode_entregar(msg: Evento) -> bool:
    if msg.vc is None or len(msg.vc) != N:
        return False
    i = msg.processId
    for k in range(N):
        if k == i: continue
        if msg.vc[k] > clock[k]:
            return False
    if msg.vc[i] != clock[i] + 1:
        return False
    if msg.parentEvtId and msg.parentEvtId not in posts:
        return False
    return True

# Tenta entregar mensagens do buffer
def tentar_buffer():
    entregou = True
    while entregou:
        entregou = False
        for msg in buffer[:]:
            if pode_entregar(msg):
                buffer.remove(msg)
                registrar_evento(msg)
                entregou = True

# Processa um evento recebido
def processar_evento(msg: Evento):
    if pode_entregar(msg):
        registrar_evento(msg)
        tentar_buffer()
    else:
        buffer.append(msg)
    mostrar_feed()

# Registra o evento no estado local
def registrar_evento(msg: Evento):
    i = msg.processId
    clock[i] = msg.vc[i]
    if msg.parentEvtId is None:
        posts[msg.evtId] = msg
    else:
        respostas[msg.parentEvtId].append(msg)

# Mostra o feed atual
def mostrar_feed():
    print(f"\n=== FEED CAUSAL (Replica {myId}) ===")
    print(f"Clock={clock}, buffer={len(buffer)}")
    for postId, p in posts.items():
        print(f"[POST] {p.evtId} by {p.autor} vc={p.vc}: {p.texto}")
        if postId in respostas:
            for r in respostas[postId]:
                print(f"   [REPLY] {r.evtId} by {r.autor} vc={r.vc}: {r.texto}")
    print("=== END FEED ===\n")

# Inicialização do servidor
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python causal.py <id>")
        sys.exit(1)
    myId = int(sys.argv[1])
    clock = [0] * N
    host, port = processos[myId].split(":")
    uvicorn.run(app, host=host, port=int(port))