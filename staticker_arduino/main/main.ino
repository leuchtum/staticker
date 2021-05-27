// Serial input
String serial_input_string = "";
bool serial_input_string_complete = false;

//
void setup() {
  Serial.begin(115200);
  // reserve 200 bytes for the serial_input_string:
  serial_input_string.reserve(200);
}

void loop() {
  check_serial_input();

}

void decode_serial_input(){
  //=====================
  // validate
  bool validated = false;
  int count_exclamation_mark = 0;
  int str_len = serial_input_string.length() + 1;
  for(int i=0; i<str_len; i++){
    char c = serial_input_string.charAt(i);
    if (c == '!'){
      count_exclamation_mark++;
    }
  }
  if (count_exclamation_mark == 2){
    validated = true;
  }

  //=====================
  // decode
  if (validated == true){
    //mode
    int mode = serial_input_string.charAt(1) - '0';
    //msg
    int msg_len = str_len-5;
    int msg[msg_len];
    for (int i=0; i<msg_len; i++){
      msg[i] = serial_input_string.charAt(i+2) - '0';
    }
    //=====================
    // process
    Serial.print(" MODE: ");
    Serial.print(mode);
    Serial.print(" MSG: ");
    for (int i=0; i<msg_len; i++){
      Serial.print(msg[i]);
    }
    Serial.println("");
  }
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
