# Relatório de Resiliência Estrutural — api-gateway
**Repositório:** spring-petclinic-microservices · **Commit:** 305a1f13e4f961001d4e6cb50a9db51dc3fc5967
**Perfil de avaliação:** MS-1.1.1 · **Data:** 2026-08-19

## Nota geral

**Nota de Resiliência 1.13 — Insatisfatório**

> *Insatisfatório: o serviço tem muito espaço para melhorias, necessita revisões e medidas corretivas para aumentar a confiabilidade e reduzir impactos de paradas — e danos a serviços adjacentes, podendo afetar o sistema como um todo. Possui baixa robustez.*

---

## O que foi avaliado

| Ponto de avaliação | O que é | Nota | Máximo |
|---|---|---|---|
| Entrada do cliente | A porta de entrada do gateway para requisições dos usuários | 0 | 5 |
| Consulta externa — serviço de clientes | Busca dos dados do dono do pet | 0 | 15 |
| Consulta externa — serviço de visitas | Busca do histórico de visitas do pet | 6 | 15 |
| Configuração de container/implantação | Como o serviço se comporta ao subir, cair, reiniciar | 0 | 18 |

---

## Achado 1 — A consulta mais importante é a que não tem nenhuma proteção
**Onde:** `CustomersServiceClient.java`, linhas 29-32
**Tipo:** Consulta externa (CE-1) — chamada ao serviço de clientes

**O que está acontecendo:** essa chamada busca os dados do dono do pet — a informação mais importante da tela. Ela não tem limite de tempo de espera, não tem circuito de proteção, não tem plano B, e não tenta de novo se falhar. Nenhuma dessas quatro proteções existe.

**Por que isso é um problema:** sem um limite de tempo, se o serviço de clientes travar (não cair — travar, continuar de pé mas sem responder), essa chamada fica esperando indefinidamente. Trava serve de dependência e não trava dá o mesmo resultado aqui: espera para sempre.

**Risco de não corrigir:** numa sobrecarga real, essa espera infinita vai segurando conexões do gateway até esgotar a capacidade dele — e aí *todo mundo* que usa o gateway sente o problema, não só quem pediu os dados do dono. É o tipo de falha que começa pequena e vira incidente geral.

**Por que a nota sobe pouco, mesmo sendo o maior risco:** este é o maior risco operacional do serviço, mas vale sozinho apenas 4 de 53 pontos possíveis — a nota não sobe muito porque ela reflete a cobertura como um todo, não o problema isolado mais grave. Corrigir só este item não "resolve" a nota; a recuperação de verdade vem de fechar várias lacunas, não uma.

**Prompt de correção pronto para um agente de código:**
```
Em spring-petclinic-api-gateway/src/main/java/org/springframework/samples/petclinic/api/application/CustomersServiceClient.java,
a chamada dentro de getOwner() não tem limite de tempo configurado. Adicione um timeout explícito de 2 segundos
usando .timeout(Duration.ofSeconds(2)) no Mono retornado. Não altere a assinatura do método nem qualquer outro
método da classe. Antes de criar uma nova constante, verifique se já existe um padrão de timeout em outro lugar
do módulo (por exemplo em VisitsServiceClient.java) e reaproveite-o. Adicione um teste confirmando que a chamada
falha em ~2.1s quando a dependência não responde, usando um stub com atraso simulado.
```

**Nota projetada após esta correção: 1.9**

---

## Achado 2 — Sem circuito de proteção na mesma consulta
**Onde:** `ApiGatewayController.java`, linhas 38-42
**Tipo:** Consulta externa (CE-1) — chamada ao serviço de clientes

**O que está acontecendo:** a chamada ao serviço de clientes é feita direto, sem nenhum circuito de proteção — diferente da chamada vizinha, para o serviço de visitas, que tem um circuito no mesmo método.

