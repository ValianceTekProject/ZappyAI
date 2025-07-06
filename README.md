# ZappyAI

The zappyAI module contains all the AI systems used to run the Zappy game.
The included AIs are:

    - An AI based on a finite state machine (FSM)
    - A Deep Q Network
    - A Proximal Policy Optimization

## Launch

To launch the AI, make sure you are using Python 3.11 and create an environment with it.

```shell
python3.11 -m venv env
```

Once this is done, you can enter the environment with `source env/bin/activate` and execute the command `pip install -r requirements.txt` to install all dependencies.

You can then execute the program using the command:

```shell
python3 Client/client.py --port PORT --team TEAM_NAME --model MODEL_CHOICE
```