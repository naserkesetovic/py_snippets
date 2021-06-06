from datetime import datetime
import sys
import os

DEBUG_MODE = False

def log(message):
    if DEBUG_MODE:
        print(message)


def process_file(filename):
    ''' Opens selected file and reads all the lines '''

    with open(filename, encoding='utf-8') as f:
        lines = [line.strip() for line in f]

    log("Total lines in file: {0}".format(len(lines)))
    return lines


def get_events_dict(lines):
    ''' Seeks the all VEVENTs and adds them to dictionary '''
    events = []
    event = {}
    eventFound = False
    eventIndex = 0
    log("Event is {0}".format(event))
    log("Events are {0}".format(events))

    for line in lines:
        if 'BEGIN:VEVENT' in line:
            eventFound = True
            eventIndex += 1
            event.clear()
            log("Found event index: {0}".format(eventIndex))

        elif 'END:VEVENT' in line:
            eventFound = False
            # clearing the list will clear memory reference, this is why we need to
            # add the copy
            events.append(event.copy())

        else:
            if eventFound:
                if ":" in line:
                    desc = line.split(':')
                    if "SUMMARY" in desc[0]:
                        event["summary"] = desc[1]
                    elif "RRULE" in desc[0]:
                        event["rule"] = desc[1]
                    elif "DESCRIPTION" in desc[0]:
                        event["description"] = desc[1]
                    elif "DTSTART" in desc[0] or "DTEND" in desc[0] or "DTSTAMP" in desc[0] or "DTMODIFIED" in desc[0]:
                        if ";" in desc[0]:
                            values = desc[0].split(";")
                            if values[1] == "VALUE=DATE":
                                event[str(values[0]).lower()] = str(datetime.strptime(desc[1], "%Y%m%d"))

                            if "TZID" in values[1]:
                                event[str(values[0]).lower()] = str(datetime.strptime(desc[1], "%Y%m%dT%H%M%S"))

                        else:
                            event[str(desc[0]).lower()] = str(datetime.strptime(desc[1], "%Y%m%dT%H%M%SZ"))

    return events

def clear_illegal(val):
    if isinstance(val, str):
        return val.replace(";", "").strip()
    
    return ""


def delete_file(file):
    if os.path.exists(file):
        try:
            os.remove(file)

        except:
            print("Unable to delete previously exported file ('{0}'). Please close if opened.".format(file))
            exit()

def get_longest_column(events):
    longest = {}
    for event in events:
        for key in event:
            longest[key] = 0

    for event in events:
        for key in event:
            if len(str(event[key])) > longest[key]:
                longest[key] = len(str(event[key]))

    return longest

if __name__ == '__main__':
    # "python ical.py filename.ics -csv/-txt/-"
    cur_line = 0
    lines = process_file(sys.argv[1])
    events = get_events_dict(lines)


    if "-csv" in sys.argv:
        delete_file("{0}_export.csv".format(sys.argv[1]))

        with open("{0}_export.csv".format(sys.argv[1]), "a", encoding="utf-8") as file:
            file.write("no;summary;description;start;end;stamp;modified;rule\n")
            
            for event in events:
                cur_line += 1
                file.write("{0};{1};{2};{3};{4};{5}\n".format(
                    cur_line,
                    clear_illegal(event.get('summary')),
                    clear_illegal(event.get('description')),
                    event.get('dtstart'),
                    event.get('dtend'),
                    clear_illegal(event.get('rule')),
                ))

    if "-txt" in sys.argv:
        delete_file("{0}_export.txt".format(sys.argv[1]))
        longest = get_longest_column(events)
        print(longest)

        with open("{0}_export.txt".format(sys.argv[1]), "a", encoding="utf-8") as file:
            for event in events:
                cur_line += 1
                file.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n".format(
                    str(cur_line).rjust(4, "0"),
                    clear_illegal(event.get('summary')).ljust(longest.get('summary')),
                    clear_illegal(event.get('description')).ljust(longest.get('summary')),
                    event.get('dtstart'),
                    event.get('dtend'),
                    clear_illegal(event.get('rule')).ljust(longest.get('summary')),
                ))

    print("There are total {0} event(s)".format(len(events)))
            

