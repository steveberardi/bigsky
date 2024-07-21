def convert_radc_to_latlon(ra, dec, invert=True):
    lat = dec
    lon = ra

    if lon > 180:
        lon -= 360

    if invert:
        lon *= -1

    return round(lat, 4), round(lon, 4)
