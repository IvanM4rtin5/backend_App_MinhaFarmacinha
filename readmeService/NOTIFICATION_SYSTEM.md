# Sistema de Notificações - Minha Farmacinha

## Visão Geral

O sistema de notificações foi implementado para fornecer lembretes automáticos baseados nos medicamentos cadastrados pelos usuários. O sistema é específico para cada usuário e utiliza as informações da tabela de medicamentos para criar notificações personalizadas.

**✅ Sistema 100% gratuito e sem dependências externas!**

## Funcionalidades Implementadas

### 1. Tipos de Notificação

- **MEDICATION_REMINDER**: Lembretes para tomar medicamentos nos horários configurados
- **LOW_STOCK_ALERT**: Alertas quando o estoque de medicamentos está baixo (≤ 5 unidades)
- **MEDICATION_EXPIRY**: Alertas de vencimento de medicamentos
- **REFILL_REMINDER**: Lembretes para reabastecer medicamentos
- **GENERAL**: Notificações gerais do sistema

### 2. Status das Notificações

- **PENDING**: Notificação criada, aguardando envio
- **SENT**: Notificação enviada com sucesso
- **READ**: Notificação lida pelo usuário
- **FAILED**: Falha no envio da notificação

### 3. Sistema de Notificações em Tempo Real

- **WebSockets**: Notificações instantâneas sem custo
- **Notificações do Navegador**: Push notifications nativas
- **Interface Web**: Exemplo completo de frontend

## Estrutura do Banco de Dados

### Tabela: notifications

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    scheduled_for TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id),
    medication_id INTEGER REFERENCES medications(id)
);
```

## Endpoints da API

### WebSocket para Notificações em Tempo Real

```
WS /api/v1/notification/ws/{user_id}
```

### Criar Notificação

```
POST /api/v1/notification/
```

### Listar Notificações do Usuário

```
GET /api/v1/notification/
Query Parameters:
- skip: int (padrão: 0)
- limit: int (padrão: 100, máximo: 1000)
- status: NotificationStatus (opcional)
```

### Buscar Notificação Específica

```
GET /api/v1/notification/{notification_id}
```

### Atualizar Notificação

```
PUT /api/v1/notification/{notification_id}
```

### Marcar como Lida

```
PATCH /api/v1/notification/{notification_id}/read
```

### Deletar Notificação

```
DELETE /api/v1/notification/{notification_id}
```

### Contar Notificações Não Lidas

```
GET /api/v1/notification/unread/count
```

### Criar Lembretes de Medicamentos

```
POST /api/v1/notification/medication-reminders
```

### Criar Alertas de Estoque Baixo

```
POST /api/v1/notification/low-stock-alerts
```

### Marcar Todas como Lidas

```
POST /api/v1/notification/mark-all-read
```

### Status do WebSocket

```
GET /api/v1/notification/websocket/status
```

## Worker de Notificações

### Funcionalidades do Worker

1. **Processamento de Notificações Pendentes**: Verifica e processa notificações agendadas
2. **Verificação de Horários**: Cria lembretes baseados nos horários configurados nos medicamentos
3. **Monitoramento de Estoque**: Cria alertas quando o estoque está baixo
4. **Envio via WebSocket**: Notificações em tempo real para usuários conectados

### Como Executar o Worker

```bash
# Executar o worker em background
python run_notification_worker.py

# Ou executar em background com nohup (Linux/Mac)
nohup python run_notification_worker.py > worker.log 2>&1 &

# Para parar o worker
pkill -f run_notification_worker.py
```

### Configuração do Worker

O worker executa em ciclos de 60 segundos por padrão e:

- Processa notificações pendentes a cada ciclo
- Verifica horários de medicamentos a cada 5 minutos
- Verifica estoque baixo a cada hora
- Envia notificações via WebSocket em tempo real

## Sistema WebSocket

### Vantagens do WebSocket

✅ **Gratuito**: Sem custos de API ou serviços externos
✅ **Tempo Real**: Notificações instantâneas
✅ **Simples**: Fácil de implementar e manter
✅ **Confiável**: Funciona offline e reconecta automaticamente
✅ **Escalável**: Suporta múltiplos usuários simultâneos

### Como Funciona

1. **Conexão**: Frontend conecta ao WebSocket com ID do usuário
2. **Processamento**: Worker cria notificações no banco
3. **Envio**: Sistema envia notificação via WebSocket se usuário conectado
4. **Recebimento**: Frontend recebe e exibe notificação instantaneamente

## Exemplo de Frontend

### HTML/JavaScript Completo

O arquivo `frontend_example.html` contém um exemplo completo de como usar o sistema:

```html
<!-- Conectar ao WebSocket -->
<script>
  const websocket = new WebSocket(
    "ws://localhost:8000/api/v1/notification/ws/1"
  )

  websocket.onmessage = function (event) {
    const data = JSON.parse(event.data)
    // Processar notificação
    showNotification(data)
  }
