import itertools

# lista de jogadores e suas notas
jogadores = [("aquino", 6.7), ("danilo", 5.4), ("diego", 4.5), ("erick", 6.6), ("jackie", 6.9),
             ("luiz", 9.8), ("monstro", 6.1), ("pk", 4.4), ("rodrigo", 5.4), ("xaxa", 7.3)]

# calcular todas as combinações possíveis de 5 jogadores em cada grupo
comb_grupos = itertools.combinations(jogadores, 5)

# inicializar a melhor diferença de soma como a soma total de todas as notas
melhor_diff = sum(nota for _, nota in jogadores)

# procurar a combinação que resulta na menor diferença de soma
for grupo1 in comb_grupos:
    # criar uma lista com os jogadores não escolhidos para o grupo 1
    grupo2 = [j for j in jogadores if j not in grupo1]

    # calcular as somas de cada grupo
    soma_grupo1 = sum(nota for _, nota in grupo1)
    soma_grupo2 = sum(nota for _, nota in grupo2)

    # calcular a diferença de soma entre os grupos
    diff = abs(soma_grupo1 - soma_grupo2)

    # atualizar a melhor diferença de soma, se necessário
    if diff < melhor_diff:
        melhor_diff = diff
        melhores_grupos = (grupo1, grupo2)

print("Melhor divisão de grupos:")
print("Grupo 1:", [jogador[0] for jogador in melhores_grupos[0]])
print("Grupo 2:", [jogador[0] for jogador in melhores_grupos[1]])
print("Diferença de soma:", melhor_diff)
