import express from "express";
import path from "path";
import fs from "fs";
import { GoogleGenAI } from "@google/genai";

const app = express();
const PORT = 3000;

const ai = new GoogleGenAI();

async function getAIHealthInsight(name: string, fbs: number, sys: number, dia: number, level: string, hasComplication: boolean): Promise<string> {
  try {
    const prompt = `ผู้รับการประเมิน: ${name}
ระดับน้ำตาลในเลือด (FBS): ${fbs} mg/dL
ความดันโลหิต (SYS/DIA): ${sys}/${dia} mmHg
มีภาวะแทรกซ้อน: ${hasComplication ? "มี" : "ไม่มี"}
ระดับความเสี่ยงตามปิงปองจราจรชีวิต 7 สี: ${level}

ในฐานะ "พยาบาลที่ปรึกษาด้านสุขภาพดิจิทัล" (Digital Health Consultant Nurse) จงให้คำแนะนำเฉพาะบุคคล (AI Health Insight) เป็นภาษาไทย ด้วยน้ำเสียงอบอุ่น สุภาพ และให้กำลังใจ โดยครอบคลุมประเด็นต่อไปนี้:
1. วิเคราะห์สถานะสุขภาพปัจจุบันอย่างเข้าใจง่าย
2. คำแนะนำด้านโภชนาการที่จำเพาะ (อ้างอิงหลัก DASH Diet เช่น เพิ่มผัก ผลไม้ ธัญพืชไม่ขัดสี นมไขมันต่ำ และจำกัดโซเดียมไม่เกิน 2,000 มก./วัน)
3. คำแนะนำด้านการออกกำลังกายและพฤติกรรมการใช้ชีวิตประจำวัน
4. ข้อควรระวังและคำเตือนทางการแพทย์อย่างชัดเจน

จัดรูปแบบให้อ่านง่าย มีการเว้นวรรคและสัญลักษณ์แสดงรายการ (bullet points)`;

    const response = await ai.models.generateContent({
      model: 'gemini-3.7-flash',
      contents: prompt,
      config: {
        systemInstruction: "คุณคือพยาบาลผู้เชี่ยวชาญด้านสุขภาพและโภชนาการ DASH Diet ให้คำปรึกษาด้วยความห่วงใยและหลักการแพทย์ที่ถูกต้อง",
        temperature: 0.7,
      }
    });

    return response.text || "ขออภัย ระบบ AI ไม่สามารถสร้างคำแนะนำได้ในขณะนี้";
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "ระบบ AI กำลังประมวลผลข้อมูลสุขภาพของคุณ แนะนำให้ควบคุมอาหารตามหลัก DASH Diet และพบแพทย์ตามนัดหมายสม่ำเสมอ";
  }
}

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// 🟢 สำคัญ: เปิดสิทธิ์ให้เบราว์เซอร์เข้าถึงไฟล์รูปภาพในโฟลเดอร์ static ได้
app.use('/static', express.static(path.join(process.cwd(), 'static')));

