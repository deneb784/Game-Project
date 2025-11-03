from dotenv import load_dotenv
import os
import prompt

load_dotenv()

pod_id = os.getenv("POD_ID")

import numpy as np
import pandas as pd
import random
import ollama
from dotenv import load_dotenv
import os
import re

# image_text = {
#     ("1.png", "여자, 아이, 바이올린, 음표, 꽃, 나무, 바닥, 오선지, 음악, 옷, 노래"),
#     ("2.png", "여자, 노파, 백발, 앞치마, 꽃, 아이, 머리, 빨강, 화분"),
#     ("3.png", "용, 기사, 칼 , 아이, 파랑, 싸움, 날개"),
#     ("4.png", "비누, 방울, 무지개, 산, 행성, 꽃, 언덕, 들판, 아이, 여행, 밤"),
#     ("5.png", "하늘, 망치, 조각, 예술, 새, 나비, 구름, 사다리, 남자"),
#     ("6.png", "책, 요정, 빛, 난쟁이, 밤, 공부"),
#     #("7.png", )
#     #(".png", ""),
# }

image_text = {
    ("1.png", "여자, 아이, 바이올린, 음표, 꽃, 나무, 바닥, 오선지, 음악, 옷, 노래"),
    ("2.png", "남자, 강아지, 공원, 나무, 산책, 햇살, 웃음, 모자, 셔츠, 운동화"),
    ("3.png", "자동차, 도로, 신호등, 건물, 하늘, 구름, 도심, 거리, 보행자, 가로수"),
    ("4.png", "고양이, 창문, 햇빛, 실내, 책상, 컵, 소파, 장난감, 털, 쿠션"),
    ("5.png", "꽃, 나비, 벌, 정원, 초록, 자연, 햇살, 잎, 물방울, 향기"),
    ("6.png", "해변, 바다, 파도, 모래, 조개, 썬베드, 파라솔, 여름, 하늘, 바람"),
    ("7.png", "아이, 장난감, 블록, 웃음, 방, 책, 바닥, 색깔, 모자, 공"),
    ("8.png", "산, 나무, 등산, 트레킹, 배낭, 하이킹, 하늘, 길, 돌, 자연"),
    ("9.png", "커피, 책, 노트북, 카페, 창문, 햇살, 의자, 탁자, 머그컵, 분위기"),
    ("10.png", "자전거, 도로, 공원, 나무, 운동, 사람, 헬멧, 바람, 햇살, 거리"),
    ("11.png", "우주, 별, 은하, 행성, 달, 천체, 망원경, 어둠, 신비, 밤하늘"),
    ("12.png", "피아노, 악보, 연주, 손, 음악, 방, 의자, 조명, 음표, 연습"),
    ("13.png", "강, 다리, 배, 물, 산, 나무, 하늘, 풍경, 평화, 자연"),
    ("14.png", "스포츠, 축구, 공, 경기, 선수, 유니폼, 관중, 골, 경기장, 태클"),
    ("15.png", "도서관, 책, 독서, 책장, 조명, 의자, 테이블, 공부, 지식, 학습"),
    ("16.png", "음식, 피자, 치즈, 토마토, 접시, 식사, 나이프, 포크, 점심, 맛있다"),
    ("17.png", "강아지, 고양이, 친구, 애완동물, 실내, 장난감, 귀여움, 털, 집, 행복"),
    ("18.png", "바다, 해돋이, 파도, 모래, 조개, 하늘, 태양, 풍경, 여름, 휴식"),
    ("19.png", "자동차, 도로, 터널, 불빛, 밤, 도시, 차선, 속도, 건물, 신호"),
    ("20.png", "축제, 불꽃놀이, 밤하늘, 사람, 카메라, 사진, 즐거움, 음악, 빛, 도시"),
    ("21.png", "음악, 기타, 콘서트, 관객, 무대, 조명, 공연, 노래, 연주, 열정"),
    ("22.png", "산책, 강아지, 공원, 나무, 길, 햇살, 웃음, 운동, 자연, 행복"),
    ("23.png", "눈, 겨울, 산, 나무, 눈사람, 스키, 얼음, 하늘, 추위, 하얀색"),
    ("24.png", "카페, 커피, 케이크, 책, 의자, 테이블, 창문, 햇살, 여유, 분위기"),
    ("25.png", "아이, 학교, 교실, 책, 연필, 공부, 친구, 칠판, 학습, 수업"),
    ("26.png", "바다, 요트, 항구, 하늘, 바람, 물결, 여행, 풍경, 휴가, 파도"),
    ("27.png", "산, 등산, 길, 배낭, 자연, 나무, 돌, 트레킹, 햇살, 풍경"),
    ("28.png", "음악, 드럼, 연주, 무대, 공연, 조명, 소리, 열정, 관객, 리듬"),
    ("29.png", "꽃, 정원, 나비, 벌, 식물, 자연, 색깔, 향기, 햇살, 평화"),
    ("30.png", "책, 독서, 조명, 테이블, 커피, 의자, 지식, 학습, 집중, 분위기")
}

