import itertools

# lista de jogadores e suas notas
jogadores = [("rr", 30), ("teba", 28), ("luiz", 27), ("ferzera", 26), ("araujo", 26),
             ("nandex", 23), ("monstro", 23), ("xaxa", 24), ("avara", 24), ("aquino", 25)]

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
