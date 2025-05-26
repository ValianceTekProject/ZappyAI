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

    } catch (const std::exception &e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 84;
    }


}