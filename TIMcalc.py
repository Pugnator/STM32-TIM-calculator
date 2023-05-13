'''
Modified version of the script from
https://stackoverflow.com/questions/51906691/stm32f4-timers-calculation-of-period-and-prescale-and-generating-1-ms-delay
'''

import argparse

import numpy as np

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd

TARGET_F = 0
CLOCK_TIM = 0
TOLERANCE = 0.0001

DESCRIPTION = """STM32 timer calculator
        --------------------------------------------------------------
        This script takes the clock frequency and target frequency as inputs, and outputs the prescaler and period values that can be used to configure a timer on the STM32 microcontroller to achieve the desired frequency.
        The script uses a combination of exact and approximate calculations to generate a list of possible values, which are sorted by error rate and prescaler value to give the user the most accurate and efficient options.
        The output is presented in a pandas dataframe, with columns for prescaler, period, frequency, error rate, and exactness. The user can then choose the combination that best fits their needs.
        --------------------------------------------------------------
        """


# -----------------------------------------------------

def calculateTimerFreq(clock, psc, arr):
    if None in [clock, psc, arr]:
        return None

    return clock / ((psc + 1) * (arr + 1))


def abs_error(num1, num2):
    return abs((num1 - num2) / num1)


def hertz(clock, prescaler, period):
    f = clock / (prescaler * period)
    return f


def perfect_divisors():
    exacts = []
    for psc in range(1, 65536):
        arr = CLOCK_TIM / (TARGET_F * psc)
        if CLOCK_TIM % psc == 0:
            if arr <= 65536:
                exacts.append(psc)
    return exacts


def add_exact_period(prescaler):
    entries = []
    arr = CLOCK_TIM / (TARGET_F * prescaler)
    if arr == int(arr):
        entry = [prescaler, arr, TARGET_F, 0.0]
        entries.append(entry)
    return entries


def possible_prescaler_value(exact_prescalers):
    possibles = []
    for psc in range(1, 65536):
        if psc in exact_prescalers:
            continue
        h1 = hertz(CLOCK_TIM, psc, 1)
        h2 = hertz(CLOCK_TIM, psc, 65536)
        if h1 >= TARGET_F >= h2:
            possibles.append(psc)
    return possibles


def close_divisor(psc, tolerance):
    arr = CLOCK_TIM / (TARGET_F * psc)
    error = abs_error(int(arr), arr)
    if error < tolerance and arr < 65536.0:
        h = hertz(CLOCK_TIM, psc, int(arr))
        return psc, int(arr), h, error
    else:
        return None


#  ------------------------------------------------------------------------
def calculate(clock, period, exact):
    global CLOCK_TIM, TARGET_F
    CLOCK_TIM = clock
    TARGET_F = period

    # Make a dataframe to hold results as we compute them
    df = pd.DataFrame(columns=['PSC', 'ARR', 'FREQ', 'ERROR'], dtype=np.double)

    # Get exact prescalars first.
    exact_prescalers = perfect_divisors()
    exact_values = []
    for index in range(len(exact_prescalers)):
        rows = add_exact_period(exact_prescalers[index])
        for rowindex in range(len(rows)):
            df = df.append(pd.DataFrame(np.array(rows[rowindex]).reshape(1, 4), columns=df.columns))

    # Get possible prescalers.
    poss_prescalers = possible_prescaler_value(exact_prescalers)
    close_prescalers = []
    for index in range(len(poss_prescalers)):
        value = close_divisor(poss_prescalers[index], TOLERANCE)
        if value is not None:
            close_prescalers.append((value[0], value[1], value[2], value[3]))
    df = df.append(pd.DataFrame(np.array(close_prescalers).reshape(len(close_prescalers), 4), columns=df.columns))

    #  Adjust PSC and ARR values by -1 to reflect the way you'd code them.
    df['PSC'] = df['PSC'] - 1
    df['ARR'] = df['ARR'] - 1

    #  Sort first by errors (zeroes and lowest errors at top of list, and
    #  then by prescaler value (ascending).
    df = df.sort_values(['ERROR', 'PSC'])

    # Make and populate column indicating if combination is exact.
    df['EXACT'] = pd.Series("?", index=df.index)
    df['EXACT'] = np.where(df['ERROR'] == 0.0, "YES", "NO")

    #  Format for output.
    df['PSC'] = df['PSC'].map('{:.0f}'.format)
    df['ARR'] = df['ARR'].map('{:.0f}'.format)
    df['FREQ'] = df['FREQ'].map('{:.6f}'.format)
    df['ERROR'] = df['ERROR'].map('{:.10f}'.format)
    return df


