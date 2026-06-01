import tkinter as tk
from tkinter import messagebox
import csv
import threading
import time

from kiosk_ui import KioskApp
# ========================================================= 
# 시리얼 연결 
# =========================================================
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("💡 [시스템 알림] pyserial 라이브러리가 감지되지 않아 가상 모드로 전환합니다.")


# 대한민국 식약처 및 의학 기준 영양소 일일 상한 섭취량 (UL)
# 💡 단백질은 고정값이 아니라 하단에서 사용자의 몸무게를 기반으로 자동 재계산됩니다.
SAFE_LIMITS = {
    "남성": {
        "베타카로틴(mcg)": 7000.0, "비타민A(mcg)": 3000.0, "비타민C(mg)": 2000.0, 
        "비타민D(mcg)": 100.0, "식물성 비타민D2(mcg)": 10000.0, "동물성 비타민D3(mcg)": 100.0, 
        "비타민E(mgα-TE)": 1000.0, "비타민K(mcg)": 120.0, "비타민B1(mg)": 1.2, 
        "비타민B2(mg)": 1.5, "비타민B3(mg)": 35.0, "비타민B6(mg)": 100.0, 
        "비타민B9(mcg DFE)": 1000.0, "비타민B12(mcg)": 500.0, "비타민B7(mcg)": 30.0, 
        "비타민B5(mg)": 10.0, "콜린(mg)": 595.0, "요오드(mcg)": 1100.0, 
        "철분(mg)": 45.0, "아연(mg)": 40.0, "셀레늄(mcg)": 400.0, 
        "구리(mcg)": 10000.0, "망간(mg)": 11.0, "크롬(mcg)": 35.0, 
        "소듐(mg)": 2300.0, "포타슘(mg)": 3500.0, "인(mg)": 4000.0, 
        "D-감마 토코페롤(mg)": 1000.0, "붕소(mg)": 20.0, "몰리브덴(mcg)": 2000.0, 
        "프로바이오틱스(CFU)": 100000000.0, "칼슘(mg)": 2500.0, "EPA + DHA(mg)": 1000.0, 
        "단백질(g)": 100.0, "루테인(mg)": 20.0, "총지아잔틴(mg)": 2.0, 
        "아스타잔틴(mg)": 12.0, "L-류신(mg)": 10000.0, "L-글루타민(mg)": 20000.0, 
        "L-이소류신(mg)": 10000.0, "L-발린(mg)": 5000.0, "마그네슘(mg)": 350.0   
    },
    "여성": {
        "베타카로틴(mcg)": 7000.0, "비타민A(mcg)": 3000.0, "비타민C(mg)": 2000.0, 
        "비타민D(mcg)": 100.0, "식물성 비타민D2(mcg)": 10000.0, "동물성 비타민D3(mcg)": 1.1, 
        "비타민E(mgα-TE)": 540.0, "비타민K(mcg)": 90.0, "비타민B1(mg)": 5.0, 
        "비타민B2(mg)": 1.2, "비타민B3(mg)": 35.0, "비타민B6(mg)": 100.0, 
        "비타민B9(mcg DFE)": 1000.0, "비타민B12(mcg)": 500.0, "비타민B7(mcg)": 30.0, 
        "비타민B5(mg)": 10.0, "콜린(mg)": 425.0, "요오드(mcg)": 1100.0, 
        "철분(mg)": 45.0, "아연(mg)": 40.0, "셀레늄(mcg)": 400.0, 
        "구리(mcg)": 10000.0, "망간(mg)": 11.0, "크롬(mcg)": 25.0, 
        "소듐(mg)": 2300.0, "포타슘(mg)": 3500.0, "인(mg)": 4000.0, 
        "D-감마 토코페롤(mg)": 1000.0, "붕소(mg)": 20.0, "몰리브덴(mcg)": 2000.0, 
        "프로바이오틱스(CFU)": 100000000.0, "칼슘(mg)": 2500.0, "EPA + DHA(mg)": 500.0, 
        "단백질(g)": 100.0, "루테인(mg)": 20.0, "총지아잔틴(mg)": 2.0, 
        "아스타잔틴(mg)": 12.0, "L-류신(mg)": 10000.0, "L-글루타민(mg)": 20000.0, 
        "L-이소류신(mg)": 10000.0, "L-발린(mg)": 5000.0, "마그네슘(mg)": 350.0   
    }
}

