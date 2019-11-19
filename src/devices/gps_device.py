import gpsd

gpsd.connect()


def get_gps_data():
    packet = gpsd.get_current()
    try:
        lat, long = packet.position()
    except:
        lat, long = ('00.000000', '00.000000')

    try:
        speed = packet.speed()
    except:
        speed = 'n/a'

    try:
        alt = packet.altitude()
    except:
        alt = 'n/a'

    try:
        gps_time = packet.time
    except:
        gps_time = 'n/a'

    return dict(position=(lat, long), speed=speed, alt=alt, gps_time=gps_time)