def parse_clock_freq(clock_freq_str):
    clock_freq_str = clock_freq_str.strip().lower()
    suffixes = {
        'hz': 1,
        'khz': 1000,
        'mhz': 1000000,
        'ghz': 1000000000
    }
    if clock_freq_str.isdigit():
        return int(clock_freq_str)
    for suffix, multiplier in suffixes.items():
        if clock_freq_str.endswith(suffix):
            prefix = clock_freq_str[:-len(suffix)]
            if prefix.isdigit():
                return int(prefix) * multiplier
    raise ValueError("Invalid clock frequency: %s" % clock_freq_str)



def parse_time(time_str):
    """Convert a human-readable time string to its corresponding number of seconds."""
    if time_str.isdigit():
        # The input is already a number, assume it's in seconds
        return int(time_str)
    elif time_str.endswith("hz"):
        # Time in herzes
        return 1.0 / int(time_str[:-2])
    elif time_str.endswith("sec"):
        # Time in seconds
        return int(time_str[:-3])
    elif time_str.endswith("m"):
        # Time in minutes
        return int(time_str[:-1]) * 60.0
    elif time_str.endswith("h"):
        # Time in hours
        return int(time_str[:-1]) * 3600.0
    elif time_str.endswith("ms"):
        # Time in milliseconds
        return int(time_str[:-2]) / 1000.0
    elif time_str.endswith("us"):
        # Time in microseconds
        return int(time_str[:-2]) / 1000000.0
    elif time_str.endswith("ns"):
        # Time in nanoseconds
        return int(time_str[:-2]) / 1000000000.0
    else:
        raise ValueError("Invalid time format: %s" % time_str)


def args_processing(parser):
    parser = argparse.ArgumentParser(description="Calculate STM32 timer period and frequency.")
    parser.add_argument("--period", help="Calculate the timer period from ARR and PSC", action="store_true")
    parser.add_argument("--exact", help="Show only values giving no error", action="store_true")
    parser.add_argument("--top", help="Get only this number of results", type=lambda x: int(x, 0))
    parser.add_argument("--tim", help="Calculate the timer ARR, PSC for specified clock frequency", action="store_true")
    parser.add_argument("--arr", help="Timer auto-reload value, 16bit", type=lambda x: int(x, 0))
    parser.add_argument("--psc", help="Timer prescaler value, 16bit", type=lambda x: int(x, 0))
    parser.add_argument("--clock", required=True, help="Timer clock frequency (Hz or human-readable string)")
    parser.add_argument("--time", help="Timer period (seconds or human-readable string)")

    return parser.parse_known_args()


def calcperiod(clock, arr, prescaler):
    clock = parse_clock_freq(clock)
    print("Calculating period for clock={}, arr={}, psc={}".format(clock, arr, prescaler))
    period = calculateTimerFreq(clock, prescaler, arr)
    if period != 0:
        print("Timer period {:.2f}ms [{:.1f}Hz]".format(1.0 / (period / 1000.0), period))
    else:
        print("Period = 0. Impossible to calculate.")    


def calctim(clock, period_sec, exact, top):
    clock = parse_clock_freq(clock)
    period = parse_time(period_sec)

    if 0 == period:
        print("Period = 0. Impossible to calculate.")
        return
    
    period = 1 / period
    
    print("Calculating a timer for clock={}Hz, period={}Hz".format(clock, period))
    output = calculate(clock, period, True)
    if exact:
        output = output.loc[output['EXACT'] == 'YES']
    if top:
        output = output.sort_values('PSC', ascending=False).head(top)
    print(output.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
    args, leftovers = args_processing(parser)
    clock = parse_clock_freq(args.clock[0])
    if args.period:
        if None in [args.clock, args.psc, args.arr]:
            parser.print_help()
            return
        calcperiod(args.clock, args.arr, args.psc)
        return

    if args.tim:
        if None in [args.clock, args.time]:
            parser.print_help()
            return
        
        calctim(args.clock, args.time, args.exact, args.top)       


if __name__ == '__main__':
    main()
