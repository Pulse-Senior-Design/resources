# Pulse Reliable Sensor Delivery over LoRa Mesh

Company: COEN Applied LLC

## Introduction

Pulse is a proposed sensor system for distributed surveillance and situational awareness where conventional connectivity is unavailable. Intended sites include deep forests, rugged terrain, remote coastlines, and offshore sensor buoys. Pulse uses an encrypted Reticulum mesh across LoRa radio and available Wi-Fi or Ethernet links. Sensors collect observations locally, relay them when a path exists, and retain them when isolated. Alternate relay paths reduce dependence on one link. Proposed collectors include authorized drones, ground vehicles, and personnel-carried devices. They retrieve nearby observations without first reaching a central server. Pulse aims to preserve information through intermittent contact. The first proof connects one ESP32 sensor to one Linux Hub. Later tests establish mesh recovery and mobile collection.

## Army Benefits

Pulse aims to preserve water, power, and equipment records across dispersed Army sites. Personnel can collect those records through local radio links instead of visiting every sensor. This supports Adaptive Sustainment and Command and Control networks. A complete outage delays delivery until a path returns. With appropriate sensors and separate decision-support software, personnel can monitor remote areas and assess environmental, infrastructure, and equipment conditions.

Manual collection requires site visits. Cloud-only cellular systems need coverage and a working service connection. Local MQTT and LoRaWAN systems can also store data during outages [3, 4]. Pulse combines mesh paths, local storage, and confirmed Hub storage in one sensor system. Its proposed advantage is simpler deployment and recovery across different links. Tests must establish that advantage.

The initial scale target uses ten devices, each taking one sample per minute. A 24-hour outage produces 14,400 readings. The proposed pass target is recovery of all readings, with no duplicate records or visits to retrieve data. A fair comparison uses the same sensors, power, storage, and outage conditions. It measures recovery time, installation work, and equipment cost. No measured improvement exists yet.

## Technical Approach

Mesh and radio. An Edge reads sensors; a Hub stores received data. Reticulum discovers paths to a destination associated with the Hub identity [2]. For example, Edge to relay A to Hub can change to Edge to relay B to Hub after a link fails. The Edge addresses the same Hub; it does not configure every hop. Recovery depends on another reachable path and path discovery. Powered relays enable forwarding; battery devices can disable it. LoRa carries compact field readings. A relay with compatible interfaces can connect the radio segment to an IP segment. Each hop consumes airtime; more paths do not guarantee more capacity.

Reliable delivery. Each role embeds a Node library with its own identity, routes, and queues. Protobuf messages carry a stable identifier, origin, sensor schema, and binary samples. The Edge journals reliable messages before transmission and restores them after restart. The Hub checks sender identity and commits raw data before returning STORED. Retries retain the identifier, so duplicate delivery creates one logical record. Unknown schemas enter quarantine after storage. A lost receipt causes another retry. When all paths fail, the Edge retains records within configured limits and reports loss or stopped sampling [1, 5].

## Mobile Data Collection

Mobile collection. An authorized drone, ground vehicle, or personnel-carried device can retrieve observations directly from nearby sensors. It needs a compatible link, a preconfigured trusted identity, and local collection software. It does not need prior contact with a central server. A drone can temporarily relay traffic when it has a path to a ground Hub. For disconnected collection, it carries a trusted onboard Hub and persistent storage. During a flyover, an isolated Edge transfers queued records to that collector. An announcement alone does not establish trust. The collector acknowledges each durable commit. The Edge retries records without receipts during a later contact.

The drone carries records to a base when no ground path exists. Its storage receipt proves onboard storage, not delivery to the base. The proposed extension keeps the onboard copy until the base confirms its copy. Tests check both transfers and interrupted contacts. This transfer between Hubs remains outside the first release [1]. Authorized local software can use decoded observations for situational awareness during the mission. Data access requires explicit trust; collection access does not authorize control commands.

## Development and Proof

First release. The design pairs an ESP32-S3 and SX1262 LoRa radio with a Linux Hub and compatible radio interface. Each Edge or Hub includes a Node library that handles Reticulum communication. Shared message definitions support different sensor types. A build tool checks local configuration before installation. The provisional technology readiness level is 2. Radio integration, storage recovery, and power use need validation [1].

Contact capacity. Useful bytes per pass cannot exceed payload rate times contact duration divided by eight. At an assumed 1 kbit/s for 60 seconds, the upper bound is 7,500 bytes, or 29 complete 256-byte records. Discovery, receipts, interference, and retries reduce that count. One device sampling each minute generates 1,440 records per day. A brief low-rate pass therefore cannot clear its daily backlog. Longer contact, a higher measured rate, or fewer samples must close the gap. These are planning assumptions, not flight results.

Test plan. A proposed six-month effort starts with one sensor and one Hub. Tests interrupt links, restart devices, lose receipts, fill storage, and reject unapproved senders. Pass criteria require recovery of retained payloads, one logical record per identifier, and no deletion before confirmed storage. The next stage adds ten devices and two relay paths. Removing the active relay checks recovery time through the alternate path. A complete partition checks persistent storage. A later drone trial measures discovery time, useful contact duration, records per pass, energy use, and confirmed base delivery. Ground and personnel-carried trials check trusted local access without a server connection. An Army partner sets mission limits before a site trial. No Pulse test results exist yet.

Team. Jacob Cohen brings Rust, C++, Linux, and industrial telemetry experience from Tarigma and GE Vernova. Yatharth Bajaj brings industrial controls and Python networking experience from JTEKT. Sujal Choukse brings database checks and automated data collection experience. All three study computer science at the University of Cincinnati. Army field validation remains a gap [6].

## Commercial Potential

Farms and water utilities provide potential commercial markets. Remote environmental and buoy monitoring provide further uses [7]. COEN Applied LLC has three employees, no capital raised, and no prior DoW business. Pulse has no sales, pilot agreements, or test results. The sales plan starts with customer interviews and a written pilot agreement. A paid pilot measures recovered records, avoided visits, and installation cost. Supported software and compatible device kits form the proposed product.

Tested sensor drivers, hardware profiles, and repeatable failure tests can reduce installation and support work. These are proposed advantages; no patent or exclusive data claim supports them. The plan seeks paid commercial pilots to support common drivers and reliability work. No customer or investor commits funding today. Army support targets mission validation, while commercial uses provide a possible path for continued development. Software rights and dependency terms need review before sales.

References: [1] Pulse Architecture Redevelopment Specification, sections 3, 8–15, 18–22. [2] Reticulum, reticulum.network/manual/understanding.html. [3] MQTT, mqtt.org. [4] The Things Network, thethingsnetwork.org/docs/lorawan/architecture/. [5] SQLite, sqlite.org/atomiccommit.html. [6] Pulse team biographies, assignment 1. [7] Pulse Architecture Development Narrative, Marine Data Mules. External sources accessed October 17, 2026.

