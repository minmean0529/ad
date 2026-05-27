import tkinter as tk
from tkinter import messagebox
import csv
import threading
import time

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("💡 [시스템 알림] pyserial 라이브러리가 감지되지 않아 가상 모드로 전환합니다.")

from kiosk_ui import KioskApp


# 대한민국 식약처 및 의학 기준 영양소 일일 상한 섭취량 (UL)
SAFE_LIMITS = {

    "남성": {
        "베타카로틴(mcg)": 7000.0,
        "비타민A(mcg)": 3000.0,
        "비타민C(mg)": 2000.0,
        "비타민D(mcg)": 100.0,
        "식물성 비타민D2(mcg)": 10000.0,
        "동물성 비타민D3(mcg)": 100.0,
        "비타민E(mgα-TE)": 1000.0,
        "비타민K(mcg)": 120.0,
        "비타민B1(mg)": 1.2,
        "비타민B2(mg)": 1.5,
        "비타민B3(mg)": 35.0,
        "비타민B6(mg)": 100.0,
        "비타민B9(mcg DFE)": 1000.0,
        "비타민B12(mcg)": 500.0,
        "비타민B7(mcg)": 30.0,
        "비타민B5(mg)": 10.0,
        "콜린(mg)": 595.0,
        "요오드(mcg)": 1100.0,
        "철분(mg)": 45.0,
        "아연(mg)": 40.0,
        "셀레늄(mcg)": 400.0,
        "구리(mcg)": 10000.0,
        "망간(mg)": 11.0,
        "크롬(mcg)": 35.0,
        "소듐(mg)": 2300.0,
        "포타슘(mg)": 3500.0,
        "인(mg)": 4000.0,
        "D-감마 토코페롤(mg)": 1000.0,
        "붕소(mg)": 20.0,
        "몰리브덴(mcg)": 2000.0,
        "프로바이오틱스(CFU)": 100000000.0,
        "칼슘(mg)": 2500.0,
        "EPA + DHA(mg)": 1000.0,
        "단백질(g)": 100.0,
        "루테인(mg)": 20.0,
        "총지아잔틴(mg)": 2.0,
        "아스타잔틴(mg)": 12.0,
        "L-류신(mg)": 10000.0,
        "L-글루타민(mg)": 20000.0,
        "L-이소류신(mg)": 10000.0,
        "L-발린(mg)": 5000.0,
        "마그네슘(mg)": 350.0
    },

    "여성": {
        "베타카로틴(mcg)": 7000.0,
        "비타민A(mcg)": 3000.0,
        "비타민C(mg)": 2000.0,
        "비타민D(mcg)": 100.0,
        "식물성 비타민D2(mcg)": 10000.0,

        # 수정됨 (기존 1.1 → 100.0)
        "동물성 비타민D3(mcg)": 100.0,

        "비타민E(mgα-TE)": 540.0,
        "비타민K(mcg)": 90.0,
        "비타민B1(mg)": 5.0,
        "비타민B2(mg)": 1.2,
        "비타민B3(mg)": 35.0,
        "비타민B6(mg)": 100.0,
        "비타민B9(mcg DFE)": 1000.0,
        "비타민B12(mcg)": 500.0,
        "비타민B7(mcg)": 30.0,
        "비타민B5(mg)": 10.0,
        "콜린(mg)": 425.0,
        "요오드(mcg)": 1100.0,
        "철분(mg)": 45.0,
        "아연(mg)": 40.0,
        "셀레늄(mcg)": 400.0,
        "구리(mcg)": 10000.0,
        "망간(mg)": 11.0,
        "크롬(mcg)": 25.0,
        "소듐(mg)": 2300.0,
        "포타슘(mg)": 3500.0,
        "인(mg)": 4000.0,
        "D-감마 토코페롤(mg)": 1000.0,
        "붕소(mg)": 20.0,
        "몰리브덴(mcg)": 2000.0,
        "프로바이오틱스(CFU)": 100000000.0,
        "칼슘(mg)": 2500.0,
        "EPA + DHA(mg)": 500.0,
        "단백질(g)": 100.0,
        "루테인(mg)": 20.0,
        "총지아잔틴(mg)": 2.0,
        "아스타잔틴(mg)": 12.0,
        "L-류신(mg)": 10000.0,
        "L-글루타민(mg)": 20000.0,
        "L-이소류신(mg)": 10000.0,
        "L-발린(mg)": 5000.0,
        "마그네슘(mg)": 350.0
    }
}


