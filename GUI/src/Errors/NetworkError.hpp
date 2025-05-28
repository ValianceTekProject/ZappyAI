//
// EPITECH PROJECT, 2025
// Network
// File description:
// Network
//

#pragma once

#include "AError.hpp"

<<<<<<< HEAD
namespace zappy {
    namespace gui {
        class NetworkError : public AError
        {
            public:
                NetworkError(const std::string &msg, const std::string &where)
                    noexcept : AError(msg, where) {};
        };
    }
=======
namespace gui {
    class NetworkError : public AError
    {
        public:
            NetworkError(const std::string &msg, const std::string &where)
                noexcept : AError(msg, where) {};
    };
>>>>>>> 205ae46 (chore: architecture)
}