POD_ID = os.getenv("POD_ID")

RUNPOD_OLLAMA_URL = f"https://{POD_ID}-11434.proxy.runpod.net"

def query_ollama(prompt: list, model: str = "EEVE-Korean-10.8B") -> str:

    client = ollama.Client(host=RUNPOD_OLLAMA_URL)

    response = client.chat(
        model=model,
        messages=prompt
    )

    return response['message']['content']

def generate_ai_description(prompt):
    messages = [
        {
            'role' : 'system',
            'content' : """ 
            너는 게임 문제를 내는 사람이야.
            다음 단어들 중 일부와 관련있는 Dixit 스타일의 모호하고 추상적인 한 문장을 만들어줘.
            문장을 짧아야 하고, 중간에 ,는 두개 이상 들어가지 않도록 해.


            단어 예시: 하늘, 망치, 조각, 예술, 새, 나비, 구름, 사다리, 남자

            출력 예시:
            "조각가의 하늘은 아직 다듬어지지 않은 돌이었다."
            """
        },
        {
            'role' : 'user',
            'content': f""" 
            다음 단어들을 보고 떠오르는 모호하고 추상적인 문장 하나를 만들어줘.
            단어 예시 : {prompt}
            """
        }
    ]

    description = query_ollama(messages)
    
    return description

def extract_model_answer(model_output: str) -> str:
    """
    모델의 응답 텍스트에서 불필요한 서론/설명을 제거하고,
    '숫자. 단어 집합 내용' 형식의 정답 문장만 추출하여 반환합니다.
    """
    
    lines = model_output.strip().split('\n')

    answer_pattern = re.compile(r'^\s*(\d+\.)\s*.*$', re.MULTILINE | re.DOTALL)
    
    for line in lines:
            
        if answer_pattern.match(line):
            return line.strip()
            
    return None


def select_similar_card(user_cards, description):
    cards = list(user_cards)
    card_list = ""
    for words in cards:
        sent = f"{words[0]}. [{words[1]}]\n"
        card_list += sent

    messages = [
        {
            "role": "system",
            "content": """
            너는 게임 문제를 맞추는 전문 분류기(Classifier)야.
            
            사용자로부터 다음 두 가지 입력을 받을 거야:
            1. '설명 문장': 문제를 풀기 위한 핵심 문장.
            2. '단어 집합 목록': **(파일명, 단어들)** 형식으로 구성된, 정답 후보 목록.
            
            너의 목표는 '설명 문장'에 **가장 의미론적으로 잘 맞는** 단어 집합 하나를 '단어 집합 목록'에서 **선택**하는 거야.
            
            ### 제약 조건 및 출력 형식 ###
            1. **반드시 방금 받은 '단어 집합 목록' 내에서만 선택해야 해.**
            2. **다른 문장, 설명, 주석 없이 오직 선택된 집합의 파일 이름과 그 내용만** 반환해야 해.
            3. **출력의 첫 글자는 무조건 선택된 집합의 파일 이름(예: 1.png)이 되어야 해.**
            4. 출력 형식은 다음과 같아:
            ```
            [선택된 집합의 파일 이름] : [선택된 집합의 단어 내용 전체]
            ```
            
            ### 예시 입력 및 출력 형식 (최종 목표) ###
            
            **사용자 입력 예시:**
            ```
            설명 문장 : 구름은 조각가였고, 하늘은 아직 다듬어지지 않은 돌이었다.
            
            단어 집합 목록 : 
            1.png : 여자, 아이, 바이올린, 음표, ...
            2.png : 여자, 노파, 백발, 앞치마, ...
            3.png : 용, 기사, 칼, 아이, 파랑, ...
            ```

            **너의 출력 (예시):**
            ```
            1.png : 여자, 아이, 바이올린, 음표, 꽃, 나무, 바닥, 오선지, 음악, 옷, 노래
            ```
            """
        },
        {
            'role' : 'user',
            'content' : f""" 
            설명 문장 : {description},
            단어 집합 목록 : {card_list}
            """
        }
    ]

    select_response = query_ollama(messages)

    select_response = extract_model_answer(select_response)

    selected_card = None

    if select_response is not None:
        file_num = select_response[0]
        for i, card in enumerate(cards):
            if card[0][0] == file_num:
                selected_card = cards[i]

    if selected_card is None:
        selected_card = random.choice(cards)

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
        
        break
    
    turn_cards[random_key][1] += 1

    if random_key == turn_player :
        turn_cards[now_player][1] += 3

    return turn_cards

