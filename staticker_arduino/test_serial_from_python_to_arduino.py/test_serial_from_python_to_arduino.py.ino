// Serial input
String serial_input_string = "";
bool serial_input_string_complete = false;

void setup() {
  Serial.begin(9600);
  // reserve 200 bytes for the serial_input_string:
  serial_input_string.reserve(200);
}

void loop() {
  check_serial_input();
}

void check_serial_input(){
  if (serial_input_string_complete) {
    // Execute command in serial input
    decode_serial_input();
    // clear the string:
    serial_input_string = "";
    serial_input_string_complete = false;
  }
}

void decode_serial_input(){
  delay(100);
  Serial.println("!gbd=0_gbo=0_gwd=0_gwo=0_obd=0_obo=0_owd=0_owo=0!");
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the serial_input_string:
    serial_input_string += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      serial_input_string_complete = true;
    }
  }
}
