from dotenv import load_dotenv
import os
import prompt

load_dotenv()

pod_id = os.getenv("POD_ID")


image_text_set = prompt.image_text

players = {f"Player{i+1}": set() for i in range(5)}

turn_number = 1
total_scores = {key: 0 for key in players.keys()}

for _ in range(3):  # 각 플레이어마다 3장씩 이미지를 나눠줌
    for i in range(5):
        if not image_text_set:
            break
        card = image_text_set.pop()  # 임의 원소
        players[f"Player{i+1}"].add(card)

while True:
    print(f"--- 턴 {turn_number} ---")
    for key in players:
        turn_number += 1
        turn_player = key
        turn_cards = {}
        # {"Player1" : [selected_card, 0]}
        description = ""

        if turn_player == "Player1" :
            selected_card, description, players = prompt.player_turn("Player1", players)
            print(f"당신이 선택한 카드: {selected_card}")
            print(f"설명: {description}")
        else :
            selected_card, description, players = prompt.ai_turn(turn_player, players)
            print(f"설명: {description}")

        turn_cards[turn_player] = [selected_card, 0]

        other_players = [p for p in players.keys() if p != turn_player]

        for other in other_players:
            if other == "Player1":
                selected_card, players = prompt.player_select_card("Player1", players)

            else :
                selected_card, players = prompt.ai_select_card(other, description, players)

            turn_cards[other] = [selected_card, 0]

        for k, v in turn_cards.items():
            print(f"{k} : {v[0][1]}")

        # voting : 함수에서는 가장 유사한 곳에 투표 후, 해당 플레이어가 turn player 면 자신의 voting에 +3
        for other in other_players:
            if other == "Player1":
                turn_cards = prompt.player_voting(turn_cards, turn_player, other)
            else : 
                turn_cards = prompt.ai_voting(turn_cards, turn_player, other, description)

        if turn_cards[turn_player][1] == 5 :
            for other in other_players:
                turn_cards[other][1] -=1
        elif turn_cards[turn_player][1] == 0 :
            for other in other_players:
                turn_cards[other][1] += 2
        else :
            turn_cards[turn_player][1] = 3
        
        for player in players.keys() :
            total_scores[player] += turn_cards[player][1]

        if any(score >= 30 for score in total_scores.values()):
            break
        
        for player in players.keys():
            if not image_text_set:
                break
            card = image_text_set.pop()
            players[player].add(card)

        print(total_scores, '\n')


print("게임 종료")

