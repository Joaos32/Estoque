# 📦 Sistema de Estoque (MVP) — FastAPI + SQLite

Um sistema simples de estoque com **soma automática** quando você adiciona um item que já existe (mesmo nome + unidade). 
Inclui um **frontend estático** (HTML/CSS/JS) servido pelo próprio FastAPI.

## ✅ Recursos
- Adicionar itens (se já existir, **soma** a quantidade)
- Listar/buscar/ordenar itens
- Marcar estoque mínimo e ver itens com baixo estoque
- Ajustar rapidamente (+1/−1/+10/−10)
- Exportar CSV
- Banco local **SQLite** (arquivo `estoque.db`)

---

## ▶️ Como rodar (Windows)

> Requer Python 3.10+ instalado.

### 1) Abrir o terminal no projeto
```bat
cd /mnt/data/estoque_app
```

### 2) Criar e ativar a venv

**PowerShell** (recomendado):
```powershell
python -m venv .venv
# Se der erro de execução de scripts, rode esta linha e ative de novo:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**CMD (Prompt de Comando):**
```bat
python -m venv .venv
.venv\Scripts\activate
```

> ⚠️ **Não use** `source` no Windows. Esse comando é do Linux/Mac.

### 3) Instalar dependências
```bat
pip install -r requirements.txt
```

### 4) Rodar o servidor
```bat
uvicorn app.main:app --reload
```
Abra: **http://127.0.0.1:8000**  
Docs interativas: **http://127.0.0.1:8000/docs**

---

## 🧩 Estrutura
```
estoque_app/
  app/
    database.py
    main.py
    models.py
    static/
      index.html
      styles.css
      app.js
  requirements.txt
  README.md
```

## 🔧 Endpoints principais
- `GET /api/items` — lista (filtros: `q`, `low_stock`, `order_by`, `order`)
- `POST /api/items` — cria **ou soma** (se já existir `name+unit`)
- `PATCH /api/items/{id}/adjust?delta=±N` — ajusta quantidade
- `PUT /api/items/{id}` — atualiza campos
- `DELETE /api/items/{id}` — remove
- `GET /api/export/csv` — exporta CSV

Sugestões de evolução:
- autenticação de usuários
- categorias e relatórios
- controle de entradas/saídas com histórico
- importação de CSV
- multi-ambiente (homolog/produção) e deploy
