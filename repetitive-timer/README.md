# Repetitive Timer

A simple repetitive timer developed with python GUI library `tkinter`.

[Download](https://github.com/HeekangPark/utilities/raw/master/repetitive-timer/dist/Repetitive%20Timer.exe)

![screenshot](https://github.com/HeekangPark/utilities/raw/master/repetitive-timer/screenshot.png)

## Motivation

There are many timers already available in the market, but most of them support only one "sub-timer".

However, in many cases, we need multiple timers. For example, in boxing, fighters fight for 3 minutes and take a minute break, then fight for another 3 minutes, take a minute break, and so on. In this case, with typical timers with only one "sub-timer", you have to set it to 3 minutes, measure, set to 1 minute, measure, 3 minutes again, measure, 1 minute again, measure, and so on.

In conclusion, I develop a timer application with multiple "sub-timer".

## Features

With **Repetitive Timer**, you can set many "sub-timers" as you want. When you press `Start` button, you may hear a beep at the end of every "sub-timers".

Let's say you set a 5-minute "sub-timer" and a 3-minute "sub-timer", and press `Start` button. In *repeating once* mode, you may hear beep twice: one 5 minutes after the timer starts, and the other 3 minutes after the first beep(8 minutes after the timer starts). In *repeating continually* mode, you may continually hear beeps in every 5 and 3 minutes: 5 minutes after the timer starts, 3 minutes after the first beep, 5 minutes again after the second beep, 3 minutes again after the third beep, and so on.

There are 6 buttons and a set of radiobuttons in the application.

- "Sub-timer" control buttons
    - `+` button : add a new "sub-timer". If you click it, a modal dialog will be appeared, asking you to enter the name and the time(second) of the new "sub-timer". Note that you may enter valid numbers for the time field.
    - `-` button : delete the selected "sub-timer". If none of "sub-timers" is selected, this button is disabled(you may not click).
    - `△` button : move up the selected "sub-timer". If none of "sub-timers" is selected, this button is disabled(you may not click).
    - `▽` button : move down the selected "sub-timer". If none of "sub-timers" is selected, this button is disabled(you may not click).
- Repeating mode radiobuttons
    - `Once` : In *repeating once* mode, the timer automatically stops after the whole "sub-timers" are run out.
    - `Continually` : In *repeating continually* mode, the timer continually repeats to run the whole "sub-timers".
- Timer control buttons
    - `Start` button : When clicked, the timer starts to run. The button will do nothing if there are no "sub-timers".
    - `Stop` button : When clicked, the timer stops to run. The button become enabled(you may click) only when the timer is running.

## Limits

The timer internally use `time.sleep()` method to measure the time. As a result, the measured time may be a little inaccurate. Practically, this error is acceptable, but you should not use the application if you want to use it for precise measurement.

There's an issue that the sound of the very first beep(the first beep right after you launch the application) is clipped (The other beeps are fine). It occurs because of the sound library I use(`playsound`). I believe this issue is practically acceptable, too.

## License

The application is under MIT License. You may download and use it freely.

## Future Works

I develop this application just for fun, so I'm not sure if I will fix bugs or upgrade the application. However, issues or pull requests are always welcomed. I might work for them when I'm not busy.
