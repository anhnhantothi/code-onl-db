import sys
import io
from contextlib import redirect_stdout

def run_python_code(code: str) -> str:
    """
    Thực thi mã Python và trả về output hoặc lỗi nếu có.
    """

    # Tạo một StringIO object để bắt stdout
    buffer = io.StringIO()

    try:
        # Dùng redirect_stdout để capture output
        with redirect_stdout(buffer):
            exec(code, {})
    except Exception as e:
        return str(e)

    return buffer.getvalue()
