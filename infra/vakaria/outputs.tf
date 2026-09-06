output "website_url" {
  description = "URL Principal da Loja com HTTPS"
  value       = "https://${var.domain_name}"
}

output "linktree_url" {
  description = "URL do Linktree Oficial"
  value       = "https://${var.domain_name}/links"
}

output "login_erp_url" {
  description = "URL do Painel ERP"
  value       = "https://${var.domain_name}/login/"
}

output "server_ip" {
  description = "IP da VPS"
  value       = var.server_ip
}

output "containers" {
  description = "Containers Ativos"
  value = {
    app      = docker_container.app.name
    postgres = docker_container.postgres.name
  }
}