**Por que isso é um problema:** sem esse circuito, cada requisição nova tenta a mesma chamada que já está falhando, sem "lembrar" que ela vem falhando. O serviço de clientes, se estiver com problema, continua recebendo carga cheia em vez de um alívio.

**Risco de não corrigir:** durante uma instabilidade do serviço de clientes, o gateway martela ele com volume total em vez de dar espaço para recuperação — o que estende a duração do problema e aumenta a chance de o serviço, ao voltar, cair de novo imediatamente.

**Prompt de correção pronto para um agente de código:**
```
Em ApiGatewayController.java, a chamada a customersServiceClient.getOwner() (por volta da linha 38-42) não está
protegida por um circuito de proteção, diferente da chamada a visitsServiceClient logo abaixo, que usa
cbFactory.create("getOwnerDetails"). Envolva a chamada a customersServiceClient.getOwner() da mesma forma,
usando um nome de instância distinto (ex: "getOwnerBasicInfo") para que o estado seja rastreado separadamente
do circuito de visitas. Esta correção depende do timeout do Achado 1 já estar aplicado — um circuito de proteção
sem timeout não consegue detectar travamentos, só erros explícitos. Não altere o comportamento de fallback da
chamada de visitas no mesmo método.
```

**Nota projetada após esta correção: 2.5**

---

## Achado 3 — Sem plano B quando a consulta falha
**Onde:** mesmo método do Achado 2
**Tipo:** Consulta externa (CE-1) — chamada ao serviço de clientes

**O que está acontecendo:** não existe um plano B para quando essa chamada falha. A chamada de visitas, ao lado, tem um plano B (retorna uma lista vazia); a de clientes, não.

**Por que isso é um problema:** quando essa chamada falha — mesmo com timeout e circuito já corrigidos — a resposta inteira do gateway falha junto.

**Risco de não corrigir:** uma instabilidade pontual no serviço de clientes derruba a resposta inteira ao usuário, mesmo que os dados de visita (que já têm plano B) continuassem disponíveis. O usuário vê uma falha maior do que o problema real.

**Prompt de correção pronto para um agente de código:**
```
No mesmo arquivo e método dos Achados 1 e 2, adicione um plano B para a chamada a customersServiceClient.getOwner()
que devolva um objeto de dados do dono degradado, porém válido (por exemplo, com um sinalizador ou campos não
essenciais nulos), em vez de propagar o erro ao cliente — seguindo o mesmo padrão de emptyVisitsForPets() usado
na chamada de visitas. O plano B não pode chamar customersServiceClient de novo, nem qualquer outro serviço —
precisa retornar um valor puramente local. Adicione um teste confirmando que o endpoint responde 200 com o objeto
degradado quando o serviço de clientes está indisponível, em vez de propagar um erro 5xx.
```

**Nota projetada após esta correção: 3.4**

---

## Achado 4 — O serviço tem um "sinal de saúde" pronto, mas ninguém está ouvindo
**Onde:** `pom.xml` (a dependência existe); `docker-compose.yml`, linhas 71-82 (não há verificação de saúde configurada para este serviço)
**Tipo:** Configuração de container/implantação (AC-1)

**O que está acontecendo:** o gateway já tem o endpoint `/actuator/health`, que funciona e responde. Mas o `docker-compose.yml` configura verificação de saúde para outros dois serviços (config-server e discovery-server) e não configura para o api-gateway.

**Por que isso é um problema:** o sinal de saúde existe e funciona, mas nada está checando ele. É como ter um sensor de fumaça instalado e desligado.

**Risco de não corrigir:** se o gateway travar ou degradar, não existe nenhum mecanismo automático que perceba isso e reinicie o container ou tire ele de circulação. Ele continua recebendo tráfego mesmo doente, e alguém só vai perceber quando o sintoma já estiver visível para o usuário final.

