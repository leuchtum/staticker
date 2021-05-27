#include <ArduinoJson.h>


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


void decode_serial_input(){
  // Init JSON document
  StaticJsonDocument<200> json_dict;

  // Deserialize the JSON document
  DeserializationError err = deserializeJson(json_dict, serial_input_string);

  // Test if parsing succeeds.
  if (err) {
    raise_error(err.f_str());
    return;
  }

  // Fetch mode
  String mode = json_dict["mode"];

  // Process mode setLED
  if(mode == "setLED"){
    const char* led_bd = json_dict["bd"];
    const char* led_bo = json_dict["bo"];
    const char* led_wd = json_dict["wd"];
    const char* led_wo = json_dict["wo"];
    bool all_exist = led_bd && led_bo && led_wd && led_wo;
    raise_error_if_missing_key(all_exist);
    if (all_exist){
      Serial.println("SET LED");
    }
  }

  // No mode found, so raise error
  else{
    raise_error("InvalidInput");
  }
}


void raise_error_if_missing_key(bool all_ok){
  if (!all_ok){
    raise_error("MissingKey");
  }    
}


void raise_error(String err){
  StaticJsonDocument<200> json_error;
  json_error["type"] = "error";
  json_error["msg"] = err;
  serializeJson(json_error, Serial);
  Serial.print("\n");
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
    
    // if newline, set a flag so the main loop can do stuff
    if (inChar == '\n') {
      serial_input_string_complete = true;
      
    }
  }
}
