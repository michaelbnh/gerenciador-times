class GerenciadorTimes:
    def __init__(self, jogadores, time1, time2, tamanho_time=7):
        self.tamanho_time = tamanho_time
        self.times = []
        self.fila = []
        self.ultimo_time_perdedor = None  # Para rastrear quem perdeu

        self._criar_times(jogadores, time1, time2)

    def _criar_times(self, jogadores, time1, time2):
        self.times = [time1.copy(), time2.copy()]

        usados = set(time1 + time2)

        for jogador in jogadores:
            if jogador not in usados:
                self.fila.append(jogador)
    
    def verificar_e_sortear(self):
        """Verifica se tem 14 jogadores na fila e sorteia times"""
        if len(self.fila) >= 14:
            # Embaralha os primeiros 14 jogadores
            import random
            jogadores_sorteados = self.fila[:14]
            random.shuffle(jogadores_sorteados)
            
            # Remove os jogadores sorteados da fila
            self.fila = self.fila[14:]
            
            # Cria os dois times
            time1 = jogadores_sorteados[:7]
            time2 = jogadores_sorteados[7:]
            
            self.times = [time1, time2]
            
            return True, time1, time2
        return False, None, None

    def adicionar_na_fila(self, nome):
        self.fila.append(nome)
        # Verifica automaticamente se já pode sortear
        return self.verificar_e_sortear()

    def time_perdeu(self, indice):
        time = self.times[indice]
        
        # Guarda quem perdeu para prioridade
        self.ultimo_time_perdedor = time.copy()

        for jogador in time:
            self.fila.append(jogador)

        self.times[indice] = []

        # Primeiro tenta completar com jogadores que estavam na fila
        while self.fila and len(self.times[indice]) < self.tamanho_time:
            self.times[indice].append(self.fila.pop(0))
        
        # Se ainda não completou, usa os perdedores (que já estão na fila no final)
        # Como os perdedores foram adicionados no início do método, 
        # eles estarão no final da fila quando os primeiros forem removidos
        
        return len(self.times[indice])  # Retorna quantos jogadores estão no time

    def completar_time_prioridade(self, indice_time):
        """Completa um time dando prioridade para quem perdeu último"""
        if self.ultimo_time_perdedor:
            # Tenta completar com os últimos perdedores primeiro
            perdedores_disponiveis = [j for j in self.ultimo_time_perdedor if j in self.fila]
            
            for jogador in perdedores_disponiveis:
                if len(self.times[indice_time]) < self.tamanho_time:
                    self.fila.remove(jogador)
                    self.times[indice_time].append(jogador)
                else:
                    break
        
        # Se ainda não completou, pega da fila normalmente
        while self.fila and len(self.times[indice_time]) < self.tamanho_time:
            self.times[indice_time].append(self.fila.pop(0))
    
    def get_status(self):
        """Retorna status atual do gerenciador"""
        return {
            'fila': self.fila,
            'times': self.times,
            'tamanho_time': self.tamanho_time,
            'pode_sortear': len(self.fila) >= 14
        }