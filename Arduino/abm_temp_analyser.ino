#include <Adafruit_MAX31865.h>
#include <Preferences.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <FS.h>
#include <LittleFS.h>

// CS, DI, DO, CLK
Adafruit_MAX31865 thermo = Adafruit_MAX31865(19, 21, 22, 23);

#define RREF        430.0
#define RNOMINAL    100.0

#define CONFIG_BUTTON_PIN 0
#define LED_BUILTIN 2

Preferences prefs;
String mesure_name = "";
String sensor_id = "";
String ssid = "";
String password = "";

String serverURL = "";

unsigned long lastTime = 0;
unsigned long timerCount = 0;
unsigned long lastSentTimerCount = 0; 

unsigned long timerDelay_normal = 60000; //1min

const size_t MARGE_SECURITE_OCTETS = 100 * 1024; // 100 KB
const char* REQ_DIR = "/pending";

void afficherResetReason();
void printWifiInfo();
void printFault();
float readTemp();
void sendTemp();
void clearScreen();
void mainMenu();
void viewTitle();
void viewMenu();
String lireLigne();
void sauvegarderRequete(const String& json);
void reenvoyerRequetesStockees();
void chargerPreferences();
void sauvegarderPreferences();

void setup() {
    pinMode(CONFIG_BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
    Serial.begin(115200);
    LittleFS.begin(true);
    delay(200);
    
    if (!LittleFS.exists(REQ_DIR)) {
        Serial.println("dir not found");
        LittleFS.mkdir(REQ_DIR);
    }
    afficherResetReason();
    thermo.begin(MAX31865_2WIRE);
    chargerPreferences();
    WiFi.begin(ssid, password);
}

void loop() {
    if (digitalRead(CONFIG_BUTTON_PIN) == LOW) {
        mainMenu();
        delay(2000);
    }

    if ((millis() - lastTime) > timerDelay_normal) {
        timerCount ++;
        lastSentTimerCount = timerCount; 
        sendTemp();
        lastTime = millis();
        sauvegarderPreferences();
    }
    
    delay(100);
    Serial.println(millis() - lastTime);
    Serial.println(timerDelay_normal);
    Serial.println(timerCount);
    Serial.println(lastSentTimerCount);
    
}

void afficherResetReason() {
    esp_reset_reason_t reason = esp_reset_reason();
    Serial.print("Cause du redémarrage : ");
    switch (reason) {
        case ESP_RST_POWERON: Serial.println("Allumage"); break;
        case ESP_RST_EXT: Serial.println("Reset externe"); break;
        case ESP_RST_SW: Serial.println("Reset logiciel"); break;
        case ESP_RST_PANIC: Serial.println("Crash (panic)"); break;
        case ESP_RST_INT_WDT: Serial.println("Watchdog interne"); break;
        case ESP_RST_TASK_WDT: Serial.println("Watchdog de tâche"); break;
        case ESP_RST_WDT: Serial.println("Watchdog système"); break;
        case ESP_RST_DEEPSLEEP: Serial.println("Réveil deep sleep"); break;
        case ESP_RST_BROWNOUT: Serial.println("Brown-out (tension basse)"); break;
        default: Serial.println("Inconnu"); break;
    }
}

void printWifiInfo() {
    wl_status_t status = WiFi.status();

    if (status == WL_CONNECTED) {
        Serial.println("Connecté au réseau Wi-Fi");

        Serial.print(" - SSID       : ");
        Serial.println(WiFi.SSID());

        Serial.print(" - Adresse IP : ");
        Serial.println(WiFi.localIP());

        Serial.print(" - MAC        : ");
        Serial.println(WiFi.macAddress());

        Serial.print(" - RSSI       : ");
        Serial.print(WiFi.RSSI());
        Serial.println(" dBm");

        Serial.print(" - Canal      : ");
        Serial.println(WiFi.channel());
    } else {
        Serial.println("Non connecté au Wi-Fi");
        Serial.print(" - Statut : ");
        switch (status) {
            case WL_NO_SSID_AVAIL: Serial.println("SSID indisponible"); break;
            case WL_CONNECT_FAILED: Serial.println("Échec de connexion"); break;
            case WL_DISCONNECTED: Serial.println("Déconnecté"); break;
            case WL_IDLE_STATUS: Serial.println("En attente"); break;
            default: Serial.println("Statut inconnu"); break;
        }
    }
}
    
// Temp

void printFault() {
    uint8_t fault = thermo.readFault();
    if (fault) {
        Serial.print("Fault 0x"); Serial.println(fault, HEX);
        if (fault & MAX31865_FAULT_HIGHTHRESH) {
        Serial.println("RTD High Threshold"); 
        }
        if (fault & MAX31865_FAULT_LOWTHRESH) {
        Serial.println("RTD Low Threshold"); 
        }
        if (fault & MAX31865_FAULT_REFINLOW) {
        Serial.println("REFIN- > 0.85 x Bias"); 
        }
        if (fault & MAX31865_FAULT_REFINHIGH) {
        Serial.println("REFIN- < 0.85 x Bias - FORCE- open"); 
        }
        if (fault & MAX31865_FAULT_RTDINLOW) {
        Serial.println("RTDIN- < 0.85 x Bias - FORCE- open"); 
        }
        if (fault & MAX31865_FAULT_OVUV) {
        Serial.println("Under/Over voltage"); 
        }
        thermo.clearFault();
    }
}

float readTemp() {
    return thermo.temperature(RNOMINAL, RREF);
}

void sendTemp() {
    digitalWrite(LED_BUILTIN, HIGH);
    
    String json = "{\"type\":\"upload\", \"data\":{\"points\": [{\"mesure_name\":\"" + mesure_name + "\", \"time\":"+timerCount+", \"temperatures\":[{\"sensor_id\":\""+ sensor_id +"\", \"value\":"+ readTemp() +"}]}]}}";
    Serial.println(json);

    if(WiFi.status()== WL_CONNECTED){
        WiFiClientSecure client;
        client.setInsecure();
        HTTPClient https;
    
        https.begin(client, serverURL);
    
        https.addHeader("Content-Type", "application/json");
        int httpsResponseCode = https.POST(json);
    
        if (httpsResponseCode > 0 && httpsResponseCode < 400) {
            reenvoyerRequetesStockees();
        } else {
            sauvegarderRequete(json);
        }
        
        https.end();
    } else {
        sauvegarderRequete(json);
    }

    digitalWrite(LED_BUILTIN, LOW);
}

// Config Menu
    
void clearScreen() {
    Serial.write(27);
    Serial.print("[2J");
    Serial.write(27);
    Serial.print("[H");
}

void mainMenu() {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
    digitalWrite(LED_BUILTIN, HIGH);
    
    bool quitter = false;
    while (!quitter) {
        clearScreen();
        viewTitle();
        viewMenu();
        String choix = lireLigne();

        if (choix == "1") {
            Serial.println("\nConfirmer le reset ?\nCela supprimera aussi les fichiers sauvegardés (y) : ");
            if (lireLigne() == "y") {
                timerCount = 0;
                lastSentTimerCount = 0; 
                clearStockage();
            }
        }
        else if (choix == "2") {
            while (!quitter) {
                clearScreen();
                viewTitle();
                Serial.println("=== MENU PFC ===\n");

                Serial.println("1) URL PFC : " + serverURL);

                choix = lireLigne();
                if (choix == "1") {
                    Serial.println("Saisir l'URL de l'API pfc : ");
                    serverURL = lireLigne();
                } else if (choix == "esc") {
                    quitter = true;
                }
            }
            quitter = false;
        }
        else if (choix == "3") {
            Serial.println("Nouveau nom de la mesure : ");
            mesure_name = lireLigne();
        }
        else if (choix == "4") {
            Serial.println("Nouveau nom de la sonde : ");
            sensor_id = lireLigne();
        }
        else if (choix == "5") {
            Serial.println("SSID Wi-Fi : ");
            ssid = lireLigne();
            WiFi.begin(ssid, password);
        }
        else if (choix == "6") {
            Serial.println("Mot de passe Wi-Fi : ");
            password = lireLigne();
            WiFi.begin(ssid, password);
        }
        else if (choix == "7") {
            while (!quitter) {
                clearScreen();
                viewTitle();
                Serial.println("=== MENU INFO ===\n");

                Serial.print(" * Temperature : ");
                Serial.print(readTemp());
                Serial.println("°C");

                Serial.println(" * Fault : ");
                printFault();

                Serial.println(" * Wifi : ");
                printWifiInfo();

                Serial.print(" * Compteur de relevés (timerCount) : ");
                Serial.println(timerCount);
                Serial.print(" * Dernier timerCount envoyé : ");
                Serial.println(lastSentTimerCount);

                choix = lireLigne();
                if (choix == "esc") {
                    quitter = true;
                }
            }
            quitter = false;
        }
        else if (choix == "8") {
            Serial.println();
            sendTemp();
        }
        else if (choix == "9") {
            clearScreen();
            quitter = true;
        }
        sauvegarderPreferences();
    }
    digitalWrite(LED_BUILTIN, LOW);
}

void viewTitle() {
    Serial.println("***********************************************************\r\n*    _     ___   __  __    _____                          *\r\n*   /_\\   | _ ) |  \\/  |  |_   _|  ___   _ __    _ __     *\r\n*  / _ \\  | _ \\ | |\\/| |    | |   / -_) | '  \\  | '_ \\    *\r\n* /_/ \\_\\ |___/ |_|  |_|    |_|   \\___| |_|_|_| | .__/    *\r\n*    _     _  _     _     _     __   __  ___   _|_|  ___  *\r\n*   /_\\   | \\| |   /_\\   | |    \\ \\ / / / __| | __| | _ \\ *\r\n*  / _ \\  | .` |  / _ \\  | |__   \\ V /  \\__ \\ | _|  |   / *\r\n* /_/ \\_\\ |_|\\_| /_/ \\_\\ |____|   |_|   |___/ |___| |_|_\\ *                         \r\n*                                                         *\r\n***********************************************************"); 
}

void viewMenu() {
    Serial.println("=== MENU CONFIGURATION ===");
    Serial.println("1. Reset timer");
    Serial.println("2. PFC");
    Serial.println("3. Nom de la mesure       : " + mesure_name);
    Serial.println("4. Nom de la sonde        : " + sensor_id);
    Serial.println("5. Wi-Fi SSID             : " + ssid);
    Serial.println("6. Wi-Fi mot de passe     : " + password);
    Serial.println("7. Info carte             : ");
    Serial.println("8. Trigger upload         : ");
    Serial.println("9. Quitter le menu");
    Serial.print("Votre choix : ");
}

String lireLigne() {
    while (!Serial.available()) delay(10);
    return Serial.readStringUntil('\n');
}

// Pref
void sauvegarderRequete(const String& json) {
    size_t freeSpace = LittleFS.totalBytes() - LittleFS.usedBytes();
    if (freeSpace < json.length() + MARGE_SECURITE_OCTETS) {
        Serial.println("Pas assez d'espace pour stocker la requête !");
        return;
    }

    String filename = String(REQ_DIR) + "/req_" + String(timerCount) + ".json"; 
    File f = LittleFS.open(filename, "w");
    if (!f) {
        Serial.println("Erreur lors de la création du fichier de requête !");
        return;
    }
    f.print(json);
    f.close();
    Serial.println("Requête sauvegardée : " + filename);
}

void reenvoyerRequetesStockees() {
    File dir = LittleFS.open(REQ_DIR);
    if (!dir || !dir.isDirectory()) {
        Serial.println("Dossier de requêtes invalide.");
        return;
    }

    File fichier = dir.openNextFile();
    while (fichier) {
        String json = fichier.readString();
        String filename = String(REQ_DIR) + "/"+ fichier.name();
        fichier.close();

        WiFiClientSecure client;
        client.setInsecure();
        HTTPClient https;
        https.begin(client, serverURL);
        https.addHeader("Content-Type", "application/json");

        int code = https.POST(json);
        https.end();

        if (code > 0 && code < 400) {
            Serial.println("Requête stockée envoyée avec succès !");
            LittleFS.remove(filename);
        } else {
            Serial.println("Échec lors du renvoi de la requête stockée.");
            return;
        }

        fichier = dir.openNextFile();
    }
}

void clearStockage() {
    File dir = LittleFS.open(REQ_DIR);
    if (!dir || !dir.isDirectory()) {
        Serial.println("Dossier de requêtes invalide.");
        return;
    }

    File fichier = dir.openNextFile();
    while (fichier) {
        String filename = String(REQ_DIR) + "/"+ fichier.name();
        fichier.close();
        LittleFS.remove(filename);
        fichier = dir.openNextFile();
    }
}

void chargerPreferences() {
    prefs.begin("config", true); // read-only
    mesure_name = prefs.getString("mesure_name", "test");
    serverURL = prefs.getString("serverURL", "https://abm.galtech.cc/api/data");
    sensor_id = prefs.getString("sensor_id", "sonde 1");
    ssid = prefs.getString("ssid", "");
    password = prefs.getString("password", "");
    timerCount = prefs.getULong("timerCount", 0);
    lastSentTimerCount = prefs.getULong("lastSentCount", 0); 
    prefs.end();
}
    
void sauvegarderPreferences() {
    prefs.begin("config", false); // write mode
    prefs.putString("mesure_name", mesure_name);
    prefs.putString("serverURL", serverURL);
    prefs.putString("sensor_id", sensor_id);
    prefs.putString("ssid", ssid);
    prefs.putString("password", password);
    prefs.putULong("timerCount", timerCount);
    prefs.putULong("lastSentCount", lastSentTimerCount); 
    prefs.end();
}