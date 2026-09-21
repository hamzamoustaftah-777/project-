import requests

# استخدم مفتاح API الخاص بك من Google AI Studio
API_KEY = "ضع_مفتاح_الـ_API_الخاص_بك_هنا"

def get_skill_info():
    return {
        "name": "script_writer",
        "description": "كتابة سيناريو فيديو قصير وديناميكي (Reels/Shorts) يناسب الموضوع المطلوب مع الخطاف والمشاهد والنص الصوتي",
        "parameters": {"topic": "موضوع الفيديو المطلوب"}
    }

def run(topic):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""أنت كاتب سيناريو محترف لمقاطع الفيديو القصيرة (Reels / Instagram / TikTok).
اكتب سيناريو فيديو ابتكاري ومميز جداً عن الموضوع التالي: '{topic}'.

نسق الإجابة مستخدماً العناوين التالية حصراً لتظهر بشكل منظم وأنيق:
📌 **الخطاف (Hook):** [اكتب خطافاً خاطفاً للأنظار في أول 3 ثوانٍ]
🎬 **المشاهد البصرية (Visuals):** [وصف المشاهد والإضاءة وزوايا التصوير]
🎙️ **النص الصوتي (Voiceover):** [الكلام المباشر والأسلوب الصوتي]
💡 **الدعوة للإجراء (CTA):** [دعوة التفاعل وحفظ المقطع]"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        res_data = res.json()
        
        if 'error' in res_data:
            return f"حدث خطأ في API: {res_data['error'].get('message', 'Unknown error')}"
            
        return res_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"حدث خطأ أثناء توليد السيناريو: {str(e)}"
