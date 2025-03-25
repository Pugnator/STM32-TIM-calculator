# STM32 Timer Calculator

## Overview
This script is for calculating STM32 timer values, including prescaler (PSC) and auto-reload register (ARR) values.  
It helps determine appropriate timer configurations for achieving a desired time period when you're lazy enough.

## Features
- Convert timer clock frequency from human-readable format (e.g., `72MHz`) to Hz.
- Convert time duration from human-readable format (e.g., `1ms`, `500us`) to seconds.
- Calculate possible prescaler and ARR values based on the provided timer clock and target time.
- Display top closest matching configurations.
- Calculate the actual timer frequency given clock, prescaler, and ARR.

## Dependencies
This script requires the following Python libraries:

- `argparse` (standard library)
- `pandas`
- `numpy`
- `re` (standard library)

Install missing dependencies using:
```sh
pip install pandas numpy
```

## Usage
```sh
python stm32_timer_calc.py --clock <frequency> --time <period> [options]
```

### Arguments:
| Argument            | Description |
|---------------------|-------------|
| `--clock`          | Timer clock frequency (e.g., `72MHz`) |
| `--time`           | Target timer period (e.g., `1ms`, `500us`) |
| `--arr`            | Timer auto-reload value (16-bit) |
| `--psc`            | Timer prescaler value (16-bit) |
| `--tim`            | Calculate ARR and PSC values for a given clock frequency |
| `--period`         | Calculate the timer period for a given clock, ARR, and prescaler |
| `--exact`          | Show only exact matches |
| `--top`            | Show the top N closest results (default: 10) |

### Example Usage
#### Calculate timer settings:
```sh
python stm32_timer_calc.py --clock 72MHz --time 1ms --tim
```

#### Calculate timer period:
```sh
python stm32_timer_calc.py --clock 72MHz --arr 999 --psc 71 --period
```

## Output Example
```
 PSC   ARR  Real Time  Error (ms)
  71   999     1.000        0.00
 143   499     1.000        0.00
  35  1999     1.000        0.00
```

## Notes
- The script assumes that the timer runs in up-counting mode.
- The maximum value for ARR and PSC is 65535 (16-bit limit).
- Input values must be valid and in supported formats (`MHz`, `ms`, `us`, etc.).

## License
This project is open-source and free to use under the MIT License.

