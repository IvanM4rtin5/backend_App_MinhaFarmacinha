# Sistema de Controle de Estoque de Medicamentos

## 📋 Visão Geral

O sistema agora inclui um controle automático de estoque de medicamentos baseado na frequência de uso e quantidade de comprimidos por caixa. Isso permite calcular automaticamente quando um medicamento vai acabar e gerenciar o estoque de forma inteligente.

## 🆕 Novas Funcionalidades

### 1. Campos Adicionados

- **`pills_per_box`**: Quantidade de comprimidos que vem na caixa do medicamento
- **`created_at`**: Data/hora quando o medicamento foi adicionado pelo usuário
- **`days_until_empty`**: Dias até o medicamento acabar (calculado automaticamente)
- **`is_low_stock`**: Indica se o medicamento está com estoque baixo (calculado automaticamente)

### 2. Campos Removidos

- **`icon`**: Removido pois não era necessário

## 🧮 Como Funciona o Cálculo

### Exemplo 1: Medicamento 1x ao dia

- **Caixa**: 10 comprimidos
- **Frequência**: 1x ao dia
- **Resultado**: Vai durar 10 dias

### Exemplo 2: Medicamento 2x ao dia

- **Caixa**: 20 comprimidos
- **Frequência**: 2x ao dia
- **Resultado**: Vai durar 10 dias

### Exemplo 3: Medicamento 3x ao dia

- **Caixa**: 30 comprimidos
- **Frequência**: 3x ao dia
- **Resultado**: Vai durar 10 dias

## 📊 Endpoints Disponíveis

### Endpoints Básicos (CRUD)

- `POST /medication/` - Criar medicamento
- `GET /medication/` - Listar medicamentos
- `GET /medication/{id}` - Buscar medicamento específico
- `PUT /medication/{id}` - Atualizar medicamento
- `DELETE /medication/{id}` - Remover medicamento

### Novos Endpoints de Estoque

- `GET /medication/low-stock/` - Listar medicamentos com estoque baixo
- `GET /medication/expired/` - Listar medicamentos que acabaram
- `PATCH /medication/{id}/stock` - Atualizar apenas o estoque
- `POST /medication/{id}/consume` - Simular consumo de um medicamento
- `POST /medication/daily-consumption` - Simular consumo diário de todos
- `POST /medication/cleanup/empty` - Remover medicamentos com estoque zero

## 🔄 Fluxo de Uso Recomendado

### 1. Criação de Medicamento

```json
{
  "name": "Paracetamol",
  "dosage": "500mg",
  "category": "Analgésico",
  "frequency": "2x ao dia",
  "schedules": ["08:00", "20:00"],
  "stock": 20,
  "pills_per_box": 20,
  "notes": "Tomar com água"
}
```

### 2. Consumo Diário Automático

O frontend deve chamar `POST /medication/daily-consumption` uma vez por dia para simular o consumo automático.

### 3. Monitoramento de Estoque

- Use `GET /medication/low-stock/` para alertar sobre medicamentos com estoque baixo
- Use `GET /medication/expired/` para identificar medicamentos que acabaram

### 4. Limpeza Automática

Use `POST /medication/cleanup/empty` para remover medicamentos com estoque zero.

## 📈 Cálculos Automáticos

### Dias até Acabar

```python
days_until_empty = stock // pills_per_day
```

### Estoque Baixo

Um medicamento é considerado com estoque baixo se:

- Tem menos de 7 dias até acabar, OU
- Tem menos de 1 caixa completa

## 🚀 Migração do Banco de Dados

Para aplicar as mudanças no banco de dados:

```bash
python migrations/add_medication_columns.py
```

### Mudanças na Tabela

```sql
-- Adicionar novas colunas
ALTER TABLE medications ADD COLUMN pills_per_box INTEGER NOT NULL DEFAULT 1;
ALTER TABLE medications ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Remover coluna antiga
ALTER TABLE medications DROP COLUMN icon;
```

## 💡 Exemplos de Uso

### Criar Medicamento

```bash
curl -X POST "http://localhost:8000/api/v1/medication/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ibuprofeno",
    "dosage": "400mg",
    "category": "Anti-inflamatório",
    "frequency": "3x ao dia",
    "schedules": ["08:00", "14:00", "20:00"],
    "stock": 30,
    "pills_per_box": 30,
    "notes": "Tomar após refeições"
  }'
```

### Simular Consumo Diário

```bash
curl -X POST "http://localhost:8000/api/v1/medication/daily-consumption" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Verificar Estoque Baixo

```bash
curl -X GET "http://localhost:8000/api/v1/medication/low-stock/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Configuração do Frontend

### 1. Agendamento de Tarefas

Configure uma tarefa agendada para chamar o endpoint de consumo diário:

```javascript
// Executar uma vez por dia às 00:00
setInterval(() => {
  if (isNewDay()) {
    fetch("/api/v1/medication/daily-consumption", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    })
  }
}, 24 * 60 * 60 * 1000)
```

### 2. Alertas de Estoque

Monitore medicamentos com estoque baixo:

```javascript
// Verificar estoque baixo periodicamente
setInterval(() => {
  fetch("/api/v1/medication/low-stock/", {
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((response) => response.json())
    .then((medications) => {
      if (medications.length > 0) {
        showLowStockAlert(medications)
      }
    })
}, 60 * 60 * 1000) // A cada hora
```

## 🎯 Benefícios

1. **Controle Automático**: O sistema calcula automaticamente quando medicamentos vão acabar
2. **Alertas Inteligentes**: Notifica sobre estoque baixo antes de acabar
3. **Limpeza Automática**: Remove medicamentos vazios automaticamente
4. **Precisão**: Baseado na frequência real de uso
5. **Flexibilidade**: Suporta diferentes frequências e quantidades

## 🔮 Próximos Passos

- Implementar notificações push para estoque baixo
- Adicionar histórico de consumo
- Criar relatórios de uso de medicamentos
- Integrar com sistema de compras automáticas
