import json

class make:
    text = ''
    color = 'white'
    bold = False

    def __init__(self, **kwargs):
        self.__json = {}
        for k, v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k, v)
        self.__format_mc()

    def __format_mc(self):
        self.__to_add('text', self.text)
        self.__to_add('bold', self.bold)
        if checkColor(self.color):
            self.__to_add('color', self.color)

    def __to_add(self, key, value):
        if value is not False and value is not None:
            self.__json[key] = value

    def get_json(self):
        return json.dumps(self.__json, separators=(',', ':'))

    @staticmethod
    def multiple_tellraw(*tellraws):
        return_list = ','.join(str(tellraw) for tellraw in tellraws)
        # Double quote is add to avoid parent heriarchy of Events
        return '["",' + return_list + ']'

    def __str__(self):
        return self.get_json()

def checkColor(color):
    if color == 'dark_red':
        return True
    elif color == 'red':
        return True
    elif color == 'gold':
        return True
    elif color == 'yellow':
        return True
    elif color == 'dark_green':
        return True
    elif color == 'green':
        return True
    elif color == 'aqua':
        return True
    elif color == 'blue':
        return True
    elif color == 'dark_blue':
        return True
    elif color == 'light_purple':
        return True
    elif color == 'white':
        return True
    elif color == 'gray':
        return True
    elif color == 'dark_gray':
        return True
    elif color == 'black':
        return True
    else:
        return False

print('[tellaraw.py] initialized.')