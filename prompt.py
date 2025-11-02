import numpy as np
import pandas as pd
import random

image_text = {
    ("1.png", "여자, 아이, 바이올린, 음표, 꽃, 나무, 바닥, 오선지, 음악, 옷, 노래"),
    ("2.png", "여자, 노파, 백발, 앞치마, 꽃, 아이, 머리, 빨강, 화분"),
    ("3.png", "용, 기사, 칼 , 아이, 파랑, 싸움, 날개"),
    ("4.png", "비누, 방울, 무지개, 산, 행성, 꽃, 언덕, 들판, 아이, 여행, 밤"),
    ("5.png", "하늘, 망치, 조각, 예술, 새, 나비, 구름, 사다리, 남자"),
    ("6.png", "책, 요정, 빛, 난쟁이, 밤, 공부"),
    #("7.png", )
    #(".png", ""),
}

def generate_ai_description(prompt):
    description = prompt
    return description

def select_similar_card(user_cards, description):
    selected_card = user_cards.pop()
    return selected_card, user_cards


def player_turn(user_key: str, players: dict):
    """
    플레이어 차례 진행
    user_key: "Player1" (실제 사람)
    players: { "Player1": set(), "Player2": set(), ... }

    반환값:
        selected_card: 플레이어가 선택한 카드(tuple)
        description: 플레이어가 입력한 설명 문장(str)
        players: 카드 제거 후 업데이트된 players 딕셔너리
    """
    user_cards = players[user_key]

    if not user_cards:
        print("플레이어 카드가 없습니다.")
        return None, "", players

    # 플레이어가 자신의 카드 중 하나 선택
    print("당신의 카드:")
    for idx, card in enumerate(user_cards):
        print(f"{idx+1}: {card}")

    while True:
        try:
            choice = int(input(f"위 카드 중 하나를 선택하세요 (1-{len(user_cards)}): "))
            if 1 <= choice <= len(user_cards):
                break
            else:
                print("범위를 벗어났습니다. 다시 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")

    # 선택한 카드 set에서 제거
    selected_card = list(user_cards)[choice-1]
    user_cards.remove(selected_card)

    # 플레이어가 카드에 대한 설명 입력
    description = input("선택한 카드에 대한 설명 문장을 입력하세요: ")

    # players 딕셔너리에 반영
    players[user_key] = user_cards

    return selected_card, description, players

def ai_turn(user_key: str, players: dict):

    user_cards = players[user_key]

    if not user_cards:
        print("플레이어 카드가 없습니다.")
        return None, "", players
    
    selected_card = user_cards.pop()

    description = generate_ai_description(selected_card[1])

    players[user_key] = user_cards

    return selected_card, description, players



def player_select_card(user_key: str, players: dict):
    user_cards = players[user_key]

    if not user_cards:
        print("플레이어 카드가 없습니다.")
        return None, "", players

    # 플레이어가 자신의 카드 중 하나 선택
    print("당신의 카드:")
    for idx, card in enumerate(user_cards):
        print(f"{idx+1}: {card}")

    while True:
        try:
            choice = int(input(f"위 카드 중 하나를 선택하세요 (1-{len(user_cards)}): "))
            if 1 <= choice <= len(user_cards):
                break
            else:
                print("범위를 벗어났습니다. 다시 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")

    # 선택한 카드 set에서 제거
    selected_card = list(user_cards)[choice-1]
    user_cards.remove(selected_card)

    return selected_card, players

def ai_select_card(user_key: str, description: str, players: dict):
    user_cards = players[user_key]

    if not user_cards:
        print("플레이어 카드가 없습니다.")
        return None, "", players
    
    selected_card, user_cards = select_similar_card(user_cards, description)

    players[user_key] = user_cards

    return selected_card, players



def player_voting(turn_cards, turn_player, now_player):
    while True:  # do-while과 같은 구조
        random_key = input(f"{now_player}, 투표할 플레이어를 입력하세요: ")
        
        if random_key not in turn_cards:
            print("잘못된 플레이어입니다. 다시 입력하세요.")
            continue
        
        if random_key == now_player:
            print("자기 자신에는 투표할 수 없습니다. 다시 선택하세요.")
            continue
        
        # 올바른 선택이면 루프 종료
        break
    
    turn_cards[random_key][1] += 1

    if random_key == turn_player :
        turn_cards[now_player][1] += 3

    return turn_cards

def ai_voting(turn_cards, turn_player, now_player):
    random_key = random.choice(list(turn_cards.keys()))

    while random_key == now_player:
        print("자기 자신에는 투표할 수 없습니다. ")
        random_key = random.choice(list(turn_cards.keys()))
    
    turn_cards[random_key][1] += 1

    if random_key == turn_player :
        turn_cards[now_player][1] += 3

    return turn_cards