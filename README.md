## Basic chess engine using Pygame and Stockfish
    
    http://philrg.pythonanywhere.com

### Install required modules
    pip install -r requirements.txt

### Install Stockfish & copy binary to engines/stockfish:

    https://stockfishchess.org/download/

### Launch webapp
    python flask_app.py

#### Additional ressources:
- https://pixabay.com/images/search/user_id%3a7990144%20white%20knight%20chess/
- https://github.com/mcostalba/Stockfish.git
- https://github.com/phracker/MacOSX-SDKs/releases/tag/10.15

#### Compiling instructions for :macOSX 10.15:
```
    export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX10.15.sdk
    uname -a
    make build ARCH=x86-64 COMP=clang
```
