# -*- coding: utf-8 -*-
import csv
import sqlite3
import sys
import time
import os
import functools

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# db = "nvs.sqlite"

class NavisionError(sqlite3.Error):
    def __init__(self, e):
        super().__init__(e)

class HaltError(Exception):
    def __init__(self):
        super().__init__("Stopped by user!")

def performance(func):
    @functools.wraps(func)
    def performance_wrapper(*args, **kwargs):
        start = time.time()
        val = func(*args, **kwargs)
        run_time = time.time() - start
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        #kv = ["{0} - {1}".format(k, v) for k,v in kwargs.items()]
        #a = ["{0}".format(a) for a in args]
        return val
    return performance_wrapper



class Navision():
    ''' Main class '''
    total_rows = 0

    def __init__(self, db, debug = False):
        self.db = db
        self.debug = debug
        pass

    @staticmethod
    def __progressbar(current = 0, total = 100, length = 30, char = "#", empty = ".", message = ""):
        ''' CLI progress bar '''
        bar = char * int(round(length * current / float(total))) + empty * (length - int(round(length * current / float(total))))
        sys.stdout.write('[{0}] {1}{2} ... {3}\r'.format(bar, round(current / float(total) * 100, 1), "%", message))
        sys.stdout.flush()

    def __debug(self, message):
        if self.debug:
            print("[{0}] {1}".format(time.strftime("%H:%M", time.localtime()), message))

    @staticmethod
    def __list_to_strings(lst, delimiter = ', '):
        ''' Formating column names '''
        total = ""

        for l in lst:
            total +="'{0}'{1}".format(l, delimiter)

        return Navision.__replace_invalid(total[:-len(delimiter)])

    @staticmethod
    def __replace_invalid(vals):
        ''' Bosnian conversions '''
        return vals.replace("È", "Č").replace("Ž", "Ž").replace("Æ", "Ć").replace("è", "č").replace("ž", "ž").replace("Š", "Š").replace("æ", "ć")

    @staticmethod
    def __form_query(q):
        ''' Format a FTS5 string '''
        result = ""
        q = q.strip()
        for k in q.split(' '):
            result += " AND " + k

        return result[5:]

    def __qd(self, sql):
        ''' Query SQL string, thread safe, with dict return '''
        results = []

        try:
            con = sqlite3.connect(self.db)
            con.row_factory = sqlite3.Row

            c = con.cursor()
            c.execute(sql)
            con.commit()

            rows = c.fetchall()
            con.close()

            for row in rows:
                results.append(dict(row))
            return results

        except sqlite3.Error as e:
            self.__debug(sql)
            con.rollback()
            raise NavisionError(e)

        finally:
            con.close()

    def __q(self, sql):
        ''' Querying SQL string, thread safe, with retrun as touple '''
        try:
            con = sqlite3.connect(self.db)
            c = con.cursor()
            c.execute(sql)
            con.commit()
            rows = c.fetchall()
            con.close()

            return rows

        except sqlite3.Error as e:
            self.__debug(sql)
            con.rollback()
            raise NavisionError(e)

        finally:
            con.close()

    @performance
    def convert_csv(self, filename, encoding = 'cp1252', delimiter = ';'):
        start = time.time()
        sql = "CREATE VIRTUAL TABLE navision USING FTS5({0});"

        cols_list = []
        cols_str = ""

        try:
            with open(filename, newline="", encoding = encoding) as f:
                c = csv.DictReader(f, delimiter = delimiter)

                for fn in c.fieldnames:
                    cols_list.append(fn)

                for rt in c:
                    self.total_rows += 1

            with open(filename, newline = '', encoding = encoding) as f:
                c = csv.DictReader(f, delimiter = delimiter)
                sql = sql.format(self.__list_to_strings(cols_list))
                cols_str = self.__list_to_strings(cols_list)

                r = self.__q(sql)

                i = 0
                for row in c:
                    current = self.__list_to_strings(row.values())
                    sql = "INSERT INTO NAVISION ({0}) VALUES ({1})".format(cols_str, current)
                    # sqlite is UTF-8 :/
                    result = self.__q(sql.encode('utf-8').decode())
                    i += 1
                    self.__progressbar(i, self.total_rows, length = 30, message = row.get('br'))

        except KeyboardInterrupt:
            raise HaltError

        self.__debug("Finished in: {0}s".format(round(time.time() - start), 2))

    @performance
    def search(self, o):
        if ">" in o:
            i = o.index(">")
            if o[i + 1] == " ":
                amount = o[(i + 2):]
            elif o[i + 1] == " " and o[i + 2] == " ":
                amount = o[(i + 3):]
            else:
                amount = o[(i + 1):]

            search_string = o[:i]
            sql = "SELECT * FROM navision WHERE (br MATCH '{0}' OR opis MATCH '{0}' OR opis2 MATCH '{0}') AND (CAST(zalihe AS decimal) > {1}) COLLATE NOCASE".format(self.__form_query(search_string), amount)

        else:
            sql = "SELECT * FROM navision WHERE br MATCH '{0}' OR opis MATCH '{0}' OR opis2 MATCH '{0}' COLLATE NOCASE".format(self.__form_query(o))

        results = self.__qd(sql)

        return results

def display_results_table(results):
    tb = Table(show_header = True, header_style = "bold magenta", box = box.SIMPLE_HEAD)
    tb.add_column("Skl.")
    tb.add_column("Opis")
    tb.add_column("Opis2")
    tb.add_column("Polica")
    tb.add_column("KOL")

    for row in results:
        tb.add_row(row.get('br'), row.get('opis'), row.get('opis2'), row.get('brpolice'), row.get('zalihe'))

    console.print(tb)

def display_results_panel(results):
    for row in results:
        console.print(Panel("[magenta][bold][underline2]{0}[/underline2][/bold][/magenta]\n  [underline]{1}[/underline]\n  [gray]{2}[/gray]\n  Polica: {3}\n  Zalihe: {4}\n  Jedinični trošak: {5} KM".format(row.get('br'), row.get('opis'), row.get('opis2'), row.get('brpolice'), row.get('zalihe'), row.get('jedinicnitrosak'))))

def display_results(results, search_string):
    console.rule("Pretraga: [bold]'{0}'[/bold]".format(search_string))
    if console.width > 100:
        display_results_table(results)
    else:
        display_results_panel(results)

    console.log("[bold]'{1}'[/bold] (rez: {0})".format(len(results), search_string))

if __name__ == '__main__':
    mydb = "navision.sqlite"
    if "-h" in sys.argv or "--help" in sys.argv:
        os.system("cls||clear")
        console.print("----------------------------------")
        console.print("-c fname    - convert the filename")
        console.print("-h          - this")
        console.print("-           - opens the prompt")
        console.print("----------------------------------")


    elif "-c" in sys.argv:
        os.system("cls||clear")
        fname = sys.argv[(sys.argv.index("-c") + 1)]
        if os.path.exists(mydb):
            os.remove(mydb)

        n = Navision(mydb, debug = True)
        n.convert_csv(fname, encoding = 'cp1252', delimiter = ';')

    else:
        try:
            os.system("cls||clear")
            n = Navision(mydb, debug = True)
            o = Prompt.ask("Traži?")
            results = n.search(o)
            display_results(results, o)

        except KeyboardInterrupt:
            raise HaltError
