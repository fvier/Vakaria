# ==============================================================================
# INFRAESTRUTURA COMO CÓDIGO (IaC) - GRIFE HF MULTIMARCAS
# ==============================================================================

# Volumes Persistentes Docker
resource "docker_volume" "postgres_data" {
  name = "${var.app_name}_postgres_data"
}

resource "docker_volume" "media_volume" {
  name = "${var.app_name}_media"
}

resource "docker_volume" "static_volume" {
  name = "${var.app_name}_static"
}

# Container PostgreSQL 16
resource "docker_container" "postgres" {
  name    = "${var.app_name}-postgres"
  image   = "postgres:16-alpine"
  restart = "unless-stopped"

  env = [
    "POSTGRES_DB=${var.postgres_db}",
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}"
  ]

  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.postgres_user} -d ${var.postgres_db}"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }

  networks_advanced {
    name = "coolify"
  }
}

# Container Django Grife HF
resource "docker_container" "app" {
  name    = "${var.app_name}-app"
  image   = "source-app:latest"
  restart = "unless-stopped"

  env = [
    "DJANGO_SETTINGS_MODULE=config.settings.local",
    "DJANGO_SECRET_KEY=${var.django_secret_key}",
    "DJANGO_ALLOWED_HOSTS=${var.domain_name},www.${var.domain_name},${var.server_ip},localhost,127.0.0.1",
    "DATABASE_URL=postgres://${var.postgres_user}:${var.postgres_password}@${docker_container.postgres.name}:5432/${var.postgres_db}"
  ]

  volumes {
    volume_name    = docker_volume.media_volume.name
    container_path = "/app/larkon/media"
  }

  volumes {
    volume_name    = docker_volume.static_volume.name
    container_path = "/app/staticfiles"
  }

  # Labels Traefik com SSL Automático Let's Encrypt
  labels {
    label = "traefik.enable"
    value = "true"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}-http.rule"
    value = "Host(`${var.domain_name}`) || Host(`www.${var.domain_name}`)"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}-http.entrypoints"
    value = "http"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}-http.middlewares"
    value = "${var.app_name}-https"
  }
  labels {
    label = "traefik.http.middlewares.${var.app_name}-https.redirectscheme.scheme"
    value = "https"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}.rule"
    value = "Host(`${var.domain_name}`)"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}.entrypoints"
    value = "https"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}.tls"
    value = "true"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}.tls.certresolver"
    value = "letsencrypt"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}-www.rule"
    value = "Host(`www.${var.domain_name}`)"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}-www.entrypoints"
    value = "https"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}-www.tls"
    value = "true"
  }
  labels {
    label = "traefik.http.routers.${var.app_name}-www.tls.certresolver"
    value = "letsencrypt"
  }
  labels {
    label = "traefik.http.services.${var.app_name}.loadbalancer.server.port"
    value = "8000"
  }
  labels {
    label = "traefik.docker.network"
    value = "coolify"
  }

  networks_advanced {
    name = "coolify"
  }

  depends_on = [docker_container.postgres]
}
