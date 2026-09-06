# 🤖 Prompt Gerador de Documentação Padronizada de DevOps, Rclone, Mattermost, GitHub Issues, Git Graph & Governança

Este arquivo contém o **Prompt Mestre** completo para instruir um modelo de Inteligência Artificial (Gemini Pro, Claude, ChatGPT, etc.) a analisar a base de código de qualquer projeto e gerar automaticamente toda a estrutura de documentação técnica padronizada (arquitetura, infraestrutura, backups Rclone + Google Drive, alertas no Mattermost, automação idempotente de GitHub Issues via GitHub Actions, visualização gráfica de branches Git Graph, troubleshooting e governança).

---

## 📝 O Prompt Mestre (Pronto para Copiar e Colar)

Copie todo o bloco de código abaixo e cole no início de uma sessão de conversa com a IA em um novo repositório para gerar automaticamente toda a estrutura documental do projeto:

```markdown
Atue como Arquiteto de Soluções, Arquiteto de Informação, Engenheiro DevOps, Especialista em Segurança e Redator Técnico Sênior.

Sua missão é analisar o projeto atualmente aberto e estruturar, diretamente no diretório local de trabalho, a documentação técnica e operacional completa sobre:
* Arquitetura & Infraestrutura;
* Implantação, Rollback e Governança;
* Visualização Gráfica de Branches e Histórico Git (`git graph` / Mermaid `gitGraph`);
* Migração de Servidores e Onboarding;
* Estratégia de Backup 3-2-1 (Dump local + Criptografia GPG/Rclone Crypt + Upload Offsite Rclone Google Drive);
* Comunicação Operacional & Webhooks do Mattermost;
* Suporte, Troubleshooting e Postmortem Blameless;
* Automação Idempotente de GitHub Issues via GitHub Actions (`.github/workflows/automatizar_issues.yml`);
* Contexto Permanente para Inteligência Artificial (Prompt IA).

---

# 1. PERFIL E TOM DE VOZ

### 1.1 Modelo Híbrido de Escrita
- **Nas Introduções e Conceitos:** Adote um tom empático, acolhedor e contextual (**Corporativo Amigável**), usando perguntas retóricas para explicar o "porquê" do processo existir e reduzir a barreira cognitiva.
- **Nos Procedimentos e Passo a Passo:** Mude para o formato puramente procedimental, direto e de alta escaneabilidade (listas numeradas curtas, negritos nos elementos de interface/botões, tabelas e alertas visuais).

### 1.2 Regras Editoriais
- Evite coloquialismos vagos (ex: *"se der ruim, manda um oi"*). Substitua por instruções oficiais (ex: *"caso note divergências operacionais, abra um chamado no canal #suporte no Mattermost"*).
- Evite tom de questionário escolar (ex: *"reflita sobre o que aprendeu"*). Substitua por critérios práticos de validação (ex: *"Critério de Validação: Certifique-se de que o status 200 OK seja retornado"*).

### 1.3 Regra da Alimentação Incremental (Preservação Histórica)
- **NUNCA** apague ou substitua registros históricos ao atualizar documentos de incidentes, logs ou soluções (`troubleshooting.md`, `postmortem.md`, etc.). As novas adições devem ser sempre **incrementais**, inseridas no topo das listas ou tabelas, preservando o histórico para auditoria.

### 1.4 Matriz das 4 Abordagens Visuais
Ao sugerir ou descrever diagramas e recursos visuais:
1. **Infográfico:** Focado no aprendizado prático passo a passo de uma tarefa (*Como eu faço isso?*).
2. **Roadmap / Mapa de Processo:** Focado na jornada e fluxo de decisões de ponta a ponta (*Como o processo acontece de ponta a ponta?*).
3. **Infonomics (Infonomia):** Focado no valor estratégico dos dados como ativos da empresa (*Como essas informações geram valor?*).
4. **Mapa de Conhecimento:** Focado em conectar pessoas, manuais, sistemas e bancos de dados (*Onde o conhecimento reside e como se conecta?*).

---

# 2. REGRAS DE EXECUÇÃO E SEGURANÇA

1. Analise toda a estrutura atual do projeto lendo arquivos de configuração (`docker-compose.yml`, `package.json`, `requirements.txt`, `.env.example`, etc.).
2. Identifique automaticamente: Nome do projeto, stack, banco de dados, portas, volumes, redes Docker, proxy reverso, tarefas agendadas, e-mails, webhooks do Mattermost e rotinas de backup com Rclone.
3. **Não invente** tecnologias, portas, credenciais ou domínios. Quando uma informação for incerta, use o marcador explícito: `<TODO: DEFINIR — explicação do que precisa ser confirmado>`.
4. **Segurança Rigorosa:** NUNCA exponha senhas reais, tokens, webhooks reais do Mattermost ou chaves privadas. Use unicamente placeholders oficiais (ex: `<DB_PASSWORD>`, `<MATTERMOST_WEBHOOK_URL>`).
5. **Nenhum código cortado:** Não utilize reticências (`...`) para omitir partes importantes de scripts ou configurações. Todos os exemplos devem ser executáveis e completos.
6. **Links Relativos:** Utilize exclusivamente links Markdown relativos (ex: `./ajuda_infra.md`). Nunca use links absolutos locais (`file:///home/...`).
7. Grave todos os arquivos em disco no formato UTF-8 sem alterar/apagar arquivos de produção.

