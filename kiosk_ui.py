import tkinter as tk
from tkinter import font
import csv

# =========================================================
# [1] 영양소 일일 상한선 데이터
# =========================================================

SAFE_LIMITS = {
    "남성": {
        "비타민A(mcg)": 3000,
        "비타민C(mg)": 2000,
        "비타민D(mcg)": 100,
        "비타민B6(mg)": 100,
        "비타민B12(mcg)": 2000,
        "철분(mg)": 45,
        "아연(mg)": 35,
        "마그네슘(mg)": 350,
        "칼슘(mg)": 2500,
        "EPA+DHA(mg)": 3000
    },

    "여성": {
        "비타민A(mcg)": 3000,
        "비타민C(mg)": 2000,
        "비타민D(mcg)": 100,
        "비타민B6(mg)": 100,
        "비타민B12(mcg)": 2000,
        "철분(mg)": 45,
        "아연(mg)": 35,
        "마그네슘(mg)": 350,
        "칼슘(mg)": 2500,
        "EPA+DHA(mg)": 3000
    }
}


# =========================================================
# [2] CSV 숫자 변환 안전 함수
# =========================================================

def safe_float(value):
    """
    빈칸, '-', None 등을 안전하게 0으로 변환
    """
    try:
        value = str(value).strip()

        if value == "" or value == "-":
            return 0.0

        return float(value)

    except:
        return 0.0


# =========================================================
# [3] 데이터 엔진
# =========================================================

class KioskBrain:

    def __init__(self, csv_file_path):

        self.db = []

        self.cart = []

        self.gender = "남성"

        # 현재 누적 영양소
        self.current_nutrients = {}

        # 모든 영양소 0 초기화
        for nutrient in SAFE_LIMITS["남성"]:
            self.current_nutrients[nutrient] = 0.0

        self.load_data(csv_file_path)

    # -----------------------------------------------------
    # CSV 로드
    # -----------------------------------------------------
    def load_data(self, file_path):

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:

                reader = csv.DictReader(f)

                for i, row in enumerate(reader):

                    # =========================================
                    # 나중에 실제 바코드 컬럼으로 변경
                    #
                    # 예시:
                    # barcode = row["바코드"]
                    # =========================================
                    barcode = str(1000 + i)

                    item = {

                        "barcode": barcode,

                        "category": row["카테고리"].strip(),

                        "name": row["제품명 (브랜드)"].strip(),

                        # =====================================
                        # 모든 영양소 저장
                        # =====================================
                        "nutrients": {

                            "베타카로틴(mcg)":
                                safe_float(row["베타카로틴(mcg)"]),

                            "비타민A(mcg)":
                                safe_float(row["비타민A(mcg)"]),

                            "비타민C(mg)":
                                safe_float(row["비타민C(mg)"]),

                            "비타민D(mcg)":
                                safe_float(row["비타민D(mcg)"]),

                            "식물성 비타민D2(mcg)":
                                safe_float(row["식물성 비타민D2(mcg)"]),

                            "동물성 비타민D3(mcg)":
                                safe_float(row["동물성 비타민D3(mcg)"]),

                            "비타민E(mgα-TE)":
                                safe_float(row["비타민E(mgα-TE)"]),

                            "비타민K(mcg)":
                                safe_float(row["비타민K(mcg)"]),

                            "비타민B1(mg)":
                                safe_float(row["비타민B1(mg)"]),

                            "비타민B2(mg)":
                                safe_float(row["비타민B2(mg)"]),

                            "비타민B3(mg)":
                                safe_float(row["비타민B3(mg)"]),

                            "비타민B6(mg)":
                                safe_float(row["비타민B6(mg)"]),

                            "비타민B9(mcg DFE)":
                                safe_float(row["비타민B9(mcg DFE)"]),

                            "비타민B12(mcg)":
                                safe_float(row["비타민B12(mcg)"]),

                            "비타민B7(mcg)":
                                safe_float(row["비타민B7(mcg)"]),

                            "비타민B5(mg)":
                                safe_float(row["비타민B5(mg)"]),

                            "콜린(mg)":
                                safe_float(row["콜린(mg)"]),

                            "요오드(mcg)":
                                safe_float(row["요오드(mcg)"]),

                            "철분(mg)":
                                safe_float(row["철분(mg)"]),

                            "아연(mg)":
                                safe_float(row["아연(mg)"]),

                            "마그네슘(mg)":
                                safe_float(row["마그네슘(mg)"]),

                            "셀레늄(mcg)":
                                safe_float(row["셀레늄(mcg)"]),

                            "구리(mcg)":
                                safe_float(row["구리(mcg)"]),

                            "망간(mg)":
                                safe_float(row["망간(mg)"]),

                            "크롬(mcg)":
                                safe_float(row["크롬(mcg)"]),

                            "소듐(mg)":
                                safe_float(row["소듐(mg)"]),

                            "포타슘(mg)":
                                safe_float(row["포타슘(mg)"]),

                            "인(mg)":
                                safe_float(row["인(mg)"]),

                            "D-감마 토코페롤(mg)":
                                safe_float(row["D-감마 토코페롤(mg)"]),

                            "붕소(mg)":
                                safe_float(row["붕소(mg)"]),

                            "몰리브덴(mcg)":
                                safe_float(row["몰리브덴(mcg)"]),

                            "프로바이오틱스(CFU)":
                                safe_float(row["프로바이오틱스(CFU)"]),

                            "칼슘(mg)":
                                safe_float(row["칼슘(mg)"]),

                            "EPA+DHA(mg)":
                                safe_float(row["EPA+DHA(mg)"]),

                            "단백질(g)":
                                safe_float(row["단백질(g)"]),

                            "루테인(mg)":
                                safe_float(row["루테인(mg)"]),

                            "총지아잔틴(mg)":
                                safe_float(row["총지아잔틴(mg)"]),

                            "아스타잔틴(mg)":
                                safe_float(row["아스타잔틴(mg)"]),

                            "L-류신(mg)":
                                safe_float(row["L-류신(mg)"]),

                            "L-글루타민(mg)":
                                safe_float(row["L-글루타민(mg)"]),

                            "L-이소류신(mg)":
                                safe_float(row["L-이소류신(mg)"]),

                            "L-발린(mg)":
                                safe_float(row["L-발린(mg)"])
                        }
                    }

                    self.db.append(item)

            print(f"✅ 데이터 로드 완료 ({len(self.db)}개 제품)")

        except Exception as e:
            print("❌ CSV 로드 실패")
            print(e)

    # -----------------------------------------------------
    # 제품 장바구니 추가
    # -----------------------------------------------------
    def add_to_cart(self, item):

        self.cart.append(item["name"])

        nutrients = item["nutrients"]

        # 누적
        for nutrient, value in nutrients.items():

            # SAFE_LIMITS에 있는 영양소만 누적
            if nutrient in self.current_nutrients:
                self.current_nutrients[nutrient] += value

    # -----------------------------------------------------
    # 초기화
    # -----------------------------------------------------
    def reset(self):

        self.cart = []

        for nutrient in self.current_nutrients:
            self.current_nutrients[nutrient] = 0.0


