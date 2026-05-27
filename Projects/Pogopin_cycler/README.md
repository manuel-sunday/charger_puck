# Pogo Pin Cycler

Firmware for a FUYU FSL30 linear rail used to cycle pogo pin contacts for durability testing.

## Hardware

| Part | Spec |
|---|---|
| Controller | Arduino Nano (ATmega328P) |
| Driver | BTT TMC2209 V1.3 |
| Motor | NEMA14, 1.8°/step, 0.95A, 200 steps/rev |
| Rail | FUYU FSL30, 100mm stroke, Tr8×2 lead screw (2mm/rev) |

### Wiring

| Arduino Pin | TMC2209 Pin |
|---|---|
| D3 | STEP |
| D2 | DIR |
| GND | GND |
| 5V | VIO |

Motor coils connect to A1/A2 (coil 1) and B1/B2 (coil 2) on the TMC2209. Use a multimeter in resistance mode to identify coil pairs — wires in the same coil read ~5Ω, wires from different coils read open circuit.

Power the TMC2209 VM pin with 12V. Set the VREF potentiometer so supply current is ~0.8A (≈ motor rated current).

## Commands

Send single characters over serial at **115200 baud**:

| Command | Action |
|---|---|
| `f` | Jog forward (~2mm) |
| `b` | Jog backward (~2mm) |
| `s` | Stop immediately |
| `r` | Start cycling |

## Cycle Behavior

1. Move forward `TRAVEL_STEPS`
2. Hold at forward position for `HOLD_MS` milliseconds
3. Move backward `TRAVEL_STEPS`
4. Repeat

Serial monitor prints `Holding...` at the forward position and `Cycle N` after each return stroke. Send `s` to stop at any point.

## Configuration

All tunable parameters are at the top of `src/main.cpp`:

```cpp
const float        STEPS_PER_MM = 792.0f;   // calibrate by measuring actual travel
const long         TRAVEL_STEPS = (long)(STEPS_PER_MM * 10);  // stroke length in mm
const long         JOG_STEPS    = (long)(STEPS_PER_MM * 2);   // jog distance in mm
const int          NUM_CYCLES   = 0;         // 0 = infinite, N = stop after N cycles
const float        MAX_SPEED    = 4000.0;    // steps/sec (Nano hardware limit ~4000)
const float        ACCEL        = 1000.0;    // steps/sec²
const unsigned long HOLD_MS     = 3000;      // hold time at forward position (ms)
const int          DIR          = 1;         // flip to -1 to reverse f/b direction
```

### Calibrating STEPS_PER_MM

The TMC2209 runs at 1/8 microstepping by default (standalone mode), giving a theoretical 800 steps/mm. The measured value on this build is **792 steps/mm**.

To recalibrate:
1. Set `JOG_STEPS` to a known large value (e.g. `STEPS_PER_MM * 50`)
2. Send `f` and measure actual travel with a ruler
3. New `STEPS_PER_MM` = old value × (expected mm / measured mm)

## Dependencies

- [AccelStepper](https://www.airspayce.com/mikem/arduino/AccelStepper/) — non-blocking stepper control
- PlatformIO with `atmelavr` platform, board `nanoatmega328new`
