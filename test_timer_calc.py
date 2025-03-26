import unittest
import subprocess
from timer_calc import parse_clock_freq, parse_time, calc_timer, calculate_timer_freq

class TestTimerCalc(unittest.TestCase):
    
    def test_parse_clock_freq(self):
        self.assertEqual(parse_clock_freq("72MHz"), 72000000)
        self.assertEqual(parse_clock_freq("16kHz"), 16000)
        self.assertEqual(parse_clock_freq("1GHz"), 1000000000)
        self.assertEqual(parse_clock_freq("500Hz"), 500)
    

    def test_parse_time(self):
        self.assertAlmostEqual(parse_time("1s"), 1, places=9)
        self.assertAlmostEqual(parse_time("10ms"), 0.01, places=9)
        self.assertAlmostEqual(parse_time("500us"), 0.0005, places=9)
        self.assertAlmostEqual(parse_time("100ns"), 1e-7, places=9)


    def test_invalid_time_format(self):
        with self.assertRaises(ValueError):
            parse_time("10abc")


    def test_out_of_range_psc_arr(self):
        result = subprocess.run(
            ['python', 'timer_calc.py', '--period', '--clock', '72MHz', '--time', '1ms', '--psc', '99000', '--arr', '-1'],
            capture_output=True, text=True)
        self.assertIn("Invalid value for PSC and ARR", result.stdout)


    def test_division_by_zero(self):
        try:
            calculate_timer_freq(72000000, -1, -1)
        except ValueError:
            pass
        except Exception as e:
            self.fail(f"Expected ValueError, but got {type(e)}")


    def test_calculateTimerFreq(self):
        self.assertEqual(calculate_timer_freq(72000000, 71, 999), 1000.0)
        self.assertEqual(calculate_timer_freq(1000000, 3, 249), 1000.0)


    def test_calctim(self):
        df = calc_timer(72000000, 0.001, exact=False, top=3)
        self.assertFalse(df.empty)
        self.assertIn("PSC", df.columns)
        self.assertIn("ARR", df.columns)
        self.assertIn("Real Time", df.columns)
    
if __name__ == "__main__":
    unittest.main()
