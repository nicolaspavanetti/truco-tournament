from basic_players import Player
from judge import card_value

class BobbyFischer(Player):
    def __init__(self, ra, name):
        super().__init__(ra, name)

    def play(self, top_card, play_hist, score_hist):
        # Verificar se pode pedir truco
        meu_time = (self.position, (self.position + 2) % 4)
        pode_truco = True
        for jogada in play_hist[-1]:
            if jogada[2] in (3, 6, 9):
                pode_truco = (jogada[0] not in meu_time)
        if score_hist[-1][1] == 12:
            pode_truco = False

        # Separar manilhas e cartas comuns
        manilhas = []
        cartas_comuns = []
        for carta in self._cards:
            valor = card_value(carta, top_card)
            if valor >= 1000:
                manilhas.append(carta)
            else:
                cartas_comuns.append(carta)

        # Pegar as melhores e as piores cartas da mão
        best_card = None
        best_value = 0
        worst_card = None
        worst_value = 9999
        for carta in cartas_comuns:
            valor = card_value(carta, top_card)
            if valor > best_value:
                best_card = carta
                best_value = valor
            if valor < worst_value:
                worst_card = carta
                worst_value = valor

        # Se só tiver manilhas, best e worst apontam para a mais fraca
        if best_card is None or worst_card is None:
            manilha_fraca = min(manilhas, key=lambda c: card_value(c, top_card))
            best_card = manilha_fraca
            worst_card = manilha_fraca

        # Verifica mão do parceiro e do melhor adversário
        meu_parceiro = (self.position + 2) % 4
        adversarios = [(self.position + 1) % 4, (self.position + 3) % 4]
        dupla_jogou = False
        valor_dupla = 0
        melhor_adversario = 0

        for jogada in play_hist[-1]:
            if jogada[2] not in ('NORMAL', 'ENCOBERTA'):
                continue
            carta = jogada[1]
            valor = card_value(carta, top_card)
            if jogada[0] == meu_parceiro:
                dupla_jogou = True
                valor_dupla = valor
            elif jogada[0] in adversarios:
                if valor > melhor_adversario:
                    melhor_adversario = valor
        
        parceiro_vencendo = dupla_jogou and valor_dupla > melhor_adversario


        # Só tem manilhas: Joga a mais fraca e pede truco se puder
        if len(cartas_comuns) == 0:
            manilha_fraca = min(manilhas, key=lambda c: card_value(c, top_card))
            if pode_truco:
                return 2, manilha_fraca
            return 1, manilha_fraca

        # Se o parceiro já jogou
        if dupla_jogou:
            if parceiro_vencendo:
                # Parceiro está ganhando, economiza descartando a pior carta
                return 1, worst_card
            else:
                # Dupla está perdendo, tenta salvar com a melhor carta
                if best_value > melhor_adversario:
                    return 1, best_card
                else:
                    # Não dá para salvar o jogo, descarta a pior
                    return 1, worst_card
                
        else:
            if melhor_adversario > 0:
                # Adversário já jogou, tenta bater a carta dele
                if best_value > melhor_adversario:
                    return 1, best_card
                else:
                    # Não dá para bater, descarta a pior carta
                    return 1, worst_card
            else:
                # Ninguém jogou ainda, abre com a pior carta para guardar as boas
                return 1, worst_card


    def respond(self, top_card, play_hist, score_hist):
        manilhas = []
        cartas_comuns = []
        for carta in self._cards:
            valor = card_value(carta, top_card)
            if valor >= 1000:
                manilhas.append(carta)
            else:
                cartas_comuns.append(carta)

        meu_time = self.position % 2
        pontos_adversario = score_hist[-1][0][1 - meu_time]
        valor_da_mao = score_hist[-1][1]

        # Confere se tem uma carta forte o suficiente para aceitar o truco
        tenho_carta_forte = any(card_value(carta, top_card) > 103 for carta in cartas_comuns)

        # Se tiver manilha: Aumentar se puder, aceitar se já for 12
        if len(manilhas) > 0:
            if valor_da_mao == 12:
                return 1
            return 2

        # Aceita o truco se tiver carta forte, truco valer 3 e adversário ter menos de 6 pontos
        if tenho_carta_forte and valor_da_mao == 3 and pontos_adversario < 6:
            return 1
        return 0

def pair_name():
    return "Bruno_Nicolas"

def create_pair():
    return (BobbyFischer(123456, "Bruno"), BobbyFischer(234567, "Nicolas"))
