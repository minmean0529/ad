import tkinter as tk
from tkinter import font
import csv


# =========================================================
# [1] 영양소 일일 상한선 데이터
# =========================================================

SAFE_LIMITS = {

    "남성": {

        "비타민B6(mg)": 100,
        "비타민B12(mcg)": 2000,
        "비타민C(mg)": 2000,
        "비타민D(mcg)": 100,
        "철분(mg)": 45,
        "칼슘(mg)": 2500,
        "EPA+DHA(mg)": 3000
    },

    "여성": {

        "비타민B6(mg)": 100,
        "비타민B12(mcg)": 2000,
        "비타민C(mg)": 2000,
        "비타민D(mcg)": 100,
        "철분(mg)": 45,
        "칼슘(mg)": 2500,
        "EPA+DHA(mg)": 3000
    }
}


# =========================================================
# [2] 데이터 처리 엔진
# =========================================================

class KioskBrain:

    def __init__(self, csv_file_path):

        self.db = []

        self.cart = []

        self.gender = "남성"

        # 영양소 누적 저장
        self.current_nutrients = {}

        self.load_data(csv_file_path)


    # =====================================================
    # CSV 데이터 로드
    # =====================================================

    def load_data(self, file_path):

        try:

            with open(file_path, 'r', encoding='utf-8-sig') as f:

                reader = csv.DictReader(f)

                for i, row in enumerate(reader):

                    # =========================================
                    # 나중에 실제 바코드 컬럼 사용 가능
                    #
                    # 예시:
                    # "barcode": row["바코드"]
                    #
                    # 현재는 테스트용 임시 바코드
                    # =========================================

                    barcode = str(1000 + i)

                    self.db.append({

                        "barcode": barcode,

                        "category": row['카테고리'].strip(),

                        "name": row['제품명 (브랜드)'].strip(),

                        "nutrients": {

                            "비타민A(mcg)": float(row["비타민A(mcg)"] or 0),

                            "비타민B6(mg)": float(row["비타민B6(mg)"] or 0),

                            "비타민B12(mcg)": float(row["비타민B12(mcg)"] or 0),

                            "비타민C(mg)": float(row["비타민C(mg)"] or 0),

                            "비타민D(mcg)": float(row["비타민D(mcg)"] or 0),

                            "철분(mg)": float(row["철분(mg)"] or 0),

                            "칼슘(mg)": float(row["칼슘(mg)"] or 0),

                            "아연(mg)": float(row["아연(mg)"] or 0),

                            "마그네슘(mg)": float(row["마그네슘(mg)"] or 0),

                            "EPA+DHA(mg)": float(row["EPA+DHA(mg)"] or 0),

                            "단백질(g)": float(row["단백질(g)"] or 0)
                        }
                    })

            print(f"✅ 데이터 로드 완료 ({len(self.db)}개 제품)")

        except Exception as e:

            print(f"❌ CSV 로드 오류: {e}")


    # =====================================================
    # 제품 추가
    # =====================================================

    def add_to_cart(self, item):

        self.cart.append(item['name'])

        for nutrient, value in item["nutrients"].items():

            if nutrient not in self.current_nutrients:

                self.current_nutrients[nutrient] = 0.0

            self.current_nutrients[nutrient] += value


    # =====================================================
    # 바코드 스캔 기능
    # =====================================================

    def scan_barcode(self, barcode):

        for item in self.db:

            if item["barcode"] == barcode:

                self.add_to_cart(item)

                return item

        return None


    # =====================================================
    # 초기화
    # =====================================================

    def reset(self):

        self.cart = []

        self.current_nutrients = {}



# =========================================================
# [3] UI 시스템
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


        # =================================================
        # 하단 장바구니 영역
        # =================================================

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


    # =====================================================
    # 화면 초기화
    # =====================================================

    def clear_frame(self):

        for widget in self.content_container.winfo_children():

            widget.destroy()


    # =====================================================
    # 장바구니 표시 업데이트
    # =====================================================

    def update_cart_display(self):

        text = " | ".join(self.brain.cart)

        if not text:

            text = "비어 있음"

        self.cart_items_label.config(
            text=f"🛒 선택 목록: {text}"
        )


    # =====================================================
    # 시작 화면
    # =====================================================

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


    # =====================================================
    # 성별 선택
    # =====================================================

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

            text="남성 (Male)",

            font=("Helvetica", 18),

            width=15,

            height=2,

            command=lambda: self.set_gender("남성")

        ).pack(side="left", padx=20)


        tk.Button(

            btn_frame,

            text="여성 (Female)",

            font=("Helvetica", 18),

            width=15,

            height=2,

            command=lambda: self.set_gender("여성")

        ).pack(side="left", padx=20)


    def set_gender(self, gender):

        self.brain.gender = gender

        self.show_category_page()


    # =====================================================
    # 카테고리 선택
    # =====================================================

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

            list(set(item['category'] for item in self.brain.db))
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


    # =====================================================
    # 제품 목록 화면
    # =====================================================

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

            if item['category'] == category
        ]


        list_frame = tk.Frame(
            self.content_container,
            bg="#1E1E1E"
        )

        list_frame.pack(pady=10)


        for prod in products:

            btn = tk.Button(

                list_frame,

                text=prod['name'],

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


    # =====================================================
    # 분석 결과 화면
    # =====================================================

    def show_result_page(self):

        self.clear_frame()

        tk.Label(

            self.content_container,

            text="📊 개인별 영양 성분 분석 결과",

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

            val = self.brain.current_nutrients.get(nutrient, 0)

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


        # =================================================
        # 영양소 상호작용 분석
        # =================================================

        if (

            self.brain.current_nutrients.get("비타민D(mcg)", 0) > 0

            and

            self.brain.current_nutrients.get("마그네슘(mg)", 0) > 0
        ):

            tk.Label(

                self.content_container,

                text="💡 비타민D와 마그네슘은 함께 섭취 시 도움이 될 수 있습니다.",

                font=("Helvetica", 15),

                fg="#00FFCC",

                bg="#1E1E1E"

            ).pack()


        if (

            self.brain.current_nutrients.get("칼슘(mg)", 0) > 0

            and

            self.brain.current_nutrients.get("철분(mg)", 0) > 0
        ):

            tk.Label(

                self.content_container,

                text="⚠️ 칼슘은 철분 흡수를 방해할 수 있습니다.",

                font=("Helvetica", 15),

                fg="orange",

                bg="#1E1E1E"

            ).pack()


        # =================================================
        # 최종 결과
        # =================================================

        final_msg = (

            "🚨 일부 성분이 상한 섭취량을 초과했습니다!"

            if any_danger

            else

            "✅ 모든 성분이 안전 범위입니다."
        )


        tk.Label(

            self.content_container,

            text=final_msg,

            font=("Helvetica", 22, "bold"),

            bg="#E74C3C" if any_danger else "#2ECC71",

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
# [4] 실행
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    # =============================================
    # CSV 파일 이름
    #
    # 나중에:
    # 실제 DB / 서버 / API 연동 가능
    # =============================================

    brain = KioskBrain("supplements_db.csv")

    app = KioskApp(root, brain)

    root.mainloop()
