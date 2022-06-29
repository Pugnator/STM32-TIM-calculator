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


def args_processing():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
    parser.add_argument('-e', '--example', nargs=1, help='Find an example with specified word')
    parser.add_argument('--getperiod', action='store_true', help='Calculate timer period from parameters')
    parser.add_argument('--calctim', action='store_true', help='Calculate timer parameters')
    parser.add_argument('--exact', action='store_true', help='Find parameters that match desired period exactly')
    parser.add_argument('--clock', nargs=1, type=int, help='Timer APB clock in Herz')
    parser.add_argument('--hz', nargs=1, type=int, help='Timer period in Herz')
    parser.add_argument('--ms', nargs=1, type=int, help='Timer period in ms')
    parser.add_argument('--s', nargs=1, type=int, help='Timer period in seconds')
    parser.add_argument('--arr', nargs=1, type=int, help='ARR value')
    parser.add_argument('--psc', nargs=1, type=int, help='PSC value')
    parser.add_argument('--top', nargs=1, type=int, help='Get top N results')

    processed_args = parser.parse_args()
    return processed_args


def main():
    args = args_processing()
    if args.getperiod:
        period = calculateTimerFreq(args.clock[0], args.psc[0], args.arr[0])
        print("Timer set to {}ms [{}Hz]".format(period, 1 / (period / 1000)))

    if args.calctim:
        if None in [args.clock]:
            return
        period = 0
        if args.ms:
            period = 1.0 / (args.ms[0] / 1000.0)
        elif args.s:
            period = 1.0 / args.s[0]
        elif args.hz:
            period = args.hz[0]

        output = calculate(args.clock[0], period, True)
        if args.exact:
            output = output.loc[output['EXACT'] == 'YES']
        if args.top:
            output = output.sort_values('PSC', ascending=False).head(args.top[0])
        print(output.to_string())


if __name__ == '__main__':
    main()
