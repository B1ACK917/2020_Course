#include <iostream>
#include <vector>

#include "CGL/vector2D.h"

#include "mass.h"
#include "rope.h"
#include "spring.h"

namespace CGL {

    Rope::Rope(Vector2D start, Vector2D end, int num_nodes, float node_mass, float k, vector<int> pinned_nodes)
    {
        auto tmp=(end-start)/(num_nodes-1);

        for(auto i=0;i<num_nodes;++i)
            masses.push_back(new Mass(start+i*tmp,node_mass,false));

        for(auto& i:pinned_nodes)
            masses[i]->pinned=true;
        
        for(auto i=0;i<num_nodes-1;++i)
            springs.emplace_back(new Spring(masses[i],masses[i+1],k));
    }

    void Rope::simulateEuler(float delta_t, Vector2D gravity)
    {
        for (auto &s : springs)
        {
            auto a=s->m1->position;
            auto b=s->m2->position;
            auto f=(s->k)*((b-a)/(b-a).norm())*((b-a).norm()-s->rest_length);
            s->m1->forces+=f;
            s->m2->forces-=f;
        }

        for (auto &m : masses)
        {
            if (!m->pinned)
            {
                m->forces+=gravity*(m->mass);
                auto a=(m->forces)/(m->mass);
                auto b=m->velocity;
                m->velocity=b+delta_t*a;
                m->position+=(m->velocity)*delta_t;
            }

            // Reset all forces on each mass
            m->forces = Vector2D(0, 0);
        }
    }

    void Rope::simulateVerlet(float delta_t, Vector2D gravity)
    {
        for (auto &s : springs)
        {
            auto a=s->m1->position;
            auto b=s->m2->position;
            auto f=(s->k)*((b-a)/(b-a).norm())*((b-a).norm()-s->rest_length);
            s->m1->forces+=f;
            s->m2->forces-=f;
        }

        for (auto &m : masses)
        {
            if (!m->pinned)
            {
                m->forces+=gravity*(m->mass);
                auto temp_position = m->position;
                auto a=(m->forces)/(m->mass);
                auto d=0.005f;
                m->position=temp_position+(1-d)*((m->position)-(m->last_position))+(a*delta_t*delta_t);
                m->last_position=temp_position;
            }
            m->forces = Vector2D(0, 0);
        }
        
    }
}
