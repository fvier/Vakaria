# 🔐 Arquitetura de Cofres Híbridos: Vaultwarden (Humanos) + OpenBao (Máquinas)

Esta receita descreve a arquitetura de gestão de credenciais e segredos da organização, separando acessos humanos de acessos automatizados de sistemas.

---

## 1. Por que Separar Cofres de Humanos e Máquinas?

| Característica | 👤 Vaultwarden (Humanos) | 🤖 OpenBao (Máquinas) |
| :--- | :--- | :--- |
| **Público-Alvo** | Pessoas (Suporte, Admins, Devs) | Scripts, APIs, Pipelines CI/CD, Containers |
| **Interface** | Extensão de Navegador, App Mobile, Web | API REST, SDKs (Python, Node, Go) |
| **Segredos** | Logins de SaaS, e-mails corporativos, senhas manuais | Credenciais de Bancos de Dados, API Keys, Tokens |
| **Recursos Chave** | Preenchimento automático no browser | **Segredos Dinâmicos com Leases auto-destrutíveis (TTL)** |

---

## 2. Conceito de Segredos Dinâmicos (Dynamic Secrets)

Em vez de salvar senhas de banco estáticas em arquivos `.env`, o OpenBao gera usuários temporários sob demanda:

```text
┌──────────┐      1. Solicita credencial      ┌──────────┐
│ Automação│ ───────────────────────────────> │ OpenBao  │
│ (Script) │ <─────────────────────────────── │  Server  │
└──────────┘    3. Recebe: User: temp_123     └────┬─────┘
                   Pass: secret_xyz                │ 2. Cria usuário
                   TTL: 1 hora                     v    no Banco
                                              ┌──────────┐
                                              │ Banco de │
                                              │  Dados   │
                                              └──────────┘
```

1. O script se autentica no OpenBao.
2. O OpenBao cria um usuário temporário no Banco de Dados com um **TTL (Time to Live)** de 1 hora.
3. Passada 1 hora, o OpenBao executa um `DROP USER` automaticamente no banco.
4. **Vantagem de Auditoria**: Se uma senha vazar, o log de auditoria do OpenBao mostra exatamente qual servidor/token solicitou a credencial naquele exato segundo.

---

## 3. Segurança por Ofuscação de Subdomínios

Para evitar atração de ataques automatizados (crawlers buscando subdomínios como `vault.empresa.com` ou `passwords.empresa.com`), utilize subdomínios discretos:

- 👉 `auth.suaempresa.org.br` ➔ Direcionado para o **Vaultwarden** (parece um portal de login padrão).
- 👉 `status.suaempresa.org.br` ➔ Direcionado para o **OpenBao** (parece um painel de monitoramento/uptime).

---

## 4. Exemplo de Código: Consumindo OpenBao em Python

```python
import os
import requests

# Exemplo de requisição para ler um segredo do OpenBao/Vault via API REST
OPENBAO_URL = os.getenv("OPENBAO_URL", "https://status.suaempresa.org.br:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

def get_database_secret(secret_path="secret/data/database/credentials"):
    headers = {"X-Vault-Token": VAULT_TOKEN}
    response = requests.get(f"{OPENBAO_URL}/v1/{secret_path}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()["data"]["data"]
        return data["username"], data["password"]
    else:
        raise Exception(f"Erro ao buscar segredo do OpenBao: {response.status_code} - {response.text}")

# Uso
if __name__ == "__main__":
    db_user, db_pass = get_database_secret()
    print(f"Credencial obtida com sucesso para o usuário: {db_user}")
```
