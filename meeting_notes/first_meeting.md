# IoT Project Initial Meeting

## MICROSERVICES

They must be simple, without introducing complicated external tools.

It is sufficient to clearly define responsibilities: even a “rough” architecture is fine, as long as it is functional.

**Dual communication between microservices:**

- It can be implemented with a sidecar, but this detail only needs to be mentioned in the presentation.
- Within the code, you can handle everything in the same service/class.

(Use configuration files for all settings, avoiding hardcoded).

## ARCHITECTURE

Must be decomposed into clear components and each must have a well-defined responsibility.

It must be modular, easily scalable and readable.

## GUI (Graphical User Interface)

Must be stylized in a simple manner.

Avoid complex CSS and strange or opaque communication mechanisms that complicate integration. (May ask how communication occurs between frontend and backend).

## TOPIC AND MODULAR ARCHITECTURE

Architecture must allow components to be clearly seen and support automatic scaling of operations as devices increase.

Avoid hardcoded values, e.g., treating topics by dynamic IDs.

## CLASS DIAGRAM

Recommended to create a class diagram for each main microservice:

- It must contain main attributes and methods.
- For small or very simple microservices, it can be generic or even avoided.
- The important thing is to be clear about class responsibilities, class composition/decomposition, and usage relationships (who uses what, where, and how).

## FINAL SUGGESTIONS

Before coding define for each class and microservice:

- Data structures used
- Communication interfaces
- Types of sanity checks
- Methods of the main classes
