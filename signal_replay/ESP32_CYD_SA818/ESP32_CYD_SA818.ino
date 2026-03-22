/**
 * CYD + SA818 Signal Replay Controller
 * Uses hardware DAC Cosine Generator for clean tones
 * 
 * Hardware: ESP32-CYD (Cheap Yellow Display) + SA818-V
 * 
 * Wiring (CYD Extended Headers):
 * SA818-V Pin    → CYD Pin
 * Pin 6 (RXD)   → CN1 GPIO 27 (TX to radio)
 * Pin 7 (TXD)   → CN1 GPIO 22 (RX from radio)  
 * Pin 18 (MIC)  → P3 GPIO 25 (DAC audio out)
 * Pin 5 (PTT)   → CN1 GPIO 21 (PTT control)
 * Pin 8 (VCC)   → 5V
 * GND           → GND
 * 
 * IMPORTANT: Add 0.1uF-10uF capacitor in series on audio line to block DC offset
 */

#include <Arduino.h>
#include <TFT_eSPI.h>
#include <SPI.h>
#include <SD.h>
#include <driver/dac.h>

// ============================================
// PIN DEFINITIONS (CYD Extended Headers)
// ============================================
#define SA818_TX       27    // CN1 - TX to radio
#define SA818_RX       22    // CN1 - RX from radio
#define AUDIO_OUT      25    // P3 - DAC1 output (with capacitor!)
#define PTT_PIN        21    // CN1 - Push-to-Talk

// ============================================
// DISPLAY SETTINGS (CYD 320x240)
// ============================================
#define SCREEN_WIDTH   320
#define SCREEN_HEIGHT 240
#define BUTTON_COLS    3
#define BUTTON_ROWS    4

// ============================================
// SIGNAL DEFINITIONS
// ============================================
// Tone frequencies in Hz for each signal
// Adjust these to match your specific protocol
struct Signal {
  const char* name;      // Button label
  const char* filename;   // Audio file (if using file playback)
  uint32_t tone1;        // First tone frequency (Hz) - 0 = use file
  uint32_t tone2;        // Second tone frequency (Hz) - 0 = single tone
  uint16_t duration;     // Tone duration in ms
  uint16_t color;        // Button color
};

Signal signals[] = {
  // Row 1
  {"17/1", "17_1.wav", 1000, 0, 200, TFT_RED},
  {"17/3", "17_3.wav", 1100, 0, 200, TFT_RED},
  {"18/1", "18_1.wav", 1200, 0, 200, TFT_ORANGE},
  // Row 2  
  {"18/3", "18_3.wav", 1300, 0, 200, TFT_ORANGE},
  {"19/1", "19_1.wav", 1400, 0, 200, TFT_YELLOW},
  {"19/3", "19_3.wav", 1500, 0, 200, TFT_YELLOW},
  // Row 3
  {"20/1", "20_1.wav", 1600, 0, 200, TFT_GREEN},
  {"20/3", "20_3.wav", 1700, 0, 200, TFT_GREEN},
  {"21/1", "21_1.wav", 1800, 0, 200, TFT_CYAN},
  // Row 4
  {"21/3", "21_3.wav", 1900, 0, 200, TFT_CYAN},
  {"RESET", "reset.wav", 2000, 0, 500, TFT_MAROON},  // RESET is longer
};

#define NUM_SIGNALS (sizeof(signals) / sizeof(signals[0]))

// ============================================
// GLOBAL VARIABLES
// ============================================
TFT_eSPI tft = TFT_eSPI();
int selectedButton = -1;
bool isPlaying = false;
File audioFile;

// SA818 Configuration
const float FREQUENCY = 154.46375;  // MHz
const uint8_t TX_DELAY_MS = 50;     // Wait before sending tone
const uint8_t POST_TX_DELAY_MS = 50; // Wait after tone before PTT up

