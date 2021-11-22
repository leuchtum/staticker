#include <ArduinoJson.h>
#include <Bounce2.h>
#include <Adafruit_NeoPixel.h>

// Serial input
String serial_input_string = "";
bool serial_input_string_complete = false;

// LED General
const int ARRAYLEN = 10;

// LED WhiteDefense
const int WD_LED_PIN = 26;
Adafruit_NeoPixel wd_led(ARRAYLEN, WD_LED_PIN, NEO_GRB + NEO_KHZ800);

// LED WhiteOffense
const int WO_LED_PIN = 34;
Adafruit_NeoPixel wo_led(ARRAYLEN, WO_LED_PIN, NEO_GRB + NEO_KHZ800);

// LED WhiteScore
const int WS_LED_PIN = 8;
Adafruit_NeoPixel ws_led(ARRAYLEN, WS_LED_PIN, NEO_GRB + NEO_KHZ800);

// LED BlackDefense
const int BD_LED_PIN = 42;
Adafruit_NeoPixel bd_led(ARRAYLEN, BD_LED_PIN, NEO_GRB + NEO_KHZ800);

// LED BlackOffense
const int BO_LED_PIN = 50;
Adafruit_NeoPixel bo_led(ARRAYLEN, BO_LED_PIN, NEO_GRB + NEO_KHZ800);

// LED BlackScore
const int BS_LED_PIN = 9;
Adafruit_NeoPixel bs_led(ARRAYLEN, BS_LED_PIN, NEO_GRB + NEO_KHZ800);

// Button General
const int DEBOUNCETIME = 50;
const int UNDOTIME = 1000;

// Button GoalWhiteDefense
const int GWD_BUTTON_PIN = 24;
Bounce2::Button gwd_button = Bounce2::Button();
int gwd_press_started = 0;
bool gwd_sended = true;

// Button OwnerWhiteDefense
const int OWD_BUTTON_PIN = 22;
Bounce2::Button owd_button = Bounce2::Button();
int owd_press_started = 0;
bool owd_sended = true;

// Button GoalWhiteOffense
const int GWO_BUTTON_PIN = 32;
Bounce2::Button gwo_button = Bounce2::Button();
int gwo_press_started = 0;
bool gwo_sended = true;

// Button OwnerWhiteOffense
const int OWO_BUTTON_PIN = 30;
Bounce2::Button owo_button = Bounce2::Button();
int owo_press_started = 0;
bool owo_sended = true;

// Button GoalBlackDefense
const int GBD_BUTTON_PIN = 40;
Bounce2::Button gbd_button = Bounce2::Button();
int gbd_press_started = 0;
bool gbd_sended = true;

// Button OwnerBlackDefense
const int OBD_BUTTON_PIN = 38;
Bounce2::Button obd_button = Bounce2::Button();
int obd_press_started = 0;
bool obd_sended = true;

// Button GoalBlackOffense
const int GBO_BUTTON_PIN = 48;
Bounce2::Button gbo_button = Bounce2::Button();
int gbo_press_started = 0;
bool gbo_sended = true;

// Button OwnerBlackOffense
const int OBO_BUTTON_PIN = 46;
Bounce2::Button obo_button = Bounce2::Button();
int obo_press_started = 0;
bool obo_sended = true;

void setup() {
  // Begin serial
  Serial.begin(115200);
  
  // reserve 200 bytes for the serial_input_string:
  serial_input_string.reserve(200);

  // Init LEDs
  wd_led.begin();
  wd_led.clear();
  wd_led.show();
  
  wo_led.begin();
  wo_led.clear();
  wo_led.show();
  
  ws_led.begin();
  ws_led.clear();
  ws_led.show();  
  
  bd_led.begin();
  bd_led.clear();
  bd_led.show();

  bo_led.begin();
  bo_led.clear();
  bo_led.show();

  bs_led.begin();
  bs_led.clear();
  bs_led.show();
  
  // Init button objects
  gwd_button.attach (GWD_BUTTON_PIN,INPUT_PULLUP);
  gwd_button.interval(DEBOUNCETIME);
  gwd_button.setPressedState(LOW);
  owd_button.attach (OWD_BUTTON_PIN,INPUT_PULLUP);
  owd_button.interval(DEBOUNCETIME);
  owd_button.setPressedState(LOW); 

  gwo_button.attach (GWO_BUTTON_PIN,INPUT_PULLUP);
  gwo_button.interval(DEBOUNCETIME);
  gwo_button.setPressedState(LOW);
  owo_button.attach (OWO_BUTTON_PIN,INPUT_PULLUP);
  owo_button.interval(DEBOUNCETIME);
  owo_button.setPressedState(LOW);
  
  gbd_button.attach (GBD_BUTTON_PIN,INPUT_PULLUP);
  gbd_button.interval(DEBOUNCETIME);
  gbd_button.setPressedState(LOW);
  obd_button.attach (OBD_BUTTON_PIN,INPUT_PULLUP);
  obd_button.interval(DEBOUNCETIME);
  obd_button.setPressedState(LOW);

  gbo_button.attach (GBO_BUTTON_PIN,INPUT_PULLUP);
  gbo_button.interval(DEBOUNCETIME);
  gbo_button.setPressedState(LOW);
  obo_button.attach (OBO_BUTTON_PIN,INPUT_PULLUP);
  obo_button.interval(DEBOUNCETIME);
  obo_button.setPressedState(LOW);
}

void loop() {
  // Check for incoming commands
  check_serial_input();

  // Check buttons
  check_button(gwd_button, gwd_press_started, gwd_sended, "gwd");
  check_button(owd_button, owd_press_started, owd_sended, "owd");
  
  check_button(gwo_button, gwo_press_started, gwo_sended, "gwo");
  check_button(owo_button, owo_press_started, owo_sended, "owo");
  
  check_button(gbd_button, gbd_press_started, gbd_sended, "gbd");
  check_button(obd_button, obd_press_started, obd_sended, "obd");
  
  check_button(gbo_button, gbo_press_started, gbo_sended, "gbo");
  check_button(obo_button, obo_press_started, obo_sended, "obo");
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
      else if (pos == "wo"){
        set_led(wo_led, red, green, blue);
      }
      else if (pos == "ws"){
        set_led(ws_led, red, green, blue);
      }
      else if (pos == "bd"){
        set_led(bd_led, red, green, blue);
      }
      else if (pos == "bo"){
        set_led(bo_led, red, green, blue);
      }
      else if (pos == "bs"){
        set_led(bs_led, red, green, blue);
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
    else if (msg == "wo"){
      wo_led.clear();
      wo_led.show();
      send("echo","clear wo");
    }
    else if (msg == "ws"){
      ws_led.clear();
      ws_led.show();
      send("echo","clear ws");
    }
    else if (msg == "bd"){
      bd_led.clear();
      bd_led.show();
      send("echo","clear bd");
    }
    else if (msg == "bo"){
      bo_led.clear();
      bo_led.show();
      send("echo","clear bo");
    }
    else if (msg == "bs"){
      bs_led.clear();
      bs_led.show();
      send("echo","clear bs");
    }
    
    else if (msg == "all"){ // {"mode":"clear","msg": "all"}
      wd_led.clear();
      wd_led.show();

      wo_led.clear();
      wo_led.show();
      
      ws_led.clear();
      ws_led.show();
      
      bd_led.clear();
      bd_led.show();
      
      bo_led.clear();
      bo_led.show();
      
      bs_led.clear();
      bs_led.show();
      
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
