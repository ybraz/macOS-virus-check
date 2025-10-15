# 🇧🇷 Guia Rápido - VirusTotal Scanner para macOS

## 🚀 Instalação Rápida

```bash
# 1. Entre no diretório do projeto
cd macos-virus-check

# 2. Execute o instalador
./install.sh

# 3. Se instalou a Quick Action, reinicie o Finder
killall Finder

# 4. Configure sua chave API
vt-check config --api-key 0c8ca843b973cfd8d78335cc01c52e28f19abaabd4df031b1b5ce353b883839a
```

## 📱 Como Usar

### Opção 1: Linha de Comando (Terminal)

```bash
# Verificar um arquivo
vt-check scan arquivo.pdf

# Verificar vários arquivos
vt-check scan *.dmg *.exe *.zip

# Verificar pasta inteira (recursivo)
vt-check scan -r ~/Downloads

# Com notificação
vt-check scan --notify arquivo-suspeito.exe
```

### Opção 2: Menu de Contexto (Finder)

1. **Clique direito** em qualquer arquivo no Finder
2. Selecione **Ações Rápidas** → **VirusTotal Scan**
3. Aguarde a notificação com o resultado
4. **Clique na notificação** para ver o relatório completo

## 🎯 Comandos Essenciais

```bash
# Ver configuração atual
vt-check config --show

# Limpar cache de resultados
vt-check config --clear-cache

# Verificar apenas o hash (sem enviar arquivo)
vt-check hash <hash-sha256>

# Ver ajuda completa
vt-check --help
```

## 🚦 Entendendo os Resultados

| Indicador | Significado | Ação |
|-----------|-------------|------|
| ✅ CLEAN | Nenhuma detecção | Arquivo seguro |
| ⚠️ SUSPICIOUS | Comportamento suspeito | Revisar com cuidado |
| 🚨 MALICIOUS | Vírus detectado! | ❌ NÃO EXECUTAR |

## ⚙️ Opções Úteis

```bash
# Forçar novo scan (ignorar cache)
vt-check scan --force-upload arquivo.exe

# Abrir relatório no navegador
vt-check scan --open-report arquivo.pdf

# Exportar resultado em JSON
vt-check scan --json arquivo.dmg

# Desabilitar cache para este scan
vt-check scan --no-cache arquivo.zip
```

## 🔧 Configuração Avançada

### Usar Variável de Ambiente (alternativa)

```bash
# Adicione ao seu ~/.zshrc ou ~/.bashrc
export VT_API_KEY="sua-chave-api-aqui"

# Recarregue o shell
source ~/.zshrc
```

### Adicionar ao PATH (se necessário)

```bash
# Adicione ao ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# Recarregue
source ~/.zshrc
```

## 📍 Onde os Dados São Armazenados

```
~/.config/vt-scanner/
├── config.json          # Sua chave API
└── cache/               # Resultados em cache (7 dias)
```

## ❓ Problemas Comuns

### "Comando não encontrado: vt-check"

**Solução:**
```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc
```

### "API key não configurada"

**Solução:**
```bash
vt-check config --api-key SUA_CHAVE_AQUI
```

### "Quick Action não aparece no menu"

**Solução:**
1. Faça logout e login novamente
2. Ou reinicie o Finder: `killall Finder`
3. Verifique em: `~/Library/Services/`

### "Erro de rate limit"

**Solução:**
- API gratuita: 4 requests/minuto, 500/dia
- Aguarde 1 minuto entre scans
- Ou use cache: `vt-check scan` (sem `--no-cache`)

## 🎓 Exemplos Práticos

### Verificar Downloads Recentes
```bash
vt-check scan -r ~/Downloads --notify
```

### Verificar Pendrive
```bash
vt-check scan -r /Volumes/PENDRIVE
```

### Verificar Anexos de Email
```bash
vt-check scan ~/Downloads/anexo*.pdf
```

### Scan Rápido com Notificação
```bash
vt-check scan --notify arquivo.dmg && say "Scan completo"
```

## 📊 Fluxo de Uso Recomendado

```
1. Baixar arquivo suspeito
   ↓
2. Clicar direito → VirusTotal Scan
   ↓
3. Aguardar notificação (15-30 segundos)
   ↓
4. Ver resultado:
   - ✅ CLEAN: Pode abrir
   - ⚠️ SUSPICIOUS: Cuidado
   - 🚨 MALICIOUS: Deletar!
```

## 🔐 Dicas de Segurança

1. **Sempre verifique antes de abrir** arquivos de fontes desconhecidas
2. **Use o modo hash** para arquivos sensíveis (não envia o arquivo)
3. **Lembre-se**: VirusTotal é público - não envie arquivos confidenciais
4. **0 detecções ≠ 100% seguro** - use como uma camada adicional de segurança

## 📞 Precisa de Ajuda?

- **Documentação completa**: [README.md](README.md)
- **Guia de início**: [QUICKSTART.md](QUICKSTART.md)
- **Arquitetura**: [ARCHITECTURE.md](ARCHITECTURE.md)

## 🎉 Pronto!

Agora você está pronto para usar o VirusTotal Scanner!

**Primeiro scan:**
```bash
vt-check scan /caminho/para/arquivo
```

**Boa sorte! 🔍**

---

## 📋 Checklist de Instalação

- [ ] Executei `./install.sh` com sucesso
- [ ] Configurei a chave API: `vt-check config --api-key ...`
- [ ] Testei um scan: `vt-check scan arquivo`
- [ ] (Opcional) Instalei a Quick Action do Finder
- [ ] (Opcional) Adicionei ao PATH: `~/.zshrc`

## 🌟 Features Favoritas

- **Cache inteligente**: Resultados instantâneos para arquivos já verificados
- **Batch scanning**: Verifique centenas de arquivos de uma vez
- **Notificações**: Receba alertas mesmo trabalhando em outra janela
- **Menu de contexto**: Verificação com apenas 2 cliques

---

*Versão 1.0.0 | Atualizado em 15/10/2025*
