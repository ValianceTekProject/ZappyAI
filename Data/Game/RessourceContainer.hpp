/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** RessourceContainer.hpp
*/

#pragma once

#include "Ressource.hpp"

#include <map>

namespace zappy {
    namespace game {
        class RessourceContainer
        {
            public:
                RessourceContainer() = default;
                RessourceContainer(const RessourceContainer &other) = default;
                ~RessourceContainer() = default;

                void clear();

                void addResource(Ressource resource, size_t quantity = 1);

                void removeResource(Ressource resource, size_t quantity = 1);

                size_t getResourceQuantity(Ressource resource) const;
                const std::map<Ressource, size_t> &getResources() const { return _resources; }

            private:
                std::map<Ressource, size_t> _resources;
        };
    }
}
