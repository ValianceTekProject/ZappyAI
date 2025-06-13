/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** IObserver
*/

#pragma once

namespace zappy {

    namespace observer {

        class IObserver {

        public:

            virtual ~IObserver() = default;

            virtual void onNotify(int signal) = 0;

        };

    }

}
