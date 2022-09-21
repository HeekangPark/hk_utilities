import time


def Timer(timers, mode, isStopped, onTick, onNext, onComplete):
    if mode == 0:  # once
        for i, timer in enumerate(timers):
            for sec in range(timer[1]):
                try:
                    stop = isStopped()
                except Exception:
                    stop = True

                if stop:
                    return
                else:
                    time.sleep(1)
                    try:
                        onTick(timer[0], sec + 1, timer[1])
                    except Exception:
                        return

            try:
                onNext()
            except Exception:
                return

        try:
            onComplete()
        except Exception:
            pass

        return

    else:  # continuously
        while True:
            for i, timer in enumerate(timers):
                for sec in range(timer[1]):
                    try:
                        stop = isStopped()
                    except Exception:
                        stop = True

                    if stop:
                        return
                    else:
                        time.sleep(1)

                        try:
                            onTick(timer[0], sec + 1, timer[1])
                        except Exception:
                            return

                try:
                    onNext()
                except Exception:
                    return