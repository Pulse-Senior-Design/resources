# Pulse

## Project Constraints Essay

**Team members:** Jacob Cohen, Sujal Choukse, and Yatharth Bajaj  
**Sentence count:** 11

### Economic

Economic constraints apply because the first release needs a Heltec WiFi LoRa 32 V4.3 board and one test sensor.  
The team has a $1,000 budget, and the three members share all equipment costs.  
The team owns three ESP32-S3 boards, but only one board has LoRa, so the first prototype must reuse this hardware.

### Security

Security applies because Pulse transfers farm sensor payloads, device identifiers, and collection times across LoRa and IP links.  
Viable deployments use persistent private keys, trusted peers, signed packets, loopback-only local RPC, and hub deduplication.  
Authentication increases ESP32 processing and energy use, but the team accepts this cost to block unauthorized data and commands.

### Social

Social constraints apply because Pulse helps farmers collect water and other field data where network access is limited.  
The system must keep readings during outages because missing water data can reduce the quality of irrigation decisions.

### Sustainability (Environmental)

Environmental constraints apply because farm devices must measure water conditions where electrical power and network access are limited.  
Pulse disables forwarding on battery devices and uses stable, powered relay devices to limit field energy use.  
This choice protects battery life but reduces route resilience where a farm cannot provide powered relay devices.
