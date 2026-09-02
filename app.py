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


def evaluate_pingpong_7_colors(sugar, sys, dia, smoke, alcohol, exercise, complication):
    """ประเมินสุขภาพตามเกณฑ์ปิงปอง 7 สี พร้อมคำแนะนำที่ละเอียดและครบถ้วน"""
    try:
        if complication == "yes":
            return {
                "level": "โรคแทรกซ้อน (สีดำ)",
                "color_name": "โรคแทรกซ้อน",
                "color_code": "black",
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
        elif sugar >= 183 or sys >= 180 or dia >= 110:
            return {
                "level": "วิกฤต (สีแดง)",
                "color_name": "วิกฤต",
                "color_code": "red",
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
        elif (155 <= sugar <= 182) or (160 <= sys <= 179) or (100 <= dia <= 109):
            return {
                "level": "อันตราย (สีส้ม)",
                "color_name": "อันตราย",
                "color_code": "orange",
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
        elif (125 <= sugar <= 154) or (140 <= sys <= 159) or (90 <= dia <= 99):
            return {
                "level": "เฝ้าระวัง (สีเหลือง)",
                "color_name": "เฝ้าระวัง",
                "color_code": "yellow",
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
        elif sugar < 125 and sys < 139 and dia < 89 and (smoke == "no"):
            return {
                "level": "คุมได้ดี (สีเขียวเข้ม)",
                "color_name": "คุมได้ดี",
                "color_code": "dark-green",
                "bg_color": "bg-emerald-700 text-white",
                "badge_color": "bg-emerald-800 text-white",
                "border_color": "border-emerald-700",
                "description": "อยู่ในเกณฑ์ที่สามารถควบคุมระดับน้ำตาลและความดันได้ดี",
                "advice": [
                    "1) รักษาพฤติกรรมสุขภาพที่ดีตามหลัก 3 อ. 3 ลด นี้ไว้อย่างต่อเนื่อง",
                    "2) รับประทานอาหารที่มีประโยชน์ตามหลัก DASH Diet และมาพบแพทย์ตามนัดสม่ำเสมอ"
                ],
                "action": "รักษาพฤติกรรมต่อเนื่อง / พบแพทย์ตามนัด"
            }
        elif (100 <= sugar <= 125) or (120 <= sys <= 139) or (80 <= dia <= 89) or (smoke == "yes") or (
                alcohol == "yes"):
            return {
                "level": "เสี่ยง (สีเขียวอ่อน)",
                "color_name": "เสี่ยง",
                "color_code": "light-green",
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
            return {
                "level": "ปกติ (สีขาว)",
                "color_name": "ปกติ",
                "color_code": "white",
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

            form_data = {
                'name': name, 'sugar': sugar, 'sys': sys, 'dia': dia,
                'smoke': smoke, 'alcohol': alcohol, 'exercise': exercise, 'complication': complication
            }

            evaluation = evaluate_pingpong_7_colors(sugar, sys, dia, smoke, alcohol, exercise, complication)
            if evaluation:
                result = {
                    "name": name, "sugar": sugar, "sys": sys, "dia": dia,
                    "smoke": smoke, "alcohol": alcohol, "complication": complication,
                    "smoke_text": "สูบบุหรี่" if smoke == "yes" else "ไม่สูบ",
                    "alcohol_text": "ดื่มสุรา" if alcohol == "yes" else "ไม่ดื่ม",
                    "evaluation": evaluation,
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


@app.route('/api/get-ai-advice', methods=['POST'])
def api_get_ai_advice():
    data = request.get_json()
    if not client:
        return jsonify({"advice": "ระบบ AI ไม่พร้อมใช้งาน"})

    try:
        prompt = f"""
        คุณคือพยาบาลผู้เชี่ยวชาญด้านสุขภาพดิจิทัล ให้คำแนะนำตามหลักเกณฑ์ปิงปองจราจรชีวิต 7 สี และหลักโภชนาการ DASH Diet
        ข้อมูลผู้รับการประเมิน:
        - ชื่อ: {data.get('name')}
        - น้ำตาล: {data.get('sugar')} mg/dl, ความดัน: {data.get('sys')}/{data.get('dia')} mmHg
        - พฤติกรรม: สูบบุหรี่ ({data.get('smoke')}), ดื่มสุรา ({data.get('alcohol')})
        - กลุ่มสีประเมิน: {data.get('color_name')}
        ให้เขียนคำแนะนำสั้นๆ กระชับ เป็นกันเอง ภาษาไทยอบอุ่น เป็นกำลังใจ เน้นย้ำการปฏิบัติตัว 3 อ. 3 ลด และการมาพบแพทย์ตามนัด
        """
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return jsonify({"advice": response.text})
    except Exception as e:
        return jsonify({"advice": f"เกิดข้อผิดพลาดในการเรียก AI: {str(e)}"})


@app.route('/api/analyze-food', methods=['POST'])
def analyze_food():
    data = request.get_json()
    query = data.get('query', '').strip()

    if not client:
        return jsonify({"error": "ระบบ AI ไม่พร้อมใช้งาน"}), 500

    try:
        prompt = f"""
        คุณคือผู้เชี่ยวชาญด้านโภชนาการและการควบคุมโรคเรื้อรัง ให้วิเคราะห์อาหารหรือเครื่องปรุงรส: "{query}"

        กฎเหล็กที่ต้องปฏิบัติอย่างเคร่งครัด:
        1. ห้ามใช้คำว่า "หน่วยบริโภค" หรือ "ส่วน" เด็ดขาด ให้ใช้หน่วยที่เป็นรูปธรรมจับต้องได้เท่านั้น
        2. ถ้าเป็นผลไม้ที่เป็นผลเดี่ยวๆ (เช่น กล้วย, ส้ม, แอปเปิ้ล, มะม่วง, ลิ้นจี่) ต้องระบุเป็น "จำนวนผล" ชัดเจน (เช่น 1 ผล, 2 ผล หรือ 1/2 ผล)
        3. ถ้าเป็นผลไม้พวงหรือผลย่อยๆ ขนาดเล็ก (เช่น องุ่น, ลำไย) หรือเนื้อผลไม้ ให้ระบุเป็น "กรัม" หรือ "ขีด" (เช่น 150 กรัม หรือ 1.5 ขีด)
        4. ถ้าเป็นอาหารคาว เนื้อสัตว์ เมนูปิ้งย่าง (เช่น หมูย่าง ไก่ย่าง) ให้ระบุเป็น "กรัม", "ขีด", "ชิ้น" หรือ "จาน" ที่เห็นภาพชัดเจน ห้ามใช้คำว่าผลเด็ดขาด
        5. ถ้าเป็นเครื่องปรุงรส ให้ระบุเป็น "ช้อนโต๊ะ" หรือ "ช้อนชา"

        คุณต้องตอบกลับมาในรูปแบบ JSON ที่มีคีย์ (Keys) ตรงตามนี้เท่านั้น ห้ามใส่เครื่องหมายอื่นครอบโค้ด JSON:
        {{
            "normal_amount": "ระบุปริมาณที่แนะนำสำหรับคนปกติเป็นจำนวนผล, กรัม, ขีด, ชิ้น หรือจาน ที่เห็นภาพชัดเจนตรงกับประเภทอาหาร",
            "normal_desc": "คำแนะนำเพิ่มเติมสั้นๆ สำหรับคนปกติ",
            "patient_amount": "ระบุปริมาณจำกัดที่ทานได้สำหรับผู้ป่วยโรคเรื้อรังเป็นจำนวนผล, กรัม, ขีด, ชิ้น หรือจานที่ชัดเจน ห้ามใช้คำว่าหน่วยบริโภคหรือส่วน",
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
        # ปรับค่าสำรองกลางๆ ที่ปลอดภัยสำหรับทุกเมนู (ไม่ใช้คำว่า 'ผล' แล้ว)
        return jsonify({
            "normal_amount": "150 - 200 กรัม หรือ 1 - 2 จาน ตามสัดส่วนพลังงานปกติ",
            "normal_desc": "รับประทานในปริมาณที่พอเหมาะและออกกำลังกายสม่ำเสมอ",
            "patient_amount": "จำกัดปริมาณไม่เกิน 100 กรัม หรือควบคุมสัดส่วนแต่น้อย",
            "patient_desc": "ควรควบคุมปริมาณไขมัน โซเดียม และน้ำตาลตามหลัก DASH Diet"
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
