package com.github.core_server;

import com.github.core_server.config.DotenvInitializer;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class CoreServerApplication {

	public static void main(String[] args) {

		SpringApplication application =
				new SpringApplication(CoreServerApplication.class);

		application.addInitializers(
				new DotenvInitializer()
		);

		application.run(args);
	}
}
