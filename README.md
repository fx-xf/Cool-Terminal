🎧 Cool Terminal - Voice-Activated Assistant with System Monitoring 🚀

 <!-- Example placeholder, replace with actual image link -->

Cool Terminal is a cutting-edge terminal application that combines a voice-activated assistant with real-time system monitoring. Whether you're a tech enthusiast or just someone who wants to have fun with voice commands, this project has something for everyone! 😎
🛠 Features

    Voice Recognition 🎙: Control your terminal with your voice using the powerful Vosk speech recognition model.
    System Monitoring 🖥: Keep track of your CPU, GPU, Disk usage, and more with real-time ASCII art diagrams.
    Interactive Responses 🎵: Get playful audio responses and interact with your system like never before.
    Customizable Content 🎨: Themed HTML content converted into vibrant ANSI-colored text for a unique terminal experience.
    Web Automation 🌐: Open your favorite websites and services directly with voice commands.

🚀 Getting Started
Prerequisites

Before you begin, ensure you have the following installed on your Linux system:

    Python 3.8+
    FFmpeg (for audio playback)
    PortAudio (for sound input)

Installation

    Clone the repository:

    bash

git clone https://github.com/fx-xf/Cool-Terminal.git
cd Cool-Terminal

Set up the virtual environment:

bash

python -m venv myenv
source myenv/bin/activate

Install dependencies:

bash

pip install -r requirements.txt

Install FFmpeg and PortAudio:

On Ubuntu/Debian:

bash

sudo apt-get update
sudo apt-get install ffmpeg portaudio19-dev

On Arch Linux:

bash

sudo pacman -S ffmpeg portaudio

On Fedora:

bash

sudo dnf install ffmpeg portaudio-devel

Download and configure the Vosk model:

    Visit the Vosk Models page and download the model that suits your needs.

    Extract the model to a directory of your choice.

    Update the MODEL_PATH variable in main.py to point to the directory where you extracted the model:

    python

        # In main.py
        MODEL_PATH = "path/to/your/vosk-model"

Running the Project

    Activate the virtual environment:

    bash

source myenv/bin/activate

Run the application:

bash

    python main.py

🎮 Usage

    Say "Hi" to start an interaction.
    Ask for your name to get a playful response.
    Request new content to refresh the terminal with themed visuals.
    Open YouTube, anime, or music with simple voice commands.
    Shut down your PC with a command (Use with caution! 😅).

🧩 Project Structure

plaintext

Cool-Terminal/
├── arts/                 # Themed content in HTML format
├── data/                 # Audio and phrase data for the assistant
├── myenv/                # Virtual environment directory
├── main.py               # Main script for running the application
├── requirements.txt      # Project dependencies
└── README.md             # This file!

🛠 Troubleshooting

    Error: PortAudio library not found
        Ensure that PortAudio is installed. On Ubuntu/Debian, use sudo apt-get install portaudio19-dev. On Fedora, use sudo dnf install portaudio-devel.

    Error: No such file or directory: 'ffplay'
        Install FFmpeg and ensure ffplay is available in your system's PATH.

    Error: Vosk model not found
        Make sure you have downloaded a Vosk model and correctly set the MODEL_PATH variable in main.py.

🤝 Contributing

We welcome contributions! Please fork this repository, create a new branch, and submit a pull request with your changes.
📜 License

This project is licensed under the MIT License. See the LICENSE file for details.
✨ Acknowledgments

    Thanks to the developers of Vosk for the amazing speech recognition library.
    Shoutout to the FFmpeg and PortAudio communities for their fantastic tools.

Made with 💻 by fx_xf
