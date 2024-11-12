# Experimental Design and System Documentation

This is an unstructured document containing my (Maxwell Madden) personal notes on experimental design/technical considerations when working with the photometry system.

## Arduino Clock Accuracy

We use an Arduino to control photometry laser/camera timing. **Arduino clocks are not guaranteed to be accurate**, esp over longer periods and may be sensitive to temperature etc. etc. For maximal timing accuracy it is likely best practice to keep trial length (each trial is independently triggered by the behavior PC) as short as possible.

- 1 minute per trial is likely a reasonable maximum, with a preferred maximum of 30 seconds. This maximum obviously only applies if you care about aligning signal to behavioral events.
- DO NOT USE the arduino **__Uno __** boards. They have a much less accurate clock (ceramic resonator) and may drift on average as much as 600 ms per minute (that's a 6 sample drift at 10 hz acquisition rate).
- USE the **__leonardo __** boards. The vast majority of the lab boards are leonardo and __to my knowledge the Uno's have not been used in the photometry system to date.__
