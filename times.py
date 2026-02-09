class GerenciadorTimes:
    def __init__(self, jogadores, time1, time2, tamanho_time=7):
        self.tamanho_time = tamanho_time
        self.times = []
        self.fila = []

        self._criar_times(jogadores, time1, time2)

    def _criar_times(self, jogadores, time1, time2):
        self.times = [time1.copy(), time2.copy()]

        usados = set(time1 + time2)

        for jogador in jogadores:
            if jogador not in usados:
                self.fila.append(jogador)

    def adicionar_na_fila(self, nome):
        self.fila.append(nome)

    def time_perdeu(self, indice):
        time = self.times[indice]

        for jogador in time:
            self.fila.append(jogador)

        self.times[indice] = []

        while self.fila and len(self.times[indice]) < self.tamanho_time:
            self.times[indice].append(self.fila.pop(0))
