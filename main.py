import csv
import re
import sys

# =========================================================
# [1] 영양소 일일 상한선 (보건복지부 기준)
# =========================================================

UPPER_LIMITS = {
    "비타민B6(mg)": 100,
    "비타민D(㎍)": 100,
    "아연(mg)": 35,
    "비타민C(mg)": 2000,
    "비타민A(㎍)": 3000,
    "마그네슘(mg)": 350,
    "철분(mg)": 45,
    "칼슘(mg)": 2500
}

class KioskBrain:
    def __init__(self, csv_file_path):
        self.db = self.load_database(csv_file_path)

        #현재 장바구니
        self.cart = [] 
        # 현재 누적 영양소
        self.current_nutrients = {}

    # =====================================================
    # CSV 데이터베이스 로드
    # =====================================================

    def load_database(self, file_path):
        
        db = {}

        try:
            
            with open(file_path, 'r', encoding='utf-8') as f:
                
                reader = csv.DictReader(f)
          
                for i, row in enumerate(reader):
                
                    # -----------------------------------
                    # 나중에 실제 바코드 컬럼으로 교체
                    # 예:
                    # barcode = row["바코드"]
                    # -----------------------------------
                    
                    barcode = str(1000 + i) # 임시 바코드 발급
                    
                    db[barcode] = {
                        "name": row["제품명"].strip(),
                        
                        "category": row["카테고리"].strip(),

                         # 브랜드 컬럼 없으면 제거 가능
                        "brand": row["브랜드"].strip(),
                        
                        "nutrients": {
    
                                  "비타민A(mcg)": float(row["비타민A(mcg)"] or 0),
                                  "비타민C(mg)" : float(row["비타민C(mg)"] or 0),
                                  "베타카로틴(mcg)" : float(row["베타카로틴(mcg)"] or 0),
                                  "비타민D(mcg)": float(row["비타민D(mcg)"] or 0),
                                  "식물성 비타민D2(mcg)" : float(row["식물성 비타민D2(mcg)"] or 0),
                                  "동물성 비타민D3(mcg)" : float(row["동물성 비타민D3(mcg)"] or 0),
                                  "비타민E(mgα-TE)" : float(row["비타민E(mgα-TE)"] or 0),
                                  "비타민K(mcg)" : float(row["비타민K(mcg)"] or 0),
                                  "비타민B1(mg)" : float(row["비타민B1(mg)"] or 0),
                                  "비타민B2(mg)" : float(row["비타민B2(mg)"] or 0),
                                  "비타민B3(mg)" : float(row["비타민B3(mg)"] or 0),
                                  "비타민B6(mg)" : float(row["비타민B6(mg)"] or 0),
                                  "비타민B9(mcg DFE)" : float(row["비타민B9(mcg DFE)"] or 0),
                                  "비타민B12(mcg)" : float(row["비타민B12(mcg)"] or 0),
                                  "비타민B7(mcg)" : float(row["비타민B7(mcg)"] or 0),
                                  "비타민B5(mg)" : float(row["비타민B5(mg)"] or 0),
                                  "콜린(mg)" : float(row["콜린(mg)"] or 0),
                                  "요도드(mcg)" : float(row["요오드(mcg)"] or 0),
                                  "철분(mg)" : float(row["철분(mg)"] or 0),
                                  "아연(mg)" : float(row["아연(mg)"] or 0),
                                  "마그네슘(mg)" : float(row["마그네슘(mg)"] or 0),
                                  "셀레늄(mcg)" : flaot(row["셀레늄(mcg)"] or 0),
                                  "구리(mcg)" : float(row["구리(mcg)"] or 0),
                                  "망간(mg)" : float(row["망간(mg)"] or 0),
                                  "크롬(mcg)" : float(row["크롬(mcg)"] or 0),
                                  "소듐(mcg)" : float(row["소듐(mcg)"] or 0),
                                  "포타슘(mg)" : float(row["포타슘(mg)"] or 0),
                                  "인(mg)": float(row["인(mg)"] or 0),
                                  "D-감마 토코페롤(mg)" : float(row["D-감마 토코페롤(mg)"] or 0),
                                  "붕소(mg)" : float(row["붕소(mg)"] or 0),
                                  "몰리브덴(mcg)" : float(row["볼리브덴(mcg)"] or 0),
                                  "프로바이오틱스(CFU)" : float(row["프로바이오틱스(CFU)"] or 0),
                                  "칼슘(mg)" : float(row["칼슘(mg)"] or 0),
                                  "EPA + DHA(mg)" : float(row["EPA + DHA(mg)"] or 0),
                                  "단백질(g)" : float(row["단백질(g)"] or 0),
                                  "루테인(mg)" : float(row["루테인(mg)"] or 0),
                                  "총지아잔틴(mg)" : float(row["총지아잔틴(mg)"] or 0),
                                  "아스타잔틴(mg)" : float(row["아스타잔틴(mg)"] or 0),
                                  "L-류신(mg)" : float(row["L-류신(mg)"] or 0),
                                  "L-글루타민(mg)" : float(row["L-글루타민(mg)"] or 0),
                                  "L-이소류신(mg)" : float(row["L-이소류신(mg)"] or 0),
                                  "L-발린(mg)" : float(row["L-발린(mg)"] or 0)
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
        self.cart.append(item['name'])
        self.accumulate_nutrients(item)
        
        return self.check_warnings(item['name'])

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
                    f"🚨 [위험] {nutrient} 상한선({limit}) 초과!
                    f"({current_val}/ {limit})" )
            
                
            elif current_val > (limit * 0.7):
                warnings.append(
                    f"🟡 [주의] {nutrient} 누적량이 상한선에 근접했습니다."
                    f"({current_val}/{limit})" )

        
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
                print(f"-{item['name']")
                
        print("-" * 40)

      # =========================================================
      # [4] 실행
      # =========================================================

   

if __name__ == "__main__":
    
    CSV_FILE_NAME = "supplements_db.csv" # 파일 이름이 이거여야 해!
    
    kiosk = KioskBrain(CSV_FILE_NAME)
    
    print("\n[테스트용 바코드 목록]")
    for code, info in list(kiosk.db.items())[:10]:
        print(f"바코드: {code} | 제품명: {info['name']}")
    
    print("\n" + "="*50)
    print("💊 영양제 과다복용 방지 키오스크")
    print("바코드를 입력하세요 (종료하려면 'q' 입력)")
    print("="*50)

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

        user_input = input("\n바코드 스캔 (ex: 1000): ").strip()
        
        if user_input.lower() == 'q':
            print("키오스크를 종료합니다.")
            break
            
        result = kiosk.scan_item(user_input)
        print("\n▶ LCD 출력 화면 ◀")
        print(result)
        kiosk.show_cart()