</script>
```

### Funcionalidades do Frontend

- ✅ Conexão automática ao WebSocket
- ✅ Recebimento de notificações em tempo real
- ✅ Notificações do navegador (push)
- ✅ Interface visual para diferentes tipos
- ✅ Reconexão automática

## Como Usar

### 1. Iniciar o Backend

```bash
# Iniciar o servidor FastAPI
uvicorn app.main:app --reload

# Em outro terminal, iniciar o worker
python run_notification_worker.py
```

### 2. Testar o Sistema

```bash
# Criar lembretes automáticos
curl -X POST "http://localhost:8000/api/v1/notification/medication-reminders" \
     -H "Authorization: Bearer YOUR_TOKEN"

# Listar notificações
curl -X GET "http://localhost:8000/api/v1/notification/" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Testar WebSocket

1. Abra o arquivo `frontend_example.html` no navegador
2. Insira o ID do usuário
3. Clique em "Conectar WebSocket"
4. As notificações aparecerão em tempo real

## Integração com Outros Sistemas

### Email (Opcional)

```python
# Exemplo de integração com email
def send_email_notification(user_email, title, message):
    # Implementar envio via email
    pass
```

### SMS (Opcional)

```python
# Exemplo de integração com SMS
def send_sms_notification(user_phone, message):
    # Implementar envio via SMS
    pass
```

### Push Notifications (Opcional)

```python
# Exemplo de integração com push notifications
def send_push_notification(user_token, title, message):
    # Implementar push notifications
    pass
```

## Exemplos de Uso

### Criar Notificação Manual

```python
from app.services.notification import NotificationService
from app.schemas.notification import NotificationCreate, NotificationType

notification_data = NotificationCreate(
    title="Lembrete: Paracetamol",
    message="Horário de tomar Paracetamol - 500mg às 14:00",
    notification_type=NotificationType.MEDICATION_REMINDER,
    user_id=1,
    medication_id=1
)

notification = NotificationService.create_notification(db, notification_data)
```

### Criar Lembretes Automáticos

```python
# Cria lembretes baseados nos medicamentos do usuário
notifications = NotificationService.create_medication_reminders(db, user_id=1)
```

### Criar Alertas de Estoque

```python
# Cria alertas para medicamentos com estoque baixo
notifications = NotificationService.create_low_stock_alerts(db, user_id=1)
```

## Configurações Adicionais

### Personalização de Horários

```python
# No worker, você pode ajustar os intervalos
if datetime.utcnow().minute % 10 == 0:  # A cada 10 minutos
    await self.check_medication_schedules()
```

### Limites de Estoque

```python
# No serviço, você pode ajustar o limite
medications = db.query(Medication).filter(Medication.stock <= 3).all()  # Limite de 3
```

## Logs e Monitoramento

O sistema gera logs detalhados:

- `notification_worker.log`: Logs do worker de notificações
- Logs de sucesso e erro para cada operação
- Métricas de notificações criadas e enviadas
- Status das conexões WebSocket

## Próximos Passos Sugeridos

1. **Configurações de Usuário**: Permitir que usuários configurem preferências de notificação
2. **Templates de Mensagem**: Criar templates personalizáveis para diferentes tipos de notificação
3. **Relatórios**: Implementar relatórios de notificações enviadas e lidas
4. **Notificações em Lote**: Otimizar envio de múltiplas notificações
5. **Testes Automatizados**: Implementar testes unitários e de integração
6. **Dashboard de Monitoramento**: Interface para monitorar o status do worker
7. **Integração com Email**: Adicionar envio de notificações por email
8. **App Mobile**: Desenvolver aplicativo móvel com push notifications

## Considerações de Segurança

- Todas as notificações são específicas por usuário
- Validação de permissões em todos os endpoints
- Logs de auditoria para ações importantes
- Proteção contra spam de notificações
- WebSocket com validação de usuário

## Troubleshooting

### Problemas Comuns

1. **Worker não inicia**: Verificar logs e dependências
2. **Notificações não são criadas**: Verificar configuração de medicamentos
3. **WebSocket não conecta**: Verificar se o servidor está rodando
4. **Performance lenta**: Ajustar intervalos do worker

### Comandos Úteis

```bash
# Verificar logs do worker
tail -f notification_worker.log

# Verificar status do worker
ps aux | grep notification_worker

# Verificar conexões WebSocket
curl http://localhost:8000/api/v1/notification/websocket/status

# Reiniciar worker
pkill -f notification_worker && python run_notification_worker.py
```

## Vantagens do Sistema Atual

✅ **Zero Custos**: Sem APIs pagas ou serviços externos
✅ **Tempo Real**: WebSockets para notificações instantâneas
✅ **Simples**: Fácil de entender e manter
✅ **Confiável**: Funciona offline e reconecta automaticamente
✅ **Escalável**: Suporta múltiplos usuários
✅ **Flexível**: Fácil de expandir com novas funcionalidades