// Simple Jinja-like template render helper for Express fallback
function renderTemplate(filePath: string, data: any = {}) {
  let template = "";
  try {
    template = fs.readFileSync(filePath, "utf-8");
  } catch (e) {
    template = "<h1>Template not found</h1>";
  }
  
  const baseHtmlPath = path.join(process.cwd(), "templates", "base.html");
  let baseHtml = "";
  try {
    baseHtml = fs.readFileSync(baseHtmlPath, "utf-8");
  } catch (e) {
    baseHtml = "<html><body>{% block content %}{% endblock %}</body></html>";
  }

  const contentMatch = template.match(/{% block content %}([\s\S]*?){% endblock %}/);
  const content = contentMatch ? contentMatch[1] : template;
  
  const titleMatch = template.match(/{% block title %}([\s\S]*?){% endblock %}/);
  const title = titleMatch ? titleMatch[1] : "HealthPingpong";

  baseHtml = baseHtml.replace(/{% block title %}[\s\S]*?{% endblock %}/, title);
  baseHtml = baseHtml.replace("{% block content %}{% endblock %}", content);

  // Simple template variable replacement for assessment results
  if (data.result) {
    baseHtml = baseHtml.replace("{{ result.level }}", data.result.level || "");
    baseHtml = baseHtml.replace("{{ result.name }}", data.result.name || "");
    baseHtml = baseHtml.replace("{{ result.description }}", data.result.description || "");
    baseHtml = baseHtml.replace("{{ result.fbs }}", data.result.fbs || "");
    baseHtml = baseHtml.replace("{{ result.sys }}", data.result.sys || "");
    baseHtml = baseHtml.replace("{{ result.dia }}", data.result.dia || "");
    baseHtml = baseHtml.replace("{{ result.action }}", data.result.action || "");
    baseHtml = baseHtml.replace("{{ result.bg_color }}", data.result.bg_color || "");
    baseHtml = baseHtml.replace("{{ result.badge_color }}", data.result.badge_color || "");
    baseHtml = baseHtml.replace("{{ result.border_color }}", data.result.border_color || "");
    baseHtml = baseHtml.replace("{{ result.ai_insight }}", data.result.ai_insight || "");
    
    if (data.result.advice && Array.isArray(data.result.advice)) {
      const adviceHtml = data.result.advice.map((item: string) => `
        <li class="flex items-start space-x-3 text-slate-700 bg-slate-50/50 p-3.5 rounded-xl border border-slate-100">
            <span class="text-emerald-600 font-bold mt-0.5">•</span>
            <span class="leading-relaxed">${item}</span>
        </li>
      `).join("");
      baseHtml = baseHtml.replace(/{% for advice_item in result\.advice %}[\s\S]*?\{% endfor %}/, adviceHtml);
    }
  } else {
    baseHtml = baseHtml.replace(/{% if result %}([\s\S]*?){% endif %}/g, "");
  }

  if (data.form_data) {
    baseHtml = baseHtml.replace('value="{{ form_data.get(\'name\', \'\') }}"', `value="${data.form_data.name || ''}"`);
    baseHtml = baseHtml.replace('value="{{ form_data.get(\'fbs\', \'\') }}"', `value="${data.form_data.fbs || ''}"`);
    baseHtml = baseHtml.replace('value="{{ form_data.get(\'sys\', \'\') }}"', `value="${data.form_data.sys || ''}"`);
    baseHtml = baseHtml.replace('value="{{ form_data.get(\'dia\', \'\') }}"', `value="${data.form_data.dia || ''}"`);
    if (data.form_data.complication) {
      baseHtml = baseHtml.replace('name="complication" value="yes"', 'name="complication" value="yes" checked');
    }
  }

  return baseHtml;
}

interface HealthResult {
  level: string;
  color_code: string;
  bg_color: string;
  badge_color: string;
  border_color: string;
  description: string;
  advice: string[];
  action: string;
  name?: string;
  fbs?: number;
  sys?: number;
  dia?: number;
}

