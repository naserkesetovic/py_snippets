def prettify_datetime(seconds, exact = True):
    # 365.2425 days in year 
    # more precise 365.242375
    # (leap year - divisible with 4, not divisible with 100)
    # (but not including years 2000 i 2400...) 

    # import math
    
    year = int(math.floor(seconds / 31556926))
    remainder = seconds % 31556926
    # year, reminder = divmod(seconds, 31556926)

    days = int(math.floor(remainder / 86400))
    remainder = seconds % 86400
    # days, reminder = divmod(seconds, 86400)

    hours = int(math.floor(remainder / 3600))
    remainder = seconds % 3600
        
    minutes = int(math.floor(remainder / 60))
    seconds = int(math.floor(remainder % 60))
    
    if exact == True:
        if (year == 0 and days == 0 and hours == 0):
            return "00:{0:02d}:{1:02d}".format(minutes, seconds)
        elif (year == 0 and days == 0):
            return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)
        elif (year == 0):
            return "{0}d {1:02d}:{2:02d}:{3:02d}".format(days, hours, minutes, seconds)
        else:
            return "{0}y {1}d {2:02d}:{3:02d}:{4:02d}".format(year, days, hours, minutes, seconds)
    else:
        if (year == 0 and days == 0 and hours == 0 and minutes < 10):
            return "Few minutes ago"
        elif (year == 0 and days == 0 and hours == 0):
            return "An hour ago"
        elif (year == 0 and days == 0 and hours < 2):
            return "Two hours ago"
        elif (year == 0 and days == 0 and hours < 12):
            return "Half a day ago"
        elif (year == 0 and days == 0):
            return "{0}:{1}".format(hours, minutes)
        elif (year == 0):
            return "{0}d {1:02d}:{2:02d}".format(days, hours, minutes)
        else:
            return "{0}y {1}d {2:02d}:{3:02d}".format(year, days, hours, minutes)
