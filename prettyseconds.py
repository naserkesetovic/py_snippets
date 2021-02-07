def pretty(seconds, exact = False):
        ''' Uljepšaj vrijednosti datuma i vremena '''

        # 365.2425 dana u godini
        # tačnije 365.242375
        # (prijestupna godina - djeljivo s 4, nije djeljivo s 100)
        # (ali ne uključujući godine 2000 i 2400...)
        # ... ali je ovo višak podataka... 

        year = int(math.floor(seconds / 31556926))
        remainder = seconds % 31556926

        days = int(math.floor(remainder / 86400))
        remainder = seconds % 86400

        hours = int(math.floor(remainder / 3600))
        remainder = seconds % 3600

        minutes = int(math.floor(remainder / 60))
        seconds = int(math.floor(remainder % 60))

        if exact is True:
            if year == 0 and days == 0 and hours == 0:
                return "00:{0:02d}:{1:02d}".format(minutes, seconds)
            elif year == 0 and days == 0:
                return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)
            elif year == 0:
                return "{0}d {1:02d}:{2:02d}:{3:02d}".format(days, hours, minutes, seconds)
            else:
                return "{0}y {1}d {2:02d}:{3:02d}:{4:02d}".format(
                    year, days, hours, minutes, seconds)
        else:
            if year == 0 and days == 0 and hours == 0 and minutes == 0 and seconds < 10:
                return "Prije par sekundi"
            elif year == 0 and days == 0 and hours == 0 and minutes == 0 and seconds < 30:
                return "Prije pola minute"
            elif year == 0 and days == 0 and hours == 0 and minutes < 1:
                return "Prije minut"
            elif year == 0 and days == 0 and hours == 0 and minutes < 5:
                return "Prije par minuta"
            elif year == 0 and days == 0 and hours == 0 and minutes < 10:
                return "Prije manje od deset minuta"
            elif year == 0 and days == 0 and hours == 0 and minutes < 30:
                return "Prije manje od pola sata"
            elif year == 0 and days == 0 and hours == 0 and minutes < 40:
                return "Prije pola sata"
            elif year == 0 and days == 0 and hours < 1:
                return "Prije sat"
            elif year == 0 and days == 0 and hours < 2:
                return "Prije dva sata"
            elif year == 0 and days == 0 and hours < 12:
                return "Prije pola dana"
            elif year == 0 and days == 0:
                return "u {0}:{1}".format(hours, minutes)
            elif year == 0:
                return "prije {0}d {1:02d}:{2:02d}".format(days, hours, minutes)
            else:
                return "prije {0}g {1}d {2:02d}:{3:02d}".format(year, days, hours, minutes)
