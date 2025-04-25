#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
README - Ferramenta OSINT
Uma solução completa para coleta e análise de informações de fontes abertas.
"""

# Ferramenta OSINT

## Visão Geral

A Ferramenta OSINT é uma aplicação web desenvolvida para auxiliar na coleta e análise de informações de fontes abertas. Ela integra quatro módulos principais:

1. **Busca em Redes Sociais**: Coleta e análise de informações de perfis em redes sociais como Twitter, Instagram e Facebook.
2. **Busca de E-mails e Informações de Contato**: Identificação de e-mails, números de telefone e outras informações de contato associadas a pessoas ou domínios.
3. **Reconhecimento de Imagens**: Análise de imagens para detecção de faces, objetos, cores e comparação de faces.
4. **Análise de Metadados de Arquivos**: Extração e análise de metadados de diferentes tipos de arquivos, revelando informações ocultas.

## Requisitos

- Python 3.10 ou superior
- Pip (gerenciador de pacotes Python)
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

## Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/osint-tool.git
cd osint-tool

# Instalar dependências
pip install -r requirements.txt

# Iniciar a aplicação
python app.py
```

A aplicação estará disponível em `http://localhost:5000` no seu navegador.

## Estrutura do Projeto

```
osint_tool/
├── app.py                  # Aplicação Flask principal
├── modules/                # Módulos da ferramenta
│   ├── social_media.py     # Módulo de busca em redes sociais
│   ├── contact_info.py     # Módulo de busca de e-mails e contatos
│   ├── image_recognition.py # Módulo de reconhecimento de imagens
│   └── metadata_analysis.py # Módulo de análise de metadados
├── templates/              # Templates HTML para a interface web
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
├── tests/                  # Testes unitários e de integração
├── docs/                   # Documentação
└── requirements.txt        # Dependências do projeto
```

## Documentação

Para informações detalhadas sobre como usar a ferramenta, consulte o [Manual do Usuário](docs/manual_usuario.md).

## Uso Ético e Responsável

Esta ferramenta foi desenvolvida para fins educacionais, de pesquisa e para uso legítimo em investigações. Ao utilizar esta ferramenta, você concorda em:

- Respeitar a privacidade das pessoas e organizações
- Utilizar as informações coletadas apenas para fins legítimos e legais
- Não utilizar a ferramenta para assédio, perseguição ou qualquer atividade maliciosa
- Cumprir todas as leis e regulamentos aplicáveis, incluindo leis de proteção de dados
- Obter as permissões necessárias antes de coletar ou analisar informações de terceiros

O uso indevido desta ferramenta pode violar leis de privacidade e proteção de dados. O usuário é o único responsável pelo uso que faz desta ferramenta e pelas consequências de suas ações.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contato

Para dúvidas, sugestões ou relatos de problemas, entre em contato através dos seguintes canais:

- E-mail: suporte@ferramentaosint.com.br
- Website: www.ferramentaosint.com.br/suporte
- Telefone: (11) 1234-5678
