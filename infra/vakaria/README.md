# 🏗️ Infraestrutura como Código (Terraform) — Vakaria Barbearia

Este diretório contém a especificação declarativa de infraestrutura como código (IaC) para provisionar, gerenciar e monitorar os containers e recursos da **Vakaria** na VPS (`147.79.110.132`).

---

## 📁 Estrutura de Arquivos

* `versions.tf`: Versão mínima do Terraform e providers (`docker`, `local`, `null`).
* `provider.tf`: Configuração do Docker Provider conectado à VPS via SSH seguro (`ssh://root@147.79.110.132`).
* `variables.tf`: Variáveis customizáveis (IP do servidor, domínio, credenciais PostgreSQL, secret keys).
* `main.tf`: Recursos gerenciados (Volumes de dados/mídia/estáticos, Containers PostgreSQL 16 e Django Gunicorn com roteamento Traefik SSL).
* `outputs.tf`: Links e metadados gerados após a aplicação da infraestrutura.

---

## 🚀 Como Utilizar

### 1. Inicializar os Providers do Terraform
```bash
cd infra/vakaria
terraform init
```

### 2. Planejar as Alterações
```bash
terraform plan
```

### 3. Aplicar a Infraestrutura
```bash
terraform apply -auto-approve
```

### 4. Consultar Outputs Gerados
```bash
terraform output
```