**Prompt de correção pronto para um agente de código:**
```
Em docker-compose.yml, adicione um bloco de verificação de saúde (healthcheck) ao serviço api-gateway (por volta
da linha 71-82), seguindo o mesmo padrão já usado para config-server e discovery-server neste arquivo (verificação
via curl contra /actuator/health). Não altere as verificações de saúde de nenhum outro serviço. Confirme com
`docker-compose config` que o novo bloco é sintaticamente válido antes de finalizar.
```

**Nota projetada após esta correção: 4.5**

---

## Achado 5 — Nenhuma preparação para desligamento seguro
**Onde:** `application.yml` do api-gateway (a configuração de desligamento gradual não existe)
**Tipo:** Configuração de container/implantação (AC-1)

**O que está acontecendo:** não há configuração de desligamento gradual (`server.shutdown: graceful`).

**Por que isso é um problema:** ao receber o sinal de desligamento (por exemplo, num deploy), o comportamento padrão do Spring Boot para de aceitar chamadas novas, mas **não espera** as chamadas em andamento terminarem antes de fechar.

**Risco de não corrigir:** todo deploy — não só um em cada dez, todo — tem chance de derrubar requisições que estavam em andamento no momento exato da troca. É a fonte de erro mais frequente da lista, porque acontece a cada deploy, não só em cenário de falha.

**Prompt de correção pronto para um agente de código:**
```
Em spring-petclinic-api-gateway/src/main/resources/application.yml, adicione:
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 20s
Se já existirem blocos server: ou spring: no arquivo, insira as chaves dentro deles em vez de duplicar a chave
de nível superior. Não altere nenhuma outra configuração deste arquivo.
```

**Nota projetada após esta correção: 5.9 — passa para Bom**

---

## Resumo acumulado

| Achado | Correção | Nota depois | Classificação depois |
|---|---|---:|---|
| — | (nota atual) | 1.13 | Insatisfatório |
| 1 | Timeout na consulta de clientes | 1.9 | Insatisfatório |
| 2 | Circuito de proteção na consulta de clientes | 2.5 | Insatisfatório |
| 3 | Plano B na consulta de clientes | 3.4 | Aceitável |
| 4 | Conectar o sinal de saúde já existente | 4.5 | Aceitável |
| 5 | Desligamento gradual | 5.85 | **Bom** |

**Esta lista não é completa — e é importante dizer isso.** Os cinco achados acima cobrem os itens de maior impacto, mas ainda restam **22 pontos não detalhados neste relatório**, distribuídos assim:

| Onde | O que falta | Pontos |
|---|---|---|
| Entrada do cliente | Bulkhead ou rate limiter — nenhuma proteção configurada | 5 |
| Consulta a clientes | Tentativa automática (retry) e pool de conexões | 3 |
| Consulta a visitas | Tentativa automática, confirmação do timeout, pool de conexões | 9 |
| Container | Limite de recurso completo, sonda de inicialização, política de disrupção | 5 |

Aplicando esses itens também, a nota chegaria a **10.0 — Excelente**. Eles ficaram de fora desta primeira leva por terem impacto individual menor — mas "menor impacto" não é "sem impacto", e vale um relatório de continuação.

**Uma ressalva sobre o teto real:** dois dos itens do container — sonda de inicialização distinta e política de disrupção (PodDisruptionBudget) — são conceitos de Kubernetes. Este serviço hoje sobe apenas via `docker-compose.yml`; não existe nenhum manifesto Kubernetes no repositório para o api-gateway. Isso significa que, **sem mudar a forma como o serviço é implantado**, esses 3 pontos específicos não são alcançáveis — não é que faltou configurar, é que a peça que receberia essa configuração não existe neste ambiente. O teto real, mantendo docker-compose, é **9.4**, não 10.0.

---

Cinco achados, cinco prompts de correção, cada um executável de forma independente por um agente de código sem precisar de mais nenhuma explicação — e cada um diz o arquivo, o estado atual, o estado alvo, e um limite explícito do que não mexer, para que aplicar um achado não arrisque efeito colateral nos outros.
