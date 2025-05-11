from flask import Blueprint, request, make_response
import subprocess
import tempfile
import os
import json

code_runner_bp = Blueprint('code_runner', __name__)
import re

def is_malicious(code: str) -> bool:
    dangerous_patterns = [
        r'\bimport\s+os\b',
        r'\bimport\s+sys\b',
        r'\beval\s*\(',
        r'\bexec\s*\(',
        r'\bos\.system\s*\(',
        r'\b__import__\s*\(',
        r'\bopen\s*\(',
        r'\bsubprocess\b',
        r'\bthreading\b',
        r'\bshutil\b',
        r'\bsocket\b'
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            return True
    return False

@code_runner_bp.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')
    if is_malicious(code):
        return make_response(json.dumps({
            'stdout': '',
            'stderr': '',
            'error': '🚫 Mã chứa lệnh nguy hiểm và đã bị chặn.'
        }, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'})
    

    try:
        # Ghi file Python tạm bằng UTF-8
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            f.flush()

            # Ép Python dùng UTF-8 mode
            env = os.environ.copy()
            env['PYTHONUTF8'] = '1'

            result = subprocess.run(
                ['python', f.name],
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace',
                env=env
            )

        # Trả JSON UTF-8 không escape unicode
        return make_response(
            json.dumps({
                'stdout': result.stdout,
                'stderr': result.stderr,
                'error': None
            }, ensure_ascii=False),
            200,
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    except subprocess.TimeoutExpired:
        return make_response(json.dumps({
            'stdout': '',
            'stderr': '',
            'error': '⏰ Code execution timed out'
        }, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'})

    except Exception as e:
        return make_response(json.dumps({
            'stdout': '',
            'stderr': '',
            'error': str(e)
        }, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'})
