pub fn nop() {}

#[derive(Debug,Clone,Default)]
pub struct Config {
        pub main: Main,
        pub servers: Vec<Server>,
}

#[derive(Debug,Clone,Default)]
pub struct Main {
        pub version: String,
	pub prefix: String,
}

#[derive(Debug,Clone,Default)]
pub struct Server {
        pub host: String,
        pub port: String,
        pub password: String,
	pub admins: String,
	pub trackspath: String,
	pub gametype: String,
}

