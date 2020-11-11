#pragma once
#include "ray.h"

class material;

struct hit_record {
    float t;
    vec3 p;
    vec3 normal;
    material* mat_ptr;
};

class hitable {
public:
    virtual bool hit(const ray& r, float tmin, float tmax, hit_record& rec) const = 0;
};

class hitable_list : public hitable {
public:
    hitable_list() {};
    hitable_list(hitable** l, int n) { list = l; list_size = n; };
    virtual bool hit(const ray& r, float tmin, float tmax, hit_record& rec) const;
    hitable** list;
    int list_size;
};

bool hitable_list::hit(const ray& r, float tmin, float tmax, hit_record& rec) const {
    hit_record temp_rec;
    bool hit_anything = false;
    double closest_so_far = tmax;
    for (int i = 0; i < list_size; i++) {
        if (list[i]->hit(r, tmin, closest_so_far, temp_rec)) {
            hit_anything = true;
            closest_so_far = temp_rec.t;
            rec = temp_rec;
        }
    }
    return hit_anything;
};