import argparse
from pprint import pprint
import re


def parse_clock_freq(clock_freq_str: str) -> int:
    match = re.match(r"(\d+(?:\.\d+)?)([kKmMgG]?[hH][zZ])?$", clock_freq_str)
    if match:
        value, unit = match.groups()
        value = float(value)
        
        unit_map = {"hz": 1, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}
        normalized_unit = (unit or "Hz").lower()
        
        if normalized_unit not in unit_map:
            raise ValueError(f"Invalid clock frequency unit: {unit}")
        
        return int(value * unit_map[normalized_unit])


def parse_time(time_str: str) -> float:
    match = re.match(r"(\d+(?:\.\d+)?)(min|[mun]?[sS])?$", time_str)
    if match:
        value, unit = match.groups()
        value = float(value)

        unit_map = {"min": 60, "s": 1, "ms": 1e-3, "us": 1e-6, "ns": 1e-9}
        normalized_unit = unit.lower() if unit else "s"

        if normalized_unit not in unit_map:
            raise ValueError(f"Invalid time unit: {unit}")

        return value * unit_map[normalized_unit]    


def perfect_divisors(n: int) -> list:
    return [i for i in range(1, n+1) if n % i == 0 and i > 0]


def calc_timer(clock_freq: int, target_time: float, exact: bool, top: int):
    results = []
    
    for psc in perfect_divisors(clock_freq):
        psc_clock = clock_freq / psc
        arr = round(target_time * psc_clock)

        if 1 <= arr:
            real_time = arr / psc_clock            
            results.append({"PSC": psc, "ARR": arr, "Real Time": real_time, "Error (ms)": round((real_time - target_time) * 1000, 3)})

    results.sort(key=lambda x: abs(x["Error (ms)"]))

    if exact:
        results = [r for r in results if r["Real Time"] == target_time]
    if top:
        results = results[:top]
    
    return results


def calculate_timer_freq(clock: int, psc: int, arr: int) -> float:
    if clock <= 0:
        raise ValueError(f"Invalid clock frequency: {clock}")

    if psc < 0 or psc > 65534 or arr < 0 or arr > 65534:
        raise ValueError("PSC and ARR should be 16-bit values (0-65534)")

    divisor = (psc + 1) * (arr + 1)

    return clock / divisor


def calc_period(clock: int, arr: int, prescaler: int) -> None:
    clock = parse_clock_freq(clock)
    print("Calculating period for clock={}, arr={}, psc={}".format(clock, arr, prescaler))
    period = calculate_timer_freq(clock, prescaler, arr)
    if period != 0:
        print("Timer period {:.2f}ms [{:.1f}Hz]".format(1.0 / (period / 1000.0), period))
    else:
        print("Period = 0. Impossible to calculate.")


def main():
    parser = argparse.ArgumentParser(description="STM32 timer calculator")
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
        clock_freq = parse_clock_freq(args.clock)        
        target_time = parse_time(args.time)   
            
        df = calc_timer(clock_freq, target_time, args.exact, args.top)
        if not df:
            print("No possible PSC and ARR found for your input")
            return
        pprint(df)
        return
    
    if args.period:
        calc_period(args.clock, args.arr, args.psc)        
        return
    
    
    parser.print_help()

if __name__ == "__main__":
    main()
