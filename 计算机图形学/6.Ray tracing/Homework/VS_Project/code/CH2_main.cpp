#include <iostream>
#include<fstream>
#include "vec3.h"

int main() {
	std::ofstream fs;
	fs.open("ray_tracing.ppm");

	auto nx = 200;
	auto ny = 100;
	fs << "P3\n" << nx << " " << ny << "\n255\n";
	for (auto j = ny - 1;j >= 0;--j) {
		for (auto i = 0;i < nx;++i) {
			vec3 col(float(i) / float(nx), float(j) / float(ny), 0.2);
			int ir = int(255.99 * col[0]);
			int ig = int(255.99 * col[1]);
			int ib = int(255.99 * col[2]);
			fs << ir << " " << ig << " " << ib << "\n";
		}
	}
}