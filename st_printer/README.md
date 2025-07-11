# ST Printer Service

## Architecture Position

The ST Printer service operates as an MQTT-based microservice that simulates individual 3D printer behavior within the automated printing lab. Each printer instance:

- Receives print job assignments from the Job Handler
- Reports temperature readings for monitoring (global temperature) and safety (anomaly detection)
- Publishes print progress updates for coordination with the Job Handler and Printer Monitoring Service

```text
┌─────────────────┐    MQTT Topics      ┌─────────────────┐
│   Job Handler   │ ──────────────────► │                 │
│                 │ device/printer/     │                 │
│                 │ {id}/assignment     │                 │
│                 │                     │                 │
################### publish separation ###########################
│                 │                     │                 │
│                 │      MQTT Topics    │                 │
│                 │ ◄────────────────── │                 │
│                 │ device/printer/     │                 │
└─────────────────┘ {id}/progress       │                 |
                                        │                 │
                                        │   ST Printer    │
┌─────────────────┐    MQTT Topics      │                 │
│   Printer       │   device/printer/   │                 │
│   Monitoring    │    {id}/progress    │                 │
│   Service       │ ◄────────────────── │                 │
│                 │                     │                 │
└─────────────────┘                     │                 │
                                        │                 │
┌──────────────────┐    MQTT Topics     │                 │
│Global Temperature│ ◄───────────────── │                 │
│                  │ device/printer/    │                 │
└──────────────────┘ {id}/temperature   └─────────────────┘
                                                │
                                                │ MQTT Topics
                                                │ device/printer/{id}/temperature
                                                │
                                                ▼
                                        ┌──────────────────┐
                                        │                  │
                                        │Printer Monitoring│
                                        └──────────────────┘

```

## Communication Protocols

### MQTT Subscriptions

#### Print Job Assignment

- **Topic**: `device/printer/{printerId}/assignment`
- **Type**: 2.2.3) PrinterAssignment
- **Purpose**: Receive print job assignments with model files and specifications

### MQTT Publications

#### Temperature Monitoring

- **Topic**: `device/printer/{printerId}/temperature`
- **Type**: 2.1.2) TemperatureReading
- **Purpose**: Report current nozzle temperature for safety monitoring

#### Print Progress Updates

- **Topic**: `device/printer/{printerId}/progress`
- **Type**: 2.2.2) PrinterProgress
- **Purpose**: Report current print status and completion percentage

See [communication.md](../communication.md) for

## Printer Features

### Print Job Management

- **Assignment Processing**: Receives and validates print job assignments
- **Model File Handling**: Processes GCODE files from provided URLs (assumes local files)
- **Print Simulation**: Simulates realistic printing behavior with time progression
- **Status Tracking**: Maintains current job state and progress information

### Temperature Simulation

- **Realistic Temperature Curves**: Simulates heating up, printing, and cooling down phases given the nozzle and bed temperatures in the PrinterAssignment
- **Thermal Behavior**: Simulates temperature fluctuations during printing
- **Safety Monitoring**: Often reports temperature anomalies for anomaly detection checks

### Printer Configuration and Operating Parameters

- printer ID
- printer type (e.g., Prusa MK3S, Creality Ender 3, Bambulab X1)
- filament type
- nozzle diameter
- max nozzle temperature, temp rate
- max bed temperature, temp rate
- print speed (function based on filament type, nozzle diameter, layer height, infill)

## Journey

The ST Printer Service follows a complete print job lifecycle:

### 1. Initialization Phase

- Load printer configuration and operating parameters
- Initialize MQTT client and connect to broker
- Subscribe to assignment topic for the specific printer ID
- Initialize temperature sensor simulation
- Set printer status to "idle"

### 2. Assignment Reception Phase

- **Job Assignment**: Receive print job assignment from Job Handler
- **Validation**: Validate job parameters (model URL, filament type, estimated time)
- **Model Download**: Fetch GCODE file from provided URL
- **Preparation**: Initialize print simulation parameters
- **Status Update**: Report "printing" status with 0% progress

### 3. Printing Simulation Phase

- **Temperature Ramp-Up**: Simulate nozzle heating to target temperature
- **Print Progress**: Incrementally update print progress over estimated time
- **Temperature Monitoring**: Continuously report realistic temperature readings
- **Progress Reporting**: Publish progress updates at regular intervals

### 4. Completion Phase

- **Print Completion**: Report 100% progress and "completed" status
- **Cool-Down**: Simulate nozzle cooling down to room temperature
- **Plate Ready**: Signal that printed object is ready for collection
- **Status Reset**: Return to "idle" status awaiting robot collection

## Separation of Concerns

The architecture follows a clear separation where:

- STBinaryPrintingService handles external interactions:
  - MQTT subscriptions and publications
  - Print job assignment processing
  - Status and progress reporting
  - Temperature data publication

- PrintingSimulator handles the core printing logic:
  - Print progress calculation
  - Temperature simulation
  - Time management
  - State transitions

- PrintJob encapsulates job-specific data:
  - Job parameters and metadata
  - Validation logic
  - Status tracking

## Service Class Structure

```mermaid
classDiagram
    class PrintingService {
        -mqtt_client: MQTTClient
        -printer_id: str
        -config: dict
        -current_job: PrintJob
        -printing_simulator: PrintingSimulator

        +__init__(printer_id: str, config_file: str)
        +start_service(): void
        +stop_service(): void
        +connect_mqtt(): void
        +disconnect_mqtt(): void

        +callback_assignment(topic: str, payload: dict): void
        +process_assignment(assignment: PrinterAssignment): void
        +validate_assignment(assignment: PrinterAssignment): bool

        +publish_temperature(): void
        +publish_progress(): void
        +publish_status_update(status: str): void

        +download_model_file(url: str): bool
        +start_print_simulation(): void
        +handle_print_completion(): void
        +handle_print_error(error: str): void

        +load_configuration(config_file: str): dict
        +get_printer_status(): dict
    }

    class PrintingSimulator {
        -job_parameters: dict
        -start_time: datetime
        -estimated_duration: int
        -current_progress: float
        -current_temperature: float
        -target_temperature: float
        -print_status: str
        
        +__init__(job_parameters: dict)
        +start_simulation(): void
        +update_progress(): float
        +calculate_temperature(): float
        +get_current_status(): str
        +is_simulation_complete(): bool
        +simulate_heating_curve(): float
        +simulate_cooling_curve(): float
        +calculate_time_remaining(): int
        +handle_simulation_error(): void
    }

    class PrintJob {
        -job_id: str
        -model_url: str
        -filament_type: str
        -estimated_time: int
        -assigned_at: datetime
        -status: str
        
        +__init__(assignment: PrinterAssignment)
        +validate(): bool
        +get_job_info(): dict
        +update_status(status: str): void
        +calculate_progress(current_time: datetime): float
    }

    PrintingService --> PrintingSimulator : uses
    PrintingService --> PrintJob : manages
    PrintingSimulator --> PrintJob : references
```
