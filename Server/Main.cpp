/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** main
*/

#include "Server.hpp"

static void displayHelp()
{
    std::cout << "USAGE: -p port -x width -y height -n name1 name2 ... -c "
                 "clientNB -f freq"
              << std::endl;
}

static bool checkArgs(int argc)
{
    if (argc < 8) {
        displayHelp();
        return false;
    }
    return true;
}

int main(int argc, char const *argv[])
{
    if (checkArgs(argc) == false)
        return KO;
    try {
        ZappyServer::Server server;

        server.parsing(argc, argv);
        server.serverLaunch();

    } catch (const ZappyServer::error::Error &e) {
        std::cerr << " Error: " << e.what() << std::endl;
        return KO;
    }
    return OK;
}
