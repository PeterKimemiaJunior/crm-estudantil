# RNF-03 — Segurança e Validação (Resumo Técnico)

Objetivo

- Garantir validação e sanitização dos inputs nos controladores Python antes de gravar na base de dados, conforme RNF-03.

Ficheiros alterados

- `custom_addons/crm_estudantil/controllers/validators.py` — novo módulo com helpers de validação e sanitização.
- `custom_addons/crm_estudantil/controllers/main.py` — `submit_lead` e `submit_oportunidade` reforçados para validar/limpar dados.
- `custom_addons/crm_estudantil/controllers/gestao.py` — `move_candidatura` valida `lead_id` e `target_stage` antes de escrever.

Validações e sanitizações implementadas

- `sanitize_text(value, max_len)`: converte para string, remove caracteres não-imprimíveis, escapa entidades HTML e aplica `max_len`.
- `validate_email(value, max_len)`: valida formato básico de email por regex e comprimento máximo.
- `sanitize_phone(value, max_len)`: mantém apenas dígitos e caracteres comuns de telefone (`+ - ( ) `) e limita comprimento.
- `sanitize_choice(value, allowed, default)`: aceita apenas valores presentes em `allowed`, caso contrário devolve `default`.
- `safe_int(value, default, min_value, max_value)`: converte com segurança para inteiro e aplica limites.
- `safe_id(value)`: converte para `int` positivo ou devolve `None`.

Como cada rota foi reforçada

- `submit_lead`:
  - Verifica campos obrigatórios (`name`, `email`, `student_number`, `course`).
  - Valida `email` com `validate_email` e usa `sanitize_text` para evitar injeção HTML nos campos de texto.
  - Sanitiza `phone` com `sanitize_phone`.
  - Converte `year` com `safe_int` (limite razoável) para evitar valores extremos.
  - Usa `safe_id` para `oportunidade_id` e confirma que a oportunidade existe antes de ligar.
  - Restringe `opportunity_type` aos valores permitidos via `sanitize_choice`.
  - Retorna mensagens de erro amigáveis sem expor stacks/erros internos.

- `submit_oportunidade`:
  - Obrigatoriedade de `name` e sanitização dos campos `company_name` e `description`.
  - Restringe `opportunity_type` a um conjunto permitido.

- `move_candidatura`:
  - Valida `lead_id` com `safe_id`.
  - Valida `target_stage` contra mapeamento aceite usando `sanitize_choice`.
  - Confirma existência do estágio no CRM antes de escrever.

Segurança adicional

- As rotas usam `sudo()` como no código original; as validações reduzem risco de gravação de dados malformados e de injeção de conteúdo HTML no armazenamento.
- Mensagens de erro genéricas para erros inesperados para evitar fuga de informação.

Testes rápidos

- Exemplo `curl` para testar `submit_lead` (ajustar host/port conforme o seu ambiente):

```bash
curl -X POST http://localhost:8069/crm_estudantil/submit_lead \
  -H "Content-Type: application/json" \
  -d '{"params":{"name":"Teste","email":"t@e.com","student_number":"123","course":"informatica"}}'
```

Observações / próximos passos recomendados

- Adicionar testes automatizados (unitários/integration) para cada validação.
- Considerar políticas adicionais de rate-limiting e CSRF se necessário no frontend/API.
