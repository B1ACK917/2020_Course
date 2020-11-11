#include <iostream>
#include <fstream>
#include "hitable.h"
#include "ray.h"
#include "sphere.h"

vec3 color(const ray& r, hitable* world) {
    hit_record rec;
    if (world->hit(r, 0.0, std::numeric_limits<float>::max(), rec)) {
        return 0.5 * vec3(rec.normal.x() + 1, rec.normal.y() + 1, rec.normal.z() + 1);
    }
    else {
        vec3 unit_direction = unit_vector(r.direction());
        float t = 0.5 * (unit_direction.y() + 1.0);
        return (1.0 - t) * vec3(1.0, 1.0, 1.0) + t * vec3(0.5, 0.7, 1.0);
    }
}

int main() {
	std::ofstream fs;
	fs.open("ray_tracing.ppm");

	auto nx = 200;
	auto ny = 100;
	fs << "P3\n" << nx << " " << ny << "\n255\n";
	vec3 lower_left_corner(-2.0, -1.0, -1.0);
	vec3 horizontal(4.0, 0.0, 0.0);
	vec3 vertical(0.0, 2.0, 0.0);
	vec3 origin(0.0, 0.0, 0.0);
	hitable* list[2];
	list[0] = new sphere(vec3(0, 0, -1), 0.5);
	list[1] = new sphere(vec3(0, -100.5, -1), 100);
	hitable* world = new hitable_list(list, 2);

	for (auto j = ny - 1;j >= 0;--j) {
		for (auto i = 0;i < nx;++i) {
			float u = float(i) / float(nx);
			float v = float(j) / float(ny);
			ray r(origin, lower_left_corner + u * horizontal + v * vertical);

			vec3 p = r.point_at_parameter(2.0);
			vec3 col = color(r,world);
			int ir = int(255.99 * col[0]);
			int ig = int(255.99 * col[1]);
			int ib = int(255.99 * col[2]);
			fs << ir << " " << ig << " " << ib << "\n";
		}
	}
	fs.close();
}