import os, importlib.util, requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY", "API_KEY = os.environ.get("GEMINI_API_KEY", "")
")
SKILLS = {}

def load_skills():
    global SKILLS
    SKILLS = {}
    skills_dir = os.path.join(os.path.dirname(__file__), 'skills')
    if not os.path.exists(skills_dir):
        os.makedirs(skills_dir)
    for filename in os.listdir(skills_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            skill_name = filename[:-3]
            filepath = os.path.join(skills_dir, filename)
            spec = importlib.util.spec_from_file_location(skill_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'get_skill_info') and hasattr(module, 'run'):
                SKILLS[skill_name] = {
                    'info': module.get_skill_info(),
                    'run': module.run
                }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>VISION N° 7 Core</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg-gradient: radial-gradient(circle at 50% 0%, #1a0b2e 0%, #080214 70%, #020005 100%);
            --card-bg: rgba(23, 12, 41, 0.75);
            --card-border: rgba(236, 72, 153, 0.25);
            --pink-accent: #ec4899;
            --pink-glow: rgba(236, 72, 153, 0.35);
            --user-msg: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
            --agent-msg: rgba(18, 10, 33, 0.9);
            --text-main: #f8fafc;
        }

        * { box-sizing: border-box; font-family: 'Tajawal', -apple-system, sans-serif; -webkit-tap-highlight-color: transparent; }

        body {
            background: var(--bg-gradient);
            color: var(--text-main);
            margin: 0; padding: 0;
            height: 100vh; display: flex; flex-direction: column;
            overflow: hidden;
        }

        .header {
            padding: calc(env(safe-area-inset-top, 20px) + 10px) 20px 14px 20px;
            background: rgba(8, 2, 20, 0.85);
            backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--card-border);
            display: flex; align-items: center; justify-content: space-between;
        }

        .brand-title {
            font-size: 20px; font-weight: 700;
            background: linear-gradient(90deg, #ec4899, #60a5fa);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin: 0;
        }

        .status-badge {
            display: flex; align-items: center; gap: 6px;
            background: rgba(236, 72, 153, 0.12); border: 1px solid rgba(236, 72, 153, 0.3);
            padding: 5px 12px; border-radius: 20px; font-size: 11px; color: #f472b6;
        }
        .dot { width: 6px; height: 6px; background: #ec4899; border-radius: 50%; box-shadow: 0 0 8px #ec4899; }

        .skills-container {
            padding: 10px 16px; display: flex; gap: 8px; overflow-x: auto;
            background: rgba(3, 1, 8, 0.6); border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            scrollbar-width: none;
        }
        .skills-container::-webkit-scrollbar { display: none; }

        .skill-chip {
            background: var(--card-bg); color: #60a5fa;
            padding: 6px 14px; border-radius: 30px;
            border: 1px solid rgba(96, 165, 250, 0.3);
            font-size: 12px; font-weight: 500; white-space: nowrap;
        }

        #chat-box {
            flex: 1; overflow-y: auto; padding: 20px 16px;
            display: flex; flex-direction: column; gap: 16px;
        }

        .message {
            max-width: 88%; padding: 14px 18px; border-radius: 20px;
            font-size: 15px; line-height: 1.7; word-break: break-word;
            animation: fadeIn 0.25s ease-out forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-msg {
            background: var(--user-msg); color: #ffffff; align-self: flex-end;
            border-bottom-left-radius: 4px; box-shadow: 0 4px 15px var(--pink-glow);
        }

        .agent-msg {
            background: var(--agent-msg); color: var(--text-main); align-self: flex-start;
            border: 1px solid var(--card-border); border-bottom-right-radius: 4px;
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        }

        .agent-msg p { margin: 0 0 8px 0; }
        .agent-msg p:last-child { margin-bottom: 0; }
        .agent-msg strong { color: #f472b6; }

        .skill-badge-used {
            display: inline-flex; align-items: center; gap: 4px;
            background: rgba(236, 72, 153, 0.2); color: #f472b6;
            padding: 4px 10px; border-radius: 8px; font-size: 12px;
            margin-bottom: 10px; font-weight: bold; border: 1px solid rgba(236, 72, 153, 0.35);
        }

        .input-wrapper {
            padding: 12px 16px calc(12px + env(safe-area-inset-bottom, 0px)) 16px;
            background: rgba(8, 2, 20, 0.95); backdrop-filter: blur(20px);
            border-top: 1px solid var(--card-border);
        }

        .input-box { display: flex; gap: 10px; align-items: center; }

        input {
            flex: 1; padding: 14px 18px; border-radius: 25px;
            border: 1px solid rgba(236, 72, 153, 0.3);
            background: rgba(23, 12, 41, 0.9); color: #ffffff;
            font-size: 15px; outline: none; transition: all 0.3s;
        }
        input:focus { border-color: #ec4899; box-shadow: 0 0 12px var(--pink-glow); }

        button {
            background: var(--user-msg); color: white; border: none;
            width: 48px; height: 48px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; cursor: pointer; flex-shrink: 0;
            box-shadow: 0 0 15px var(--pink-glow);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="brand-title">VISION N° 7 Core</h1>
        <div class="status-badge"><span class="dot"></span><span>مستقل 24/7</span></div>
    </div>

    <div class="skills-container" id="skills-list"></div>

    <div id="chat-box">
        <div class="message agent-msg">✨ مرحباً بك! نظامك المستقل جاهز للعمل على Render.</div>
    </div>

    <div class="input-wrapper">
        <div class="input-box">
            <input type="text" id="user-input" placeholder="اكتب أمرك..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">➔</button>
        </div>
    </div>

    <script>
        async function fetchSkills() {
            try {
                let res = await fetch('/get_skills');
                let data = await res.json();
                document.getElementById('skills-list').innerHTML = data.map(s => `<div class="skill-chip">⚡ ${s}</div>`).join('');
            } catch(e) {}
        }

        async function sendMessage() {
            let input = document.getElementById('user-input');
            let text = input.value.trim();
            if(!text) return;

            let chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `<div class="message user-msg">${text}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                let response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text})
                });
                let data = await response.json();
                
                let rawReply = data.reply;
                let skillHeader = '';
                
                if (rawReply.includes('⚙️ [استخدام مهارة')) {
                    let parts = rawReply.split('\\n\\n');
                    skillHeader = `<div class="skill-badge-used">${parts[0]}</div>`;
                    rawReply = parts.slice(1).join('\\n\\n');
                }

                let htmlContent = marked.parse(rawReply);
                chatBox.innerHTML += `<div class="message agent-msg">${skillHeader}${htmlContent}</div>`;
            } catch(e) {
                chatBox.innerHTML += `<div class="message agent-msg">حدث خطأ في الاتصال بالخادم.</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        fetchSkills();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_skills')
def get_skills():
    load_skills()
    return jsonify(list(SKILLS.keys()))

@app.route('/chat', methods=['POST'])
def chat():
    user_prompt = request.json.get('prompt', '')
    load_skills()
    
    skills_description = "\n".join([f"- {n}: {d['info']['description']} (Parameters: {d['info']['parameters']})" for n, d in SKILLS.items()])
    
    system_instruction = f"""أنت مساعد ذكي ومستقل. لديك المهارات التالية:
{skills_description}

إذا كانت هناك مهارة مناسبة، أجب بنفس التنسيق التالي فقط:
USE_SKILL: <skill_name> | PARAM: <parameter_value>

إذا لم تكن هناك مهارة، أجب بشكل عادي."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        res_data = res.json()
        
        if 'error' in res_data:
            return jsonify({'reply': f"خطأ في API: {res_data['error'].get('message', 'Unknown error')}"})
            
        reply = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        if reply.startswith("USE_SKILL:"):
            parts = reply.split("|")
            skill_name = parts[0].replace("USE_SKILL:", "").strip()
            param_val = parts[1].replace("PARAM:", "").strip() if len(parts) > 1 else ""
            if skill_name in SKILLS:
                skill_result = SKILLS[skill_name]['run'](param_val)
                return jsonify({'reply': f"⚙️ [استخدام مهارة {skill_name}]\n\n{skill_result}"})
                
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f"حدث خطأ: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
