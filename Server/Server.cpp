/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Server
*/

#include "Server.hpp"

int handlerFlag(char const *argv[], int i, std::string flag)
{
    std::stringstream stream;
    int res = -1;

    if (std::string(argv[i]) == flag && argv[i + 1]) {
            stream << std::string(argv[i + 1]);
            stream >> res;
    }
    return res;
}

void zappy::server::Server::parsingName(int &index, char const *argv[])
{
    int nameCount = 0;

    while (argv[index]) {
        if (std::string(argv[index]).find("-") == 0)
            break;
        _namesTeam.push_back(argv[index]);
        nameCount += 1;
        index += 1;
        zappy::game::Team team(argv[index]);
        _teamList.push_back(team);
    }

    if (nameCount == 0)
        throw error::InvalidArg("Flag -n must have at least on argument !");

}

void zappy::server::Server::parsing(int argc, char const *argv[])
{
    for (int i = 1; i < argc; ++i) {
        if (!argv[i])
            throw error::Error("Error in argument list");

        std::string currentArg = argv[i];

        if (currentArg == "-n") {
            ++i;
            parsingName(i, argv);
            --i;
            continue;
        }

        int value = handlerFlag(argv, i, currentArg);
        if (value != -1) {
            if (currentArg == "-p")
                _port = value;
            else if (currentArg == "-x")
                _width = value;
            else if (currentArg == "-y")
                _height = value;
            else if (currentArg == "-c")
                _clientNb = value;
            else if (currentArg == "-f")
                _freq = value;
            i += 1;
        } else
            throw error::InvalidArg("Unknown or badly formatted argument: " + currentArg);
    }

    if (_port == -1 || _width == -1 || _height == -1 ||
        _clientNb == -1 || _freq == -1 || _namesTeam.empty())
        throw error::InvalidArg("Missing arguments: -p -x -y -c -f -n <names>");
}

void zappy::server::Server::serverLaunch()
{
    _servSocket = my_socket(AF_INET, SOCK_STREAM, 0);
    if (_servSocket < 0)
        throw zappy::error::ServerConnection("Socket failed");

    servAddr.sin_addr.s_addr = INADDR_ANY;
    servAddr.sin_port = htons(_port);
    servAddr.sin_family = AF_INET;

    if (my_bind(_servSocket, (struct sockaddr *) &servAddr, sizeof(servAddr)) < 0) {
        close(_servSocket);
        if (errno == EADDRINUSE)
            throw zappy::error::ServerConnection("Port already used");
        throw zappy::error::ServerConnection("bind failed");
    }
    if (my_listen(_servSocket, (_clientNb * _namesTeam.size())) < 0) {
        close(_servSocket);
        throw zappy::error::ServerConnection("listen failed");
    }

    std::cout << "Zappy Server listening on port " << _port << "...\n";
    fds.push_back({_servSocket, POLLIN, 0});

    
    std::thread networkThread(&zappy::server::Server::serverLoop, this);
    std::thread gameThread(&zappy::game::Game::gameLoop, this);

    networkThread.detach();
    gameThread.detach();

    close(_servSocket);
}
