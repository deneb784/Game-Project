from dotenv import load_dotenv
import os
import prompt
import gradio as gr

load_dotenv()

pod_id = os.getenv("POD_ID")

image_text_set = {f"Card{i}" for i in range(30)} # 기존 'prompt.image_text' 대체
players = {f"Player{i+1}": set() for i in range(5)}
turn_number = 1
total_scores = {key: 0 for key in players.keys()}
turn_cards = {}
description = ""
current_turn_index = 0
player_keys = list(players.keys())

# 초기 카드 분배
for _ in range(3):
    for i in range(5):
        if not image_text_set:
            break
        card = image_text_set.pop()
        players[f"Player{i+1}"].add(card)

def update_game_state(log_message):
    """현재 점수와 로그 메시지를 결합하여 반환합니다."""
    score_text = "\n".join([f"{p}: {s}" for p, s in total_scores.items()])
    return score_text, log_message

def run_game_step(selected_card, input_description, voted_card):

    global turn_number, current_turn_index, players, total_scores, turn_cards, description, image_text_set

    # 게임 종료 조건 확인 (루프 종료 역할)
    if any(score >= 30 for score in total_scores.values()):
        return update_game_state("게임 종료! 최종 점수: " + str(total_scores))

    log = []
    
    # 턴 시작
    turn_player = player_keys[current_turn_index % len(player_keys)]
    
    # --- 1. 카드 선택 및 설명 단계 ---
    log.append(f"\n--- 턴 {turn_number}, 이야기꾼: {turn_player} ---")

