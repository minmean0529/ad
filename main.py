import csv
import sys

# =========================================================
# [1] 영양소 일일 상한선 (보건복지부 기준)
# =========================================================

UPPER_LIMITS = {
    "비타민B6(mg)": 100,
    "비타민D(mcg)": 100,
    "아연(mg)": 35,
    "비타민C(mg)": 2000,
    "비타민A(mcg)": 3000,
    "마그네슘(mg)": 350,
    "철분(mg)": 45,
    "칼슘(mg)": 2500
}

# =========================================================
# [2] 영양소 상호작용 규칙
# =========================================================

INTERACTION_RULES = [

    # -------------------------------------------------
    # 철분 관련
    # -------------------------------------------------

    {
        "nutrients": ["철분(mg)", "칼슘(mg)"],
        "type": "위험",
        "message": "철분과 칼슘은 동일한 흡수 통로(DMT1)를 사용하여 서로의 흡수를 방해할 수 있습니다."
    },

    {
        "nutrients": ["철분(mg)", "아연(mg)"],
        "type": "위험",
        "message": "철분과 아연은 미네랄 간 흡수 경쟁이 발생하여 흡수 효율이 감소할 수 있습니다."
    },

    {
        "nutrients": ["철분(mg)", "마그네슘(mg)"],
        "type": "위험",
        "message": "철분과 마그네슘을 함께 복용하면 철분 흡수율이 감소하고 소화 장애가 발생할 수 있습니다."
    },

    {
        "nutrients": ["철분(mg)", "단백질(g)"],
        "type": "주의",
        "message": "단백질 보충제에 포함된 칼슘·아연·마그네슘 등이 철분 흡수를 방해할 수 있습니다."
    },

    # -------------------------------------------------
    # 칼슘 관련
    # -------------------------------------------------

    {
        "nutrients": ["칼슘(mg)", "마그네슘(mg)"],
        "type": "주의",
        "message": "칼슘과 마그네슘을 고함량으로 동시에 복용하면 흡수 경쟁이 발생할 수 있습니다."
    },

    {
        "nutrients": ["칼슘(mg)", "아연(mg)"],
        "type": "주의",
        "message": "고용량 칼슘은 아연의 체내 흡수를 방해할 수 있습니다."
    },

    {
        "nutrients": ["비타민D(mcg)", "칼슘(mg)"],
        "type": "주의",
        "message": "비타민D는 칼슘 흡수를 증가시키므로 과다 복용 시 혈중 칼슘 농도가 높아질 수 있습니다."
    },

    # -------------------------------------------------
    # 비타민 관련
    # -------------------------------------------------

    {
        "nutrients": ["비타민C(mg)", "비타민B12(mcg)"],
        "type": "주의",
        "message": "고용량 비타민C는 비타민B12의 안정성 및 흡수를 방해할 수 있습니다."
    },

    {
        "nutrients": ["비타민D(mcg)", "비타민A(mcg)"],
        "type": "위험",
        "message": "비타민A 과다 복용은 비타민D 작용을 방해할 수 있으며 간독성·두통·탈모·뼈 약화 위험이 있습니다."
    },

    {
        "nutrients": ["비타민C(mg)", "마그네슘(mg)"],
        "type": "주의",
        "message": "비타민C와 마그네슘을 고용량으로 함께 복용하면 설사나 속 쓰림이 발생할 수 있습니다."
    },

    # -------------------------------------------------
    # 유산균 관련
    # -------------------------------------------------

    {
        "nutrients": ["프로바이오틱스(CFU)", "비타민C(mg)"],
        "type": "주의",
        "message": "강한 산성 환경으로 인해 유산균 생존율이 감소할 수 있습니다."
    },

    # -------------------------------------------------
    # 오메가3 관련
    # -------------------------------------------------

    {
        "nutrients": ["EPA+DHA(mg)", "비타민E(mgα-TE)"],
        "type": "주의",
        "message": "고함량으로 함께 복용 시 멍·코피·출혈 위험이 증가할 수 있습니다."
    },

    # -------------------------------------------------
    # 루테인 관련
    # -------------------------------------------------

    {
        "nutrients": ["비타민A(mcg)", "루테인(mg)"],
        "type": "추천",
        "message": "비타민A와 루테인은 모두 눈 건강에 도움을 주는 성분으로 기능이 일부 유사합니다."
    }
]
# =========================================================
# [3] 안전한 숫자 변환 함수
# =========================================================

