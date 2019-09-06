#!/usr/bin/env python
"""
Script/Module for dumping Atlas TC/SSC modules after calibration at SeaBird
"""

import os, time, sys, re, argparse, logging
import serial
import serial.tools.list_ports

LOGGER = None
FLOGGER = None
try:
    import colorlog

    LOGGER = colorlog.getLogger("ModuleDumper")
    sh = colorlog.StreamHandler()
    sh.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s %(name)s: %(message)s",
            log_colors={
                "DEBUG": "white,bg_black",
                "INFO": "blue",
                "WARNING": "red",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )
except:
    LOGGER = logging.getLogger("ModuleDumper")
    sh = logging.StreamHandler()
    # handler.setFormatter(logging.Formatter(' * %(name)s : %(message)s'))
    sh.setFormatter(logging.Formatter("\033[1;31m%(name)s : %(message)s\033[0m"))
LOGGER.addHandler(sh)

# patterns and formats
######################
dtpat = re.compile(r"(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2})")
cafepat = re.compile(
    r"CAFE \d{4}/\d{2}/\d{2}  \d{2}:\d{2}:\d{2}  [0-9A-F]{5} [0-9A-F]{5} [0-9A-F]{5}"
)
crlfpat = re.compile(r" *\r\n")
linend = "\n"
isofmt = "%Y-%m-%d %H:%M:%S"
moddtfmt = "%m/%d/%Y %H:%M:%S"


