Twitter Distribuído — Consistência Eventual vs Consistência Causal

Este projeto implementa duas versões simplificadas de um Twitter distribuído, com o objetivo de demonstrar, na prática, as diferenças entre consistência eventual e consistência causal em sistemas distribuídos.
A aplicação foi desenvolvida em Python utilizando FastAPI, com comunicação entre réplicas via API REST, e executada localmente em múltiplos processos simulando nós distribuídos.

📌 Objetivo do Projeto

Demonstrar como diferentes modelos de consistência afetam o comportamento de um sistema distribuído, especialmente em cenários onde:
Mensagens podem chegar fora de ordem
Há dependência causal entre eventos (post → reply)
A comunicação entre processos é assíncrona

🧠 Modelos de Consistência Implementados
1️⃣ Consistência Eventual

Na consistência eventual, o sistema garante que, na ausência de novas atualizações, todas as réplicas eventualmente convergem para o mesmo estado.
No entanto, não há garantia de preservação da ordem causal entre os eventos.

Características:

Uso de relógio lógico de Lamport
Comunicação assíncrona entre réplicas
Replies podem chegar antes do post original
Replies sem post conhecido são exibidos como órfãos
📁 Arquivo: eventualidade.py

2️⃣ Consistência Causal

Na consistência causal, o sistema garante que eventos causalmente relacionados sejam entregues respeitando sua ordem lógica.
Um reply só pode ser entregue após o post original ter sido entregue.

Características:

Uso de relógios lógicos vetoriais
Verificação explícita de causalidade
Uso de buffer para armazenar mensagens que ainda não podem ser entregues
Nenhum reply órfão é exibido
📁 Arquivo: causal.py

🏗️ Arquitetura do Sistema

3 réplicas independentes
Cada réplica executa em uma porta diferente
Comunicação via HTTP (/post e /share)
Replicação assíncrona usando threads
Não há coordenador central

Cada processo mantém seu próprio estado local (posts, replies, relógios).

⚙️ Tecnologias Utilizadas

Python 3.10+
FastAPI
Uvicorn
Requests
Pydantic

📦 Instalação

Clone o repositório e instale as dependências:

pip install -r requirements.txt

▶️ Como Executar

Consistência Eventual
Abra 3 terminais e execute:

python eventualidade.py 0
python eventualidade.py 1
python eventualidade.py 2


As réplicas serão iniciadas nas portas:

9090
9091
9092

Consistência Causal
Abra 3 terminais e execute:

python causal.py 0
python causal.py 1
python causal.py 2


As réplicas serão iniciadas nas portas:

8080
8081
8082

🧪 Testes Realizados
🔹 Teste 1 — Consistência Eventual

Enviar um reply antes do post original
Observar o reply sendo exibido como órfão
Enviar o post original
Verificar que o sistema eventualmente converge

Resultado esperado:
✔ Reply órfão é permitido temporariamente

🔹 Teste 2 — Consistência Causal

Enviar um reply antes do post original
Observar que o reply não é entregue
O reply permanece no buffer
Após o envio do post, o reply é automaticamente entregue

Resultado esperado:
✔ Ordem causal sempre respeitada
❌ Nenhum reply órfão é exibido

🔍 Comparação entre os Modelos
Critério	         Consistência Eventual   	  Consistência Causal
Ordem causal	     ❌ Não garantida	        ✅ Garantida
Replies órfãos	   ✅ Possíveis	              ❌ Não ocorrem
Complexidade	     Baixa	                    Maior
Buffer	           Não	                      Sim
Relógio lógico	   Lamport	                  Vetorial

📚 Conclusão
Este projeto evidencia, de forma prática, como a escolha do modelo de consistência impacta diretamente o comportamento de um sistema distribuído.
Enquanto a consistência eventual prioriza disponibilidade e simplicidade, a consistência causal oferece maior coerência lógica entre eventos relacionados.

👤 Autor
Projeto desenvolvido para fins acadêmicos na disciplina de Sistemas Distribuídos.