def safe_float(value):

    try:
        if value is None:
            return 0.0

        value = str(value).strip()

        if value == "":
            return 0.0

        return float(value)

    except:
        return 0.0


# =========================================================
# [4] 메인 클래스
# =========================================================

class KioskBrain:

    def __init__(self, csv_file_path):

        self.db = self.load_database(csv_file_path)

        # 현재 장바구니
        self.cart = []

        # 현재 누적 영양소
        self.current_nutrients = {}


    # =====================================================
    # CSV 데이터베이스 로드
    # =====================================================

    def load_database(self, file_path):

        db = {}

        try:

            with open(file_path, 'r', encoding='utf-8-sig') as f:

                reader = csv.DictReader(f)

                for i, row in enumerate(reader):

                    # -----------------------------------
                    # 실제 바코드 사용
                    # CSV에 "바코드" 컬럼 필요
                    # -----------------------------------

                    barcode = row["바코드"].strip()

                    db[barcode] = {

                        "name": row["제품명"].strip(),

                        "category": row["카테고리"].strip(),

                        # 브랜드 컬럼 없으면 제거 가능
                        "brand": row["브랜드"].strip(),

                        "nutrients": {

                            "베타카로틴(mcg)": safe_float(row["베타카로틴(mcg)"]),

                            "비타민A(mcg)": safe_float(row["비타민A(mcg)"]),

                            "비타민C(mg)": safe_float(row["비타민C(mg)"]),

                            "비타민D(mcg)": safe_float(row["비타민D(mcg)"]),

                            "식물성 비타민D2(mcg)": safe_float(row["식물성 비타민D2(mcg)"]),

                            "동물성 비타민D3(mcg)": safe_float(row["동물성 비타민D3(mcg)"]),

                            "비타민E(mgα-TE)": safe_float(row["비타민E(mgα-TE)"]),

                            "비타민K(mcg)": safe_float(row["비타민K(mcg)"]),

                            "비타민B1(mg)": safe_float(row["비타민B1(mg)"]),

                            "비타민B2(mg)": safe_float(row["비타민B2(mg)"]),

                            "비타민B3(mg)": safe_float(row["비타민B3(mg)"]),

                            "비타민B6(mg)": safe_float(row["비타민B6(mg)"]),

                            "비타민B9(mcg DFE)": safe_float(row["비타민B9(mcg DFE)"]),

                            "비타민B12(mcg)": safe_float(row["비타민B12(mcg)"]),

                            "비타민B7(mcg)": safe_float(row["비타민B7(mcg)"]),

                            "비타민B5(mg)": safe_float(row["비타민B5(mg)"]),

                            "콜린(mg)": safe_float(row["콜린(mg)"]),

                            "요오드(mcg)": safe_float(row["요오드(mcg)"]),

                            "철분(mg)": safe_float(row["철분(mg)"]),

                            "아연(mg)": safe_float(row["아연(mg)"]),

                            "마그네슘(mg)": safe_float(row["마그네슘(mg)"]),

                            "셀레늄(mcg)": safe_float(row["셀레늄(mcg)"]),

                            "구리(mcg)": safe_float(row["구리(mcg)"]),

                            "망간(mg)": safe_float(row["망간(mg)"]),

                            "크롬(mcg)": safe_float(row["크롬(mcg)"]),

                            "소듐(mg)": safe_float(row["소듐(mg)"]),

                            "포타슘(mg)": safe_float(row["포타슘(mg)"]),

                            "인(mg)": safe_float(row["인(mg)"]),

                            "D-감마 토코페롤(mg)": safe_float(row["D-감마 토코페롤(mg)"]),

                            "붕소(mg)": safe_float(row["붕소(mg)"]),

                            "몰리브덴(mcg)": safe_float(row["몰리브덴(mcg)"]),

                            "프로바이오틱스(CFU)": safe_float(row["프로바이오틱스(CFU)"]),

                            "칼슘(mg)": safe_float(row["칼슘(mg)"]),

                            "EPA+DHA(mg)": safe_float(row["EPA+DHA(mg)"]),

                            "단백질(g)": safe_float(row["단백질(g)"]),

                            "루테인(mg)": safe_float(row["루테인(mg)"]),

                            "총지아잔틴(mg)": safe_float(row["총지아잔틴(mg)"]),

                            "아스타잔틴(mg)": safe_float(row["아스타잔틴(mg)"]),

                            "L-류신(mg)": safe_float(row["L-류신(mg)"]),

                            "L-글루타민(mg)": safe_float(row["L-글루타민(mg)"]),

                            "L-이소류신(mg)": safe_float(row["L-이소류신(mg)"]),

                            "L-발린(mg)": safe_float(row["L-발린(mg)"])
                        }
                    }

            print(f"✅ 데이터베이스 로드 완료! (총 {len(db)}개 제품)")
            return db

        except Exception as e:

            print(f"❌ CSV 로드 에러: {e}")
            print("파일 이름 또는 CSV 컬럼명을 확인해주세요.")
            sys.exit(1)


    # =====================================================
    # 영양소 누적
    # =====================================================

    def accumulate_nutrients(self, item):

        for nutrient, value in item["nutrients"].items():

            # current_nutrients에 없으면 자동 생성
            if nutrient not in self.current_nutrients:

                self.current_nutrients[nutrient] = 0.0

            self.current_nutrients[nutrient] += value


    # =====================================================
    # 바코드 스캔
    # =====================================================

    def scan_item(self, barcode):

        if barcode not in self.db:
            return "⚠️ 등록되지 않은 바코드입니다."

        item = self.db[barcode]

        self.cart.append(item)

        self.accumulate_nutrients(item)

        return self.check_warnings(item["name"])


    # =====================================================
    # 상한선 검사 + 상호작용 검사
    # =====================================================

    def check_warnings(self, latest_item):

        warnings = []

        # -------------------------------
        # 상한선 검사
        # -------------------------------

        for nutrient, limit in UPPER_LIMITS.items():

            current_val = self.current_nutrients.get(nutrient, 0)

            if current_val > limit:

                warnings.append(
                    f"🚨 [위험] {nutrient} 상한선 초과 "
                    f"({current_val:.1f} / {limit})"
                )

            elif current_val > (limit * 0.7):

                warnings.append(
                    f"🟡 [주의] {nutrient} 상한선 근접 "
                    f"({current_val:.1f} / {limit})"
                )


        # -------------------------------
        # 영양소 상호작용 검사
        # -------------------------------

        for rule in INTERACTION_RULES:

            found = True

            for nutrient in rule["nutrients"]:

                if self.current_nutrients.get(nutrient, 0) <= 0:

                    found = False
                    break

            if found:

                if rule["type"] == "위험":

                    warnings.append(
                        f"🚨 [영양소 충돌] {rule['message']}"
                    )

                elif rule["type"] == "추천":

                    warnings.append(
                        f"💡 [추천 조합] {rule['message']}"
                    )


        # -------------------------------
        # 출력
        # -------------------------------

        if not warnings:

            return f"✅ [{latest_item}] 스캔 완료. 안전한 조합입니다."

        else:

            warning_msg = "\n".join(warnings)

            return (
                f"❌ [{latest_item}] 스캔 경고!\n\n"
                f"{warning_msg}"
            )


    # =====================================================
    # 현재 장바구니 출력
    # =====================================================

    def show_cart(self):

        print("\n🛒 [현재 복용 예정 영양제]")

        if not self.cart:

            print("비어있음")

        else:

            for item in self.cart:
                print(f"- {item['name']}")

        print("-" * 40)


# =========================================================
# [5] 실행
# =========================================================

if __name__ == "__main__":

    CSV_FILE_NAME = "supplements_db.csv"

    kiosk = KioskBrain(CSV_FILE_NAME)

    print("\n[테스트용 바코드 목록]")

    for code, info in list(kiosk.db.items())[:10]:

        print(f"바코드: {code} | 제품명: {info['name']}")

    print("\n" + "=" * 50)
    print("💊 영양제 과다복용 방지 키오스크")
    print("바코드를 입력하세요 (종료하려면 q 입력)")
    print("=" * 50)

    while True:

        # ============================================
        # 현재:
        # 키보드 입력 방식
        #
        # 나중에:
        # 바코드 스캐너 / 카메라 인식 연결 가능
        #
        # 예시:
        # barcode = scan_barcode_camera()
        #
        # OpenCV + pyzbar 사용 예정
        # ============================================

        user_input = input("\n바코드 스캔: ").strip()

        if user_input.lower() == 'q':

            print("키오스크를 종료합니다.")
            break

        result = kiosk.scan_item(user_input)

        print("\n▶ LCD 출력 화면 ◀")
        print(result)

        kiosk.show_cart()
