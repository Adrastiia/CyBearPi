# CyBearPi
A prototype smart toy built on Raspberry Pi that demonstrates the cybersecurity challenges of IoT children’s toys.  
The project is part of research on **cybersecurity in IoT**, with a focus on privacy and data protection in smart toys.  
Developed as a part of the final assignment at VERN' University.


<img src="https://github.com/user-attachments/files/22127572/medo_f.bmp" alt="">
<img src="https://github.com/user-attachments/assets/85162717-4891-463d-bcb6-38f6355f742d" alt="">

---

## Features
- **Voice interaction**: Wake word detection with *Picovoice Porcupine* and command recognition with *Rhino Speech-to-Intent*.  
- **Touchscreen UI**: Menu with buttons for Story Time, Fun Fact, Music, Photo, and Sleep.  
- **Photo capture**: Takes pictures with Raspberry Pi camera and stores them locally + in MongoDB.  
- **Entertainment**: Plays public domain children’s music, tells stories, and shares fun facts.  
- **MongoDB integration**: Stores photos.  
- **Cybersecurity testing**: Designed with intentional vulnerabilities to demonstrate attacks and mitigations.  

---

## System Architecture
- **Hardware**: Raspberry Pi, ReSpeaker 2-Mics Pi HAT, ILI9341 TFT display, CSI camera.  
- **Software**: Python 3, MongoDB Atlas, Picovoice SDK.   

---

## Security Testing
This toy was intentionally built with weak configurations to demonstrate:
- Hardcoded credentials
- Insecure communication (HTTP / no TLS)
- Weak access control

---

Project Goals
- Raise awareness about cybersecurity risks in children’s IoT toys.
- Highlight risks of hardcoded credentials, weak access control, and unencrypted communication.
- Provide a controlled test environment for penetration testing.
- Serve as a practical component of a cybersecurity thesis.

---

## Disclaimer
**This project is for educational and research purposes only**
