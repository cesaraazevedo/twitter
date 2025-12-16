
# Testes de Consistência Causal

# Teste 1: criar post em réplica 1 (autor César) - Usando objeto PowerShell
$postCesar = @{
    processId   = 1
    evtId       = "p-101"
    autor       = "César"
    texto       = "teste do primeiro post"
    parentEvtId = $null
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8081/post" -Method POST -ContentType "application/json" -Body $postCesar

# Teste 2: criar reply em réplica 0 (autor Augusto)
$replyAugusto = @{
    processId   = 0
    evtId       = "r-101"
    autor       = "Augusto"
    texto       = "Comentando o post do César"
    parentEvtId = "p-101"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/post" -Method POST -ContentType "application/json" -Body $replyAugusto

# Teste 3: criar outro post em réplica 2 (autor Miranda)
$postMiranda = @{
    processId   = 2
    evtId       = "p-202"
    autor       = "Miranda"
    texto       = "Post independente"
    parentEvtId = $null
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8082/post" -Method POST -ContentType "application/json" -Body $postMiranda

# ================================
# Testes de Consistência Eventual
# ================================

# Teste 4: criar reply em réplica 1 (autor Azevedo)
$replyAzevedo = @{
    processId   = 1
    evtId       = "r-202"
    autor       = "Azevedo"
    texto       = "Comentando o post do Miranda"
    parentEvtId = "p-202"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:9090/post" -Method POST -ContentType "application/json" -Body $replyAzevedo

# Teste 5: criar reply em réplica 2 (autor Camaron)
$replyCamaron = @{
    processId   = 2
    evtId       = "r-303"
    autor       = "Camaron"
    texto       = "Outro comentário no post do Miranda"
    parentEvtId = "p-202"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:9091/post" -Method POST -ContentType "application/json" -Body $replyCamaron

# Teste 6: criar reply em réplica 0 (autor Augusto)
$replyAugusto2 = @{
    processId   = 0
    evtId       = "r-404"
    autor       = "Augusto"
    texto       = "Comentando novamente o post do Miranda"
    parentEvtId = "p-202"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:9092/post" -Method POST -ContentType "application/json" -Body $replyAugusto2