INTERACTION_RULES = [ { "nutrients": ["철분(mg)", "칼슘(mg)"], "type": "위험", "message": "철분과 칼슘은 동일한 흡수 통로(DMT1)를 사용하여 서로의 흡수를 방해할 수 있습니다." }, 
                      { "nutrients": ["철분(mg)", "아연(mg)"], "type": "위험", "message": "철분과 아연은 미네랄 간 흡수 경쟁이 발생하여 흡수 효율이 감소할 수 있습니다." }, 
                      { "nutrients": ["철분(mg)", "마그네슘(mg)"], "type": "위험", "message": "철분과 마그네슘을 함께 복용하면 철분 흡수율이 감소하고 소화 장애가 발생할 수 있습니다." }, 
                      { "nutrients": ["철분(mg)", "단백질(g)"], "type": "주의", "message": "단백질 보충제에 포함된 칼슘·아연·마그네슘 등이 철분 흡수를 방해할 수 있습니다." }, 
                      { "nutrients": ["칼슘(mg)", "마그네슘(mg)"], "type": "주의", "message": "칼슘과 마그네슘을 고함량으로 동시에 복용하면 흡수 경쟁이 발생할 수 있습니다." }, 
                      { "nutrients": ["칼슘(mg)", "아연(mg)"], "type": "주의", "message": "고용량 칼슘은 아연의 체내 흡수를 방해할 수 있습니다." }, 
                      { "nutrients": ["비타민D(mcg)", "칼슘(mg)"], "type": "주의", "message": "비타민D는 칼슘 흡수를 증가시키므로 과다 복용 시 혈중 칼슘 농도가 높아질 수 있습니다." }, 
                      { "nutrients": ["비타민C(mg)", "비타민B12(mcg)"], "type": "주의", "message": "고용량 비타민C는 비타민B12의 안정성 및 흡수를 방해할 수 있습니다." }, 
                      { "nutrients": ["비타민D(mcg)", "비타민A(mcg)"], "type": "위험", "message": "비타민A 과다 복용은 비타민D 작용을 방해할 수 있으며 간독성·두통·탈모·뼈 약화 위험이 있습니다." }, 
                      { "nutrients": ["비타민C(mg)", "마그네슘(mg)"], "type": "주의", "message": "비타민C와 마그네슘을 고용량으로 함께 복용하면 설사나 속 쓰림이 발생할 수 있습니다." }, 
                      { "nutrients": ["프로바이오틱스(CFU)", "비타민C(mg)"], "type": "주의", "message": "강한 산성 환경으로 인해 유산균 생존율이 감소할 수 있습니다." }, 
                      { "nutrients": ["EPA+DHA(mg)", "비타민E(mgα-TE)"], "type": "주의", "message": "고함량으로 함께 복용 시 멍·코피·출혈 위험이 증가할 수 있습니다." }, 
                      { "nutrients": ["비타민A(mcg)", "루테인(mg)"], "type": "추천", "message": "비타민A와 루테인은 모두 눈 건강에 도움을 주는 성분으로 기능이 일부 유사합니다." } ]

#=========================================================
#안전한 숫자 변환
#=========================================================

def safe_float(val):
    try:
        if value is None:
            return 0.0
        value = str(value).strip()
        if value == '':
            return 0.0
        return float(value)
    except:
        return 0.0
#=========================================================
# 메인 엔진
# =========================================================
   

class KioskBrain:
    def __init__(self, csv_file_path):
        self.db = {}
        self.cart = []
        self.current_nutrients = {}
        self.latest_warnings = []
        self.gender = "남성"
        self.height = 0.0      
        self.weight = 0.0      
        self.bmi = 0.0  
        self.load_data(csv_file_path)

 #=========================================================
 # 초기화
 # =========================================================

def reset(self):
        self.cart = []
        self.current_nutrients = {}
        self.latest_warnings = []

#=========================================================
# csv 로드
# =========================================================
#     
        

