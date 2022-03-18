#![allow(non_snake_case)]
#![allow(non_camel_case_types)]

extern crate toml;
use std::net::TcpStream;
use std::io::prelude::*;
use std::sync::{Arc,Mutex};
use std::fs;
use std::str;
use std::env;
use std::path::PathBuf;
pub mod structs;
pub mod messages;
pub mod loops;

fn connect_server(cnfroot: &structs::Config, handler: u32) -> (Arc<Mutex<TcpStream>>,u32) {
	let stream = Arc::new(Mutex::new(TcpStream::connect(format!("{}:{}",&cnfroot.server.host,&cnfroot.server.port)).unwrap()));

	let mut cloned_stream = stream.lock().unwrap();
	cloned_stream.read(&mut [0;4]).unwrap();

	let mut ver = [0;12];
	cloned_stream.read(&mut ver).unwrap();

	drop(cloned_stream);

	assert_eq!(str::from_utf8(&ver).unwrap().trim_matches(char::from(0)),"GBXRemote 2");
	println!("Connection acquired to server.");

	let (mut stream,mut handler2) = messages::send_message(messages::transform_xmlrpc(format!(r#"mc
mn Authenticate
pa
paa va str SuperAdmin
paa va str {}"#,cnfroot.server.password)),stream,handler).unwrap();

	(stream,handler2) = messages::send_message(messages::transform_xmlrpc(String::from(r#"mc
mn EnableCallbacks
pa
paa va bool true"#)),stream,handler2).unwrap();

	(stream,handler2)
}

fn main() {
	let mut path = PathBuf::new();
	path.push(env::current_dir().expect("No cwd?"));
	path.push("cnf.toml");
	let filestr = fs::read_to_string(&path).expect("Couldn't read config");
	let cnfroot: structs::Config = toml::from_str(&filestr).unwrap();
	println!(r#"
        ..........             ..........       
       ,*//////////,.       .,//////////*,      
        .*//////////*,     .**/////////*.       
          ,*//////////,.  ,*/////////*,         
           .,*////////**,*//////////*.          
             .,//////////////(##%%(,            
               ,/(((((///((##%%%#*.             
                ,(%%%%%%%%%%%%#/,               
               */##%%%%%%%%#(**,,.              
             .,//////((((//*,,,,,,,.            
            ,/#%&&%#(*,,,,,,,*/(#%(/,           
          .*#%%%%%%%%#*. .*(#%%%%%%%(*.         
        .,*(%%%%%%%%(*.   .*(%%%%%%%%#/*.       
      .,*(#%%%%%%%%/.       ,/%%%%%%%%%%#(,     
     ./((((((((((/,           ,/((((((((((/,    

xrd v{}"#,&cnfroot.main.version);
	let sockarray = connect_server(&cnfroot,0x80000000);
	loops::event(sockarray.0,sockarray.1,cnfroot);
}
