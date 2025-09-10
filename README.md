# 🚀 OpenAI Integration Hub

O OpenAI Integration Hub é um projeto que visa criar uma biblioteca modular e reutilizável para a integração com a API da OpenAI. Desenvolvido com uma abordagem from scratch (sem o uso da biblioteca oficial ou frameworks como LangChain), este hub centraliza todas as funcionalidades essenciais para interagir com modelos de IA.

Com interfaces CLI e Web, ele oferece flexibilidade para desenvolvedores e uma experiência amigável para usuários. Este projeto é um exemplo prático de como construir integrações robustas e manuteníveis, focando em princípios de clean code, tratamento de erros e otimização.

# Como rodar o backend FastAPI

1. Instale as dependências (se ainda não fez):
	```
	pip install -r requirements.txt
	```

2. Para rodar o backend web (FastAPI):
	```
	python run.py
	```
	Ou, se preferir, use diretamente o Uvicorn:
	```
	python -m uvicorn uweb_interface.backend.app:app --reload
	```

3. Acesse a documentação interativa em:
	http://127.0.0.1:8000/docs

Esses comandos devem ser executados a partir da raiz do projeto.