def load_data(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    barcode = row.get("바코드", "").strip()

                    if barcode == "":
                        continue
                    
                    self.db[barcode] = {
                        "barcode": barcode,
                        "name": row['제품명 (브랜드)'].strip(),
                        "category": row['카테고리'].strip(),
                        "brand": row['브랜드'].strip(),       
                        "nutrients": {
                            "베타카로틴(mcg)": safe_float(row.get('베타카로틴 (mcg)', 0)),
                            "비타민A(mcg)": safe_float(row.get('비타민 A (mcg)',0)),
                            "비타민C(mg)": safe_float(row.get('비타민 C (mg)',0)),
                            "비타민D(mcg)": safe_float(row.get('비타민 D (mcg)',0)),
                            "식물성 비타민D2(mcg)": safe_float(row.get('식물성 비타민 D2 (mcg)',0)),
                            "동물성 비타민D3(mcg)": safe_float(row.get('동물성 비타민 D3 (mcg)',0)),
                            "비타민E(mgα-TE)": safe_float(row.get('비타민 E (mgα-TE)',0)),
                            "비타민K(mcg)": safe_float(row.get('비타민 K (mcg)',0)),
                            "비타민B1(mg)": safe_float(row.get('비타민 B1 (mg)',0)),
                            "비타민B2(mg)": safe_float(row.get('비타민 B2 (mg)',0)),
                            "비타민B3(mg)": safe_float(row.get('비타민 B3 (mg)',0)),
                            "비타민B6(mg)": safe_float(row.get('비타민 B6 (mg)',0)),
                            "비타민B9(mcg DFE)": safe_float(row.get('비타민 B9 (mcg DFE)',0)),
                            "비타민B12(mcg)": safe_float(row.get('비타민 B12 (mcg)',0)),
                            "비타민B7(mcg)": safe_float(row.get('비타민 B7 (mcg)',0)),
                            "비타민B5(mg)": safe_float(row.get('비타민 B5 (mg)',0)),
                            "콜린(mg)": safe_float(row.get('콜린 (mg)',0)),
                            "요오드(mcg)": safe_float(row.get('요오드 (mcg)',0)),
                            "철분(mg)": safe_float(row.get('철분 (mg)',0)),
                            "아연(mg)": safe_float(row.get('아연 (mg)',0)),
                            "마그네슘(mg)":safe_float(row.get('마그네슘 (mg)',0)),
                            "셀레늄(mcg)": safe_float(row.get('셀레늄 (mcg)',0)),
                            "구리(mcg)": safe_float(row.get('구리 (mcg)',0)),
                            "망간(mg)":safe_float(row.get('망간 (mg)',0)),
                            "크롬(mcg)": safe_float(row.get('크롬 (mcg)',0)),
                            "소듐(mg)": safe_float(row.get('소듐 (mg)',0)),
                            "포타슘(mg)": safe_float(row.get('포타슘 (mg)',0)),
                            "인(mg)": safe_float(row.get('인 (mg)',0)),
                            "D-감마 토코페롤(mg)": safe_float(row.get('D-감마 토코페롤 (mg)',0)),
                            "붕소(mg)": safe_float(row.get('붕소 (mg)',0)),
                            "몰리브덴(mcg)": safe_float(row.get('몰리브덴 (mcg)',0)),
                            "프로바이오틱스(CFU)": safe_float(row.get('프로바이오틱스 (CFU)',0)),
                            "칼슘(mg)": safe_float(row.get('칼슘 (mg)',0)),
                            "EPA + DHA(mg)": safe_float(row.get('EPA + DHA (mg)',0)),
                            "단백질(g)": safe_float(row.get('단백질 (g)',0)),
                            "루테인(mg)": safe_float(row.get('루테인 (mg)',0)),
                            "총지아잔틴(mg)": safe_float(row.get('총지아잔틴 (mg)',0)),
                            "아스타잔틴(mg)": safe_float(row.get('아스타잔틴 (mg)',0)),
                            "L-류신(mg)": safe_float(row.get('L-류신 (mg)',0)),
                            "L-글루타민(mg)": safe_float(row.get('L-글루타민 (mg)',0)),
                            "L-이소류신(mg)": safe_float(row.get('L-이소류신 (mg)',0)),
                            "L-발린(mg)": safe_float(row.get('L-발린 (mg)',0))
                        }
                    }
            print(f"✅ 데이터베이스 로드 성공! 총 {len(self.db)}개 품목 매핑 완료.")
        except Exception as e:
            print(f"❌ CSV 파일 로드 중 오류 발생: {e}")
            sys.exit(1)
 #=========================================================
 # 영양소 누적
 # =========================================================
def accumulate_nutrients(self, item):
        for nutrient, value in item['nutrients'].items():
           if nutrient not in self.current_nutrients: 
               self.current_nutrients[nutrient] = 0.0
           self.current_nutrients[nutrient] += value

#=========================================================
# 장바구니 추가
# =========================================================       

def add_to_cart(self, item):
        self.cart.append(item)
        self.accumulate_nutrients(item)
        self.check_warnings()
#=========================================================
#바코드 스캔
#=========================================================
def scan_item(self, barcode):
       
       if barcode not in self.db:
           return "⚠️ 등록되지 않은 제품입니다. 다른 제품을 스캔해 주세요."
       item = self.db[barcode]
       self.add_to_cart(item)
       return f"✅ [{item['name']}] 스캔완료"
    
 #=========================================================
 # 경고 검사
 # ========================================================
def check_warnings(self):
        warnings = []
        limit_data = SAFE_LIMITS[self.gender]
        for nutrient, limit in limit_data.items():
            current_val = self.current_nutrients.get(nutrient, 0)
            if current_val > limit:
                warnings.append(f"⚠️ {nutrient} 상한선 초과"
                                f" {current_val:.1f} /  {limit}"
                               )  
            elif current_val > (limit * 0.7):
                warnings.append(f"⚠️ [주의] {nutrient} 상한선  근접"
                                f" {current_val:.1f} /  {limit}"
                               ) 
        for rule in INTERACTION_RULES:
            found = True
            for nutrient in rule['nutrients']:
                if self.current_nutrients.get(nutrient, 0) <= 0:
                    found = False
                    break          
            if found:
                if rule["type"] == "위험":
                    warnings.append(f"⚠️ [영양소 충돌] {rule['message']}")
                elif rule["type"] == "주의":
                    warnings.append(f"⚠️ [주의조합] {rule['message']}") 
                elif rule["type"] == "추천":  
                    warnings.append(f"✅ [추천 조합] {rule['message']}")
        self.latest_warnings = warnings
 #=========================================================
 # 시리얼 스레드
 # =========================================================
def serial_worker(brain):
    if not SERIAL_AVAILABLE:
        return
    try:
        arduino = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)
        print("아두이노 연결 완료")
        while True:
            if arduino.in_wainting:
                barcode = arduino.readline().decode().strip()

                if barcode:
                    result = brain.scan_item(barcode)
                    print(result)
            time.sleep(0.1)
    except Exception as e:
        print(f"시리얼 연결 실패: {e}")      

