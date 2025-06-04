/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Utils
*/

#pragma once

#include <csignal>
#include <iostream>

#include "IObserver.hpp"

namespace zappy {
    
    namespace server {
        class Server;
    }
    namespace game {
        class Game;
    }

    namespace utils {

        class Signal : public zappy::observer::IObserver {
            public:
                explicit Signal(zappy::server::Server &server, zappy::game::Game &game);

                void onNotify(int sig) override;

                static void initSignalHandling(Signal *instance);
                static void signalWrapper(int sig);
                static void my_signal(int sig, sighandler_t handler);

                void stopServer(int sig);
                void closeClients();

            private:
                server::Server &_server;
                game::Game &_game;
                static Signal *_instance;
    };

    }

}
