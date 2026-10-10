# Como funciona

A Omie informa quantos títulos atrasados existem, mas não informa quanto eles somam por faixa. As habilidades
oficiais pedem ao modelo de IA para somar os valores lidos — e é nessa soma de cabeça que número se corrompe.

Esta skill separa as duas coisas. A **quantidade** vem do campo que a própria Omie informa. O **valor** vem de um
script que lê os títulos pela API, soma por dois caminhos (direto e página a página) e só entrega o total se: leu
exatamente quantos títulos a Omie disse que existem, nada ficou de fora pelo limite de páginas, todo título tinha
valor numérico e as duas somas bateram. Se qualquer uma dessas falhar, a faixa sai sem valor e com o motivo.

Cada total vem com uma linha de conferência ("37 registros lidos de 37 informados pela Omie") para você conferir no
painel do Omie quando quiser. A skill só lê: não dá baixa, não altera título e não diz quem cobrar.

O script precisa de Python e das chaves da API do Omie no `.env` do projeto — por isso esta skill roda no Claude
Code. As chaves nunca passam pelo chat.