class ModuleMeta(object):
    """
    Somewhere to put module metadata read from header
    """

    ####################################
    def __init__(self, headerlines):
        """"""
        self.rawheader = headerlines
        self.prefix = ""
        self.softvers = None
        self.dumpdt = None
        self.ndumprec = 0
        self.modtype = None
        self.modserial = None
        self.cellserial = None
        self.ioserial = None
        self.sampintv = None
        self.avgintv = None
        self.voltage = None
        self.cafe = False
        self.badclock = False
        self.nodump = False
        self.comment = ""

    ##########################
    def parseheader(self):
        """
        Read the output of the wakeup or STATUS command, extract metadata
        """
        for line in self.rawheader.split("\n"):

            pat = "QUITTING"
            if pat in line:
                self.prefix = line
                continue

            pat = "VERSION NUMBER"
            if pat in line:
                self.softvers = line[28:].strip()
                continue

            pat = "DATE/TIME IS"
            if pat in line:
                meta = line[22:].strip()
                matchobj = dtpat.match(meta)
                if matchobj:
                    try:
                        self.dumpdt = time.mktime(time.strptime(meta, moddtfmt))
                    except:
                        self.nodump = True
                        self.comment += " *** Cannot read module date/time: {}\n".format(
                            meta
                        )
                    continue

            pat = "NUMBER RECORDS IS"
            if pat in line:
                self.ndumprec = line[22:].strip()
                continue

            pat = "MODULE TYPE IS"
            if pat in line:
                self.modtype = line[22:].strip()
                continue

            pat = "SERIAL NUMBER IS"
            if pat in line:
                self.modserial = line[22:].strip()
                continue

            pat = "COND S/N IS"
            if pat in line:
                meta = line[22:].strip()
                serials = meta.split("/")
                self.cellserial = serials[1]
                self.ioserial = serials[0]
                continue

            pat = "SAMPLING INTERVAL IS"
            if pat in line:
                meta = line[22:].strip()
                self.sampintv = meta
                if meta == "00:01:00":
                    self.nodump = False
                    self.comment += " *** Sample interval is {}\n".format(meta)
                elif meta != "00:02:00":
                    self.nodump = True
                    self.comment += " *** Sample interval is {}\n".format(meta)
                continue

            pat = "AVERAGE INTERVAL IS"
            if pat in line:
                self.avgintv = line[22:].strip()
                if int(self.avgintv) != 24:
                    self.nodump = True
                    self.comment += " *** Average interval is {}\n".format(meta)
                continue

            pat = "BATTERY VOLTAGE IS"
            if pat in line:
                self.voltage = line[22:].strip()
                continue

        return self.modserial

    def meta_summary(self, compclock, tolerance, prefix=0):
        """
        Check module clock against computer clock
        Print metadata summary
        """
        dtdelta = int(compclock - self.dumpdt)
        dtdays = int(abs(dtdelta) / 86400)
        dthours = int((abs(dtdelta) - (dtdays * 86400)) / 3600)
        dtmins = int((abs(dtdelta) - (dtdays * 86400) - (dthours * 3600)) / 60)
        dtsecs = int(abs(dtdelta) - (dtdays * 86400) - (dthours * 3600) - (dtmins * 60))
        dtsign = "-"
        if dtdelta < 0:
            dtsign = "+"

        if abs(dtdelta) > tolerance:
            self.badclock = True

        if self.prefix and prefix:
            sys.stderr.write("\n{}\n\n".format(self.prefix))

        sys.stderr.write("\n")
        LOGGER.info("Module Type        : {}".format(self.modtype))
        LOGGER.info("Module Serial      : {}".format(self.modserial))
        LOGGER.info("Cell Serial        : {}".format(self.cellserial))
        LOGGER.info("Cond I/O Serial    : {}".format(self.ioserial))

        sys.stderr.write("\n")
        LOGGER.info(
            "Computer Time      : {}".format(
                time.strftime(isofmt, time.localtime(compclock))
            )
        )
        if self.nodump:
            LOGGER.warning(
                "Module Time        : {}".format(
                    time.strftime(isofmt, time.localtime(self.dumpdt))
                )
            )
        else:
            LOGGER.info(
                "Module Time        : {}".format(
                    time.strftime(isofmt, time.localtime(self.dumpdt))
                )
            )
        if self.badclock:
            LOGGER.warning(
                "Module Clock Error : {} {} d {:02d}:{:02d}:{:02d}".format(
                    dtsign, dtdays, dthours, dtmins, dtsecs
                )
            )
        else:
            LOGGER.info(
                "Module Clock Error : {} {} d {:02d}:{:02d}:{:02d}".format(
                    dtsign, dtdays, dthours, dtmins, dtsecs
                )
            )

        sys.stderr.write("\n")
        LOGGER.info("Voltage            : {}".format(self.voltage))
        if self.nodump:
            LOGGER.warning("Sample Interval    : {}".format(self.sampintv))
            LOGGER.warning("Average Interval   : {} hours".format(int(self.avgintv)))
        else:
            LOGGER.info("Sample Interval    : {}".format(self.sampintv))
            LOGGER.info("Average Interval   : {} hours".format(int(self.avgintv)))
        LOGGER.info("Number of Records  : {}".format(int(self.ndumprec)))
        sys.stderr.write("\n")
        if self.cafe:
            LOGGER.warning("*** Downloaded data include blocks with sync field 'CAFE'")
            sys.stderr.write("\n")

        if not prefix:
            FLOGGER.info("\nModule Type        : {}".format(self.modtype))
            FLOGGER.info("Module Serial      : {}".format(self.modserial))
            FLOGGER.info("Cell Serial        : {}".format(self.cellserial))
            FLOGGER.info("Cond I/O Serial    : {}".format(self.ioserial))
            FLOGGER.info(
                "\nComputer Time      : {}".format(
                    time.strftime(isofmt, time.localtime(compclock))
                )
            )
            FLOGGER.info(
                "Module Time        : {}".format(
                    time.strftime(isofmt, time.localtime(self.dumpdt))
                )
            )
            FLOGGER.info(
                "Module Clock Error : {} {} d {:02d}:{:02d}:{:02d}".format(
                    dtsign, dtdays, dthours, dtmins, dtsecs
                )
            )
            FLOGGER.info("\nVoltage            : {}".format(self.voltage))
            FLOGGER.info("Sample Interval    : {}".format(self.sampintv))
            FLOGGER.info("Average Interval   : {} hours".format(int(self.avgintv)))
            FLOGGER.info("Number of Records  : {}\n".format(int(self.ndumprec)))
            if self.cafe:
                FLOGGER.info(
                    "*** Downloaded data include blocks with sync field 'CAFE'"
                )
            FLOGGER.info("\n-----\n")


def ask_for_port():
    """
    Show a list of ports and ask the user for a choice. To make selection
    easier on systems with long device names, also allow the input of an
    index.
    """
    sys.stderr.write("\n--- Available ports:\n\n")
    ports = []
    # for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
    for n, (port, desc, hwid) in enumerate(
        sorted(serial.tools.list_ports.grep(r"usb")), 1
    ):
        # sys.stderr.write(' {:2}: {:20}\n\n'.format(n, port))
        sys.stderr.write(" {:2}: {:20}: {}\n".format(n, port, desc))
        ports.append(port)
    if len(ports):
        while True:
            port = eval(input("\n--- Enter port index or full name or X to exit: "))
            sys.stderr.write("\n")
            if isinstance(port, str) and port.upper() == "X":
                sys.exit(0)
            try:
                index = port - 1
                if not 0 <= index < len(ports):
                    LOGGER.warning("*** Invalid index!")
                    continue
            except ValueError:
                pass
            else:
                port = ports[index]
            return port
    else:
        LOGGER.warning("*** No serial ports detected ... aborting")
        sys.exit(0)