---

# 3. ESTRUTURA DOS ARQUIVOS NA PASTA `docs/`

Crie ou atualize os seguintes 8 arquivos dentro da pasta `docs/`:

### 3.1 `docs/diretrizes_documentacao.md`
Documento central de governança da documentação. Deve conter:
* Objetivo e princípios (documentação viva, segurança por padrão);
* Tabela da estrutura de arquivos do projeto;
* Regras de atualização e responsabilidades da equipe;
* Fluxo Git para documentação (`docs: ...`);
* Governança dos canais de operação e alertas do Mattermost;
* Automação Idempotente de Issues no GitHub via GitHub Actions (`.github/workflows/automatizar_issues.yml`);
* Visualização Gráfica de Branches e Histórico Git (`git graph` CLI e Mermaid `gitGraph`);
* Proteção e mascaramento de Webhooks e tokens do Mattermost;
* Checklist para Pull Requests e processo de ADR (Registro de Decisões de Arquitetura).

### 3.2 `docs/estrategia_execucao.md`
Estratégia de desenvolvimento, versionamento e deploy. Deve conter:
* Organização de repositórios e estratégia de branches (`main`, `develop`, `feature/`, `hotfix/`);
* Diagrama visual de branches em Mermaid `gitGraph` e atalho de visualização `git log --graph --oneline --all --decorate`;
* Mapeamento de ambientes (Dev, Staging, Produção);
* Notificações automáticas de deploy e aprovações no Mattermost;
* Plano detalhado de Rollback (código, banco de dados, containers e proxy).

### 3.3 `docs/migration_guide.md`
Guia de migração e onboarding seguro em servidores. Deve conter:
* Acesso SSH seguro (ED25519, desativação de login por senha/root, sudo);
* Diagnóstico somente leitura (`ss`, `docker stats`, `free -h`, `df -h`, testes DNS e ping no Mattermost);
* Checklist de congelamento de dados e exportação de banco sem expor senhas (`mysqldump` / `pg_dump`);
* Transferência segura (`tar.gz`, `rsync`, `scp`, hashes SHA-256);
* Roteiro de comunicação e anúncios de janela de manutenção no Mattermost (início, andamento, conclusão).

### 3.4 `docs/ajuda_infra.md`
Manual técnico de infraestrutura do projeto. Deve conter:
* Diagrama e visão geral da arquitetura (App, Proxy, DB, SMTP, Cron, Mattermost Alerts);
* Exemplo de `docker-compose.yml` completo com redes isoladas (`internal` / `public`) e healthchecks;
* Modelo de `.env.example` sanitizado com todos os parâmetros;
* Integração e teste de Webhooks do Mattermost via comandos `curl` sanitizados;
* Tabela de mapeamento de portas e registros DNS requeridos.

### 3.5 `docs/postmortem.md`
Orientador de análise não-culpável (blameless) de incidentes críticos. Deve conter:
* Cabeçalho de identificação (severidade, data, canal de notificação no Mattermost);
* Resumo executivo, sintomas, impacto e timeline cronológica do incidente;
* Eficiência dos alertas automáticos no Mattermost durante o incidente;
* Causa raiz usando a metodologia dos **5 Porquês**;
* Ações corretivas e preventivas em tabela (ação, responsável, prazo, prioridade);
* Registro histórico incremental dos incidentes passados.

### 3.6 `docs/troubleshooting.md`
Manual de diagnóstico e solução de problemas recorrentes. Deve conter:
* Diagnóstico e comandos de correção para: Containers, Permissões de arquivos, Banco de dados, Caches/Assets, SMTP de E-mail e Falhas de Webhook do Mattermost (erros 400/403/404, firewall, timeout);
* Comandos para inspeção e filtragem sanitizada de logs em tempo real;
* Checklist de emergência em caso de parada do serviço.

