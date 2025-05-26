/*
** EPITECH PROJECT, 2025
** B-NWP-400-BDX-4-1-jetpack-baptiste.blambert
** File description:
** Error
*/

#pragma once

    #include <stdexcept>

namespace ZappyServer {
    namespace error {
        class Error : std::exception {
            public:
                Error(std::string msg)
                    : _errorMsg(msg)
                {}

                char const *getMessage() const;

                const char *what() const throw();
            protected:
            private:
                std::string _errorMsg;
        };

        // Erreur spécifique pour vérification arg
        class InvalidArg : public Error {
            public:
                InvalidArg(std::string msg) : Error(msg) {}
        };

        // Erreur spécifique pour les erreurs de connection serveur
        class ServerConnection : public Error {
            public:
                ServerConnection(std::string msg) : Error(msg) {}
        };
    }
}