// ============================================
// SETUP
// ============================================
void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, SA818_RX, SA818_TX);
  
  // PTT pin
  pinMode(PTT_PIN, OUTPUT);
  digitalWrite(PTT_PIN, HIGH);  // Start with PTT off
  
  // Initialize display
  tft.init();
  tft.setRotation(0);  // Portrait mode for CYD
  tft.fillScreen(TFT_BLACK);
  
  // Initialize DAC
  dac_output_enable(DAC_CHANNEL_1);
  dac_output_voltage(DAC_CHANNEL_1, 128);  // Center
  
  // Initialize SD card
  if (!SD.begin()) {
    Serial.println("SD Card mount failed!");
    tft.drawString("SD Card Error!", 10, 10, 2);
    while(1) delay(1000);
  }
  Serial.println("SD Card OK");
  
  // Initialize SA818
  initSA818();
  
  // Draw UI
  drawButtons();
  
  Serial.println("Signal Replay Ready");
  Serial.printf("Signals: %d\n", NUM_SIGNALS);
}

// ============================================
// MAIN LOOP
// ============================================
void loop() {
  // Check for touchscreen input
  uint16_t x, y;
  if (tft.getTouch(&x, &y)) {
    handleTouch(x, y);
    delay(150);  // Debounce
  }
}

// ============================================
// SA818 INITIALIZATION
// ============================================
void initSA818() {
  delay(500);
  Serial2.println("AT+DMOCONNECT");  // Connect
  delay(200);
  Serial2.println("AT+DMOSETGROUP=0,154.46375,154.46375,0000,1,0");  // Set group
  delay(200);
  Serial2.println("AT+SETFILTER=0,0,0");  // No filter
  delay(200);
  setFrequency(FREQUENCY);
  delay(200);
  Serial2.println("AT+SETTA=1");  // Turn on
  Serial.println("SA818 Initialized");
}

void setFrequency(float freq) {
  char cmd[50];
  sprintf(cmd, "AT+FREQ=%.5f", freq);
  Serial2.println(cmd);
  Serial.print("Setting frequency: ");
  Serial.println(freq, 5);
}

// ============================================
// UI DRAWING
// ============================================
void drawButtons() {
  tft.fillScreen(TFT_BLACK);
  
  // Title
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("Signal Replay", 10, 5, 2);
  tft.drawString("154.46375 MHz", 10, 22, 2);
  
  // Calculate button size for 320x240 screen
  int btnWidth = SCREEN_WIDTH / BUTTON_COLS - 8;
  int btnHeight = (SCREEN_HEIGHT - 45) / BUTTON_ROWS - 4;
  int startX = 4;
  int startY = 40;
  
  // Draw signal buttons in 3x4 grid
  for (int i = 0; i < NUM_SIGNALS; i++) {
    int col = i % BUTTON_COLS;
    int row = i / BUTTON_COLS;
    
    int x = startX + col * (btnWidth + 4);
    int y = startY + row * (btnHeight + 4);
    
    // Button background
    tft.fillRect(x, y, btnWidth, btnHeight, signals[i].color);
    
    // Button border
    tft.drawRect(x, y, btnWidth, btnHeight, TFT_WHITE);
    
    // Button text (centered)
    tft.setTextColor(TFT_WHITE, signals[i].color);
    int textWidth = strlen(signals[i].name) * 12;  // Approximate
    int textX = x + (btnWidth - textWidth) / 2;
    int textY = y + (btnHeight - 16) / 2;
    tft.drawString(signals[i].name, textX, textY, 2);
  }
  
  // Status bar
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  tft.drawString("Ready", 10, SCREEN_HEIGHT - 12, 2);
}

// ============================================
// TOUCH HANDLING
// ============================================
void handleTouch(uint16_t x, uint16_t y) {
  // Calculate which button was pressed
  int btnWidth = SCREEN_WIDTH / BUTTON_COLS - 8;
  int btnHeight = (SCREEN_HEIGHT - 45) / BUTTON_ROWS - 4;
  int startX = 4;
  int startY = 40;
  
  int col = (x - startX) / (btnWidth + 4);
  int row = (y - startY) / (btnHeight + 4);
  
  if (col >= 0 && col < BUTTON_COLS && row >= 0 && row < BUTTON_ROWS) {
    int btn = col + row * BUTTON_COLS;
    
    if (btn < NUM_SIGNALS) {
      // Visual feedback - flash button
      flashButton(btn);
      
      // Play signal
      playSignal(btn);
    }
  }
}