def set_profile(self, gender, height, weight):
        self.gender = gender
        self.height = height
        self.weight = weight
        height_m = height / 100.0
        if height_m > 0:
            self.bmi = round(weight / (height_m ** 2), 1)
        else:
            self.bmi = 0.0
            
        # 💡 [핵심 구현] 사용자의 몸무게를 기반으로 단백질 하루 최대 상한선을 동적 갱신 (체중 * 2.0g)
        max_protein = round(weight * 2.0, 1)
        SAFE_LIMITS["남성"]["단백질(g)"] = max_protein
        SAFE_LIMITS["여성"]["단백질(g)"] = max_protein
        print(f"⚙️ 단백질 상한선 동적 설정 완료: 체중 {weight}kg -> 일일 최대 {max_protein}g")
        
        self.reset()

   

class KioskGuideFlow:
    def __init__(self, root, brain, on_complete_callback):
        self.root = root
        self.brain = brain
        self.on_complete = on_complete_callback
        
        self.gender = "남성"
        self.height_str = ""
        self.weight_str = ""
        
        self.frame = tk.Frame(root, bg="#000000")
        self.frame.pack(fill="both", expand=True)
        
        self.show_privacy_screen()

    def show_privacy_screen(self):
        self.clear_frame()
        
        center_container = tk.Frame(self.frame, bg="#000000")
        center_container.pack(expand=True)
        
        title = tk.Label(center_container, text="📋 개인정보 수집 · 이용 동의", font=("Noto Sans KR", 15, "bold"), fg="#DEFF9A", bg="#000000")
        title.pack(pady=(10, 10))
        
        text_frame = tk.Frame(center_container, bg="#151515", bd=1, relief="solid")
        text_frame.pack(pady=5, padx=20, fill="both", expand=True)
        
        privacy_text = (
            "▶ 수집·이용 목적\n"
            "   키오스크 기반 맞춤형 영양소 추천 서비스 제공\n\n"
            "▶ 수집하는 항목\n"
            "   성별, 키, 몸무게\n\n"
            "▶ 보유 및 이용 기간\n"
            "   키오스크 이용일로부터 1년 보관 후 파기\n\n"
            "▶ 동의 거부 권리 및 불이익\n"
            "   귀하는 동의를 거부할 권리가 있으나, 거부 시\n"
            "   맞춤형 영양소 추천 서비스 이용이 제한됩니다."
        )
        
        text_label = tk.Label(text_frame, text=privacy_text, font=("Noto Sans KR", 11), fg="#FFFFFF", bg="#151515", justify="left", anchor="w", padx=15, pady=15)
        text_label.pack(fill="both", expand=True)
        
        btn_frame = tk.Frame(center_container, bg="#000000")
        btn_frame.pack(pady=10)
        
        reject_btn = tk.Label(btn_frame, text="동의 안함", font=("Noto Sans KR", 11, "bold"), width=9, height=1, bg="#3A3A3C", fg="#FFFFFF", relief="raised", bd=1)
        reject_btn.bind("<Button-1>", lambda e: self.reject_privacy())
        reject_btn.pack(side="left", padx=15)
        
        agree_btn = tk.Label(btn_frame, text="동의함", font=("Noto Sans KR", 11, "bold"), width=9, height=1, bg="#DAFFDE", fg="#000000", relief="raised", bd=1)
        agree_btn.bind("<Button-1>", lambda e: self.show_gender_screen())
        agree_btn.pack(side="left", padx=15)

    def reject_privacy(self):
        messagebox.showwarning("서비스 제한 안내", "개인정보 수집에 동의하셔야만\n맞춤형 영양소 추천 서비스를 이용하실 수 있습니다.")
        self.show_privacy_screen()

    def show_gender_screen(self):
        self.clear_frame()
        self.current_step = "GENDER"
        
        title = tk.Label(self.frame, text="성별을 선택해 주세요", font=("Noto Sans KR", 20, "bold"), fg="#FFFFFF", bg="#000000")
        title.pack(expand=True, pady=(20, 0))
        
        btn_frame = tk.Frame(self.frame, bg="#000000")
        btn_frame.pack(expand=True, pady=(0, 20))
        
        male_btn = tk.Label(btn_frame, text="👨 남성 (Male)", font=("Noto Sans KR", 14, "bold"), width=12, height=2, bg="#DAFFDE", fg="#000000", relief="raised", bd=1)
        male_btn.bind("<Button-1>", lambda e: self.select_gender("남성"))
        male_btn.pack(side="left", padx=20)
        
        female_btn = tk.Label(btn_frame, text="👩 여성 (Female)", font=("Noto Sans KR", 14, "bold"), width=12, height=2, bg="#DAFFDE", fg="#000000", relief="raised", bd=1)
        female_btn.bind("<Button-1>", lambda e: self.select_gender("여성"))
        female_btn.pack(side="left", padx=20)

    def select_gender(self, gender):
        self.gender = gender
        self.show_number_pad_screen("HEIGHT")

    def show_number_pad_screen(self, step):
        self.clear_frame()
        self.current_step = step
        
        if step == "HEIGHT":
            msg, unit, current_val = "본인의 신장(키)을 입력하세요", " cm", self.height_str
        else:
            msg, unit, current_val = "본인의 체중(몸무게)을 입력하세요", " kg", self.weight_str

        center_container = tk.Frame(self.frame, bg="#000000")
        center_container.pack(expand=True)

        top_frame = tk.Frame(center_container, bg="#000000")
        top_frame.pack(pady=5)

        title = tk.Label(top_frame, text=msg, font=("Noto Sans KR", 15, "bold"), fg="#FFFFFF", bg="#000000")
        title.pack(side="left", padx=10)
        
        display_text = current_val + unit if current_val else "0" + unit
        self.display_label = tk.Label(top_frame, text=display_text, font=("Helvetica", 18, "bold"), fg="#DEFF9A", bg="#151515", width=10, bd=1, relief="solid")
        self.display_label.pack(side="left", padx=10)
        
        pad_frame = tk.Frame(center_container, bg="#000000")
        pad_frame.pack(pady=5)
        
        buttons = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '.', '0', '⌫']
        row, col = 0, 0
        
        for btn_txt in buttons:
            cmd = lambda x=btn_txt: self.press_key(x)
            btn = tk.Label(pad_frame, text=btn_txt, font=("Helvetica", 12, "bold"), width=5, height=1, bg="#DAFFDE", fg="#000000", relief="raised", bd=1)
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.grid(row=row, column=col, padx=5, pady=4)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        action_frame = tk.Frame(center_container, bg="#000000")
        action_frame.pack(pady=5)
        
        prev_label = tk.Label(action_frame, text="◀ 이전", font=("Noto Sans KR", 11, "bold"), width=8, height=1, bg="#3A3A3C", fg="#FFFFFF", relief="raised", bd=1)
        prev_label.bind("<Button-1>", lambda e: self.go_back())
        prev_label.pack(side="left", padx=10)
        
        next_text = "선택 완료 ▶" if step == "WEIGHT" else "다음 ▶"
        next_label = tk.Label(action_frame, text=next_text, font=("Noto Sans KR", 11, "bold"), width=10, height=1, bg="#DEFF9A", fg="#000000", relief="raised", bd=1)
        next_label.bind("<Button-1>", lambda e: self.go_next())
        next_label.pack(side="left", padx=10)

    def press_key(self, key):
        if self.current_step == "HEIGHT":
            val = self.height_str
        else:
            val = self.weight_str
            
        if key == '⌫':
            val = val[:-1]
        elif key == '.':
            if '.' not in val and len(val) > 0:
                val += '.'
        else:
            if len(val) < 5:
                val += key
                
        if self.current_step == "HEIGHT":
            self.height_str = val
            unit = " cm"
        else:
            self.weight_str = val
            unit = " kg"
            
        self.display_label.config(text=val + unit if val else "0" + unit)

    def go_back(self):
        if self.current_step == "HEIGHT":
            self.show_gender_screen()
        elif self.current_step == "WEIGHT":
            self.show_number_pad_screen("HEIGHT")

    def go_next(self):
        try:
            if self.current_step == "HEIGHT":
                h = float(self.height_str)
                if not (100 <= h <= 250):
                    raise ValueError
                self.show_number_pad_screen("WEIGHT")
                
            elif self.current_step == "WEIGHT":
                h = float(self.height_str)
                w = float(self.weight_str)
                if not (20 <= w <= 250):
                    raise ValueError
                
                self.brain.set_profile(self.gender, h, w)
                
                self.frame.destroy()
                self.on_complete()
                
        except ValueError:
            messagebox.showerror("입력값 검증 요망", "올바른 신체 스펙 숫자를 입력해 주세요.\n(예: 키 100~250cm, 몸무게 20~250kg 내외)")

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


