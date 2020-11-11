#include <iostream>

// do not modify it.
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include "PathTracer.h"

int main(int argc, char *argv[])
{
	// initialization.
	PathTracer tracer;
	tracer.initialize(256, 144);
	
	// rendering.
	double timeConsuming = 0.0f;
	unsigned char *pixels = tracer.render(timeConsuming);

	// save pixels to .png file using stb_image.
	stbi_flip_vertically_on_write(1);
	stbi_write_png("./result_2k.png",
		tracer.getWidth(),
		tracer.getHeight(),
		4,
		static_cast<void*>(tracer.getImage()),
		tracer.getWidth() * 4);

	std::cout << "Rendering Finished.\n";
	std::cout << "Time consuming: " << timeConsuming << " secs.\n";

	return 0;
}