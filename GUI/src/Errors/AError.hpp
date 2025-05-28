/*
** EPITECH PROJECT, 2025
<<<<<<< HEAD
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
=======
** B-OOP-400-BDX-4-1-gui-baptiste.blambert
>>>>>>> 205ae46 (chore: architecture)
** File description:
** AError
*/

#pragma once

#include "IError.hpp"

<<<<<<< HEAD
namespace zappy {
    namespace gui {
        class AError : public IError
        {
            public:
                AError(const std::string &msg, const std::string &where) noexcept;

                const char *what() const noexcept;
                const char *where() const noexcept;

            private:
                std::string _msg;
                std::string _where;
        };
    }
=======
namespace gui {
    class AError : public IError
    {
        public:
            AError(const std::string &msg, const std::string &where) noexcept;

            const char *what() const noexcept;
            const char *where() const noexcept;

        private:
            std::string _msg;
            std::string _where;
    };
>>>>>>> 205ae46 (chore: architecture)
}
