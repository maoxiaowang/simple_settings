def str2bool(string, default: bool = None, silent=False):
    """
    str to bool
    """
    if isinstance(string, bool):
        return string
    elif isinstance(string, str):
        if string in ('true', 'True'):
            return True
        elif string in ('false', 'False'):
            return False
        else:
            if default is not None:
                return default
            if not silent:
                raise ValueError
    else:
        if default is not None:
            return default
        if not silent:
            raise TypeError
