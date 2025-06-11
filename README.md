# ControlPilot

**ControlPilot** is an AI-powered assistant for SCADA engineers, designed to generate Jython scripts for Ignition based on natural language prompts. Inspired by tools like GitHub Copilot, it streamlines development inside industrial automation environments.

## Overview

ControlPilot connects a FastAPI backend to OpenAI’s GPT-4o model. Users enter prompts through the Ignition Vision interface and receive real-time, context-aware script suggestions for automation tasks.

## Features

- AI-assisted Jython script generation
- Ignition Vision interface integration
- Secure, local FastAPI backend
- Compatible with GPT-4o via OpenAI API

## Tech Stack

- Ignition (Vision + Jython)
- FastAPI (Python)
- OpenAI Python SDK
- Java HTTP integration (Ignition → API)

## Architecture

1. User enters prompt in Ignition Vision
2. Prompt sent to local FastAPI server
3. OpenAI API returns generated script
4. Result is previewed in Ignition UI

## Project Structure

ControlPilot/
├── main.py # FastAPI backend
├── .env.example # Example config
├── .gitignore # Git exclusions
├── README.md # Project documentation
└── assets/ # (Optional) Screenshots

## License

This project is licensed under the MIT License.

## Author

**Elvis Alam**  
GitHub: [@theelvisalam](https://github.com/theelvisalam)