def listen_to_arduino(app_instance):
    if not SERIAL_AVAILABLE:
        return

    arduino_port = '/dev/cu.usbmodem31301' 
    try:
        ser = serial.Serial(arduino_port, 115200, timeout=1)
        time.sleep(2)
        print("🔌 아두이노 브릿지 통신 라인 연결 완료.")
        
        while True:
            if ser.in_waiting > 0:
                scanned_data = ser.readline().decode('utf-8-sig').strip()
                if scanned_data and scanned_data != "SYSTEM_READY":
                    print(f"📷 스캔 데이터 수신: {scanned_data}")
                    
                    matched_item = None
                    for item in app_instance.brain.db:
                        if scanned_data.lower() in item['name'].lower():
                            matched_item = item
                            break
                    
                    if matched_item:
                        app_instance.handle_product_selection(matched_item)
                        
    except Exception as e:
        print(f"⚠️ 아두이노 시리얼 라인 연결 실패: {e}")


def start_main_kiosk_system():
    app = KioskApp(root, brain, SAFE_LIMITS)
    
    serial_thread = threading.Thread(target=listen_to_arduino, args=(app,), daemon=True)
    serial_thread.start()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("개인 맞춤형 헬스케어 영양제 키오스크")
    
    # 원래 메인 창 크기에 맞춰 변경해 줘! (기본값 800x600 세팅)
    root.geometry("800x450") 
    root.resizable(False, False) 
    root.configure(bg="#000000") 
    
    brain = KioskBrain('supplements_db.csv')
    guide_flow = KioskGuideFlow(root, brain, start_main_kiosk_system)
    
    root.mainloop()
