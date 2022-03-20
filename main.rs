#![allow(non_snake_case)]
#![allow(non_camel_case_types)]
#![allow(unused_assignments)]
#[macro_use]

extern crate clone_all;
use std::net::TcpStream;
use std::io::prelude::*;
use std::io::BufReader;
use std::sync::{Arc,Mutex};
use std::fs::File;
use std::str;
use std::thread;
use std::env;
use std::usize;
use std::path::PathBuf;
use aho_corasick::AhoCorasick;
pub mod structs;
pub mod messages;
pub mod loops;
use loops::event;

pub fn connect_server(server: &structs::Server, handler: u32) -> (Arc<Mutex<TcpStream>>,Arc<Mutex<u32>>) {
	let stream = Arc::new(Mutex::new(TcpStream::connect(format!("{}:{}",&server.host,&server.port)).unwrap()));
	let mut handler = Arc::new(Mutex::new(handler));

	let mut cloned_stream = stream.lock().unwrap();
	cloned_stream.read(&mut [0;4]).unwrap();

	let mut ver = [0;12];
	cloned_stream.read(&mut ver).unwrap();

	drop(cloned_stream);

	assert_eq!(str::from_utf8(&ver).unwrap().trim_matches(char::from(0)),"GBXRemote 2");
	println!("Connection acquired to server.");

	handler = messages::send_message(messages::transform_xmlrpc(format!(r#"mc
mn Authenticate
pa
paa va str SuperAdmin
paa va str {}"#,&server.password)),Arc::clone(&stream),Arc::clone(&handler)).unwrap().1;

	handler = messages::send_message(messages::transform_xmlrpc(String::from(r#"mc
mn EnableCallbacks
pa
paa va bool true"#)),Arc::clone(&stream),Arc::clone(&handler)).unwrap().1;

	(stream,handler)
}

fn parse_xrd(parse: PathBuf) -> structs::Config {
	let fr = BufReader::new(File::open(&parse).expect("Couldn't open config"));
	let ac_findvh = AhoCorasick::new_auto_configured(&["^^"]);
	let ac_verbs = AhoCorasick::new_auto_configured(&["version","prefix","host","port","password","trackspath","admins","gametype"]);
	let mut cnfroot = structs::Config::default();
	let mut srvvec = Vec::new();
	let mut srvcount: u16 = 0;
	for line in fr.lines() {
		let lineu = line.unwrap();
		if ac_findvh.is_match(&lineu) {
			srvvec.push(structs::Server::default());
			srvcount+=1;
			continue;
		} if ac_verbs.is_match(&lineu) {
			let mat = ac_verbs.find(&lineu).unwrap();
			
			match mat {
				_ if mat.pattern() == 0 => cnfroot.main.version = (&lineu[..][&lineu.find("|").unwrap()+1..].to_string()).to_owned(),
				_ if mat.pattern() == 1 => cnfroot.main.prefix = (&lineu[..][&lineu.find("|").unwrap()+1..].to_string()).to_owned(),
				_ if mat.pattern() == 2 => if srvcount > 0 { srvvec[usize::from(srvcount-1)].host = (&lineu[..][&lineu.find("|").unwrap()+1..].to_string()).to_owned() } else { continue; },
				_ if mat.pattern() == 3 => if srvcount > 0 { srvvec[usize::from(srvcount-1)].port = (&lineu[..][&lineu.find("|").unwrap()+1..].to_string()).to_owned() } else { continue; },
				_ if mat.pattern() == 4 => if srvcount > 0 { srvvec[usize::from(srvcount-1)].password = (&lineu[..][&lineu.find("|").unwrap()+1..].to_string()).to_owned() } else { continue; },
				_ if mat.pattern() == 5 => if srvcount > 0 { srvvec[usize::from(srvcount-1)].trackspath = (&lineu[..][&lineu.find("|").unwrap()+1..].to_string()).to_owned() } else { continue; },
				_ if mat.pattern() == 6 => if srvcount > 0 { srvvec[usize::from(srvcount-1)].admins = (&lineu[..][&lineu.find("|").unwrap()+1..].to_string()).to_owned() } else { continue; },
				_ if mat.pattern() == 7 => if srvcount > 0 { srvvec[usize::from(srvcount-1)].gametype = (&lineu[..][&lineu.find("|").unwrap()+1..].to_string()).to_owned() } else { continue; },
				_ => structs::nop(),
			};
		}
	} cnfroot.servers = srvvec;
	cnfroot
}

fn main() {
	let mut path = PathBuf::new();
	path.push(env::current_dir().expect("No cwd?"));
	path.push("cnf.xrd");
	let cnfroot = parse_xrd(path);
	let mut handles = Vec::new();
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
	for x in &cnfroot.servers {
		let sockarray = connect_server(&x,0x80000000);
		handles.push(thread::spawn({clone_all!(cnfroot, x); move || {
			event(sockarray,(cnfroot.main,x));
		}}));
	} for x in handles {
		x.join().unwrap();
	}
}