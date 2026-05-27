#include <Arduino.h>
#include <AccelStepper.h>

// STEP=pin3  DIR=pin2
// f=jog forward  b=jog backward  s=stop  r=run cycles

// Motor: NEMA14, 200 steps/rev (1.8 deg/step)
// Lead screw: Tr8x2, 2 mm/rev
// Full-step: 200/2 = 100 steps/mm
// Adjust MICROSTEPS until travel distance is correct (try 8, 16, 32, 64, 256)
// Rail max speed: 70 mm/s. Nano + AccelStepper limit: ~4000 steps/sec.
// Speed cap at each setting: 1/16->2.5mm/s  1/8->5mm/s  1/4->10mm/s  1->40mm/s
// To approach 70 mm/s you need a faster board (e.g. ESP32) or full stepping.
const int   DIR          = 1;      // flip to -1 if f/b are backwards
// Measured: 51200 steps = 64.6 mm → 792 steps/mm ≈ 1/8 microstepping
const float STEPS_PER_MM = 792.0f;
const long  TRAVEL_STEPS = (long)(STEPS_PER_MM * 10);    // 100 mm stroke
const long  JOG_STEPS    = (long)(STEPS_PER_MM * 2);     // 50 mm per press
const int   NUM_CYCLES   = 0;    // 0 = infinite, any positive number = that many cycles
const float        MAX_SPEED  = 4000.0;
const float        ACCEL      = 1000.0;
const unsigned long HOLD_MS   = 3000;   // ms to hold at forward position

AccelStepper stepper(AccelStepper::DRIVER, 3, 2);

bool          cycling   = false;
bool          goingFwd  = true;
bool          holding   = false;
unsigned long holdUntil = 0;
int           cycles    = 0;

void setup() {
  Serial.begin(115200);
  stepper.setMaxSpeed(MAX_SPEED);
  stepper.setAcceleration(ACCEL);
  Serial.println("f=fwd  b=back  s=stop  r=cycle");
}

void loop() {
  while (Serial.available()) {
    char cmd = Serial.read();
    if      (cmd == 'f') { cycling = false; stepper.move( DIR * JOG_STEPS); }
    else if (cmd == 'b') { cycling = false; stepper.move(-DIR * JOG_STEPS); }
    else if (cmd == 's') { cycling = false; stepper.stop(); Serial.println("Stopped."); }
    else if (cmd == 'r' && !cycling) {
      cycling  = true;
      goingFwd = true;
      cycles   = 0;
      stepper.move(DIR * TRAVEL_STEPS);
      Serial.println("Cycling...");
    }
  }

  stepper.run();

  if (!cycling) return;

  if (holding) {
    if (millis() >= holdUntil) {
      holding = false;
      stepper.move(-DIR * TRAVEL_STEPS);
      goingFwd = false;
    }
    return;
  }

  if (stepper.distanceToGo() != 0) return;

  if (goingFwd) {
    holding   = true;
    holdUntil = millis() + HOLD_MS;
    Serial.println("Holding...");
  } else {
    cycles++;
    Serial.print("Cycle "); Serial.println(cycles);
    if (NUM_CYCLES > 0 && cycles >= NUM_CYCLES) { cycling = false; Serial.println("Done."); return; }
    stepper.move(DIR * TRAVEL_STEPS);
    goingFwd = true;
  }
}
