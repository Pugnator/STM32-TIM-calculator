## STM32 Timer Calculator

This is a script that helps calculate the prescaler and period values for a timer on the STM32 microcontroller in order to achieve a target frequency.

## Prerequisites

* Python 2.7/3.x
* Numpy
* Pandas

## Example usage:

TIM clock = 100MHz, timer period 1 second, get only precise valuses, top 3

```
python TIMcalc.py --tim --clock=100MHz --time=1sec --top=3 --strict

Calculating a timer for clock=100000000Hz, period=1Hz

PSC    ARR      FREQ         ERROR EXACT
9999   9999  1.000000  0.0000000000   YES
9998  10000  1.000000  0.0000000000   YES
9997  10001  1.000000  0.0000000000   YES
```


Calculate timer period if PSC=700, ARR=65000 and TIM clock is 64MHz

```
python TIMcalc.py --period --psc=700 --arr=65000 --clock=64MHz

Calculating period for clock=64000000, arr=65000, psc=700
Timer period 1000.00ms [1.0Hz]
```


```
options:

  -h, --help     show this help message and exit
  --period       Calculate the timer period from ARR and PSC
  --strict       Show only values for timer period without error
  --top     	 Get only this number of results
  --tim          Calculate the timer ARR, PSC for specified clock frequency
  --arr	         Timer auto-reload value, 16bit
  --psc          Timer prescaler value, 16bit
  --clock        Timer clock frequency (Hz or human-readable string)
  --time         Timer period (seconds or human-readable string)
  ```
  
## License

This project is licensed under the Creative Common License - see the LICENSE file for details.


## Acknowledgments

* This script was modified from a script found on [StackOverflow](https://stackoverflow.com/questions/51906691/stm32f4-timers-calculation-of-period-and-prescale-and-generating-1-ms-delay).