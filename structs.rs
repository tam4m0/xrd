extern crate serde;
use serde_derive::*;
use serde::*;
use serde::ser::*;

#[derive(Deserialize)]
pub struct Config {
        pub main: Main,
        pub server: Server,
}

#[derive(Deserialize)]
pub struct Main {
        pub version: String,
}

#[derive(Deserialize)]
pub struct Server {
        pub host: String,
        pub port: String,
        pub password: String,
}

