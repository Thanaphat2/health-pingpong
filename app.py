from flask import Flask, render_template, request, jsonify
from google import genai
import json

app = Flask(__name__)
app.secret_key = 'health_pingpong_secret_key'

api_key = "AQ.Ab8RN6Lk_d4FPuPVVB1iIXQMkicc46RT4ToMxelqjgaPJLPbsg"

try:
    client = genai.Client(api_key=api_key) if api_key else genai.Client()
except Exception:
    client = None


def evaluate_pingpong_7_colors(sugar, sys, dia, smoke, alcohol, exercise, complication, underlying_diseases=None):
    """ประเมินสุขภาพตามเกณฑ์ปิงปอง 7 สี (อ้างอิงตามอินโฟกราฟิกทางการ) พร้อมรองรับผู้มีโรคประจำตัว"""
    if underlying_diseases is None:
        underlying_diseases = []

    try:
        # ตรวจสอบว่ามีโรคประจำตัวเรื้อรังหรือไม่ (เบาหวาน, ความดัน, ไขมัน, ไต, หัวใจ)
        has_disease = any(
            d in underlying_diseases for d in ["diabetes", "hypertension", "kidney", "heart", "dyslipidemia"])

        # 1. สีดำ: โรคแทรกซ้อน (น้ำตาล 125-154, ความดัน 160-179/100-109 และมีภาวะแทรกซ้อน) หรือเลือก complication เป็น yes
        if complication == "yes" or (
                (125 <= sugar <= 154) and (160 <= sys <= 179 or 100 <= dia <= 109) and complication == "yes"):
            return {
                "level": "โรคแทรกซ้อน (สีดำ)",
                "color_name": "โรคแทรกซ้อน",
                "color_code": "#1c1917",  # สีดำ สไตล์ Tailwind stone-900
                "bg_color": "bg-stone-900 text-white",
                "badge_color": "bg-neutral-900 text-white border border-neutral-700",
                "border_color": "border-black",
                "description": "ตรวจพบภาวะแทรกซ้อนจากโรคเรื้อรัง (เบาหวาน/ความดันโลหิตสูง)",
                "advice": [
                    "ระยะวิกฤต: เมื่อมีสัญญาณเตือน (เจ็บหน้าอก หอบเหนื่อย ปากเบี้ยว แขนขาอ่อนแรง) นำส่งโรงพยาบาลทันทีหรือโทร 1669",
                    "ปฏิบัติตามคำสั่งและพบแพทย์ตามนัดอย่างเคร่งครัด พร้อมนำรายการยาปัจจุบันติดตัวไปด้วย"
                ],
                "action": "พบแพทย์ด่วนที่สุด (Urgent Medical Attention)"
            }

        # 2. สีแดง: วิกฤต (น้ำตาล >= 183 หรือ ความดัน >= 180/110)
        elif sugar >= 183 or sys >= 180 or dia >= 110:
            return {
                "level": "วิกฤต (สีแดง)",
                "color_name": "วิกฤต",
                "color_code": "#dc2626",  # สีแดง (red-600)
                "bg_color": "bg-red-600 text-white",
                "badge_color": "bg-red-700 text-white",
                "border_color": "border-red-600",
                "description": "ระดับน้ำตาลในเลือดหรือความดันโลหิตสูงอยู่ในระดับวิกฤตอันตราย",
                "advice": [
                    "1) รับประทานยาต่อเนื่องตามแพทย์สั่งอย่างเคร่งครัด ห้ามหยุดยาเอง",
                    "2) ควบคุมอาหารตามหลัก DASH Diet ลดหวาน มัน เค็มจัด และงดบุหรี่/สุราเด็ดขาด",
                    "3) พบแพทย์ตามนัดทุก 4 สัปดาห์ หรือรีบไปพบแพทย์ทันทีหากมีอาการผิดปกติรุนแรง"
                ],
                "action": "พบแพทย์ทันที / ห้องฉุกเฉิน"
            }

        # 3. สีส้ม: อันตราย (น้ำตาล 155-182 หรือ ความดัน 160-179/100-109)
        elif (155 <= sugar <= 182) or (160 <= sys <= 179) or (100 <= dia <= 109):
            return {
                "level": "อันตราย (สีส้ม)",
                "color_name": "อันตราย",
                "color_code": "#f97316",  # สีส้ม (orange-500)
                "bg_color": "bg-orange-500 text-white",
                "badge_color": "bg-orange-600 text-white",
                "border_color": "border-orange-500",
                "description": "ระดับน้ำตาลหรือความดันโลหิตสูงมาก เสี่ยงต่อภาวะแทรกซ้อนเฉียบพลัน",
                "advice": [
                    "1) ควบคุมอาหารอย่างเข้มงวดตามหลัก DASH Diet (เน้นผัก ผลไม้ ธัญพืช ลดโซเดียมไม่เกิน 2,000 มก./วัน)",
                    "2) ตรวจภาวะแทรกซ้อนทางตา ไต หัวใจ อย่างน้อยปีละ 1 ครั้งตามคำแนะนำแพทย์",
                    "3) พบแพทย์ตามนัดทุก 4 สัปดาห์ และจดบันทึกค่าความดัน/น้ำตาลจากบ้านมาให้แพทย์ดูด้วย"
                ],
                "action": "พบแพทย์ภายใน 1-2 วัน"
            }

        # 4. สีเหลือง: เฝ้าระวัง (น้ำตาล 125-154 หรือ ความดัน 140-159/90-99)
        elif (125 <= sugar <= 154) or (140 <= sys <= 159) or (90 <= dia <= 99):
            return {
                "level": "เฝ้าระวัง (สีเหลือง)",
                "color_name": "เฝ้าระวัง",
                "color_code": "#facc15",  # สีเหลือง (yellow-400)
                "bg_color": "bg-yellow-400 text-slate-900",
                "badge_color": "bg-yellow-400 text-gray-900",
                "border_color": "border-yellow-400",
                "description": "ระดับน้ำตาลหรือความดันโลหิตสูงกว่าเกณฑ์ปกติ เริ่มเข้าสู่โซนอันตราย",
                "advice": [
                    "1) ปรับเปลี่ยนพฤติกรรมตามหลัก 3 อ. 3 ลด: อาหาร DASH Diet, ออกกำลังกายสม่ำเสมอ, จัดการอารมณ์ไม่ให้เครียด และลด ละ เลิกบุหรี่กับสุรา",
                    "2) มาพบแพทย์ตามนัดทุก 2-3 เดือนเพื่อติดตามอาการและประเมินผลเลือด/ความดันอย่างใกล้ชิด",
                    "3) นอนหลับพักผ่อนให้เพียงพอ 6-8 ชั่วโมง และหมั่นวัดค่าสุขภาพที่บ้านสม่ำเสมอ"
                ],
                "action": "พบแพทย์ตามนัด / ปรับพฤติกรรม"
            }

        # 5. กลุ่มควบคุมได้ดีหรือปกติ (น้ำตาล < 125 และ ความดัน < 139/89)
        elif sugar < 125 and sys < 139 and dia < 89:
            # ถ้ามีโรคประจำตัว แต่คุมค่าได้ตามเกณฑ์ -> ได้ "สีเขียวเข้ม (คุมได้ดี)"
            if has_disease or sugar >= 100 or sys >= 120 or dia >= 80:
                return {
                    "level": "คุมได้ดี (สีเขียวเข้ม)",
                    "color_name": "คุมได้ดี",
                    "color_code": "#047857",  # สีเขียวเข้ม (emerald-700)
                    "bg_color": "bg-emerald-700 text-white",
                    "badge_color": "bg-emerald-800 text-white",
                    "border_color": "border-emerald-700",
                    "description": "มีโรคประจำตัว แต่สามารถควบคุมระดับน้ำตาลและความดันให้อยู่ในเกณฑ์ได้ดี",
                    "advice": [
                        "1) 3 อ. 3 ลด และรับประทานยาต่อเนื่องตามแพทย์สั่ง",
                        "2) พบแพทย์ทุก 2-3 เดือน และลดการบริโภคน้ำตาล/อาหารมันเค็ม"
                    ],
                    "action": "รักษาพฤติกรรมต่อเนื่อง / พบแพทย์ตามนัด"
                }
            else:
                # ถ้าไม่มีโรคประจำตัว และค่าต่ำกว่าเกณฑ์ปกติจริง ๆ (น้ำตาล < 100 และ ความดัน < 120/80) -> ได้ "สีขาว (ปกติ)"
                return {
                    "level": "ปกติ (สีขาว)",
                    "color_name": "ปกติ",
                    "color_code": "#10b981",  # สีเขียว/ขาวสะอาดตา (emerald-500)
                    "bg_color": "bg-emerald-500 text-white",
                    "badge_color": "bg-gray-100 text-gray-800",
                    "border_color": "border-gray-300",
                    "description": "ระดับน้ำตาลและแรงดันโลหิตอยู่ในเกณฑ์ปกติ สุขภาพดีเยี่ยม",
                    "advice": [
                        "1) คงพฤติกรรม 3 อ. 3 ลด (ทานผักผลไม้ ออกกำลังกายสม่ำเสมอ อารมณ์แจ่มใส งดบุหรี่และสุรา)",
                        "2) ตรวจสุขภาพวัดความดันและน้ำตาลซ้ำทุก 1 ปีเพื่อรักษาสุขภาพให้แข็งแรงระยะยาว"
                    ],
                    "action": "รักษาสุขภาพอย่างต่อเนื่อง"
                }

        # 6. สีเขียวอ่อน: เสี่ยง (น้ำตาล 100-125 หรือ ความดัน 120-139/80-89 หรือมีพฤติกรรมสูบบุหรี่/ดื่มสุรา)
        elif (100 <= sugar <= 125) or (120 <= sys <= 139) or (80 <= dia <= 89) or (smoke == "yes") or (
                alcohol == "yes"):
            if has_disease:
                return {
                    "level": "คุมได้ดี (สีเขียวเข้ม)",
                    "color_name": "คุมได้ดี",
                    "color_code": "#047857",
                    "bg_color": "bg-emerald-700 text-white",
                    "badge_color": "bg-emerald-800 text-white",
                    "border_color": "border-emerald-700",
                    "description": "มีโรคประจำตัว ควบคุมระดับน้ำตาลและความดันตามคำแนะนำแพทย์",
                    "advice": [
                        "1) 3 อ. 3 ลด และรับประทานยาต่อเนื่องตามแพทย์สั่ง",
                        "2) พบแพทย์ทุก 2-3 เดือนเพื่อติดตามอาการ"
                    ],
                    "action": "รักษาพฤติกรรมต่อเนื่อง / พบแพทย์ตามนัด"
                }
            else:
                return {
                    "level": "เสี่ยง (สีเขียวอ่อน)",
                    "color_name": "เสี่ยง",
                    "color_code": "#38bdf8",  # สีฟ้า/เขียวอ่อน (sky-400)
                    "bg_color": "bg-sky-400 text-white",
                    "badge_color": "bg-emerald-200 text-emerald-900",
                    "border_color": "border-emerald-300",
                    "description": "อยู่ในกลุ่มเสี่ยงเริ่มสูง (Pre-hypertension / Pre-diabetes หรือมีพฤติกรรมเสี่ยง)",
                    "advice": [
                        "1) ลด ละ เลิกบุหรี่และเครื่องดื่มแอลกอฮอล์อย่างเด็ดขาดเพื่อลดภาระหลอดเลือด",
                        "2) เพิ่มการออกกำลังกายแบบแอโรบิก (เช่น เดินเร็ว) ครั้งละ 30 นาที สัปดาห์ละ 3-5 วัน และควบคุมน้ำหนักตัว",
                        "3) วัดความดันและตรวจระดับน้ำตาลซ้ำทุก 1-3 เดือนเพื่อประเมินความเปลี่ยนแปลง"
                    ],
                    "action": "ปรับพฤติกรรม / ตรวจสุขภาพประจำปี"
                }
        else:
            if has_disease:
                return {
                    "level": "คุมได้ดี (สีเขียวเข้ม)",
                    "color_name": "คุมได้ดี",
                    "color_code": "#047857",
                    "bg_color": "bg-emerald-700 text-white",
                    "badge_color": "bg-emerald-800 text-white",
                    "border_color": "border-emerald-700",
                    "description": "มีโรคประจำตัว ติดตามอาการและพบแพทย์สม่ำเสมอ",
                    "advice": ["ปฏิบัติตามคำแนะนำของแพทย์อย่างเคร่งครัด"],
                    "action": "พบแพทย์ตามนัด"
                }
            return {
                "level": "ปกติ (สีขาว)",
                "color_name": "ปกติ",
                "color_code": "#10b981",
                "bg_color": "bg-emerald-500 text-white",
                "badge_color": "bg-gray-100 text-gray-800",
                "border_color": "border-gray-300",
                "description": "ระดับน้ำตาลและแรงดันโลหิตอยู่ในเกณฑ์ปกติ",
                "advice": ["รักษาสุขภาพอย่างต่อเนื่อง"],
                "action": "รักษาสุขภาพ"
            }
    except Exception:
        return None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    result = None
    form_data = {}
    if request.method == 'POST':
        try:
            name = request.form.get('name', 'ผู้ใช้งานทั่วไป')
            sugar = float(request.form.get('sugar', 90))
            sys = int(request.form.get('sys', 120))
            dia = int(request.form.get('dia', 80))
            smoke = request.form.get('smoke', 'no')
            alcohol = request.form.get('alcohol', 'no')
            exercise = request.form.get('exercise', 'moderate')
            complication = request.form.get('complication', 'no')

            # รับค่าโรคประจำตัวจากฟอร์มแบบ Checkbox หลายตัวเลือก
            underlying_diseases = request.form.getlist('underlying_disease')

            form_data = {
                'name': name, 'sugar': sugar, 'sys': sys, 'dia': dia,
                'smoke': smoke, 'alcohol': alcohol, 'exercise': exercise,
                'complication': complication, 'underlying_disease': underlying_diseases
            }

            # ประเมินผลสุขภาพโดยส่งตัวแปรโรคประจำตัวเข้าไปด้วย
            evaluation = evaluate_pingpong_7_colors(sugar, sys, dia, smoke, alcohol, exercise, complication,
                                                    underlying_diseases)

            # เรียก AI แนะนำเพิ่มเติม
            ai_advice = ""
            if client and evaluation:
                try:
                    prompt = f"""
                    คุณคือพยาบาลผู้เชี่ยวชาญด้านสุขภาพดิจิทัล ให้คำแนะนำตามหลักเกณฑ์ปิงปองจราจรชีวิต 7 สี และหลักโภชนาการ DASH Diet
                    ข้อมูลผู้รับการประเมิน:
                    - ชื่อ: {name}
                    - น้ำตาล: {sugar} mg/dl, ความดัน: {sys}/{dia} mmHg
                    - พฤติกรรม: สูบบุหรี่ ({smoke}), ดื่มสุรา ({alcohol})
                    - โรคประจำตัว: {', '.join(underlying_diseases) if underlying_diseases else 'ไม่มี'}
                    - กลุ่มสีประเมิน: {evaluation['color_name']}
                    ให้เขียนคำแนะนำสั้นๆ กระชับ เป็นกันเอง ภาษาไทยอบอุ่น เป็นกำลังใจ เน้นย้ำการปฏิบัติตัว 3 อ. 3 ลด และการมาพบแพทย์ตามนัด
                    """
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    ai_advice = response.text
                except Exception as e:
                    ai_advice = f"ระบบ AI ไม่สามารถสร้างคำแนะนำได้ในขณะนี้"

            if evaluation:
                result = {
                    "name": name, "sugar": sugar, "sys": sys, "dia": dia,
                    "smoke": smoke, "alcohol": alcohol, "complication": complication,
                    "underlying_disease": underlying_diseases,
                    "smoke_text": "สูบบุหรี่" if smoke == "yes" else "ไม่สูบ",
                    "alcohol_text": "ดื่มสุรา" if alcohol == "yes" else "ไม่ดื่ม",
                    "evaluation": evaluation,
                    "ai_advice": ai_advice,
                    "level": evaluation['level'], "description": evaluation['description'],
                    "bg_color": evaluation['bg_color'], "border_color": evaluation['border_color'],
                    "badge_color": evaluation['badge_color'], "advice": evaluation['advice'],
                    "action": evaluation['action']
                }
            else:
                result = {"error": "ข้อมูลไม่ถูกต้อง"}
        except ValueError:
            result = {"error": "กรุณากรอกข้อมูลตัวเลขให้ถูกต้อง"}

    return render_template('assessment.html', result=result, form_data=form_data)


