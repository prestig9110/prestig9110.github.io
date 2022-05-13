def _is_numb ( digit ):
    return digit.isdigit() if digit[:1] != '-' else digit[1:].isdigit()

def _allowed_file(filename):
    allowed_types = set(["png", "jpg", "jpeg", "gif"])
    print("Check if image types is allowed")
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_types