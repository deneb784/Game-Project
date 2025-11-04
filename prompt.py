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
#     #  (".png", ""),
# }

image_text = {
    ("1.png", "여자, 아이, 바이올린, 음표, 꽃, 나무, 바닥, 오선지, 음악, 옷, 노래"),
    ("2.png", "여자, 노파, 백발, 앞치마, 꽃, 아이, 머리, 빨강, 화분"),
    ("3.png", "용, 기사, 칼 , 아이, 파랑, 싸움, 날개"),
    ("4.png", "비누, 방울, 무지개, 산, 행성, 꽃, 언덕, 들판, 아이, 여행, 밤"),
    ("5.png", "하늘, 망치, 조각, 예술, 새, 나비, 구름, 사다리, 남자"),
    ("6.png", "책, 요정, 빛, 난쟁이, 밤, 공부"),
    ("7.png", "바벨탑, 천국의 계단, 구름, 계단, 숲, 달팽이, 하늘, 구름, 신"),
    ("8.png", "풀, 파리지옥, 식충식물, 남자, 사람, 씨앗, 밭, 노을"),
    ("9.png", "행성, 꼬치, 장난감, 주판, 밤, 별, 목성, 태양"),
    ("10.png", "그림자, 세이렌, 토끼, 조명, 연극, 문, 방, 이상한 나라의 앨리스, 물고기"),
    ("11.png", "가방, 망토, 괴물, 책, 물건, 물, 삼키다"),
    ("12.png", "선물, 상자, 포장, 남자, 여자, 아이, 둘, 끈, 박스"),
    ("13.png", "여자, 치마, 새장, 물고기, 그물, 어항, 머리, 바다"),
    ("14.png", "가면, 얼굴, 화남, 슬픔, 웃음, 감정"),
    ("15.png", "허수아비, 밀짚모자, 지팡이, 왕, 넥타이, 해바라기, 밭, 들판"),
    ("16.png", "자유의 여신상, 촛불, 횃불, 손, 바다, 사람, 투모로우, 지구온난화"),
    ("17.png", "음식, 식탁, 닭, 닭다리, 바베큐, 바나나, 칼, 식탁보, 만찬, 난장판"),
    ("18.png", "가을, 단풍, 체스, 조명, 격자, 남녀, 소개팅, 만남, 대회"),
    ("19.png", "행성, 남자, 노인, 의자, 음악, 트럼펫, 홀스트"),
    ("20.png", "세이렌, 여자, 노을, 바다, 거인, 걸리버 여행기, 배, 범선, 여행, 섬, 여신"),
    ("21.png", "망토, 비밀, 조직, 눈, 일루미나티, 집, 귀신, 모임"),
    ("22.png", "개, 신사, 기팡이, 강아지, 동물, 안경, 양복, 시계"),
    ("23.png", "딸기, 여자, 임신, 난쟁이, 쿠션, 컵, 과일"),
    ("24.png", "비, 우산, 아빠, 딸, 돌, 길, 화살"),
    ("25.png", "여자, 모자, 문신, 등, 수련, 지도, 가로등, 숲, 나비, 가부좌, 명상"),
    ("26.png", "하늘, 섬, 공중, 구름, 종이, 식물, 물뿌리개, 남자, 여자, 아이"),
    ("27.png", "쥐, 종이, 배, 종이배, 남자, 아이, 모자, 학사모, 물"),
    ("28.png", "뼈, 화석, 공룡, 괴물, 두개골, 거대, 발굴"),
    ("29.png", "여자, 귀신, 생머리, 아이, 악령, 영혼, 락, 밴드, 기타"),
    ("30.png", "도시, 위, 물, 바다, 워터월드, 보트, 표류, 청년, 꽃"),
    ("31.png", "오징어, 영국, 신사, 중절모, 넥타이, 콧수염, 포스터, 커피, 흑백"),
    ("32.png", "잉크, 생물, 세포, 생명과학, 종이, 논문, 책상, 책"),
    ("33.png", "달팽이, 거미줄, 나뭇잎, 울타리, 집, 마을, 물방울, 버섯, 애벌레"),
    ("34.png", "연, 나무, 가족, 주말, 공원, 여행, 피크닉, 돗자리, 부모"),
    ("35.png", "구름, 소라, 빵, 헤일로, 코코넛, 문양, 상형문자, 번개"),
    ("36.png", "수박, 털실, 씨, 뜨개질, 늑대, 그림자, 손, 발톱, 조명"),
    ("37.png", "고양이, 점성술, 스노우볼, 어항, 금붕어, 별, 예언, 마녀"),
    ("38.png", "거미줄, 마루, 슈즈, 발레, 신발, 끈, 신발끈, 무용, 귀신"),
    ("39.png", "워터월드, 표류, 상어, 폭풍, 항해, 조난, 음악가"),
    ("40.png", "도깨비, 발자국, 들판, 조사, 괴물, 고대, 화석, 위험"),
    ("41.png", "바다, 침대, 공주, 용왕, 물고기, 해파리, 공기, 방울, 용궁"),
    ("42.png", "업, 성, 열기구, 하늘, 하울의 움직이는 성, 이동"),
    ("43.png", "물방울, 섬, 무인도, 들판, 꽃, 비, 빗방울"),
    ("44.png", "회전목마, 노을, 놀이공원, 괴물, 공룡, 태엽, 오르골, 아이들"),
    ("45.png", "거인, 진격의 거인, 배낭, 집, 괴물, 도시, 먹다, 삼키다"),
    ("46.png", "늑대, 양, 마리오네트, 흰색, 빨강, 연극, 행복"),
    ("47.png", "모래시계, 아이, 할머니, 시간, 모래, 책상"),
    ("48.png", "토끼, 기사, 문, 3개, 칼, 투구, 갑옷, 칼 "),
    ("49.png", "원숭이, 충치, 꽹과리, 인형, 메이드, 잠옷, 저주"),
    ("50.png", "뱀, 메두사, 과학자, 실험, 발표, 약품, 머리, 3개"),
    ("51.png", "얼음, 과일, 괴물, 고대, 탐험가, 광대, 남극"),
    ("52.png", "가면, 새, 나무, 풀, 열매, 보따리, 무도회"),
    ("53.png", "돋보기, 나무, 마을, 집, 개미, 난쟁이, 걸리버 여행기"),
    ("54.png", "사제, 바이올린, 괴물, 황금, 토벌, 마법사, 음악, 정신, 음표"),
    ("55.png", "감옥, 환자, 독방, 침대, 죄수, 철창, 범죄"),
    ("56.png", "곰, 인형, 여자, 아이, 흑인, 눈물, 청진지, 병, 마음, 상처"),
    ("57.png", "우비, 무지개, 파도, 폭풍, 키, 배, 항해, 탐험, 아이"),
    ("58.png", "풍선, 껌, 남자, 낮잠, 휴식, 들판, 풀밭, 하늘, 여유"),
    ("59.png", "도깨비, 아저씨, 나무, 숲, 동굴, 아이, 납치, 유혹"),
    ("60.png", "심장, 망치, 강철, 주조, 용광로, 제철소, 여자, 이별, 다짐"),
    ("61.png", "노파, 마녀, 망토, 오렌지, 행성, 태양, 예언, 점성술"),
    ("62.png", "낚시, 물고기, 아이, 모자, 바늘, 니모, 하늘, 헤엄"),
    ("63.png", "여자, 흑인, 임신, 아이, 마루, 그림자, 엄마"),
    ("64.png", "태양, 우산, 양산, 나그네, 햇살, 더위, 덥다"),
    ("65.png", "연극, 노파, 아이, 무대, 막, 앞치마, 이야기"),
    ("66.png", "문어, 괴물, 사이보그, 로봇, 조명, 잠수함, 무기, 전투"),
    ("67.png", "외줄타기, 달, 서커스, 도시, ET, 자전거"),
    ("68.png", "개구리, 공주, 모자, 왕비, 우산, 햇살, 비, 웅덩이, 의자, 앉다"),
    ("69.png", "공주, 배우, 여자, 빨강, 드레스, 그림, 명화, 화가, 마리오네트, 조종하다"),
    ("70.png", "가면, 여자, 본성, 성악설, 가죽, 위장, 철창, 인격, 인성, 드러내다"),
    ("71.png", "남매, 아이, 남자, 여자, 늑대, 그림자, 헨젤과 그레텔"),
    ("72.png", "노을, 가을, 노인, 지팡이, 낙엽, 나무, 은행잎, 산, 외로움, 걷다"),
    ("73.png", "행성, 나무, 나무꾼, 도끼, 새, 구름, 베다, 열매"),
    ("74.png", "칼, 피리, 여자, 여행, 가방, 나들이, 산, 들판, 이기어검"),
    ("75.png", "달팽이, 풍차, 집, 들판, 기어가다, 바람"),
    ("76.png", "도시, 호수, 겨울, 하늘, 유리, 깨지다, 천장"),
    ("77.png", "토끼, 숲, 나무, 음악, 화살, 사냥꾼"),
    ("78.png", "손, 지구, 지구본, 신, 헤일로, 환경, 전지전능"),
    ("79.png", "새, 양탄자, 용, 독수리, 날다, 원주민, 인디언, 올가미, 알라딘"),
    ("80.png", "유리, 물병, 비, 빗방울, 물, 풍경, 스노우볼"),
    ("81.png", "숲, 나무, 공포, 의자, 레이스, 외로움"),
    ("82.png", "손금, 수맥, 물, 돋보기, 흐름, 운명"),
    ("83.png", "까마귀, 모래, 모래사장, 해변, 모래성, 남자, 선탠, 휴가, 여름"),
    ("84.png", "가면, 경극, 중국, 여인, 상형문자, 카드, 운명"),
    ("85.png", "방석, 만년필, 양탄자, 비행, 가격표, 새, 날다"),
    ("86.png", "유니콘, 백마, 무지개, 다리, 넘다, 절벽"),
    ("87.png", "괴물, 요정, 물고기, 이빨, 육식, 공룡"),
    ("89.png", "촛불, 촛농, 밤, 양초, 분위기"),
    ("90.png", "그릇, 눈, 지켜보다, 사냥감, 감시, 포크, 접시"),
    ("92.png", "우산, 낙하산, 여자, 비, 밤, 달, 날다"),
    ("93.png", "새, 역전, 날다, 하늘, 땅, 뒤집히다, 참새"),
    ("94.png", "열기구, 탄산, 샴페인, 도시, 하늘, 터지다"),
    ("95.png", "달, 여자, 아이, 계단, 포옹, 따뜻함"),
    ("96.png", "여자, 남자, 얼굴, 착시, 갈매기, 중절모, 새장, 바다"),
    ("97.png", "나무, 꽃, 마지막 잎새, 들판, 돌, 길"),
    ("98.png", "알, 깨다, 사람, 박혁거세, 예술, 태초, 탄생, 인간"),
    ("100.png", "사슴, 머리, 박제, 고양이, 벽, 액자, 방, 보다"),
    ("101.png", "시계, 우주, 시간, 바늘, 없음, 무한"),
    ("102.png", "도미노, 난쟁이, 어둠, 세우다, 무너지다"),
    ("103.png", "칼, 덩굴, 풀, 자르다, 묶다"),
    ("104.png", "깃털, 저울, 황금, 무게, 가격, 가치"),
    ("105.png", "꼭두각시, 마리오네트, 의자, 목각인형"),
    ("106.png", "까마귀, 밤, 낮, 들판, 풍경, 달, 별, 은하수, 견우와 직녀"),
    ("107.png", "촛불, 양초, 촛농, 꺼지다, 비교"),
    ("108.png", "물고기, 금붕어, 무리, 불꽃, 헤엄치다"),

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