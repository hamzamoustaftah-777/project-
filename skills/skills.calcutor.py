def get_skill_info():
    return {
        "name": "calculator",
        "description": "إجراء العمليات الحسابية الرياضية المباشرة والحلول المباشرة",
        "parameters": {"expression": "العملية الحسابية المراد حسابها مثل 150 * 12"}
    }

def run(expression):
    try:
        # تنظيف المدخلات وحساب الناتج
        clean_expr = str(expression).replace('×', '*').replace('÷', '/').strip()
        result = eval(clean_expr, {"__builtins__": None}, {})
        return f"نتيجة الحساب هي: **{result}**"
    except Exception as e:
        return f"حدث خطأ في إجراء العملية الحسابية: {str(e)}"