class KioskBrain:

    def __init__(self, csv_file_path):

        self.db = []
        self.cart = []

        self.gender = "남성"
        self.height = 0.0
        self.weight = 0.0
        self.bmi = 0.0

        self.current_nutrients = {}

        self.load_data(csv_file_path)

    # 안전한 숫자 변환
    def safe_float(self, value):

        try:

            if value is None:
                return 0.0

            value = str(value).replace(",", "").strip()

            if value == "":
                return 0.0

            return float(value)

        except ValueError:
            return 0.0

    def load_data(self, file_path):

        try:

            with open(file_path, 'r', encoding='utf-8-sig') as f:

                reader = csv.DictReader(f)

                for row in reader:

                    def get_val(column_name):
                        return self.safe_float(
                            row.get(column_name, 0.0)
                        )

                    self.db.append({

                        "category": row.get(
                            '카테고리',
                            ''
                        ).strip(),

                        "name": row.get(
                            '제품명 (브랜드)',
                            ''
                        ).strip(),

                        "nutrients": {

                            "베타카로틴(mcg)": get_val('베타카로틴 (mcg)'),
                            "비타민A(mcg)": get_val('비타민 A (mcg)'),
                            "비타민C(mg)": get_val('비타민 C (mg)'),
                            "비타민D(mcg)": get_val('비타민 D (mcg)'),
                            "식물성 비타민D2(mcg)": get_val('식물성 비타민 D2 (mcg)'),
                            "동물성 비타민D3(mcg)": get_val('동물성 비타민 D3 (mcg)'),
                            "비타민E(mgα-TE)": get_val('비타민 E (mgα-TE)'),
                            "비타민K(mcg)": get_val('비타민 K (mcg)'),
                            "비타민B1(mg)": get_val('비타민 B1 (mg)'),
                            "비타민B2(mg)": get_val('비타민 B2 (mg)'),
                            "비타민B3(mg)": get_val('비타민 B3 (mg)'),
                            "비타민B6(mg)": get_val('비타민 B6 (mg)'),
                            "비타민B9(mcg DFE)": get_val('비타민 B9 (mcg DFE)'),
                            "비타민B12(mcg)": get_val('비타민 B12 (mcg)'),
                            "비타민B7(mcg)": get_val('비타민 B7 (mcg)'),
                            "비타민B5(mg)": get_val('비타민 B5 (mg)'),
                            "콜린(mg)": get_val('콜린 (mg)'),
                            "요오드(mcg)": get_val('요오드 (mcg)'),
                            "철분(mg)": get_val('철분 (mg)'),
                            "아연(mg)": get_val('아연 (mg)'),
                            "마그네슘(mg)": get_val('마그네슘 (mg)'),
                            "셀레늄(mcg)": get_val('셀레늄 (mcg)'),
                            "구리(mcg)": get_val('구리 (mcg)'),
                            "망간(mg)": get_val('망간 (mg)'),
                            "크롬(mcg)": get_val('크롬 (mcg)'),
                            "소듐(mg)": get_val('소듐 (mg)'),
                            "포타슘(mg)": get_val('포타슘 (mg)'),
                            "인(mg)": get_val('인 (mg)'),
                            "D-감마 토코페롤(mg)": get_val('D-감마 토코페롤 (mg)'),
                            "붕소(mg)": get_val('붕소 (mg)'),
                            "몰리브덴(mcg)": get_val('몰리브덴 (mcg)'),
                            "프로바이오틱스(CFU)": get_val('프로바이오틱스 (CFU)'),
                            "칼슘(mg)": get_val('칼슘 (mg)'),
                            "EPA + DHA(mg)": get_val('EPA + DHA (mg)'),
                            "단백질(g)": get_val('단백질 (g)'),
                            "루테인(mg)": get_val('루테인 (mg)'),
                            "총지아잔틴(mg)": get_val('총지아잔틴 (mg)'),
                            "아스타잔틴(mg)": get_val('아스타잔틴 (mg)'),
                            "L-류신(mg)": get_val('L-류신 (mg)'),
                            "L-글루타민(mg)": get_val('L-글루타민 (mg)'),
                            "L-이소류신(mg)": get_val('L-이소류신 (mg)'),
                            "L-발린(mg)": get_val('L-발린 (mg)')
                        }
                    })

            print(
                f"✅ 데이터베이스 로드 성공! "
                f"총 {len(self.db)}개 품목 매핑 완료."
            )

        except FileNotFoundError:

            print(
                "❌ supplements_db.csv 파일을 찾을 수 없습니다."
            )

        except Exception as e:

            print(
                f"❌ CSV 파일 로드 중 오류 발생: {e}"
            )

    def add_to_cart(self, item):

        self.cart.append(item['name'])

        for key, value in item['nutrients'].items():

            if key not in self.current_nutrients:
                self.current_nutrients[key] = 0.0

            self.current_nutrients[key] += value

    def set_profile(self, gender, height, weight):

        self.gender = gender
        self.height = height
        self.weight = weight

        height_m = height / 100.0

        if height_m > 0:

            self.bmi = round(
                weight / (height_m ** 2),
                1
            )

        else:
            self.bmi = 0.0

        # 단백질 상한 동적 계산
        max_protein = round(weight * 2.0, 1)

        SAFE_LIMITS["남성"]["단백질(g)"] = max_protein
        SAFE_LIMITS["여성"]["단백질(g)"] = max_protein

        print(
            f"⚙️ 단백질 상한선 설정 완료 "
            f"({max_protein}g)"
        )

        self.reset()

    def reset(self):

        self.cart = []

        self.current_nutrients = {

            key: 0.0
            for key in SAFE_LIMITS[self.gender].keys()
        }