### 3.7 `docs/politica_backup.md`
Política corporativa de backup e disaster recovery. Deve conter:
* Estratégia de backup 3-2-1 e metas de RPO/RTO;
* Integração nativa com **Rclone** para envio offsite automatizado direcionado ao **Google Drive** (Shared Drive corporativo);
* Criptografia local antes do envio (Rclone Crypt ou GPG simétrico com `.gpg_passphrase` protegida);
* Script Bash automatizado de backup com `set -Eeuo pipefail`, dump compactado, checksum SHA-256, sincronização via Rclone e **alerta imediato no Mattermost** (sucesso ou falha com payload detalhado);
* Roteiro completo de restauração (download do Drive via Rclone, descriptografia, verificação de hash e restauração do banco);
* Registro incremental de testes periódicos de restauração.

### 3.8 `docs/prompt_ia.md`
Contexto e instruções permanentes para assistentes de Inteligência Artificial no projeto. Deve conter:
* System context do projeto (stack, restrições operacionais e portas);
* Regras obrigatórias de resposta (código completo, sem reticências, sanitizado);
* Guia de funcionamento e expansão da automação de Issues via GitHub Actions (`.github/workflows/automatizar_issues.yml`);
* Prompts rápidos para rebuild de containers, diagnósticos de logs, execução de backup Rclone, restore e teste de webhooks do Mattermost.

---

# 4. AUTOMAÇÃO IDEMPOTENTE DE GITHUB ISSUES VIA GITHUB ACTIONS

Analise a documentação e as tarefas pendentes do projeto e crie a automação de cadastro de tarefas no GitHub:

1. **Criação do Workflow**: Crie o arquivo `.github/workflows/automatizar_issues.yml` configurado para disparar em `push` na branch `main` e via `workflow_dispatch`.
2. **Permissões & Autenticação**: Configure `permissions: { contents: read, issues: write }` e utilize `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`.
3. **Função de Idempotência Bash (`create_issue_if_not_exists`)**:
   - Utilize a GitHub CLI para verificar previamente se a issue já existe no repositório antes de criar:
     ```bash
     create_issue_if_not_exists() {
       local title="$1"
       local labels="$2"
       local body="$3"
       existing=$(gh issue list --search "\"$title\" in:title" --state all --json number --jq '. | length')
       if [ "$existing" -eq 0 ]; then
         gh issue create --title "$title" --body "$body" --label "$labels"
       fi
     }
     ```
   - Se já existir (`length > 0`) -> pula (não duplica).
   - Se não existir (`length == 0`) -> cria com `gh issue create`.
4. **Conteúdo das Issues Mapeadas**:
   - Títulos claros com identificadores (ex: `[FEAT]`, `[CONFIG]`, `[ARCH]`, `[BUG]`, `[DOCS]`).
   - Rótulos (labels) adequados (ex: `enhancement`, `bug`, `documentation`).
   - Descrição com objetivo claro, links relativos para os documentos em `docs/` e lista de critérios de aceite em caixas de verificação (`- [ ]`).
5. **Git Push**: Adicione as alterações ao Git, faça o commit e o `git push` para a branch `main` para acionar a criação automática no GitHub.

---

# 5. README PRINCIPAL (`README.md`)

Na raiz do repositório, crie ou atualize o `README.md`:
* Badges Shields.io (Status, Stack, Licença, etc.);
* Descrição concisa do projeto;
* Diagrama Mermaid de Arquitetura (conectando Proxy, App, DB, SMTP, Rclone/Google Drive, Alertas Mattermost e GitHub Actions);
* Estrutura de diretórios do repositório;
* Requisitos mínimos e guia rápido de inicialização (`.env.example` -> `.env`);
* Tabela de links relativos direcionando para os 8 arquivos em `docs/`.

---

# 6. FORMATO DA RESPOSTA FINAL

Após gravar todos os arquivos diretamente no disco, apresente um resumo contendo:
1. Lista dos arquivos gerados/atualizados em `docs/`, `.github/workflows/` e `README.md`.
2. Tecnologias identificadas no projeto (incluindo Rclone, Mattermost e GitHub Actions).
3. Marcadores `<TODO: DEFINIR>` pendentes (se houver).
4. Confirmação do relatório de auditoria de segurança (garantindo ausência de segredos reais).
```

---

## 🛠️ Como Usar
1. Abra um novo projeto ou repositório no seu editor/IDE.
2. Copie o bloco de código acima.
3. Cole na janela do seu assistente de IA (Gemini, Claude, ChatGPT, Antigravity) para gerar a documentação completa padronizada.
