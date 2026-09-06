# Histórico de versões

## 1.1.0 — 2026-08-09

- endurecimento das configurações, autenticação, autorização e sessões;
- proteção CSRF, limitação de requisições e cabeçalhos HTTP de segurança;
- remoção de credenciais padrão e validação obrigatória de segredos em produção;
- persistência das vendas integradas no PostgreSQL, com migration Alembic;
- correção do healthcheck e ampliação da migração SQLite/PostgreSQL;
- geração estável de relatórios PDF paginados e correções nos downloads CSV/XLSX;
- testes automatizados para os fluxos críticos de segurança e integração;
- alinhamento da documentação e dos arquivos de deploy.