function evaluateHealth(fbs: number, sys: number, dia: number, hasComplication: boolean): HealthResult {
  if (hasComplication) {
    return {
      level: "โรคแทรกซ้อน (สีดำ)",
      color_code: "black",
      bg_color: "bg-black text-white",
      badge_color: "bg-neutral-900 text-white border border-neutral-700",
      border_color: "border-black",
      description: "ตรวจพบภาวะแทรกซ้อนจากโรคเรื้อรัง (เบาหวาน/ความดันโลหิตสูง)",
      advice: [
        "พบแพทย์ด่วนที่สุดเพื่อประเมินอวัยวะเป้าหมาย (หัวใจ ไต ตา หลอดเลือดสมอง)",
        "ห้ามปรับเปลี่ยนขนาดยาเองเด็ดขาด ปฏิบัติตามคำสั่งแพทย์อย่างเคร่งครัด",
        "ควบคุมอาหารจำกัดโซเดียม น้ำตาล และไขมันตามหลักโภชนาการ DASH Diet อย่างเคร่งครัด",
        "สังเกตอาการฉุกเฉิน เช่น แน่นหน้าอก หอบเหนื่อย แขนขาอ่อนแรง หน้ามืด วูบ"
      ],
      action: "พบแพทย์ด่วนที่สุด (Urgent Medical Attention)"
    };
  }

  if (fbs >= 183 || sys >= 180 || dia >= 110) {
    return {
      level: "วิกฤต (สีแดง)",
      color_code: "red",
      bg_color: "bg-red-600 text-white",
      badge_color: "bg-red-700 text-white",
      border_color: "border-red-600",
      description: "ระดับน้ำตาลในเลือดหรือความดันโลหิตสูงอยู่ในระดับวิกฤตอันตราย",
      advice: [
        "ควรพบแพทย์ทันทีภายในวันนี้หรือไปห้องฉุกเฉินโรงพยาบาลใกล้บ้าน",
        "หากมีอาการปวดหัวรุนแรง แน่นหน้าอก คลื่นไส้ อาเจียน ตามัว ให้รีบไปพบแพทย์ทันที",
        "งดอาหารรสเค็มจัด หวานจัด และงดเครื่องดื่มแอลกอฮอล์โดยเด็ดขาด",
        "วัดความดันโลหิตและระดับน้ำตาลซ้ำทุก 1-2 ชั่วโมงจนกว่าจะถึงสถานพยาบาล"
      ],
      action: "พบแพทย์ทันที / ห้องฉุกเฉิน"
    };
  }

  if ((155 <= fbs && fbs <= 182) || (160 <= sys && sys <= 179) || (100 <= dia && dia <= 109)) {
    return {
      level: "อันตราย (สีส้ม)",
      color_code: "orange",
      bg_color: "bg-orange-500 text-white",
      badge_color: "bg-orange-600 text-white",
      border_color: "border-orange-500",
      description: "ระดับน้ำตาลหรือความดันโลหิตสูงมาก เสี่ยงต่อภาวะแทรกซ้อนเฉียบพลัน",
      advice: [
        "ควรพบแพทย์โดยเร็วภายใน 1-2 วันนี้ เพื่อปรับแผนการรักษา",
        "รับประทานยาตามแพทย์สั่งสม่ำเสมอ ห้ามขาดยา",
        "ควบคุมปริมาณโซเดียมไม่เกิน 2,000 มก./วัน ตามหลัก DASH Diet",
        "วัดความดันและน้ำตาลทุกวัน พร้อมจดบันทึกค่าเพื่อแจ้งแพทย์"
      ],
      action: "พบแพทย์ภายใน 1-2 วัน"
    };
  }

  if ((125 <= fbs && fbs <= 154) || (140 <= sys && sys <= 159) || (90 <= dia && dia <= 99)) {
    return {
      level: "เฝ้าระวัง (สีเหลือง)",
      color_code: "yellow",
      bg_color: "bg-yellow-300 text-gray-900",
      badge_color: "bg-yellow-400 text-gray-900",
      border_color: "border-yellow-400",
      description: "ระดับน้ำตาลหรือความดันโลหิตสูงกว่าเกณฑ์ปกติ เริ่มเข้าสู่โซนอันตราย",
      advice: [
        "พบแพทย์ตามนัดหมายปกติ และแจ้งผลตรวจให้แพทย์ทราบ",
        "ปรับเปลี่ยนพฤติกรรมสุขภาพ เน้นทานผัก ผลไม้ ธัญพืชไม่ขัดสี และลดเค็ม",
        "ออกกำลังกายสม่ำเสมอ ลดอาหารหวาน มัน เค็ม",
        "ตรวจวัดระดับน้ำตาลและดันโลหิตสัปดาห์ละ 2-3 ครั้ง"
      ],
      action: "พบแพทย์ตามนัด / ปรับพฤติกรรม"
    };
  }

  if (fbs < 125 && sys < 139 && dia < 89) {
    if (!(fbs < 100 && sys < 120 && dia < 80)) {
      return {
        level: "คุมได้ดี (สีเขียวเข้ม)",
        color_code: "dark-green",
        bg_color: "bg-emerald-700 text-white",
        badge_color: "bg-emerald-800 text-white",
        border_color: "border-emerald-700",
        description: "อยู่ในเกณฑ์ที่สามารถควบคุมระดับน้ำตาลและความดันได้ดี",
        advice: [
          "รักษาพฤติกรรมสุขภาพที่ดีนี้ไว้อย่างต่อเนื่อง",
          "รับประทานอาหารตามหลัก DASH Diet (เน้นผัก ผลไม้ นมไขมันต่ำ ปลา)",
          "ออกกำลังกายสม่ำเสมอสัปดาห์ละ 150 นาที",
          "พบแพทย์ตามนัดหมายเพื่อติดตามอาการสม่ำเสมอ"
        ],
        action: "รักษาพฤติกรรมต่อเนื่อง / พบแพทย์ตามนัด"
      };
    }
  }

  if ((100 <= fbs && fbs <= 125) || (120 <= sys && sys <= 139) || (80 <= dia && dia <= 89)) {
    return {
      level: "เสี่ยง (สีเขียวอ่อน)",
      color_code: "light-green",
      bg_color: "bg-emerald-100 text-emerald-900",
      badge_color: "bg-emerald-200 text-emerald-900",
      border_color: "border-emerald-300",
      description: "อยู่ในกลุ่มเสี่ยงเริ่มสูง (Pre-hypertension / Pre-diabetes)",
      advice: [
        "ปรับเปลี่ยนพฤติกรรมสุขภาพโดยด่วนเพื่อป้องกันไม่ให้เป็นโรคเรื้อรัง",
        "ใช้หลักอาหาร DASH Diet ลดหวาน มัน เค็ม เพิ่มการทานผักและใยอาหาร",
        "เพิ่มกิจกรรมทางกาย ออกกำลังกายสม่ำเสมอ",
        "ควบคุมน้ำหนักให้อยู่ในเกณฑ์มาตรฐาน"
      ],
      action: "ปรับพฤติกรรม / ตรวจสุขภาพประจำปี"
    };
  }

  return {
    level: "ปกติ (สีขาว)",
    color_code: "white",
    bg_color: "bg-white text-gray-800 border-2 border-gray-200",
    badge_color: "bg-gray-100 text-gray-800",
    border_color: "border-gray-300",
    description: "ระดับน้ำตาลและแรงดันโลหิตอยู่ในเกณฑ์ปกติ สุขภาพดีเยี่ยม",
    advice: [
      "รักษาสุขภาพและพฤติกรรมที่ดีเช่นนี้ต่อไป",
      "รับประทานอาหารที่มีประโยชน์ ครบ 5 หมู่ (เช่น DASH Diet)",
      "ออกกำลังกายสม่ำเสมอ และพักผ่อนให้เพียงพอ",
      "ตรวจสุขภาพประจำปีอย่างน้อยปีละ 1 ครั้ง"
    ],
    action: "รักษาสุขภาพอย่างต่อเนื่อง"
  };
}