# -----------------------------
# 아두이노 연결
# -----------------------------

def listen_to_arduino(app_instance, root):

    if not SERIAL_AVAILABLE:
        return

    arduino_port = '/dev/cu.usbmodem31301'

    try:

        ser = serial.Serial(
            arduino_port,
            115200,
            timeout=1
        )

        time.sleep(2)

        print(
            "🔌 아두이노 브릿지 통신 라인 연결 완료."
        )

        while True:

            if ser.in_waiting > 0:

                scanned_data = (
                    ser.readline()
                    .decode(
                        'utf-8-sig',
                        errors='ignore'
                    )
                    .strip()
                )

                if (
                    scanned_data and
                    scanned_data != "SYSTEM_READY"
                ):

                    print(
                        f"📷 스캔 데이터 수신: "
                        f"{scanned_data}"
                    )

                    matched_item = None

                    for item in app_instance.brain.db:

                        # 기존 in 비교 제거
                        if (
                            scanned_data.lower().strip()
                            ==
                            item['name'].lower().strip()
                        ):

                            matched_item = item
                            break

                    if matched_item:

                        # Tkinter 메인스레드 안전 처리
                        root.after(
                            0,
                            lambda m=matched_item:
                            app_instance.handle_product_selection(m)
                        )

    except serial.SerialException as e:

        print(
            f"⚠️ 시리얼 연결 실패: {e}"
        )

    except Exception as e:

        print(
            f"⚠️ 아두이노 연결 오류: {e}"
        )


# -----------------------------
# 메인 시작
# -----------------------------

def start_main_kiosk_system(root, brain):

    app = KioskApp(
        root,
        brain,
        SAFE_LIMITS
    )

    serial_thread = threading.Thread(
        target=listen_to_arduino,
        args=(app, root),
        daemon=True
    )

    serial_thread.start()


# -----------------------------
# 실행
# -----------------------------

if __name__ == '__main__':

    root = tk.Tk()

    root.title(
        "개인 맞춤형 헬스케어 영양제 키오스크"
    )

    root.geometry("800x450")

    root.resizable(False, False)

    root.configure(bg="#000000")

    brain = KioskBrain('supplements_db.csv')

    app = KioskApp(
        root,
        brain,
        SAFE_LIMITS
    )

    serial_thread = threading.Thread(
        target=listen_to_arduino,
        args=(app, root),
        daemon=True
    )

    serial_thread.start()

    root.mainloop()
