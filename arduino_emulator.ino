const int numPoints = 48;
const float startFreq = 4000.0;
const float stopFreq = 198000.0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    // Leemos el comando enviado por el PC
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "send") {
      digitalWrite(LED_BUILTIN, HIGH); // Encender LED al recibir 'send'

      for (int i = 0; i < numPoints; i++) {
        // Cálculo de frecuencia en escala logarítmica (igual que la Nordic)
        float freq = startFreq * pow(stopFreq / startFreq, (float)i / (numPoints - 1));

        // Simulación de una impedancia coherente (Circuito RC Paralelo: R=1k, C=10nF)
        float R = 1000.0;
        float C = 10e-9;
        float omega = 2.0 * PI * freq;
        float denom = 1.0 + pow(omega * R * C, 2);
        
        float real = R / denom;
        float imag = - (omega * pow(R, 2) * C) / denom;
        float magnitude = sqrt(real * real + imag * imag);
        float phase_deg = atan2(imag, real) * 180.0 / PI;

        // Enviar datos en el formato CSV exacto que espera serialPlotterPC.py:
        // freq,mag,phase,real,imag
        Serial.print(freq, 2);
        Serial.print(",");
        Serial.print(magnitude, 3);
        Serial.print(",");
        Serial.print(phase_deg, 3);
        Serial.print(",");
        Serial.print(real, 3);
        Serial.print(",");
        Serial.println(imag, 3);

        delay(15); // Simulación del tiempo que tardaría el AFE en medir
      }
      digitalWrite(LED_BUILTIN, LOW); // Apagar LED al finalizar el barrido
    }
  }
}