def ai_voting(turn_cards, turn_player, now_player, description):
    cards = []
    for player_key, card_list in turn_cards.items():
        if player_key == now_player:
            continue
        cards.append(card_list[0])

    card_list = ""
    for words, i in enumerate(cards[1]):
        sent = f"{i}. [{words}]\n"
        card_list += sent

    messages = [
        {
            "role": "system",
            "content": """
            너는 게임 문제를 맞추는 전문 분류기(Classifier)야.
            
            사용자로부터 다음 두 가지 입력을 받을 거야:
            1. '설명 문장': 문제를 풀기 위한 핵심 문장.
            2. '단어 집합 목록': **(파일명, 단어들)** 형식으로 구성된, 정답 후보 목록.
            
            너의 목표는 '설명 문장'에 **가장 의미론적으로 잘 맞는** 단어 집합 하나를 '단어 집합 목록'에서 **선택**하는 거야.
            
            ### 제약 조건 및 출력 형식 ###
            1. **반드시 방금 받은 '단어 집합 목록' 내에서만 선택해야 해.**
            2. **다른 문장, 설명, 주석 없이 오직 선택된 집합의 파일 이름과 그 내용만** 반환해야 해.
            3. **출력의 첫 글자는 무조건 선택된 집합의 파일 이름(예: 1.png)이 되어야 해.**
            4. 출력 형식은 다음과 같아:
            ```
            [선택된 집합의 파일 이름] : [선택된 집합의 단어 내용 전체]
            ```
            
            ### 예시 입력 및 출력 형식 (최종 목표) ###
            
            **사용자 입력 예시:**
            ```
            설명 문장 : 구름은 조각가였고, 하늘은 아직 다듬어지지 않은 돌이었다.
            
            단어 집합 목록 : 
            1.png : 여자, 아이, 바이올린, 음표, ...
            2.png : 여자, 노파, 백발, 앞치마, ...
            3.png : 용, 기사, 칼, 아이, 파랑, ...
            ```

            **너의 출력 (예시):**
            ```
            1.png : 여자, 아이, 바이올린, 음표, 꽃, 나무, 바닥, 오선지, 음악, 옷, 노래
            ```
            """
        },
        {
            'role' : 'user',
            'content' : f""" 
            설명 문장 : {description},
            단어 집합 목록 : {card_list}
            """
        }
    ]


    select_response = query_ollama(messages)

    select_response = extract_model_answer(select_response)
        
    selected_card = None

    if select_response is not None:
        file_num = select_response[0]
        for i, card in enumerate(cards):
            if card[0][0] == file_num:
                selected_card = cards[i]

    if selected_card is None:
        selected_card = random.choice(cards)

    key = [k for k, v in turn_cards.items() if v[0] == selected_card]
    

    turn_cards[key[0]][1] += 1

    if key == turn_player :
        turn_cards[now_player][1] += 3

    return turn_cards

image_text_set = image_text

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
            selected_card, description, players = player_turn("Player1", players)
            print(f"당신이 선택한 카드: {selected_card}")
            print(f"설명: {description}")
        else :
            selected_card, description, players = ai_turn(turn_player, players)
            print(f"설명: {description}")

        turn_cards[turn_player] = [selected_card, 0]

        other_players = [p for p in players.keys() if p != turn_player]

        for other in other_players:
            if other == "Player1":
                selected_card, players = player_select_card("Player1", players)

            else :
                selected_card, players = ai_select_card(other, description, players)

            turn_cards[other] = [selected_card, 0]

        for k, v in turn_cards.items():
            print(f"{k} : {v[0][1]}")

        # voting : 함수에서는 가장 유사한 곳에 투표 후, 해당 플레이어가 turn player 면 자신의 voting에 +3
        for other in other_players:
            if other == "Player1":
                turn_cards = player_voting(turn_cards, turn_player, other)
            else : 
                turn_cards = ai_voting(turn_cards, turn_player, other, description)

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