# =========================================================
# [4] UI
# =========================================================

class KioskApp:

    def __init__(self, root, brain):

        self.root = root

        self.brain = brain

        self.root.title("영양제 안전 분석 시스템")

        self.root.geometry("1000x850")

        self.root.configure(bg="#1E1E1E")

        self.content_container = tk.Frame(
            self.root,
            bg="#1E1E1E"
        )

        self.content_container.pack(
            fill="both",
            expand=True
        )

        # 하단 장바구니
        self.cart_bar = tk.Frame(
            self.root,
            bg="#2D2D2D",
            height=100
        )

        self.cart_bar.pack(
            side="bottom",
            fill="x"
        )

        self.cart_items_label = tk.Label(
            self.cart_bar,
            text="🛒 선택 목록: 비어 있음",
            font=("Helvetica", 13),
            fg="#00FFCC",
            bg="#2D2D2D",
            padx=20
        )

        self.cart_items_label.pack(pady=25)

        self.show_start_page()

    # -----------------------------------------------------
    def clear_frame(self):

        for widget in self.content_container.winfo_children():
            widget.destroy()

    # -----------------------------------------------------
    def update_cart_display(self):

        text = " | ".join(self.brain.cart)

        if text == "":
            text = "비어 있음"

        self.cart_items_label.config(
            text=f"🛒 선택 목록: {text}"
        )

    # -----------------------------------------------------
    def show_start_page(self):

        self.clear_frame()

        self.brain.reset()

        self.update_cart_display()

        tk.Label(
            self.content_container,
            text="💊\nSAFE NUTRI-CHECK",
            font=("Helvetica", 50, "bold"),
            fg="#00FFCC",
            bg="#1E1E1E"
        ).pack(pady=80)

        tk.Button(
            self.content_container,
            text="키오스크 시작",
            font=("Helvetica", 22, "bold"),
            command=self.show_gender_page,
            bg="#00FFCC",
            width=15,
            height=2
        ).pack()

    # -----------------------------------------------------
    def show_gender_page(self):

        self.clear_frame()

        tk.Label(
            self.content_container,
            text="사용자의 성별을 선택하세요",
            font=("Helvetica", 30),
            fg="white",
            bg="#1E1E1E"
        ).pack(pady=80)

        btn_frame = tk.Frame(
            self.content_container,
            bg="#1E1E1E"
        )

        btn_frame.pack()

        tk.Button(
            btn_frame,
            text="남성",
            font=("Helvetica", 18),
            width=15,
            height=2,
            command=lambda: self.set_gender("남성")
        ).pack(side="left", padx=20)

        tk.Button(
            btn_frame,
            text="여성",
            font=("Helvetica", 18),
            width=15,
            height=2,
            command=lambda: self.set_gender("여성")
        ).pack(side="left", padx=20)

    # -----------------------------------------------------
    def set_gender(self, gender):

        self.brain.gender = gender

        self.show_category_page()

    # -----------------------------------------------------
    def show_category_page(self):

        self.clear_frame()

        self.update_cart_display()

        tk.Label(
            self.content_container,
            text=f"[{self.brain.gender}] 영양제 종류 선택",
            font=("Helvetica", 25),
            fg="#00FFCC",
            bg="#1E1E1E"
        ).pack(pady=30)

        categories = sorted(
            list(
                set(item["category"] for item in self.brain.db)
            )
        )

        grid_frame = tk.Frame(
            self.content_container,
            bg="#1E1E1E"
        )

        grid_frame.pack(pady=10)

        for i, cat in enumerate(categories):

            btn = tk.Button(
                grid_frame,
                text=cat,
                font=("Helvetica", 14),
                width=18,
                height=2,
                command=lambda c=cat: self.show_brand_page(c)
            )

            btn.grid(
                row=i // 3,
                column=i % 3,
                padx=10,
                pady=10
            )

        tk.Button(
            self.content_container,
            text="🚀 분석 리포트 확인",
            font=("Helvetica", 18, "bold"),
            bg="#FFCC00",
            fg="black",
            padx=30,
            pady=15,
            command=self.show_result_page
        ).pack(side="bottom", pady=40)

    # -----------------------------------------------------
    def show_brand_page(self, category):

        self.clear_frame()

        tk.Label(
            self.content_container,
            text=f"[{category}] 제품 목록",
            font=("Helvetica", 22),
            fg="white",
            bg="#1E1E1E"
        ).pack(pady=30)

        products = [
            item for item in self.brain.db
            if item["category"] == category
        ]

        list_frame = tk.Frame(
            self.content_container,
            bg="#1E1E1E"
        )

        list_frame.pack(pady=10)

        for prod in products:

            btn = tk.Button(
                list_frame,
                text=prod["name"],
                font=("Helvetica", 14),
                width=55,
                pady=10,
                command=lambda p=prod: [
                    self.brain.add_to_cart(p),
                    self.update_cart_display(),
                    self.show_category_page()
                ]
            )

            btn.pack(pady=5)

        tk.Button(
            self.content_container,
            text="🔙 뒤로 가기",
            command=self.show_category_page
        ).pack(pady=20)

    # -----------------------------------------------------
    def show_result_page(self):

        self.clear_frame()

        tk.Label(
            self.content_container,
            text="📊 영양 성분 분석 결과",
            font=("Helvetica", 30, "bold"),
            fg="white",
            bg="#1E1E1E"
        ).pack(pady=40)

        res_frame = tk.Frame(
            self.content_container,
            bg="#1E1E1E"
        )

        res_frame.pack(pady=10)

        any_danger = False

        limit_data = SAFE_LIMITS[self.brain.gender]

        for nutrient, limit in limit_data.items():

            val = self.brain.current_nutrients[nutrient]

            if val == 0:
                continue

            is_over = val > limit

            color = "#E74C3C" if is_over else "#2ECC71"

            if is_over:
                any_danger = True

            status_text = (
                f"{nutrient}: "
                f"{val:.1f} / {limit}"
            )

            tk.Label(
                res_frame,
                text=status_text,
                font=("Helvetica", 18, "bold"),
                fg=color,
                bg="#1E1E1E",
                pady=8
            ).pack()

        # 최종 메시지
        if any_danger:

            final_msg = (
                "🚨 일부 성분이 상한 섭취량을 초과했습니다!"
            )

            final_color = "#E74C3C"

        else:

            final_msg = (
                "✅ 모든 성분이 안전 범위입니다."
            )

            final_color = "#2ECC71"

        tk.Label(
            self.content_container,
            text=final_msg,
            font=("Helvetica", 22, "bold"),
            bg=final_color,
            fg="white",
            padx=30,
            pady=20
        ).pack(pady=30)

        tk.Button(
            self.content_container,
            text="🔄 처음으로 돌아가기",
            font=("Helvetica", 15),
            command=self.show_start_page,
            bg="#00FFCC"
        ).pack(side="bottom", pady=30)


# =========================================================
# [5] 프로그램 실행
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    # =========================================
    # CSV 파일명 입력
    # =========================================
    brain = KioskBrain("supplements_db.csv")

    app = KioskApp(root, brain)

    root.mainloop()
