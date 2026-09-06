from flask import Flask, render_template, request, jsonify
from google import genai
import os
import json

app = Flask(__name__)
app.secret_key = 'health_pingpong_secret_key'

# 🔒 ดึง API Key จาก Environment Variable โดยปลอดภัย (GitHub จะไม่บล็อก)
api_key = os.environ.get("GEMINI_API_KEY", "").strip()

try:
    client = genai.Client(api_key=api_key) if api_key else None
except Exception as e:
    print(f"Gemini initialization error: {e}")
    client = None


def evaluate_pingpong_7_colors(sys, dia, smoke, alcohol, exercise, complication, underlying_diseases=None):
    """ประเมินสุขภาพตามเกณฑ์ปิงปอง 7 สี อ้างอิงตามเกณฑ์ความดันโลหิตที่กำหนด"""
    if underlying_diseases is None:
        underlying_diseases = []

    try:
        has_disease = any(
            d in underlying_diseases for d in ["diabetes", "hypertension", "kidney", "heart", "dyslipidemia"])

        # 1. สีดำ (โรคแทรกซ้อน): มีภาวะแทรกซ้อน หรือความดัน >= 160/100 mmHg ร่วมกับมีภาวะแทรกซ้อน
        if complication == "yes" or ((sys >= 160 or dia >= 100) and complication == "yes"):
            return {
                "level": "โรคแทรกซ้อน (สีดำ)",
                "color_name": "โรคแทรกซ้อน",
                "color_code": "#1c1917",
                "bg_color": "bg-stone-900 text-white",
                "badge_color": "bg-neutral-900 text-white border border-neutral-700",
                "border_color": "border-black",
                "description": "ตรวจพบภาวะแทรกซ้อนจากโรคเรื้อรังร่วมกับระดับความดันโลหิตสูง",
                "advice": [
                    "1) เมื่อมีสัญญาณเตือน เช่น เจ็บหน้าอก หอบเหนื่อย ปากเบี้ยว พูดไม่ชัด แขนขาอ่อนแรง ให้นำส่งโรงพยาบาลเร็วที่สุด หรือโทร 1669",
                    "2) ปฏิบัติตามคำสั่งของแพทย์อย่างเคร่งครัด และมีผู้ดูแลใกล้ชิด"
                ],
                "action": "พบแพทย์ด่วนที่สุด / ห้องฉุกเฉิน (โทร 1669)"
            }

        # 2. สีแดง (วิกฤต): ความดันโลหิต >= 180 / 110 mmHg
        elif sys >= 180 or dia >= 110:
            return {
                "level": "วิกฤต (สีแดง)",
                "color_name": "วิกฤต",
                "color_code": "#dc2626",
                "bg_color": "bg-red-600 text-white",
                "badge_color": "bg-red-700 text-white",
                "border_color": "border-red-600",
                "description": "ระดับความดันโลหิตสูงอยู่ในระดับวิกฤตอันตราย",
                "advice": [
                    "1) 3 อ. 3 ลด",
                    "2) รับประทานยาต่อเนื่อง",
                    "3) ลดการบริโภคหวาน มัน เค็ม และงดสูบบุหรี่/สุราเด็ดขาด",
                    "4) ตรวจภาวะแทรกซ้อนทางตา ไต หัวใจ เท้า อย่างน้อยปีละ 1 ครั้ง",
                    "5) พบแพทย์ตามนัดทุก 4 สัปดาห์ หรือเมื่อมีอาการผิดปกติ",
                    "6) ได้รับการติดตามเยี่ยมบ้าน"
                ],
                "action": "พบแพทย์ทันที"
            }

        # 3. สีส้ม (อันตราย): ความดันโลหิต 160-179 / 100-109 mmHg
        elif (160 <= sys <= 179) or (100 <= dia <= 109):
            return {
                "level": "อันตราย (สีส้ม)",
                "color_name": "อันตราย",
                "color_code": "#f97316",
                "bg_color": "bg-orange-500 text-white",
                "badge_color": "bg-orange-600 text-white",
                "border_color": "border-orange-500",
                "description": "ระดับความดันโลหิตสูงมาก เสี่ยงต่อภาวะแทรกซ้อน",
                "advice": [
                    "1) 3 อ. 3 ลด",
                    "2) รับประทานยาต่อเนื่อง",
                    "3) ลดการบริโภคหวาน, มัน, เค็ม",
                    "4) ตรวจภาวะแทรกซ้อนทางตา ไต หัวใจ เท้า อย่างน้อยปีละ 1 ครั้ง",
                    "5) พบแพทย์ตามนัดทุก 4 สัปดาห์ หรือเมื่อมีอาการผิดปกติ",
                    "6) ได้รับการติดตามเยี่ยมบ้าน"
                ],
                "action": "พบแพทย์ภายใน 1-2 วัน"
            }

        # 4. สีเหลือง (เฝ้าระวัง): ความดันโลหิต 140-159 / 90-99 mmHg
        elif (140 <= sys <= 159) or (90 <= dia <= 99):
            return {
                "level": "เฝ้าระวัง (สีเหลือง)",
                "color_name": "เฝ้าระวัง",
                "color_code": "#facc15",
                "bg_color": "bg-yellow-400 text-slate-900",
                "badge_color": "bg-yellow-400 text-gray-900",
                "border_color": "border-yellow-400",
                "description": "ระดับความดันโลหิตสูงกว่าเกณฑ์ปกติ เข้าสู่โซนเฝ้าระวัง",
                "advice": [
                    "1) 3 อ. 3 ลด",
                    "2) รับประทานยาต่อเนื่อง",
                    "3) พบแพทย์ทุก 2-3 เดือน",
                    "4) ลดการบริโภคน้ำตาล มัน เค็ม",
                    "5) ตรวจภาวะแทรกซ้อนทางตา ไต หัวใจ เท้า อย่างน้อยปีละ 1 ครั้ง"
                ],
                "action": "พบแพทย์ตามนัด / ปรับพฤติกรรม"
            }

        # 5. สีเขียวเข้ม (คุมได้ดี): มีโรคประจำตัว (ความดันฯ) และควบคุมความดันโลหิตได้ < 139 / 89 mmHg
        elif has_disease and (sys < 140 and dia < 90):
            return {
                "level": "คุมได้ดี (สีเขียวเข้ม)",
                "color_name": "คุมได้ดี",
                "color_code": "#047857",
                "bg_color": "bg-emerald-700 text-white",
                "badge_color": "bg-emerald-800 text-white",
                "border_color": "border-emerald-700",
                "description": "มีโรคประจำตัว แต่สามารถควบคุมระดับความดันโลหิตให้อยู่ในเกณฑ์ได้ดี",
                "advice": [
                    "1) 3 อ. 3 ลด",
                    "2) รับประทานยาต่อเนื่อง",
                    "3) พบแพทย์ทุก 2-3 เดือน",
                    "4) ลดการบริโภคน้ำตาลสำหรับผู้ป่วยเบาหวาน",
                    "5) ลดการบริโภคอาหารเค็มสำหรับผู้ป่วยความดันโลหิตสูง"
                ],
                "action": "รักษาพฤติกรรมต่อเนื่อง / พบแพทย์ตามนัด"
            }

        # 6. สีเขียวอ่อน (เสี่ยง): ความดันโลหิต 120-139 / 80-89 mmHg
        elif (120 <= sys <= 139) or (80 <= dia <= 89):
            return {
                "level": "เสี่ยง (สีเขียวอ่อน)",
                "color_name": "เสี่ยง",
                "color_code": "#38bdf8",
                "bg_color": "bg-sky-400 text-white",
                "badge_color": "bg-emerald-200 text-emerald-900",
                "border_color": "border-emerald-300",
                "description": "อยู่ในกลุ่มเสี่ยงเริ่มสูง (Pre-hypertension)",
                "advice": [
                    "1) 3 อ. 3 ลด",
                    "2) วัดความดันโลหิต และตรวจวัดความดันโลหิตทุก 1-3 เดือน",
                    "3) พบแพทย์ทุก 2-3 เดือน",
                    "4) ลดการบริโภคอาหารเค็มสำหรับผู้ป่วยความดันโลหิตสูง"
                ],
                "action": "ปรับพฤติกรรม / ตรวจติดตามสุขภาพ"
            }

        # 7. สีขาว (ปกติ): ความดันโลหิต < 120 / 80 mmHg และไม่มีโรคประจำตัว
        elif sys < 120 and dia < 80 and not has_disease:
            return {
                "level": "ปกติ (สีขาว)",
                "color_name": "ปกติ",
                "color_code": "#10b981",
                "bg_color": "bg-emerald-500 text-white",
                "badge_color": "bg-gray-100 text-gray-800",
                "border_color": "border-gray-300",
                "description": "ระดับความดันโลหิตอยู่ในเกณฑ์ปกติ สุขภาพดีเยี่ยม",
                "advice": [
                    "1) 3 อ. 3 ลด",
                    "2) ตรวจวัดความดันโลหิตทุก 1 ปี"
                ],
                "action": "รักษาสุขภาพอย่างต่อเนื่อง"
            }

        # Fallback สำรอง
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
                "description": "ระดับความดันโลหิตอยู่ในเกณฑ์ปกติ",
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
            sys = int(request.form.get('sys', 120))
            dia = int(request.form.get('dia', 80))
            smoke = request.form.get('smoke', 'no')
            alcohol = request.form.get('alcohol', 'no')
            exercise = request.form.get('exercise', 'moderate')
            complication = request.form.get('complication', 'no')
            underlying_diseases = request.form.getlist('underlying_disease')

            form_data = {
                'name': name, 'sys': sys, 'dia': dia,
                'smoke': smoke, 'alcohol': alcohol, 'exercise': exercise, 
                'complication': complication, 'underlying_disease': underlying_diseases
            }

            evaluation = evaluate_pingpong_7_colors(sys, dia, smoke, alcohol, exercise, complication, underlying_diseases)
            
            ai_advice = ""
            if client and evaluation:
                try:
                    prompt = f"""
                    คุณคือพยาบาลผู้เชี่ยวชาญด้านสุขภาพดิจิทัล ให้คำแนะนำตามหลักเกณฑ์ปิงปองจราจรชีวิต 7 สี และหลักโภชนาการ DASH Diet
                    ข้อมูลผู้รับการประเมิน:
                    - ชื่อ: {name}
                    - ความดันโลหิต: {sys}/{dia} mmHg
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
                    "name": name, "sys": sys, "dia": dia,
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
    raw_query = data.get('query', '').strip()
    return jsonify(get_smart_fallback_analysis(raw_query)), 200


def get_smart_fallback_analysis(query):
    q = query.lower()
    
    if any(k in q for k in ["ไข่ดาว", "ไข่เจียว", "ไข่ตุ๋น", "ไข่ต้ม", "ไข่"]):
        return {
            "patient_amount": f"1 ส่วนของ {query}: เท่ากับ ไข่ไก่ 1 ฟอง (ให้พลังงานประมาณ 75-150 กิโลแคลอรี ขึ้นอยู่กับวิธีปรุง) | โควตาสูงสุดต่อวัน: แนะนำไม่เกิน 1-2 ฟองต่อวัน (ตามโควต้าเนื้อสัตว์และไขมันใน DASH Diet)",
            "patient_desc": "• ปริมาณที่แนะนำ: ทานเนื้อสัตว์และไข่ตามสัดส่วนโควต้า DASH Diet (ไข่ 1 ฟอง = เนื้อสัตว์ 1 ส่วน)\n• ข้อควรระวัง: หากเป็นเมนูทอดใช้น้ำมันมาก จะมีไขมันอิ่มตัวและคอเลสเตอรอลสูง ควรจำกัดเพื่อสุขภาพหัวใจ\n• ทางเลือกที่ดีกว่า: เลือกเป็นไข่ต้ม ไข่ตุ๋น หรือไข่ลวก โดยไม่ต้องใช้น้ำมันและลดการปรุงรสเค็ม"
        }
    elif any(k in q for k in ["ลำไย", "มังคุด", "เงาะ", "ลองกอง", "ทุเรียน", "มะม่วง", "ผลไม้"]):
        return {
            "patient_amount": f"1 ส่วนของ {query}: เท่ากับประมาณ 4-8 ลูก/ชิ้น (ให้พลังงานราวๆ 60 กิโลแคลอรี) | โควตาสูงสุดต่อวัน: หากเลือกกิน{query}เป็นผลไม้ในโควตา จะกินได้ประมาณ 16-32 ลูก/ชิ้นต่อวัน (แบ่งทาน 4-5 ส่วน/วัน)",
            "patient_desc": f"• ปริมาณที่แนะนำ: ทานตามโควต้าผลไม้ 4-5 ส่วนต่อวัน เพื่อรับโพแทสเซียมและใยอาหาร\n• ข้อควรระวัง: {query}มีรสหวานและน้ำตาลสูง ควรระวังไม่ทานปริมาณมากในคราวเดียวเพื่อป้องกันน้ำตาลในเลือดสูง\n• ทางเลือกที่ดีกว่า: ทานสดตามฤดูกาลในปริมาณที่พอเหมาะ และกระจายทานสลับกับผลไม้รสไม่หวานจัด"
        }
    elif any(k in q for k in ["ข้าว", "แป้ง", "เส้น", "ขนมปัง", "บะหมี่"]):
        return {
            "patient_amount": f"1 ส่วนของ {query}: เท่ากับ ข้าวสุก 1 ทัพพี (หรือเส้นสุก 1 ทัพพี, ขนมปัง 1 แผ่น ให้พลังงานราว 80 กิโลแคลอรี) | โควตาสูงสุดต่อวัน: แนะนำตามหลัก DASH Diet 6-8 ส่วน (ทัพพี) ต่อวัน",
            "patient_desc": "• ปริมาณที่แนะนำ: ทาน 6-8 ส่วนต่อวัน เน้นธัญพืชไม่ขัดสีเพื่อเพิ่มกากใย\n• ข้อควรระวัง: ระวังแป้งขัดขาวและไขมันแฝงจากกระบวนการผัดหรือทอด\n• ทางเลือกที่ดีกว่า: เลือกทานข้าวซ้อมมือ ข้าวกล้อง หรือขนมปังโฮลวีต"
        }
    elif any(k in q for k in ["ผัก", "คะน้า", "ผักบุ้ง", "กะหล่ำ", "บร็อคโคลี"]):
        return {
            "patient_amount": f"1 ส่วนของ {query}: เท่ากับ ผักสด 2 ทัพพี หรือผักสุก 1 ทัพพี (ให้ใยอาหารและโพแทสเซียมสูง) | โควตาสูงสุดต่อวัน: แนะนำ 4-5 ส่วนต่อวัน",
            "patient_desc": f"• ปริมาณที่แนะนำ: ทาน 4-5 ส่วนต่อวัน ช่วยควบคุมและลดระดับความดันโลหิต\n• ข้อควรระวัง: หลีกเลี่ยงการปรุงรสเค็มจัดหรือใช้น้ำปลา/ซอสปริมาณมาก\n• ทางเลือกที่ดีกว่า: ทานผักสดหรือผักลวก นึ่ง โดยเลี่ยงน้ำซุปเค็มจัด"
        }
    else:
        return {
            "patient_amount": f"1 ส่วนของ {query}: เท่ากับปริมาณมาตรฐาน 1 ส่วนโควต้าอาหารตามหลัก DASH Diet | โควตาสูงสุดต่อวัน: บริโภคในปริมาณที่เหมาะสมตามโควต้าพลังงาน 2,000 Kcal",
            "patient_desc": f"• ปริมาณที่แนะนำ: ควบคุมสัดส่วน {query} ให้สอดคล้องกับโควต้าประจำวันและจำกัดโซเดียมรวมไม่เกิน 1,500 - 2,300 มก./วัน\n• ข้อควรระวัง: หลีกเลี่ยงอาหารรสเค็มจัด ของทอด เมนูผัดน้ำมันท่วม และไขมันอิ่มตัวสูง\n• ทางเลือกที่ดีกว่า: เลือกใช้วิธีต้ม นึ่ง ลวก หรืออบ และเพิ่มการทานผักผลไม้สดเพื่อสุขภาพหลอดเลือด"
        }


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
