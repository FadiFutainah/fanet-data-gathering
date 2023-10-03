speed_rate = 1


# TODO: implement smart speed rate
def update_speed_rate(new_speed):
    global speed_rate
    speed_rate = new_speed


def multiply_by_speed_rate(value):
    global speed_rate
    return value * speed_rate
