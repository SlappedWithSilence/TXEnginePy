# TXEngine (Py)

TXEngine is a text-based game engine, originally written in Java. The goal of this project is to create a rich toolset of game elements that empower designers to build flexible and unique worlds. With TXEngine, designers create games entirely by manipulating a set of JSON files--no code needed. TXEngine also features a rich content designer that can assist users of the engine with writing, tracking, and checking their JSON game components (coming soon).

This repository houses a Python rewrite and overhaul of the original TXEngine code. 

## How to Install
- TBD

## What's New?
TXEngine (Py) features a number of major improvements as compared to TXEngine (Java):

### Microservice Architecture
TXEngine (Py) splits the core logic of the engine away from the text rendering logic. This split increases the engine's maintainability, flexibility, and customizability.

TXEngine's backend makes use of FastAPI and comes bundled with a Python-Native text rendering client based on Rich!

### Improved Asset Schema
One major flaw of TXEngine (Java) was the confusing and complicated nature of the JSON asset schema. It was inflexible and difficult to document. TXEngine (Py) makes use of a streamlined JSON schema that is self-documenting, easy to update, and flexible!

### Remote Play
Since TXEngine (Py)'s backend is built on top of a REST-API framework, it can easily be set up to run on a remote machine. Access TXEngine (Py) from anywhere, even your phone!

# Contributing

TXEngine (Py) is open to contribution. Open a pull-request, and I'll do my best to review it quickly. Any PR that is poorly documented or does not adhere to the coding standards for this repository will be rejected.

## Developing
 - TBD
