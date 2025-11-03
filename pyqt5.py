import sys
import os
import re
import random
from dotenv import load_dotenv
import ollama

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QScrollArea, QGridLayout, 
    QMessageBox, QTextEdit, QFrame
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QRunnable, QThreadPool, QSize

# --- .env 및 환경 변수 로드 ---
load_dotenv()
POD_ID = os.getenv("POD_ID")
if not POD_ID:
    print("오류: .env 파일에 POD_ID가 설정되지 않았습니다.")
    sys.exit(1)

RUNPOD_OLLAMA_URL = f"https://{POD_ID}-11434.proxy.runpod.net"

# --- 이미지 및 키워드 데이터 ---
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

# --- 스레드 작업자 클래스 ---

class WorkerSignals(QObject):
    """
    작업자 스레드의 시그널 정의
    finished: 작업 완료 시 결과(객체)를 방출
    error: 오류 발생 시 (오류 메시지)를 방출
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class Worker(QRunnable):
    """
    QThreadPool에서 실행될 작업자
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

# --- 클릭 가능한 카드 위젯 ---

class ClickableCard(QLabel):
    """
    클릭 시 시그널을 방출하며, 263x383 비율을 유지하는 커스텀 QLabel
    """
    clicked = pyqtSignal(object) # card_data를 방출

    def __init__(self, card_data, size=150, parent=None):
        super(ClickableCard, self).__init__(parent)
        self.card_data = card_data # ("1.png", "키워드...")
        self.image_path = os.path.join("images", self.card_data[0])
        
        # --- 수정된 비율 계산 로직 ---
        # 원본 이미지 비율: 너비 263, 높이 383
        CARD_WIDTH_RATIO = 263
        CARD_HEIGHT_RATIO = 383
        
        # 'size'를 새로운 너비(new_width)로 사용
        new_width = size
        # 새로운 높이는 비율(383/263)에 맞춰 계산
        new_height = int(new_width * (CARD_HEIGHT_RATIO / CARD_WIDTH_RATIO))
        
        self.setFixedSize(new_width, new_height)
        # --- 수정된 비율 계산 로직 끝 ---
        
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            
            # 픽스맵 스케일링 시, 계산된 new_width와 new_height 사용
            self.setPixmap(pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.setText(f"이미지 없음\n{self.card_data[0]}")
            self.setStyleSheet("border: 1px solid red;")
            
        self.setScaledContents(False)
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
        self.normal_style = f"border: 1px solid black; background-color: white;"
        self.selected_style = f"border: 3px solid blue; background-color: lightblue;"
        self.setStyleSheet(self.normal_style)

    def mousePressEvent(self, event):
        self.clicked.emit(self.card_data)

    def set_selected(self, selected):
        if selected:
            self.setStyleSheet(self.selected_style)
        else:
            self.setStyleSheet(self.normal_style)

# --- 메인 게임 윈도우 ---

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dixit 스타일 AI 게임")
        self.setGeometry(100, 100, 1200, 900)

        # Ollama 클라이언트 초기화
        try:
            self.ollama_client = ollama.Client(host=RUNPOD_OLLAMA_URL)
            # 클라이언트 테스트
            self.ollama_client.list() 
        except Exception as e:
            QMessageBox.critical(self, "Ollama 연결 오류", f"Ollama 호스트({RUNPOD_OLLAMA_URL})에 연결할 수 없습니다. .env 파일과 RunPod 상태를 확인하세요.\n오류: {e}")
            sys.exit(1)

        self.threadpool = QThreadPool()
        self.init_ui()
        self.init_game_state()
        self.start_new_game()

    def init_ui(self):
        """UI의 기본 레이아웃을 설정합니다."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 1. 스코어보드
        self.scoreboard_layout = QHBoxLayout()
        main_layout.addLayout(self.scoreboard_layout)
        
        # 2. 게임 상태 및 로그
        status_layout = QHBoxLayout()
        self.status_label = QLabel("게임을 시작합니다...")
        self.status_label.setFont(QFont("Arial", 14, QFont.Bold))
        status_layout.addWidget(self.status_label)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFixedHeight(150)
        
        status_vlayout = QVBoxLayout()
        status_vlayout.addWidget(self.status_label)
        status_vlayout.addWidget(self.log_display)
        main_layout.addLayout(status_vlayout)

        # 3. 테이블 (제출된 카드)
        self.table_label = QLabel("테이블")
        self.table_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(self.table_label)
        
        self.table_scroll = QScrollArea()
        self.table_scroll.setWidgetResizable(True)
        self.table_widget = QWidget()
        self.table_layout = QHBoxLayout(self.table_widget)
        self.table_layout.setAlignment(Qt.AlignCenter)
        self.table_scroll.setWidget(self.table_widget)
        self.table_scroll.setMinimumHeight(220)
        main_layout.addWidget(self.table_scroll)

        # 4. 플레이어1 입력 영역 (설명)
        self.description_input_layout = QHBoxLayout()
        self.description_label = QLabel("설명:")
        self.description_input = QLineEdit()
        self.description_submit_btn = QPushButton("설명 제출")
        self.description_submit_btn.clicked.connect(self.on_player1_description_submit)
        self.description_input_layout.addWidget(self.description_label)
        self.description_input_layout.addWidget(self.description_input)
        self.description_input_layout.addWidget(self.description_submit_btn)
        self.set_description_input_enabled(False) # 처음엔 비활성화
        main_layout.addLayout(self.description_input_layout)

        # 5. 플레이어1 손
        self.hand_label = QLabel("당신의 손 (Player1)")
        self.hand_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(self.hand_label)
        
        self.hand_scroll = QScrollArea()
        self.hand_scroll.setWidgetResizable(True)
        self.hand_widget = QWidget()
        self.hand_layout = QHBoxLayout(self.hand_widget)
        self.hand_layout.setAlignment(Qt.AlignCenter)
        self.hand_scroll.setWidget(self.hand_widget)
        self.hand_scroll.setMinimumHeight(220)
        main_layout.addWidget(self.hand_scroll)

    def init_game_state(self):
        """게임에 필요한 변수들을 초기화합니다."""
        self.image_text_set = set(image_text)
        self.players = {f"Player{i+1}": set() for i in range(5)}
        self.total_scores = {key: 0 for key in self.players.keys()}
        self.player_order = list(self.players.keys())
        self.current_turn_index = -1
        self.turn_number = 0

        # 라운드별 변수
        self.game_state = "IDLE" # "P1_TURN_CHOOSE", "AWAITING_SUBMISSIONS", "AWAITING_VOTES", "ROUND_END"
        self.turn_player = ""
        self.current_description = ""
        self.turn_cards = {} # { "Player1": [card_data, vote_count], ... }
        self.player_votes = {} # { "Player2": "Player1" (voted for P1), ... }
        self.p1_selected_card_for_turn = None
        self.submitted_card_widgets = {} # { "Player1": ClickableCard, ... }
        
        # AI 응답 매핑용 (투표 시 카드 -> 플레이어)
        self.vote_card_to_player_map = {}

    def start_new_game(self):
        self.log("새 게임을 시작합니다.")
        # 3장씩 카드 분배
        for _ in range(3):
            for player_key in self.players:
                if not self.image_text_set:
                    self.log("오류: 덱에 카드가 부족합니다.")
                    return
                self.players[player_key].add(self.image_text_set.pop())
        
        self.update_scoreboard_ui()
        self.display_player1_hand()
        
        self.current_turn_index = -1
        self.start_next_turn()

    def log(self, message):
        """게임 로그에 메시지를 추가합니다."""
        self.log_display.append(message)
        QApplication.processEvents() # UI가 즉시 업데이트되도록 함

    # --- UI 업데이트 함수 ---

    def update_scoreboard_ui(self):
        """스코어보드 UI를 현재 점수로 업데이트합니다."""
        # 레이아웃 비우기
        while self.scoreboard_layout.count():
            child = self.scoreboard_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        for player, score in self.total_scores.items():
            label = QLabel(f"{player}: {score}점")
            label.setFont(QFont("Arial", 12, QFont.Bold if player == "Player1" else QFont.Normal))
            label.setStyleSheet("border: 1px solid #ccc; padding: 5px; border-radius: 5px;")
            self.scoreboard_layout.addWidget(label)

    def display_player1_hand(self):
        """Player1의 손에 있는 카드를 UI에 표시합니다."""
        # 레이아웃 비우기
        while self.hand_layout.count():
            child = self.hand_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for card_data in self.players["Player1"]:
            card_widget = ClickableCard(card_data, size=180)
            card_widget.clicked.connect(self.on_player1_hand_card_clicked)
            self.hand_layout.addWidget(card_widget)
        
        # 선택된 카드 표시 초기화
        self.p1_selected_card_for_turn = None

    def display_table_cards(self):
        """테이블(제출된 카드) UI를 표시합니다."""
        self.submitted_card_widgets = {}
        self.vote_card_to_player_map = {}
        
        # 레이아웃 비우기
        while self.table_layout.count():
            child = self.table_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.status_label.setText(f"설명: \"{self.current_description}\" | 투표하세요!")
        
        # 카드를 섞어서 표시
        shuffled_players = list(self.turn_cards.keys())
        random.shuffle(shuffled_players)
        
        # Player1이 투표자인지 (즉, 턴 플레이어가 아닌지) 확인
        is_p1_voting = (self.turn_player != "Player1")
        
        for player_key in shuffled_players:
            card_data = self.turn_cards[player_key][0]
            card_widget = ClickableCard(card_data, size=180)
            
            # 맵핑: 카드 데이터 -> 플레이어 키
            self.vote_card_to_player_map[card_data] = player_key 
            
            # --- 수정된 로직 ---
            if is_p1_voting:
                # P1이 투표자일 경우
                if player_key == "Player1":
                    # P1 자신의 카드: 클릭 비활성화 (스타일만 적용)
                    card_widget.setStyleSheet("border: 2px solid gray; background-color: #eee;")
                else:
                    # P1이 투표할 다른 카드: 클릭 연결
                    card_widget.clicked.connect(self.on_table_card_clicked)
            else:
                # P1이 턴 플레이어일 경우 (투표 안 함)
                # 어떤 카드에도 클릭 이벤트를 연결하지 않습니다.
                pass 
            # --- 수정된 로직 끝 ---

            self.table_layout.addWidget(card_widget)
            self.submitted_card_widgets[player_key] = card_widget

    def clear_ui_for_new_turn(self):
        """새 턴을 위해 테이블과 입력창을 초기화합니다."""
        while self.table_layout.count():
            child = self.table_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.set_description_input_enabled(False)
        self.description_input.clear()
        self.status_label.setText("")
        self.p1_selected_card_for_turn = None
        # 손에 있는 카드들 선택 해제
        for i in range(self.hand_layout.count()):
            widget = self.hand_layout.itemAt(i).widget()
            if isinstance(widget, ClickableCard):
                widget.set_selected(False)

    def set_description_input_enabled(self, enabled):
        """설명 입력 UI 활성화/비활성화"""
        self.description_label.setEnabled(enabled)
        self.description_input.setEnabled(enabled)
        self.description_submit_btn.setEnabled(enabled)

    # --- 게임 로직: 턴 진행 ---

    def start_next_turn(self):
        """다음 플레이어의 턴을 시작합니다."""
        self.game_state = "PROCESSING" # 턴 처리 중 다른 입력 방지
        self.clear_ui_for_new_turn()
        
        # 턴 인덱스 및 플레이어 업데이트
        self.current_turn_index = (self.current_turn_index + 1) % len(self.player_order)
        self.turn_player = self.player_order[self.current_turn_index]
        self.turn_number += 1
        
        # 라운드 변수 초기화
        self.turn_cards = {}
        self.player_votes = {}
        self.current_description = ""
        
        self.log(f"\n--- 턴 {self.turn_number} ({self.turn_player}의 차례) ---")
        
        if self.turn_player == "Player1":
            self.prompt_player1_turn()
        else:
            self.run_ai_turn(self.turn_player)

    def prompt_player1_turn(self):
        """Player1이 턴 플레이어일 때 UI를 설정합니다."""
        self.game_state = "P1_TURN_CHOOSE"
        self.status_label.setText("당신의 턴입니다. 카드를 선택하고 설명을 입력하세요.")
        self.set_description_input_enabled(True)
        self.display_player1_hand() # 카드 선택 초기화

    def on_player1_hand_card_clicked(self, card_data):
        """Player1의 손에 있는 카드가 클릭되었을 때의 로직"""
        
        # P1이 턴 플레이어일 때: 설명할 카드 선택
        if self.game_state == "P1_TURN_CHOOSE":
            self.p1_selected_card_for_turn = card_data
            # 모든 카드를 선택 해제
            for i in range(self.hand_layout.count()):
                widget = self.hand_layout.itemAt(i).widget()
                if isinstance(widget, ClickableCard):
                    widget.set_selected(widget.card_data == card_data)
            self.log(f"선택한 카드: {card_data[0]}")

        # 다른 플레이어의 턴일 때: 설명에 맞는 카드 제출
        elif self.game_state == "AWAITING_SUBMISSIONS":
            if "Player1" in self.turn_cards:
                self.log("이미 카드를 제출했습니다.")
                return
                
            self.log(f"Player1이 {card_data[0]} 카드를 제출합니다.")
            self.players["Player1"].remove(card_data)
            self.turn_cards["Player1"] = [card_data, 0] # [카드, 투표 수]
            self.display_player1_hand() # UI에서 카드 제거
            
            # 모든 카드가 제출되었는지 확인
            self.check_all_cards_submitted()

    def on_player1_description_submit(self):
        """Player1이 '설명 제출' 버튼을 눌렀을 때"""
        if self.game_state != "P1_TURN_CHOOSE":
            return
            
        description = self.description_input.text().strip()
        
        if not self.p1_selected_card_for_turn:
            QMessageBox.warning(self, "카드 미선택", "먼저 설명할 카드를 선택하세요.")
            return
        if not description:
            QMessageBox.warning(self, "설명 없음", "카드에 대한 설명을 입력하세요.")
            return
            
        self.log(f"당신이 선택한 카드: {self.p1_selected_card_for_turn[0]}")
        self.log(f"입력한 설명: {description}")

        self.current_description = description
        
        # 선택한 카드 손에서 제거 및 턴 카드에 추가
        self.players["Player1"].remove(self.p1_selected_card_for_turn)
        self.turn_cards[self.turn_player] = [self.p1_selected_card_for_turn, 0]
        
        self.display_player1_hand() # UI 업데이트
        self.set_description_input_enabled(False) # 입력창 비활성화
        
        # 다음 단계(다른 플레이어 카드 제출)로 이동
        self.start_submission_phase()

    def run_ai_turn(self, player_key):
        """AI가 턴 플레이어일 때 스레드에서 AI 로직을 실행합니다."""
        self.game_state = "PROCESSING"
        self.status_label.setText(f"{player_key}가 생각 중입니다...")
        
        if not self.players[player_key]:
            self.log(f"오류: {player_key}의 손에 카드가 없습니다.")
            self.start_submission_phase() # 그냥 넘어감
            return

        # AI가 카드 선택 및 설명 생성
        selected_card = self.players[player_key].pop()
        
        worker = Worker(self.generate_ai_description, selected_card[1])
        worker.signals.finished.connect(
            lambda desc: self.on_ai_turn_complete(player_key, selected_card, desc)
        )
        worker.signals.error.connect(self.on_ai_error)
        self.threadpool.start(worker)

    def on_ai_turn_complete(self, player_key, selected_card, description):
        """AI 턴 플레이어의 설명 생성이 완료되었을 때"""
        self.log(f"{player_key}가 카드({selected_card[0]})를 선택했습니다.")
        self.log(f"{player_key}의 설명: \"{description}\"")
        
        self.current_description = description
        self.turn_cards[player_key] = [selected_card, 0] # [카드, 투표 수]
        
        # 다음 단계(다른 플레이어 카드 제출)로 이동
        self.start_submission_phase()

    # --- 게임 로직: 카드 제출 ---

    def start_submission_phase(self):
        """턴 플레이어를 제외한 모든 플레이어가 카드를 제출하는 단계를 시작합니다."""
        self.game_state = "AWAITING_SUBMISSIONS"
        self.status_label.setText(f"설명: \"{self.current_description}\" | 카드 제출 대기 중...")
        
        other_players = [p for p in self.players.keys() if p != self.turn_player]
        
        for player_key in other_players:
            if player_key == "Player1":
                # Player1은 UI를 통해 직접 선택
                self.log("당신의 차례: 설명에 가장 잘 맞는 카드를 손에서 선택하세요.")
                # 손에 있는 카드들 선택 가능하게 (스타일 초기화)
                for i in range(self.hand_layout.count()):
                    widget = self.hand_layout.itemAt(i).widget()
                    if isinstance(widget, ClickableCard):
                        widget.set_selected(False)
            else:
                # AI는 스레드에서 카드 선택
                self.run_ai_card_selection(player_key, self.current_description)

    def run_ai_card_selection(self, player_key, description):
        """AI가 설명에 맞는 카드를 스레드에서 선택합니다."""
        user_cards = self.players[player_key]
        if not user_cards:
            self.log(f"오류: {player_key}가 제출할 카드가 없습니다.")
            self.check_all_cards_submitted() # 강제로 다음 단계로
            return

        self.log(f"{player_key}가 설명에 맞는 카드를 고르는 중...")
        
        worker = Worker(self.select_similar_card, user_cards, description)
        worker.signals.finished.connect(
            lambda result: self.on_ai_card_selected(player_key, result[0]) # result[0] = selected_card
        )
        worker.signals.error.connect(self.on_ai_error)
        self.threadpool.start(worker)

    def on_ai_card_selected(self, player_key, selected_card):
        """AI가 카드 선택을 완료했을 때"""
        if selected_card not in self.players[player_key]:
            # AI가 반환한 카드가 없거나 이상할 경우, 랜덤 카드 선택
            if not self.players[player_key]:
                self.log(f"오류: {player_key}가 제출할 카드가 없습니다. (AI 반환 오류)")
                self.check_all_cards_submitted()
                return
            selected_card = self.players[player_key].pop()
            self.log(f"{player_key}가 AI 오류로 랜덤 카드를 제출합니다: {selected_card[0]}")
        else:
            self.players[player_key].remove(selected_card)
            self.log(f"{player_key}가 카드를 제출했습니다: {selected_card[0]}")

        self.turn_cards[player_key] = [selected_card, 0]
        self.check_all_cards_submitted()

    def check_all_cards_submitted(self):
        """모든 플레이어가 카드를 제출했는지 확인합니다."""
        if len(self.turn_cards) == len(self.players):
            self.log("모든 플레이어가 카드를 제출했습니다. 투표를 시작합니다.")
            self.start_voting_phase()

    # --- 게임 로직: 투표 ---

    def start_voting_phase(self):
        """모든 플레이어가 투표하는 단계를 시작합니다."""
        self.game_state = "AWAITING_VOTES"
        self.player_votes = {} # 투표 기록 초기화
        self.display_table_cards() # 섞인 카드들을 테이블에 표시
        
        voting_players = [p for p in self.players.keys() if p != self.turn_player]
        
        for player_key in voting_players:
            if player_key == "Player1":
                self.log("당신의 차례: 턴 플레이어의 카드를 맞춰보세요! (자신의 카드는 선택 불가)")
                # P1은 UI 클릭으로 투표 (on_table_card_clicked)
            else:
                self.run_ai_voting(player_key, self.current_description)

    def on_table_card_clicked(self, card_data):
        """Player1이 테이블의 카드를 클릭(투표)했을 때"""
        if self.game_state != "AWAITING_VOTES":
            return
        if "Player1" in self.player_votes:
            self.log("이미 투표했습니다.")
            return

        # 맵에서 클릭된 카드의 원 주인(player_key)을 찾음
        voted_player_key = self.vote_card_to_player_map.get(card_data)
        
        if not voted_player_key:
            self.log("오류: 투표한 카드의 주인을 찾을 수 없습니다.")
            return

        if voted_player_key == "Player1":
            self.log("자신의 카드에는 투표할 수 없습니다.")
            return
            
        self.log(f"Player1이 {voted_player_key}의 카드에 투표했습니다.")
        self.player_votes["Player1"] = voted_player_key # 투표 기록
        
        # 투표한 카드 하이라이트
        widget = self.sender()
        if isinstance(widget, ClickableCard):
            widget.set_selected(True)
        
        self.check_all_votes_cast()

    def run_ai_voting(self, voter_key, description):
        """AI가 투표할 카드를 스레드에서 선택합니다."""
        self.log(f"{voter_key}가 투표할 카드를 고르는 중...")
        
        # AI가 투표할 수 있는 카드 목록 (자신 제외)
        # (카드 데이터, 원 주인) 튜플의 리스트
        votable_cards = []
        for player_key, (card_data, _) in self.turn_cards.items():
            if player_key != voter_key:
                votable_cards.append((card_data, player_key))

        if not votable_cards:
            self.log(f"오류: {voter_key}가 투표할 카드가 없습니다.")
            self.check_all_votes_cast()
            return

        worker = Worker(self.ai_vote_logic, votable_cards, description, voter_key)
        worker.signals.finished.connect(self.on_ai_vote_complete)
        worker.signals.error.connect(self.on_ai_error)
        self.threadpool.start(worker)
        
    def ai_vote_logic(self, votable_cards, description, voter_key):
        """AI가 투표할 카드를 고르는 실제 로직 (스레드에서 실행됨)"""
        # votable_cards = [(card_data, owner_key), ...]
        
        # 프롬프트에 넣을 카드 목록 생성
        card_list_prompt = ""
        # AI가 선택한 카드(파일명)와 실제 주인(player_key)을 매핑
        filename_to_owner_map = {}
        
        for card_data, owner_key in votable_cards:
            filename = card_data[0]
            keywords = card_data[1]
            card_list_prompt += f"{filename} : [{keywords}]\n"
            filename_to_owner_map[filename] = owner_key

        messages = [
            {
                "role": "system",
                "content": """
                너는 게임 문제를 맞추는 전문 분류기(Classifier)야.
                '설명 문장'에 **가장 의미론적으로 잘 맞는** 단어 집합 하나를 '단어 집합 목록'에서 **선택**해야 해.
                
                ### 제약 조건 및 출력 형식 ###
                1. **반드시 방금 받은 '단어 집합 목록' 내에서만 선택해야 해.**
                2. **다른 문장, 설명, 주석 없이 오직 선택된 집합의 파일 이름과 그 내용만** 반환해야 해.
                3. **출력의 첫 글자는 무조건 선택된 집합의 파일 이름(예: 1.png)이 되어야 해.**
                4. 출력 형식은 다음과 같아:
                `[선택된 집합의 파일 이름] : [선택된 집합의 단어 내용 전체]`
                """
            },
            {
                'role' : 'user',
                'content' : f""" 
                설명 문장 : {description},
                단어 집합 목록 : {card_list_prompt}
                """
            }
        ]
        
        select_response_raw = self.query_ollama(messages)
        select_response = self.extract_model_answer(select_response_raw)
        
        voted_owner_key = None
        if select_response:
            # "1.png : [단어...]" 형식에서 "1.png" 추출
            match = re.match(r'^\s*([\w\.-]+)', select_response)
            if match:
                selected_filename = match.group(1)
                if selected_filename in filename_to_owner_map:
                    voted_owner_key = filename_to_owner_map[selected_filename]

        # AI가 이상한 답을 주거나, 자신을 뽑으려 한 경우 (votable_cards에 자신은 없음)
        if voted_owner_key is None:
            # 랜덤 투표
            voted_owner_key = random.choice(list(filename_to_owner_map.values()))
            
        return (voter_key, voted_owner_key) # (투표한 AI, 투표받은 플레이어)

    def on_ai_vote_complete(self, result):
        """AI의 투표가 완료되었을 때"""
        voter_key, voted_player_key = result
        
        if voted_player_key:
            self.log(f"{voter_key}가 {voted_player_key}의 카드에 투표했습니다.")
            self.player_votes[voter_key] = voted_player_key
            
            # AI가 투표한 카드 UI에 표시 (선택 사항)
            if voted_player_key in self.submitted_card_widgets:
                # 간단하게 테두리 색 변경 등으로 표시 가능
                pass 
                
        else:
            self.log(f"오류: {voter_key}의 투표가 잘못되었습니다.")
            # 투표를 안 한 것으로 처리
            
        self.check_all_votes_cast()

    def check_all_votes_cast(self):
        """모든 투표가 완료되었는지 확인합니다."""
        voting_players_count = len(self.players) - 1
        if len(self.player_votes) == voting_players_count:
            self.log("모든 투표가 완료되었습니다. 점수를 계산합니다.")
            self.calculate_scores()
        
    # --- 게임 로직: 점수 계산 및 턴 종료 ---

    def calculate_scores(self):
        """투표 결과에 따라 점수를 계산하고 적용합니다."""
        self.game_state = "PROCESSING"
        
        # 1. 투표 집계 (누가 몇 표 받았는지)
        for voter, voted_player in self.player_votes.items():
            if voted_player in self.turn_cards:
                self.turn_cards[voted_player][1] += 1 # 득표 수 증가

        # 2. 점수 계산
        turn_player_votes = self.turn_cards[self.turn_player][1]
        total_voters = len(self.players) - 1
        
        turn_player_card_widget = self.submitted_card_widgets.get(self.turn_player)
        if turn_player_card_widget:
             # 정답 카드(턴 플레이어 카드) 하이라이트
            turn_player_card_widget.setStyleSheet("border: 4px solid gold; background-color: lightyellow;")

        # 턴 플레이어의 카드에 대한 설명 (키워드) 표시
        for player_key, widget in self.submitted_card_widgets.items():
            card_data, votes = self.turn_cards[player_key]
            label_text = f"{player_key}의 카드 ({votes}표)\n{card_data[0]}"
            # (간단하게) 툴팁으로 키워드 표시
            widget.setToolTip(f"키워드: {card_data[1]}")
            # 또는 위젯을 수정하여 라벨을 추가할 수 있음
        
        # 경우의 수에 따른 점수 부여
        if turn_player_votes == total_voters:
            # 모두가 맞힘
            self.log("모두가 턴 플레이어의 카드를 맞혔습니다! (턴 플레이어 0점)")
            for player_key in self.players:
                if player_key != self.turn_player:
                    self.total_scores[player_key] += 2 # 맞힌 사람
                    self.log(f"{player_key} +2점")
                    
        elif turn_player_votes == 0:
            # 아무도 못 맞힘
            self.log("아무도 턴 플레이어의 카드를 맞히지 못했습니다! (턴 플레이어 0점)")
            for player_key in self.players:
                if player_key != self.turn_player:
                    self.total_scores[player_key] += 2 # 다른 모든 사람
                    self.log(f"{player_key} +2점")
        
        else:
            # 일부만 맞힘
            self.log("일부 플레이어만 맞혔습니다.")
            # 턴 플레이어 점수
            self.total_scores[self.turn_player] += 3
            self.log(f"{self.turn_player} +3점")
            
            # 정답 맞힌 사람들 점수
            for voter, voted_player in self.player_votes.items():
                if voted_player == self.turn_player:
                    self.total_scores[voter] += 3
                    self.log(f"{voter} +3점 (정답)")

        # 3. 추가 점수 (다른 사람을 속인 경우)
        for player_key in self.players:
            if player_key != self.turn_player:
                votes_received = self.turn_cards[player_key][1]
                if votes_received > 0:
                    self.total_scores[player_key] += votes_received
                    self.log(f"{player_key} +{votes_received}점 (유인 성공)")

        self.update_scoreboard_ui()
        self.log(f"현재 총점: {self.total_scores}")
        
        # 3초간 결과 표시 후 다음 턴
        self.game_state = "ROUND_END"
        # QTimer.singleShot(3000, self.end_round) # -> 스레드 문제로 복잡해짐
        
        # 간단하게 버튼으로 대체
        self.next_turn_btn = QPushButton("다음 턴으로")
        self.next_turn_btn.clicked.connect(self.end_round)
        self.table_layout.addWidget(self.next_turn_btn)

    def end_round(self):
        """라운드를 종료하고 다음 턴을 준비합니다."""
        if self.game_state != "ROUND_END": return
        
        # '다음 턴' 버튼 제거
        if hasattr(self, 'next_turn_btn'):
            self.next_turn_btn.deleteLater()
            del self.next_turn_btn

        # 승리 조건 확인
        if any(score >= 30 for score in self.total_scores.values()):
            self.game_over()
            return

        # 덱에서 카드 1장씩 보충
        self.log("각 플레이어에게 카드를 1장씩 보충합니다.")
        for player_key in self.players:
            if not self.image_text_set:
                self.log("덱에 카드가 모두 떨어졌습니다!")
                break
            card = self.image_text_set.pop()
            self.players[player_key].add(card)
        
        self.display_player1_hand() # Player1 손 UI 업데이트
        
        self.start_next_turn()

    def game_over(self):
        """게임 종료 처리"""
        self.game_state = "GAME_OVER"
        winner = max(self.total_scores, key=self.total_scores.get)
        self.log(f"게임 종료! 최종 점수: {self.total_scores}")
        QMessageBox.information(self, "게임 종료", f"승자: {winner}!\n\n최종 점수:\n{self.total_scores}")
        self.status_label.setText(f"게임 종료! 승자: {winner}")
        self.set_description_input_enabled(False)
        # (옵션) 새 게임 시작 버튼 활성화


    # --- AI 모델 호출 및 헬퍼 함수 (원본 코드에서 가져옴) ---
    
    def on_ai_error(self, error_message):
        """AI 스레드에서 오류 발생 시 처리"""
        self.log(f"AI 오류 발생: {error_message}")
        # (필요시) 게임 상태를 안전하게 복구하는 로직 추가
        
    def query_ollama(self, prompt: list, model: str = "EEVE-Korean-10.8B") -> str:
        """
        Ollama 클라이언트를 사용하여 AI 모델에 쿼리합니다.
        (스레드 안전: self.ollama_client는 init에서 생성됨)
        """
        try:
            response = self.ollama_client.chat(
                model=model,
                messages=prompt
            )
            return response['message']['content']
        except Exception as e:
            # 이 함수는 스레드에서 실행되므로, 에러를 다시 raise하여 Worker가 잡도록 함
            raise Exception(f"Ollama 쿼리 중 오류 발생: {e}")

    def generate_ai_description(self, prompt_keywords):
        """AI가 키워드를 보고 추상적인 설명을 생성합니다. (스레드에서 실행됨)"""
        messages = [
            {
                'role' : 'system',
                'content' : """ 
                너는 게임 문제를 내는 사람이야.
                다음 단어들 중 일부와 관련있는 Dixit 스타일의 모호하고 추상적인 한 문장을 만들어줘.
                문장은 짧아야 하고, 중간에 ,는 두개 이상 들어가지 않도록 해.

                단어 예시: 하늘, 망치, 조각, 예술, 새, 나비, 구름, 사다리, 남자
                출력 예시: "조각가의 하늘은 아직 다듬어지지 않은 돌이었다."
                """
            },
            {
                'role' : 'user',
                'content': f""" 
                다음 단어들을 보고 떠오르는 모호하고 추상적인 문장 하나를 만들어줘.
                단어 예시 : {prompt_keywords}
                """
            }
        ]
        description = self.query_ollama(messages)
        # 따옴표 제거
        description = description.strip().replace('"', '')
        return description

    def extract_model_answer(self, model_output: str) -> str:
        """모델의 응답 텍스트에서 정답 문장만 추출합니다."""
        if model_output is None:
            return None
        
        lines = model_output.strip().split('\n')
        
        # 원본 로직: "1. 어쩌고" 형식만 찾음
        answer_pattern_num = re.compile(r'^\s*(\d+\.)\s*.*$', re.MULTILINE)
        # 수정: "1.png : 어쩌고" 형식도 찾음 (AI가 형식을 다르게 줄 수 있으므로)
        answer_pattern_file = re.compile(r'^\s*([\w\.-]+\.png)\s*:.*$', re.MULTILINE | re.IGNORECASE)
        
        for line in lines:
            line_strip = line.strip()
            if answer_pattern_num.match(line_strip) or answer_pattern_file.match(line_strip):
                return line_strip
                
        # 매칭되는 형식이 없으면, 그냥 첫 줄 반환 (AI가 예시와 다른 답을 줄 경우 대비)
        if lines:
            return lines[0].strip()
            
        return None

    def select_similar_card(self, user_cards, description):
        """
        AI가 자신의 카드 중 설명과 가장 유사한 카드를 선택합니다. (스레드에서 실행됨)
        반환: (selected_card 튜플, user_cards 세트) - 원본 함수 시그니처 유지
        """
        cards = list(user_cards)
        if not cards:
            return None, user_cards
            
        card_list = ""
        for card_tuple in cards:
            # card_tuple = ("1.png", "키워드...")
            sent = f"{card_tuple[0]} : [{card_tuple[1]}]\n"
            card_list += sent

        messages = [
            {
                "role": "system",
                "content": """
                너는 게임 문제를 맞추는 전문 분류기(Classifier)야.
                '설명 문장'에 **가장 의미론적으로 잘 맞는** 단어 집합 하나를 '단어 집합 목록'에서 **선택**해야 해.
                
                ### 제약 조건 및 출력 형식 ###
                1. **반드시 방금 받은 '단어 집합 목록' 내에서만 선택해야 해.**
                2. **다른 문장, 설명, 주석 없이 오직 선택된 집합의 파일 이름과 그 내용만** 반환해야 해.
                3. **출력의 첫 글자는 무조건 선택된 집합의 파일 이름(예: 1.png)이 되어야 해.**
                4. 출력 형식은 다음과 같아:
                `[선택된 집합의 파일 이름] : [선택된 집합의 단어 내용 전체]`
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

        select_response_raw = self.query_ollama(messages)
        select_response = self.extract_model_answer(select_response_raw)
        
        selected_card = None
        if select_response:
            # "1.png : [단어...]" 형식에서 "1.png" 추출
            match = re.match(r'^\s*([\w\.-]+)', select_response)
            if match:
                selected_filename = match.group(1)
                for card in cards:
                    if card[0] == selected_filename:
                        selected_card = card
                        break

        if selected_card is None:
            # AI가 답을 못 찾거나 형식이 다르면 랜덤 선택
            selected_card = random.choice(cards)

        # 원본 함수는 (선택된 카드, *수정된* 카드 셋)을 반환했지만,
        # 여기서는 (선택된 카드, *원본* 카드 셋)을 반환하고,
        # 이 함수를 호출한 쪽(on_ai_card_selected)에서 손(players)을 수정합니다.
        return selected_card, user_cards


# --- 애플리케이션 실행 ---

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())