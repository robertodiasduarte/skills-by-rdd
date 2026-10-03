# Compatibilidade por capacidades

## Capacidade essencial

A execução completa exige pesquisa web atual e capacidade de abrir as páginas encontradas. Sem isso, a skill não pode afirmar que produziu uma newsletter atual do período.

## Modos

| Modo | Capacidades | Comportamento |
|---|---|---|
| Pesquisa | Web, sem escrita persistente | Pesquisa, curadoria e newsletter; deduplicação apenas na execução atual |
| Pesquisa + arquivos | Web e pasta gravável | Mantém fontes aprovadas e histórico entre edições |
| Pesquisa + arquivos + Python 3 | Web, pasta gravável e Python 3.10+ | Usa os utilitários locais de janela, cadastro e histórico |
| Agendado | Capacidades anteriores + scheduler do host | Pode ser executado diária ou semanalmente conforme configuração do usuário |
| Sem web | Sem pesquisa atual | Não gerar newsletter atual como se tivesse pesquisado; informar limitação |

## Persistência

O diretório `STATE_DIR` é uma convenção documental para uma pasta gravável escolhida pelo usuário ou pelo host. A skill não presume que essa variável exista automaticamente.

O pacote da skill pode ser somente leitura. Não grave estado mutável dentro do diretório da skill quando o host não garantir persistência e integridade.

## Agendamento

A skill é compatível com execução recorrente, mas não cria agenda por conta própria. O host deve oferecer scheduler, automação ou tarefa recorrente, e a configuração deve declarar pelo menos público, cadência e fuso.

## Portabilidade

Os scripts usam Python 3.10+ e biblioteca padrão. A pesquisa web é descrita por capacidade, não por fornecedor específico. A instalação nativa e o modo de empacotamento variam conforme o ambiente.