app.get("/", (req, res) => {
  const html = renderTemplate(path.join(process.cwd(), "templates", "index.html"));
  res.send(html);
});

app.get("/assessment", (req, res) => {
  const html = renderTemplate(path.join(process.cwd(), "templates", "assessment.html"));
  res.send(html);
});

app.post("/assessment", async (req, res) => {
  const name = req.body.name || "ผู้รับการประเมิน";
  const fbs = parseFloat(req.body.fbs) || 0;
  const sys = parseFloat(req.body.sys) || 0;
  const dia = parseFloat(req.body.dia) || 0;
  const hasComplication = req.body.complication === "yes";

  const result: any = evaluateHealth(fbs, sys, dia, hasComplication);
  result.name = name;
  result.fbs = fbs;
  result.sys = sys;
  result.dia = dia;
  
  result.ai_insight = await getAIHealthInsight(name, fbs, sys, dia, result.level, hasComplication);

  const html = renderTemplate(path.join(process.cwd(), "templates", "assessment.html"), {
    result,
    form_data: { name, fbs, sys, dia, complication: hasComplication }
  });
  res.send(html);
});

app.get("/dash-diet", (req, res) => {
  const html = renderTemplate(path.join(process.cwd(), "templates", "dash-diet.html"));
  res.send(html);
});

