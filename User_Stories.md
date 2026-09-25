# Pulse User Stories and Use Cases

## Team Members

- Jacob Cohen
- Sujal Choukse
- Yatharth Bajaj

## Stakeholder Map

| Category | Stakeholders | Main needs |
| --- | --- | --- |
| Primary | Farm operations manager; field technician | Receive field measurements at the hub. Preserve measurements during a radio outage. |
| Secondary | Deployment engineer; sensor integration developer; support technician | Reject invalid configurations. Add sensor types through stable contracts. Find delivery faults. |
| Hidden | Farm data steward; downstream analytics operator; radio compliance authority | Reject unapproved senders. Receive consistent records. Use approved radio settings. |

The stories use the project records, architecture, current components, configuration examples, and automated tests as requirement sources.

## User Stories

### US-01 (primary)

As a farm operations manager,
I want field measurements to reach the farm hub after outages that end before the 3,600-second message expiry,
so that I can detect irrigation problems without visiting each sensor site.

### US-02 (primary)

As a field technician,
I want important samples to remain in the delivery queue until the hub stores them,
so that a radio outage does not remove the farm's measurement history.

### US-03 (secondary)

As a deployment engineer,
I want the system to reject an invalid device configuration before installation,
so that each field device starts with a supported hardware and software combination.

### US-04 (secondary)

As a sensor integration developer,
I want to add a sensor through the stable driver and decoder contracts,
so that a new sensor does not require a change to the transport protocol.

### US-05 (hidden)

As a farm data steward,
I want the hub to accept records only from approved component identities,
so that unapproved devices cannot add records to the farm data set.

## INVEST Check

| Story | INVEST check |
| --- | --- |
| US-01 | **Independent:** The team can test delivery without a dashboard. **Negotiable:** The story does not select a radio or screen. **Valuable:** The manager receives measurements after an outage. **Estimable:** The Edge-to-Hub path defines the work. **Small:** The story covers one delivery result. **Testable:** A test can disconnect and restore the link. |
| US-02 | **Independent:** The team can test queue behavior by itself. **Negotiable:** The story does not select a queue implementation. **Valuable:** The farm keeps important measurements. **Estimable:** The acknowledgement and queue limits define the work. **Small:** The story covers one stored sample. **Testable:** A test can inspect the queue, database, and status. |
| US-03 | **Independent:** The Builder can validate a file without field hardware. **Negotiable:** The story does not select an input tool. **Valuable:** The engineer finds faults before installation. **Estimable:** The configuration rules define the work. **Small:** The story covers one validation result. **Testable:** A test can check the process result and error text. |
| US-04 | **Independent:** The team can add one driver and one decoder. **Negotiable:** The story does not select a sensor model. **Valuable:** The project can support another sensor. **Estimable:** The driver and decoder contracts define the work. **Small:** The story covers one sensor type. **Testable:** Protocol tests can compare the record before and after transport. |
| US-05 | **Independent:** The team can test identity checks with test keys. **Negotiable:** The story does not select a key tool. **Valuable:** The data set excludes unapproved senders. **Estimable:** The trust table defines the work. **Small:** The story covers one sender decision. **Testable:** A test can use approved and unapproved identities. |

## Use Cases

### UC-01: Deliver Queued Telemetry

- **Expands:** US-02
- **Primary actor:** Field technician
- **Secondary actors:** Edge component, field Node, hub Node, and Hub component

#### Preconditions

1. The field configuration uses `ack = "stored"`.
2. The outbound queue has space for at least one reliable message.
3. The field and hub Nodes have approved peer identities.
4. One sensor has a sample interval of 60 seconds.
5. The Hub database has no row for the test message identifier.
6. The radio link is available before the test starts.

#### Main Success Flow

1. The field technician starts the field Node, Edge, hub Node, and Hub.
2. The system validates each configuration and registers the Hub destination.
3. The field technician disconnects the field link before the next sample time.
4. The Edge collects one sample. The field Node keeps the message in its reliable queue.
5. The field technician restores the link before the message expires.
6. The field Node sends the queued message with its original message identifier.
7. The hub Node checks the sender identity and gives the message to the Hub.
8. The Hub validates the message and commits one database row.
9. The Hub sends a `STORED` acknowledgement after the commit.
10. The field Node removes the acknowledged message from its reliable queue.

