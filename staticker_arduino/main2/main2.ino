#include <ArduinoJson.h>
#include <Bounce2.h>


// Serial input
String serial_input_string = "";
bool serial_input_string_complete = false;


// Button General
const int min_pressed_time = 300;


// Button GoalWhiteDefense
const int GWD_PIN = 6;
Bounce gwd_button = Bounce();


void setup() {
  Serial.begin(9600);
  // reserve 200 bytes for the serial_input_string:
  serial_input_string.reserve(200);

  // Init bounce objects
  gwd_button.attach (GWD_PIN,INPUT_PULLUP);
  gwd_button.interval(25);
}


void loop() {
  // Check for incoming commands
  check_serial_input();
  
  // Update bounce objects
  gwd_button.update();

  // Check if state of button changed and if so process change
  check_button(gwd_button, "gwd");

}


void check_button(Bounce button, String button_indent){
  if (button.fell()){
    send("pressed", button_indent);
  }
}


void decode_serial_input(){
  // Init JSON document
  StaticJsonDocument<128> json_dict;

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
    const char* led_bd = json_dict["lbd"];
    const char* led_bo = json_dict["lbo"];
    const char* led_wd = json_dict["lwd"];
    const char* led_wo = json_dict["lwo"];
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


void send(String mode, String msg){
  core_send(mode, msg);
}


void raise_error_if_missing_key(bool all_ok){
  if (!all_ok){
    raise_error("MissingKey");
  }    
}


void raise_error(String err){
  core_send("error",err);
}


void core_send(String mode, String msg){
  StaticJsonDocument<64> json;
  json["mode"] = mode;
  json["msg"] = msg;
  serializeJson(json, Serial);
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
