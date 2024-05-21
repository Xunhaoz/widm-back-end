def api_input_check(args, api_input):
    for arg in args:
        if arg not in api_input:
            return False
    return True


def api_input_get(args, api_input):
    res = []
    for arg in args:
        res.append(api_input[arg])
    return res
