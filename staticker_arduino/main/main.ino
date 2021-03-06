#include <ArduinoJson.h>
#include <Bounce2.h>
#include <Adafruit_NeoPixel.h>


// Serial input
String serial_input_string = "";
bool serial_input_string_complete = false;

// LED General
const int ARRAYLEN = 10;
const int WD_LED_PIN = 7;
Adafruit_NeoPixel wd_led(ARRAYLEN, WD_LED_PIN, NEO_GRB + NEO_KHZ800);

// Button General
const int DEBOUNCETIME = 30;
const int UNDOTIME = 1500;

// Button GoalWhiteDefense
const int GWD_BUTTON_PIN = 6;
Bounce2::Button gwd_button = Bounce2::Button();
int gwd_press_started = 0;
bool gwd_sended = true;

// Button OwnerWhiteDefense
const int OWD_BUTTON_PIN = 5;
Bounce2::Button owd_button = Bounce2::Button();
int owd_press_started = 0;
bool owd_sended = true;

void setup() {
  Serial.begin(115200);
  // reserve 200 bytes for the serial_input_string:
  serial_input_string.reserve(200);

  // Init LEDs
  wd_led.begin();
  wd_led.clear();
  wd_led.show();

  // Init button objects
  gwd_button.attach (GWD_BUTTON_PIN,INPUT_PULLUP);
  gwd_button.interval(DEBOUNCETIME);
  gwd_button.setPressedState(LOW);

  owd_button.attach (OWD_BUTTON_PIN,INPUT_PULLUP);
  owd_button.interval(DEBOUNCETIME);
  owd_button.setPressedState(LOW); 
}


void loop() {
  // Check for incoming commands
  check_serial_input();

  // Check buttons
  check_button(gwd_button, gwd_press_started, gwd_sended, "gwd");
  check_button(owd_button, owd_press_started, owd_sended, "owd");
}


void check_button(Bounce2::Button & button, int & press_started, bool & sended, String button_indent){
  // Init variables
  int pressed_time;

  // Update button object
  button.update();

  // Detect rising edge and start timing
  if (button.pressed()){
    press_started = millis();
    sended = false;
  }

  // Calculate the time the button has already been pressed
  pressed_time = millis() - press_started;

  // if button is released before UNDOTIME has passed, it's a normal press
  if (button.released()){
    if (pressed_time < UNDOTIME){
      send("pressed", button_indent);
    }
    sended = true;
  }

  // If button is still pressed after UNDOTIME has passed, it's an UNDO press
  if (button.isPressed() && sended == false && pressed_time > UNDOTIME){
    send("pressed", "undo_" + button_indent);
    sended = true;
  }
}


void decode_serial_input(){
  // Init JSON document
  StaticJsonDocument<512> json_dict;

  // Deserialize the JSON document
  DeserializationError err = deserializeJson(json_dict, serial_input_string);

  // Test if parsing succeeds
  if (err) {
    raise_error(err.f_str());
    return;
  }

  // Fetch mode
  String mode = json_dict["mode"];

  // Process mode setled
  // {"mode":"setled","msg":{"pos":"wd","R":[1,2,3,4,5,6,7,8,9,10],"G":[1,2,3,4,5,6,7,8,9,10],"B":[1,2,3,4,5,6,7,8,9,10]}}
  if(mode == "setled"){
    // Bool if error in nested json
    bool nested_exists = true;
    
    // Fetch non-nested json
    String pos = json_dict["msg"]["pos"];

    // Fetch nested json
    int red[ARRAYLEN];
    for (int i=0; i<ARRAYLEN; i++){
      red[i] = json_dict["msg"]["R"][i];
      if (!red[i] && red[i] != 0){
        nested_exists = false;
      }
    }

    // Fetch nested json
    int green[ARRAYLEN];
    for (int i=0; i<ARRAYLEN; i++){
      green[i] = json_dict["msg"]["G"][i];
      if (!green[i] && green[i] != 0){
        nested_exists = false;
      }
    }

    // Fetch nested json
    int blue[ARRAYLEN];
    for (int i=0; i<ARRAYLEN; i++){
      blue[i] = json_dict["msg"]["B"][i];
      if (!blue[i] && blue[i] != 0){
        nested_exists = false;
      }
    }

    // Check if non-nested and nested are valid
    if (nested_exists){
      if (pos == "wd"){
        set_led(wd_led, red, green, blue);
      }
      send("echo","setled");
    }
    else{
      raise_error("MissingKey or InvalidValues");
    }
  }
  else if(mode == "clear"){
    String msg = json_dict["msg"];
    if (msg == "wd"){
      wd_led.clear();
      wd_led.show();
      send("echo","clear wd");
    }
    else if (msg == "all"){
      wd_led.clear();
      wd_led.show();
      send("echo","clear all");
    }
    else{
      raise_error("MissingKey or InvalidValues");
    }
    
  }
  else{
    raise_error("MissingMode or InvalidInput");
  }
}


void set_led(Adafruit_NeoPixel & led, int red[ARRAYLEN], int green[ARRAYLEN], int blue[ARRAYLEN]){
  for (int i=0; i<ARRAYLEN; i++){
    led.setPixelColor(i, led.Color(red[i], green[i], blue[i]));
  }
  led.show();
}


void send(String mode, String msg){
  core_send(mode, msg);
}


void raise_error(String err){
  core_send("error",err);
}


void core_send(String mode, String msg){
  StaticJsonDocument<64> json;
  json["mode"] = mode;
  json["msg"] = msg;

  // Write to serial with additional linebreak
  serializeJson(json, Serial);
  Serial.print("\n");
}


void check_serial_input(){
  if (serial_input_string_complete) {
    // Execute encoded command
    decode_serial_input();
    
    // clear the string:
    serial_input_string = "";
    serial_input_string_complete = false;
  }
}


void serialEvent() {
  // This function is called automatically after each loop
  // Copied from Examples --> Communication --> SerialEvent
  
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
