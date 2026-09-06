variable "server_ip" {
  description = "Endereço IPv4 da VPS de Produção"
  type        = string
  default     = "147.79.110.132"
}

variable "ssh_user" {
  description = "Usuário SSH para conexão e provisionamento"
  type        = string
  default     = "root"
}

variable "docker_host" {
  description = "Endpoint do Docker remoto na VPS via SSH"
  type        = string
  default     = "ssh://root@147.79.110.132"
}

variable "domain_name" {
  description = "Domínio principal da loja"
  type        = string
  default     = "grifehf.com.br"
}

variable "app_name" {
  description = "Nome do projeto / aplicação"
  type        = string
  default     = "grifehf"
}

variable "postgres_db" {
  description = "Nome do banco de dados PostgreSQL"
  type        = string
  default     = "grifehf"
}

variable "postgres_user" {
  description = "Usuário do banco de dados PostgreSQL"
  type        = string
  default     = "grifehf"
}

variable "postgres_password" {
  description = "Senha do banco de dados PostgreSQL (Defina via TF_VAR_postgres_password ou terraform.tfvars)"
  type        = string
  sensitive   = true
}

variable "django_secret_key" {
  description = "SECRET_KEY de produção do Django (Defina via TF_VAR_django_secret_key ou terraform.tfvars)"
  type        = string
  sensitive   = true
}
