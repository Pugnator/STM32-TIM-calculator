Helps to calculate STM32 TIM timer's parameters

Example usage:

TIm clock = 100MHz, timer period 1000ms, get only precise valuses, top 3

```
TIMcalc.py --calctim --clock=100000000 --ms=1000 --top=3 --exact

PSC    ARR      FREQ         ERROR EXACT
0  9999   9999  1.000000  0.0000000000   YES
0  7999  12499  1.000000  0.0000000000   YES
0  6399  15624  1.000000  0.0000000000   YES
```


Calculate timer period if PSC=700, ARR=65000 and TIM clock is 64MHz

```
TIMcalc.py --getperiod --psc=700 --arr=65000 --clock=64000000

Timer set to 1.404565245248833ms [711.964078125Hz]
```


```
options:
  -h, --help            show this help message and exit
  -e EXAMPLE, --example EXAMPLE
                        Find an example with specified word
  --getperiod           Calculate timer period from parameters
  --calctim             Calculate timer parameters
  --exact               Find parameters that match desired period exactly
  --clock CLOCK         Timer APB clock in Herz
  --hz HZ               Timer period in Herz
  --ms MS               Timer period in ms
  --s S                 Timer period in seconds
  --arr ARR             ARR value
  --psc PSC             PSC value
  --top TOP             Get top N results
  ```