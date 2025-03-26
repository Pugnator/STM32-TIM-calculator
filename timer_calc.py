import argparse
import pandas as pd
import numpy as np
import re


def parse_clock_freq(clock_freq_str: str) -> int:
    match = re.match(r"(\d+(?:\.\d+)?)([kKmMgG]?[hHzZ]*)", clock_freq_str)
    if match:
        value, unit = match.groups()
        value = float(value)
        unit = unit.lower()
        
        unit_map = {"hz": 1, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}
        multiplier = unit_map.get(unit, 1)
        return int(value * multiplier)
    
    raise ValueError(f"Invalid clock frequency format: {clock_freq_str}")


def parse_time(time_str: str) -> float:
    match = re.match(r"(\d+(?:\.\d+)?)([mun]?[sS]?)", time_str)
    if match:
        value, unit = match.groups()
        value = float(value)
        
        unit_map = {"s": 1, "ms": 1e-3, "us": 1e-6, "ns": 1e-9}
        multiplier = unit_map.get(unit, 1)
        return value * multiplier
    
    raise ValueError(f"Invalid time format: {time_str}")


def perfect_divisors(n: int) -> list:
    return [i for i in range(1, n+1) if n % i == 0]


def possible_prescaler_value(clock_freq: int) -> list:
    return perfect_divisors(clock_freq)


def calc_timer(clock_freq: int, target_time: int, exact: bool, top: int) -> pd.DataFrame:
    best_diff = float('inf')
    best_psc, best_arr, best_real_time = None, None, None
    results = []
    
    for psc in possible_prescaler_value(clock_freq):
        psc_clock = clock_freq / psc
        arr = round(target_time * psc_clock)
        
        if 1 <= arr <= 65535:
            real_time = arr / psc_clock
            diff = abs(real_time - target_time)
            results.append((psc, arr, real_time))
            
            if diff < best_diff:
                best_psc, best_arr, best_real_time = psc, arr, real_time
                best_diff = diff
    
    df = pd.DataFrame(results, columns=["PSC", "ARR", "Real Time"])
    df["Error (ms)"] = (df["Real Time"] - target_time) * 1000
    df = df.sort_values("Error (ms)", ascending=True)
    
    if exact:
        df = df[df["Real Time"] == target_time]
    if top:
        df = df.head(top)
    
    return df


def calculate_timer_freq(clock: int, psc: int, arr: int) -> float:
    if None in [clock, psc, arr]:
        return None

    return clock / ((psc + 1) * (arr + 1))


def calc_period(clock: int, arr: int, prescaler: int) -> None:
    clock = parse_clock_freq(clock)
    print("Calculating period for clock={}, arr={}, psc={}".format(clock, arr, prescaler))
    period = calculate_timer_freq(clock, prescaler, arr)
    if period != 0:
        print("Timer period {:.2f}ms [{:.1f}Hz]".format(1.0 / (period / 1000.0), period))
    else:
        print("Period = 0. Impossible to calculate.")


def main():
    parser = argparse.ArgumentParser(description="STM32 timer calculator", add_help=False)
    parser.add_argument("--clock", type=str, help="Timer clock frequency (e.g., 72MHz)")
    parser.add_argument("--time", type=str, help="Target timer period (e.g., 1ms, 500us)")
    parser.add_argument("--arr", help="Timer auto-reload value, 16bit", type=lambda x: int(x, 0))
    parser.add_argument("--psc", help="Timer prescaler value, 16bit", type=lambda x: int(x, 0))
    parser.add_argument("--tim", help="Calculate the timer ARR, PSC for specified clock frequency", action="store_true")
    parser.add_argument("--period", help="Calculate the timer period for specified clock frequency", action="store_true")
    parser.add_argument("--exact", action="store_true", help="Show only exact matches")
    parser.add_argument("--top", type=int, default=10, help="Show top N closest results")
    
    args = parser.parse_args()

    if args.tim:
        if args.clock is None or args.time is None:
            print("Error: --clock and --time are required")
            parser.print_help()

        clock_freq = parse_clock_freq(args.clock)
        target_time = parse_time(args.time)
        df = calc_timer(clock_freq, target_time, args.exact, args.top)
        print(df.to_string(index=False))
        return
    
    if args.period:
        if None in [args.clock, args.psc, args.arr]:
            print("Error: --clock, --arr, --psc are required")
            parser.print_help()
            return
        
        calc_period(args.clock, args.arr, args.psc)
        return
    
    
    parser.print_help()

if __name__ == "__main__":
    main()
