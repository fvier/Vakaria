# 🌐 Checklist e Modelo de Configuração de Zona DNS & E-mail Corporativo

Este documento serve como receita para configuração inicial ou migração de zonas DNS da organização, cobrindo apontamentos de aplicação, serviços de e-mail (Google Workspace e servidor próprio Postal SMTP) e segurança (SPF, DKIM, DMARC).

---

## 1. Tabela de Registros Padrão (Modelo de Referência)

| Tipo | Nome (Host) | Dados / Destino | Finalidade / Serviço |
| :--- | :--- | :--- | :--- |
| **A** | `@` | `76.76.21.21` | Apontamento do site principal (ex: Vercel) |
| **CNAME** | `www` | `site.vercel.app` | Alias para o domínio principal com WWW |
| **MX** | `@` | `1 smtp.google.com` | Servidor de E-mails Principal (Google Workspace) |
| **TXT** | `@` | `"v=spf1 include:_spf.google.com ~all"` | Validação de Envio SPF |
| **TXT** | `google._domainkey` | `"v=DKIM1; k=rsa; p=MIGfMA0GCSqG..."` | Autenticação de Assinatura DKIM |
| **TXT** | `_dmarc` | `"v=DMARC1; p=none; rua=mailto:dmarc@suaempresa.org.br"` | Política de Proteção Antispam DMARC |

---

## 2. Subdomínios de Aplicação e Serviços de TI (Exemplo VPS)

| Tipo | Nome (Host) | Destino / IP | Serviço Vinculado |
| :--- | :--- | :--- | :--- |
| **A** | `auth` | `IP_DA_VPS` | Vaultwarden (Cofre de senhas corporativo) |
| **A** | `status` | `IP_DA_VPS` | OpenBao (Gerenciador de segredos de sistemas) |
| **A** | `chat` | `IP_DA_VPS` | Mattermost / Chat interno |
| **A** | `educa` | `IP_DA_VPS` | Moodle / EAD |
| **A** | `postal` | `IP_DA_VPS` | Servidor de Disparo Transactional (Postal SMTP) |
| **A** | `vpn` | `IP_DA_VPS` | Servidor de VPN corporativa |
| **A** | `wiki` | `IP_DA_VPS` | Wiki de documentação interna |

---

## 3. Configuração de Envio Transacional (Moodle/ERP com Postal SMTP)

Para garantir que e-mails de sistemas (como redefinição de senha ou notificações) não caiam no SPAM:

1. **SPF específico do subdomínio do sistema (ex: `educa.suaempresa.org.br`):**
   ```text
   TXT  educa  "v=spf1 a mx include:spf.postal.suaempresa.org.br ~all"
   ```
2. **Registro CNAME para Return-Path:**
   ```text
   CNAME  psrp.educa  rp.postal.suaempresa.org.br
   ```
3. **Registro CNAME para Rastreamento de Abertura/Cliques:**
   ```text
   CNAME  track.educa  track.postal.suaempresa.org.br
   ```

---

## 4. Passos para Migração Sem Disruptura (Downtime Zero)

1. **Reduzir o TTL** dos registros DNS na zona antiga para 300 segundos (5 minutos) 24h antes da migração.
2. **Exportar a tabela completa de registros DNS** do provedor antigo antes de alterar os NameServers (NS).
3. **Replicar todos os registros A, MX, CNAME e TXT** no novo provedor (ex: Cloudflare).
4. **Alterar os NameServers (NS)** no Registro.br / Registrar.
5. Validadar a propagação usando ferramentas como `dig` ou `dnschecker.org`:
   ```bash
   dig MX suaempresa.org.br +short
   dig TXT suaempresa.org.br +short
   ```