def clear_input_buffer(ser):
    """
    Write any extraneous serial input to stderr (like 'ENTERING MONITOR SNOOZE')
    """
    sys.stderr.write("\n")
    LOGGER.warning("***** Unprocessed input buffer content *****")
    sys.stderr.write("\n")
    capture = ""
    rx = 1
    while rx:
        rx = ser.read(ser.in_waiting or 1)
        if rx:
            capture += rx.decode()
    if capture != "":
        LOGGER.info(capture.strip())
    sys.stderr.write("\n")
    LOGGER.warning("********************************************")
    sys.stderr.write("\n")
    ser.reset_input_buffer()


def wake_tc_get_header(ser, debug=0):
    """
    Send Ctrl-C Ctrl-C to TC module to wake it up, capture header content
    Get computer's UTC time for comparison to time reported in module header
    If debug flag, write module response to stderr
    """
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    command = "\x03\x03"
    for c in command:
        n = ser.write(c.encode())
        if debug:
            LOGGER.debug("{} byte ({}) written to port".format(n, repr(c)))
        time.sleep(0.1)

    utc = time.gmtime()
    timecheck = time.mktime(tuple(list(utc[:8]) + [time.localtime().tm_isdst]))
    # timecheck = time.mktime(time.gmtime())
    capture = ""
    rx = 1
    while rx:
        rx = ser.read(ser.in_waiting or 1).decode()
        if rx:
            if debug:
                LOGGER.debug(rx)
            capture += rx

    if capture.strip():
        return timecheck, crlfpat.sub(linend, capture)
    return None, None


def wake_ssc_get_header(ser, debug=0):
    """
    Wait 10 seconds for response to waking SSC module, capture header content
    Get computer's UTC time for comparison to time reported in module header
    If debug flag, write module response to stderr
    """
    ser.reset_output_buffer()

    xloop = 0
    while not ser.in_waiting:
        xloop += 1
        if xloop > 1000:
            return None, None
        time.sleep(0.01)
    utc = time.gmtime()
    timecheck = time.mktime(tuple(list(utc[:8]) + [time.localtime().tm_isdst]))
    # timecheck = time.mktime(time.gmtime())
    capture = ""
    rx = 1
    while rx:
        rx = ser.read(ser.in_waiting or 1).decode()
        if rx:
            if debug:
                sys.stderr.write(rx)
            capture += rx

    if capture.strip():
        return timecheck, crlfpat.sub(linend, capture)
    return None, None


def send_cmd(ser, command, debug=0):
    """
    Send command to module, wait for response
    Return response
    """
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    for c in command:
        n = ser.write(c.encode())
        if debug:
            LOGGER.debug("{} byte ({}) written to port".format(n, repr(c)))
        time.sleep(0.1)

    out = ""
    rx = 1
    while rx:
        rx = ser.read(ser.in_waiting or 1)
        if rx:
            out += rx.decode()
            if debug:
                LOGGER.debug(rx)

    return out


def dump_data(ser, meta, args):
    """
    Send 'TEXT.DUMP' command to module, wait for response
    Write response (hopefully module header and data) to stderr and output file.
    Check each record for sync flag 'CAFE', change output file name as necessary.
    """
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    command = "TEXT.DUMP\r"
    rx = ""
    ntry = 0
    while not rx or (rx.split()[-1] != "data?"):
        rx = send_cmd(ser, command, args.debug)
        #      sys.stderr.write(rx)
        ntry += 1
        if ntry > 3:
            LOGGER.warning("Wrong response to dump command ({})".format(command))
            return 0

    command = "Y"
    rx = ""
    ntry = 0
    while not rx or (rx.split()[-1] != "ready"):
        rx = send_cmd(ser, command, args.debug)
        # sys.stderr.write(rx)
        ntry += 1
        if ntry > 3:
            LOGGER.warning("Wrong response to dump command ({})".format(command))
            return 0

    c = "\r"
    n = ser.write(c.encode())
    if args.debug:
        LOGGER.debug("{} byte ({}) written to port\n".format(n, repr(c)))
    time.sleep(0.05)

    dumpst = time.time()
    suff = ""
    if meta.badclock:
        suff = "-badclock"

    fname = "{}/{}sb.{}{}".format(args.path, meta.modserial, args.calday, suff)
    fh = open(fname, "w")

    fraw = ""
    rxline = 1
    while rxline:
        rxline = ser.readline()
        if rxline:
            sys.stdout.write(rxline.decode())
            fout = crlfpat.sub(linend, rxline.decode())
            if cafepat.search(fout):
                meta.cafe = True
            fh.write(fout)
    fh.close()

    if meta.cafe:
        frename = fname + "-cafe"
        os.rename(fname, frename)
        fname = frename

    dumpend = time.time()
    fsize = os.stat(fname).st_size
    sys.stderr.write("\n\n")
    if meta.badclock or meta.cafe:
        LOGGER.warning("Wrote {} bytes to {}".format(fsize, fname))
    else:
        LOGGER.info("Wrote {} bytes to {}".format(fsize, fname))
    LOGGER.info(
        "Dumped {} records in {:.1f} seconds".format(meta.ndumprec, (dumpend - dumpst))
    )

    FLOGGER.info("Wrote {} bytes to {}".format(fsize, fname))
    FLOGGER.info(
        "Dumped {} records in {:.1f} seconds".format(meta.ndumprec, (dumpend - dumpst))
    )

    return fsize


