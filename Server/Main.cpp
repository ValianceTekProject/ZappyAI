/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** main
*/


#include "Server.hpp"

int main(int argc, char const *argv[])
{
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