#### Alternate Flow: Duplicate Transmission

1. The field Node retransmits the message with the same message identifier before it receives the acknowledgement.
2. The Hub finds the existing duplicate key and does not create a second logical record.
3. The Hub sends a `STORED` acknowledgement for the committed record.
4. The field Node removes the acknowledged message from its reliable queue.

#### Exception Flow: Unapproved Sender

1. The hub Node receives the queued message from an identity that is not in its trust table.
2. The hub Node rejects the message as `UNAUTHORIZED`.
3. The Hub does not receive the message and does not add a database row.
4. The field Node keeps the message until a valid acknowledgement or the configured expiry.

#### Postcondition

The Hub stores exactly one row for an approved message. The field queue has no copy after the `STORED` acknowledgement.

### UC-02: Validate a Device Configuration

- **Expands:** US-03
- **Primary actor:** Deployment engineer
- **Secondary actors:** Builder and sensor driver registry

#### Preconditions

1. The deployment engineer can run the Builder.
2. The `sim-env` driver is in the selected Edge build.
3. The engineer has a device configuration file that follows schema version 1.
4. The source configuration file is under version control.

#### Main Success Flow

1. The deployment engineer selects the target platform and the device configuration file.
2. The engineer runs the Builder validation command.
3. The Builder parses the file and checks all required sections.
4. The Builder checks the platform, local carrier, acknowledgement mode, driver name, and sample interval.
5. The Builder reports a successful result and returns process status 0.
6. The deployment engineer marks the unchanged file as ready for the next build step.

#### Alternate Flow: List Included Drivers

1. The deployment engineer does not know which sensor drivers are in the selected build.
2. The engineer runs the Builder command that lists drivers.
3. The Builder prints each included driver name.
4. The engineer selects `sim-env` and returns to step 2 of the main flow.

#### Exception Flow: Driver Is Not Included

1. The configuration names a driver that is not in the selected build.
2. The Builder rejects the configuration and returns a nonzero process status.
3. The Builder reports the invalid driver name and the available driver names.
4. The Builder leaves the source configuration file unchanged.

#### Postcondition

A successful result identifies one unchanged configuration as valid for the selected platform. A failed result does not approve the configuration.

## Acceptance Criteria

### UC-01 Acceptance Criteria

#### AC-01.1 - Main Success Flow

Given an approved field identity, an empty Hub database, and a field configuration that requests `STORED`,
When the technician disconnects the link for one sample and restores it before the 3,600-second expiry,
Then the Hub contains exactly one row for the message identifier and the field queue contains zero copies after acknowledgement.

#### AC-01.2 - Alternate Flow

Given the Hub already stored a message with one origin and message identifier,
When the Hub receives the same message two more times,
Then the Hub contains exactly one logical row for that origin and message identifier and returns `STORED`.

#### AC-01.3 - Exception Flow

Given the hub Node trust table does not contain the field identity,
When that field identity sends one message to the Hub destination,
Then the hub Node reports `UNAUTHORIZED` and the Hub adds zero rows for the message identifier.

### UC-02 Acceptance Criteria

#### AC-02.1 - Main Success Flow

Given a schema version 1 Linux configuration with a 128-character hexadecimal peer identity, `loopback_tcp`, `stored`, and the included `sim-env` driver,
When the deployment engineer runs the Builder validation command,
Then the command returns process status 0 and reports zero validation errors.

#### AC-02.2 - Alternate Flow

Given the selected Edge build includes the `sim-env` driver,
When the deployment engineer runs the Builder driver-list command,
Then the command output contains `sim-env` exactly once.

#### AC-02.3 - Exception Flow

Given a configuration that names `missing-driver` and a source file with a recorded hash,
When the deployment engineer runs the Builder validation command,
Then the command returns a nonzero status, names `missing-driver`, lists available drivers, and preserves the source file hash.