# ==============================================================================
# ==============================================================================
#                          Execution Starts Here
# ==============================================================================


parser = argparse.ArgumentParser(
    description="Dump data from TC/SSC ATLAS modules using pyserial library"
)
parser.add_argument(
    "-p",
    "--path",
    action="store",
    dest="path",
    default="./",
    help="Optional path to files",
)
parser.add_argument(
    "--calday",
    action="store",
    dest="calday",
    default="xxx",
    help="Day-of-year for calibration (001-366)",
    required=True,
)
parser.add_argument(
    "--clock",
    "--tolerance",
    action="store",
    dest="clocksecs",
    default=90,
    help="Tolerance for flagging module clocktime (seconds)",
)
parser.add_argument(
    "-v",
    "--verbose",
    "--debug",
    action="store_true",
    dest="debug",
    help="Flag for verbose output",
)
parser.add_argument(
    "-ll",
    "--loglevel",
    type=str,
    dest="loglevel",
    default="INFO",
    help="Set the logging level",
    choices=[
        "DEBUG",
        "debug",
        "INFO",
        "info",
        "WARNING",
        "warning",
        "ERROR",
        "error",
        "CRITICAL",
        "critical",
    ],
)

args = parser.parse_args()
if args.path.endswith("/"):
    args.path = args.path[:-1]

LOGGER.setLevel(args.loglevel.upper())

port = ask_for_port()

# defaults are what is needed: 9600,N,8,1
try:
    ser = serial.Serial(port, timeout=2, inter_byte_timeout=0.1, xonxoff=True)
except:
    LOGGER.warning(" *** Unknown serial port: '{}' ... aborting".format(port))
    sys.exit(1)
time.sleep(1)

if ser.isOpen():

    sys.stderr.write("Serial port is open ...\n\n")
    flogname = "{}/sb{}_{}.log".format(
        args.path, args.calday, time.strftime("%d%b%Y-%H%M", time.localtime())
    )
    FLOGGER = logging.getLogger("SessionLog")
    fh = logging.FileHandler(flogname)
    fh.setFormatter(logging.Formatter("%(message)s"))
    FLOGGER.addHandler(fh)
    FLOGGER.setLevel(logging.INFO)

    while True:

        if ser.in_waiting:
            clear_input_buffer(ser)

        select = eval(
            'input("Connect to module and Enter module type (T:TC, S:SSC) or X to Exit : ")'
        )

        if select.upper() not in ("X", "S", "T"):
            continue

        if select.upper() == "X":
            if ser.in_waiting:
                clear_input_buffer(ser)
            sys.stderr.write("\nUser abort ... exiting\n\n")
            break

        else:
            # dump SSC: press button on board
            if select.upper() == "S":
                sys.stdout.write(
                    "Press white button switch on module CPU board to wake module (10 sec timeout)\n"
                )
                tmcheck, header = wake_ssc_get_header(ser, args.debug)
            # dump TC: control-C to start
            elif select.upper() == "T":
                tmcheck, header = wake_tc_get_header(ser, args.debug)

            if header and header.strip():
                modmeta = ModuleMeta(header)
                if modmeta.parseheader():
                    modmeta.meta_summary(tmcheck, int(args.clocksecs), 1)
                else:
                    LOGGER.warning(
                        "Could not parse header: {}".format(repr(modmeta.rawheader))
                    )
                    if ser.in_waiting:
                        clear_input_buffer(ser)
                    continue
            else:
                LOGGER.warning("Header not dumped")
                if ser.in_waiting:
                    clear_input_buffer(ser)
                continue

        if not modmeta:
            continue

        if modmeta.nodump:
            LOGGER.warning("Download aborted:\n{}".format(modmeta.comment))
            continue

        yorn = eval('input("Download data from this module? [Y/n] : ")')
        if not yorn:
            yorn = "Y"
        if yorn.upper() != "Y":
            continue

        if dump_data(ser, modmeta, args):
            modmeta.meta_summary(tmcheck, int(args.clocksecs), 0)

    ser.close()
    if os.stat(flogname).st_size == 0:
        os.unlink(flogname)

else:
    sys.stderr.write("\n")
    LOGGER.warning("*** Serial port {} not opened ***".format(port))

sys.exit()