app.post("/api/analyze-food", async (req, res) => {
  const query = req.body.query || "";
  try {
    const prompt = `ผู้ใช้งานต้องการวิเคราะห์โภชนาการของอาหารหรือเครื่องปรุง: "${query}"
อ้างอิงตามหลักคู่มือมาตรฐานโภชนาการและ DASH Diet

ตอบกลับมาในรูปแบบ JSON ที่มีโครงสร้างดังนี้เท่านั้น (ห้ามใส่เครื่องหมาย markdown หรือคำอธิบายอื่นนอกเหนือจาก JSON):
{
  "normal_amount": "ระบุปริมาณที่แนะนำสำหรับคนปกติ / ผู้รักสุขภาพ",
  "normal_desc": "คำแนะนำเพิ่มเติมสั้นๆ สำหรับคนปกติในการเผาผลาญและใช้พลังงาน",
  "patient_amount": "ระบุปริมาณจำกัดที่ทานได้สำหรับคนป่วย / ควบคุมเบาหวานและความดัน (ระบุปริมาณคาร์บหรือปริมาณโซเดียมเป็นหน่วยบริโภคที่ชัดเจน เช่น ช้อนชา ทัพพี หรือมิลลิกรัม)",
  "patient_desc": "ระบุข้อควรระวังตามหลักโภชนาการหรือ DASH Diet เช่น ปริมาณน้ำตาลแฝง หรือผลกระทบต่อระดับน้ำตาลในเลือดและโซเดียม"
}`;

    const response = await ai.models.generateContent({
      model: 'gemini-3.7-flash',
      contents: prompt,
      config: {
        systemInstruction: "คุณคือผู้เชี่ยวชาญด้านโภชนาการและการควบคุมโรคเรื้อรัง (เบาหวานและความดันโลหิตสูง) อ้างอิงตามหลักคู่มือมาตรฐานโภชนาการและ DASH Diet ตอบกลับเป็น JSON เพียวๆ เท่านั้น ห้ามมี markdown หรือข้อความอื่น",
        temperature: 0.3,
      }
    });

    let rawText = response.text || "{}";
    rawText = rawText.replace(/```json/g, "").replace(/```/g, "").trim();
    const jsonResult = JSON.parse(rawText);
    res.json(jsonResult);
  } catch (error) {
    console.error("Gemini Food Analysis Error:", error);
    res.status(500).json({
      normal_amount: "รับประทานได้ตามความเหมาะสมของพลังงาน (สัดส่วน 5 หมู่)",
      normal_desc: "รักษาสมดุลโภชนาการและควบคุมน้ำหนักตัวให้อยู่ในเกณฑ์ปกติ",
      patient_amount: "จำกัดปริมาณเทียบเท่า 1 คาร์บ หรือควบคุมปริมาณโซเดียม",
      patient_desc: "อ้างอิงเกณฑ์มาตรฐานโภชนาการ เพื่อความปลอดภัยและช่วยควบคุมระดับน้ำตาลและดันโลหิตให้คงที่"
    });
  }
});

app.get("/complications", (req, res) => {
  const html = renderTemplate(path.join(process.cwd(), "templates", "complications.html"));
  res.send(html);
});

app.get("/skt", (req, res) => {
  const html = renderTemplate(path.join(process.cwd(), "templates", "skt.html"));
  res.send(html);
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on http://localhost:${PORT}`);
});