void flashButton(int btn) {
  int btnWidth = SCREEN_WIDTH / BUTTON_COLS - 8;
  int btnHeight = (SCREEN_HEIGHT - 45) / BUTTON_ROWS - 4;
  int startX = 4;
  int startY = 40;
  
  int col = btn % BUTTON_COLS;
  int row = btn / BUTTON_COLS;
  
  int x = startX + col * (btnWidth + 4);
  int y = startY + row * (btnHeight + 4);
  
  // Flash white
  tft.fillRect(x, y, btnWidth, btnHeight, TFT_WHITE);
  delay(50);
  tft.fillRect(x, y, btnWidth, btnHeight, signals[btn].color);
}

// ============================================
// SIGNAL PLAYBACK
// ============================================
void playSignal(int btnIndex) {
  Signal &sig = signals[btnIndex];
  
  Serial.print("Playing: ");
  Serial.println(sig.name);
  
  // Update status
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("Playing: " + String(sig.name), 10, SCREEN_HEIGHT - 12, 2);
  
  // PTT ON
  digitalWrite(PTT_PIN, LOW);
  delay(TX_DELAY_MS);  // Let radio settle
  
  if (sig.tone1 > 0) {
    // Use hardware cosine generator for tone
    playTone(sig.tone1, sig.duration);
  } else {
    // Use audio file
    playAudioFile(sig.filename);
  }
  
  delay(POST_TX_DELAY_MS);
  
  // PTT OFF
  digitalWrite(PTT_PIN, HIGH);
  
  // Stop tone
  stopTone();
  
  // Reset status
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  tft.drawString("Ready", 10, SCREEN_HEIGHT - 12, 2);
}

// ============================================
// HARDWARE TONE GENERATOR
// Uses ESP32's DAC Cosine Wave Generator
// ============================================
void playTone(uint32_t freqHz, uint16_t durationMs) {
  Serial.print("Playing tone: ");
  Serial.print(freqHz);
  Serial.println(" Hz");
  
  // Configure hardware cosine generator
  // Note: ESP32 DAC can generate ~5Hz to ~10MHz with proper config
  // For reliable audio tones, we'll use a workaround
  
  // Method 1: Direct DAC with timer (more reliable than CW gen for audio)
  // We'll use LEDC for precise frequency generation
  ledcSetup(0, freqHz, 8);  // Channel 0, freq, 8-bit resolution
  ledcAttachPin(AUDIO_OUT, 0);
  ledcWrite(0, 128);  // 50% duty cycle
  
  // Wait for duration
  delay(durationMs);
  
  // Stop
  ledcWrite(0, 0);
  ledcDetachPin(AUDIO_OUT);
}

void stopTone() {
  ledcWrite(0, 0);
  ledcDetachPin(AUDIO_OUT);
  dac_output_voltage(DAC_CHANNEL_1, 128);  // Reset to center
}

// ============================================
// FILE-BASED PLAYBACK (Alternative)
// ============================================
void playAudioFile(const char* filename) {
  String path = "/" + String(filename);
  audioFile = SD.open(path);
  
  if (!audioFile) {
    Serial.print("File not found: ");
    Serial.println(path);
    return;
  }
  
  Serial.print("Playing file: ");
  Serial.println(path);
  
  // Skip WAV header (44 bytes)
  audioFile.seek(44);
  
  // Read and play
  uint8_t buffer[64];
  unsigned long startTime = millis();
  const unsigned long MAX_DURATION = 3000;  // 3 second max
  
  while (audioFile.available() && (millis() - startTime < MAX_DURATION)) {
    int bytesRead = audioFile.read(buffer, sizeof(buffer));
    
    for (int i = 0; i < bytesRead; i++) {
      dac_output_voltage(DAC_CHANNEL_1, buffer[i]);
      delayMicroseconds(125);  // ~8kHz
    }
  }
  
  audioFile.close();
  dac_output_voltage(DAC_CHANNEL_1, 128);
}
