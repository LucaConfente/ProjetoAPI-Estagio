# Guia de Uso: Interface Web

## Introdução
A interface web permite interação visual com a API OpenAI, facilitando testes e integração.

## Estrutura
- **Frontend**: ReactJS, arquivos em `uweb_interface/frontend/`
- **Backend**: FastAPI, arquivos em `uweb_interface/backend/`

## Funcionalidades
- Consulta de modelos
- Envio de mensagens para chat/completions
- Visualização de respostas e erros

## Como Executar
1. Inicie o backend:
   ```bash
   python uweb_interface/backend/app.py
   ```
2. Inicie o frontend:
   ```bash
   cd uweb_interface/frontend
   npm install
   npm start
   ```

## Testes
- Testes automatizados para backend e frontend garantem funcionamento dos principais fluxos.
