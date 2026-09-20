# Regras do projeto

- Não mover scripts sem atualizar suas referências.
- Não assumir que o working directory é o diretório atual (`pwd`).
- Caminhos devem ser derivados do diretório do projeto/working directory.
- Não substituir Bash por outra linguagem sem necessidade.
- Preservar a estrutura existente do backend.
- Antes de alterar um script, verificar quais outros scripts o chamam.
- Não remover funcionalidades existentes durante refatorações.
- Preferir alterações pequenas e testáveis.

# Novas regras para o gui

- analisar a pasta, ver oque cada arquivo faz, gerar um plano de ação antes de implementar as funções
- ler cada arquivo, ver sua função e checar se nada ficara quebrado
- O arquivo "vonvakvas.sh" na raiz é uma api que chama o resto dos scripts, use ele para os botões do gui que iram executar certa ação
- caso precise ajustar ou adicionar algo no arquivo "vonvakvas.sh" (api) pode adicionar


# Regras gerais

- evitar usar /tmp por bloat de ram e minha ram ser lenta e encher muito rapido, 8gb é sofrido
