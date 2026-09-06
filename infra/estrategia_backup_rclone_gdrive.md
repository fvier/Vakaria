# 📦 Estratégia de Backup Offsite Automatizado com Rclone e Google Drive

Esta receita reúne o padrão corporativo para configuração de backups offsite seguros e incrementais usando **Rclone** direcionados a um **Drive Compartilhado (Shared Drive)** do Google Workspace, com alertas automáticos em webhook em caso de falha.

---

## 1. Vantagens do Rclone
* **Manutenção Zero**: O Rclone gerencia a renovação de tokens OAuth do Google Drive automaticamente sem precisar de scripts Python manuais.
* **Cópia Incremental**: Transfere apenas arquivos alterados ou novos.
* **Criptografia Integrada (Rclone Crypt)**: Criptografa o conteúdo antes do upload para a nuvem.

---

## 2. Instalação e Configuração

### Passo 1: Instalação
```bash
# Ubuntu / Debian / Hosts Linux
sudo apt install rclone

# openSUSE
sudo zypper install rclone
```

### Passo 2: Configuração Interativa do Remote
Execute no servidor:
```bash
rclone config
```
1. Selecione `n` (New remote).
2. Nomeie o remote como `prod-gdrive`.
3. Escolha o tipo `Google Drive` (número correspondente na lista).
4. Siga as instruções para autorizar o acesso à conta do Google Drive da organização.

---

## 3. Estrutura Recomendada no Drive Compartilhado

Organize o Drive Compartilhado da seguinte forma:

```text
Projetos - Backups/
├── MeuAppPro/
│   ├── Banco/
│   └── Arquivos/
├── MeuSaaS/
│   └── Banco/
└── Outros/
```

---

## 4. Scripts e Comandos Práticos

### A. Copiar arquivo de dump de banco de dados:
```bash
rclone copy /backups/prod-database.sql.gz prod-gdrive:Projetos_Backups/MeuAppPro/Banco/
```

### B. Sincronização incremental de diretório de mídias:
```bash
rclone copy /var/www/uploads prod-gdrive:Projetos_Backups/MeuAppPro/Arquivos/ --size-only
```

---

## 5. Script Shell Completo para Cron com Alerta no Mattermost / Webhook

Salve este script como `/usr/local/bin/executar_backup_rclone.sh`:

```bash
#!/bin/bash
# Script de Backup Offsite Rclone com Notificação por Webhook

ORIGEM="/backups/banco_dados.sql.gz"
DESTINO="prod-gdrive:Projetos_Backups/Sistema/Banco/"
WEBHOOK_URL="https://seu-mattermost.com/hooks/SEU_WEBHOOK_KEY"

# Executa o backup
if rclone copy "$ORIGEM" "$DESTINO" --quiet; then
    echo "[SUCCESS] Backup concluído com sucesso em $(date)"
else
    # Notifica o canal de alertas no Mattermost/Discord/Slack
    PAYLOAD=$(cat <<EOF
{
  "text": "🚨 **FALHA NO BACKUP OFFSITE**\n- **Host**: $(hostname)\n- **Origem**: $ORIGEM\n- **Erro**: Falha na sincronização do Rclone com o Google Drive."
}
EOF
    )
    curl -X POST -H 'Content-Type: application/json' --data "$PAYLOAD" "$WEBHOOK_URL"
    exit 1
fi
```

Dê permissão de execução:
```bash
chmod +x /usr/local/bin/executar_backup_rclone.sh
```
