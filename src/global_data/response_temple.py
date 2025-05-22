def make_response_template(massage, code, content):
    res = {
        "message": massage,
        "code": code,
        "content": content
    }
    return res