@app.route('/api/analyze-food', methods=['POST'])
def analyze_food():
    data = request.get_json()
    query = data.get('query', '').strip()

    if not client:
        return jsonify({"error": "ระบบ AI ไม่พร้อมใช้งาน"}), 500

    try:
        prompt = f"""
        คุณคือผู้เชี่ยวชาญด้านโภชนาการและการควบคุมโรคเรื้อรัง ให้วิเคราะห์อาหารหรือเครื่องปรุงรส: "{query}"

        อ่านกฎการบังคับใช้หน่วยวัดตามประเภทอาหารด้านล่างนี้แล้วปฏิบัติตามอย่างเคร่งครัด 100% ห้ามสลับหมวดเด็ดขาด:
        1. หากเป็น "ผลไม้ผลเดี่ยว" (เช่น กล้วย, ส้ม, แอปเปิ้ล, มะม่วง, ฝรั่ง) -> บังคับใช้หน่วยเป็น **"ผล"** หรือ **"ลูก"** เท่านั้น
        2. หากเป็น "ผลไม้พวง / ผลไม้ลูกเล็กๆ ที่นับเป็นเม็ดไม่ได้" (เช่น องุ่น, ลำไย, เบอร์รี่) -> บังคับใช้หน่วยเป็น **"กรัม"** หรือ **"ขีด"** เท่านั้น ห้ามใช้ผลหรือทัพพีเด็ดขาด
        3. หากเป็น "ข้าว แป้ง เส้น ขนมจีน" (เช่น ข้าวสวย, ข้าวเหนียว, เส้นหมี่, โจ๊ก) -> บังคับใช้หน่วยเป็น **"ทัพพี"** เท่านั้น ห้ามใช้ผลหรือจาน
        4. หากเป็น "เนื้อสัตว์ เมนูปิ้ง/ย่าง/ทอด" (เช่น หมูย่าง, หมูทอด, ไก่ทอด, ปลา) -> บังคับใช้หน่วยเป็น **"กรัม"**, **"ขีด"** หรือ **"ชิ้น"** เท่านั้น
        5. หากเป็น "เครื่องปรุงรส" (เช่น น้ำปลา, เกลือ, น้ำตาล) -> บังคับใช้หน่วยเป็น **"ช้อนชา"** หรือ **"ช้อนโต๊ะ"** เท่านั้น

        คุณต้องตอบกลับมาในรูปแบบ JSON ที่มีคีย์ (Keys) ตรงตามนี้เท่านั้น ห้ามใส่เครื่องหมายอื่นครอบโค้ด JSON:
        {{
            "normal_amount": "ระบุปริมาณที่แนะนำสำหรับคนปกติโดยใช้หน่วยที่ถูกต้องตามกฎข้างต้นอย่างเคร่งครัด",
            "normal_desc": "คำแนะนำเพิ่มเติมสั้นๆ สำหรับคนปกติ",
            "patient_amount": "ระบุปริมาณจำกัดที่ทานได้สำหรับผู้ป่วยโรคเรื้อรังโดยใช้หน่วยที่ถูกต้อง ห้ามใช้คำว่าหน่วยบริโภคหรือส่วน",
            "patient_desc": "ข้อควรระวังตามหลัก DASH Diet และปริมาณโซเดียมหรือไขมัน/น้ำตาล"
        }}
        """

        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        text_response = response.text.strip()

        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]

        result_json = json.loads(text_response.strip())
        return jsonify(result_json)

    except Exception as e:
        q_lower = query.lower()
        if any(f in q_lower for f in ["องุ่น", "ลำไย"]):
            fallback_normal = "150 - 200 กรัม (1.5 - 2 ขีด)"
            fallback_patient = "จำกัดปริมาณไม่เกิน 100 กรัม (1 ขีด) ต่อครั้ง"
        elif any(f in q_lower for f in ["กล้วย", "ส้ม", "แอปเปิ้ล", "มะม่วง", "ฝรั่ง"]):
            fallback_normal = "1 - 2 ผล"
            fallback_patient = "จำกัดปริมาณไม่เกิน 1 ผลต่อครั้ง"
        elif any(r in q_lower for r in ["ข้าว", "เส้น", "ก๋วยเตี๋ยว", "ขนมจีน", "โจ๊ก"]):
            fallback_normal = "2 - 3 ทัพพี"
            fallback_patient = "จำกัดไม่เกิน 1 ทัพพีต่อมื้อ"
        elif any(m in q_lower for m in ["หมู", "ไก่", "เนื้อ", "ปลา", "ย่าง", "ทอด", "ผัด"]):
            fallback_normal = "150 - 200 กรัม หรือ 1 - 2 ชิ้น"
            fallback_patient = "จำกัดปริมาณไม่เกิน 100 กรัม หรือ 1 ชิ้นเล็ก"
        else:
            fallback_normal = "1 - 2 ทัพพี"
            fallback_patient = "จำกัดปริมาณไม่เกิน 1 ทัพพี"

        return jsonify({
            "normal_amount": fallback_normal,
            "normal_desc": "รับประทานในปริมาณที่พอเหมาะและออกกำลังกายสม่ำเสมอ",
            "patient_amount": fallback_patient,
            "patient_desc": "ควรควบคุมปริมาณน้ำตาล โซเดียม และไขมันตามหลัก DASH Diet"
        })


@app.route('/dash-diet')
def dash_diet():
    return render_template('dash-diet.html')


@app.route('/skt')
def skt():
    return render_template('skt.html')


@app.route('/complications')
def complications():
    return render_template('complications.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
