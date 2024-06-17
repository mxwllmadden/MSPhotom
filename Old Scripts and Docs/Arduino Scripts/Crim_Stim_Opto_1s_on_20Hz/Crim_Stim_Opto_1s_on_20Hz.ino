const int outStim = 7;
const int BoxIn = 3;
int BoxTTL = 1;

void setup() {
  pinMode(outStim, OUTPUT);
  pinMode(BoxIn, INPUT);   
}

void loop() {
   BoxTTL = digitalRead(BoxIn); //Note that "on" for MedAssociates TTL output is 0 and "off" is 1 
   if(BoxTTL == 0)
    {
       for (int x = 0; x < 20 ; x++){   // 20 Hz 1s on
       digitalWrite(outStim, HIGH);
       delay(5); //5 ms on
       digitalWrite(outStim, LOW);
       delay(45); //45 ms off - 20 Hz pulse
       }
    }
    else
    {
     digitalWrite(outStim, LOW); 
    }
 }
