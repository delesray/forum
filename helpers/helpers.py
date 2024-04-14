def humanize_error_msg(data):
    """
    With string manipulation is checked which column uniqueness is violated
    todo този месидж към програмиста ли е или към юзър?
    """
    if data.errno == 1062:
        data = data.msg.split()
        entity = data[-1][1:-1].split('_')[0]
        return f'Such {entity} already exists!'
    return data
